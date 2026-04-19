"""PaySim model trainer — builds fraud detection model from PaySim dataset for AegisRisk."""

import json
import pickle
import onnxmltools
from onnxmltools.convert.common.data_types import FloatTensorType
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from xgboost import XGBClassifier
from aegis_shared.utils.logging import get_logger
from app.config import settings

logger = get_logger("ml_trainer")


# Features aligned with the Gateway schema AND the enrichment phase
FEATURES = [
    # Financial Velocity & Stats (Fetched from Redis during inference)
    "amount",
    "amount_vs_avg_ratio",
    "sender_txn_count",
    "sender_avg_amount",
    "sender_max_amount",
    "sender_total_volume",
    "account_age_hours",
    "txn_count_1h",
    "velocity_score",
    # State Changes (Calculated during inference based on DB lookups)
    "is_new_account",
    "is_new_receiver",
    "balance_diff_orig",
    "balance_diff_dest",
    "oldBalanceOrig",
    "newBalanceOrig",
    "oldBalanceDest",
    "newBalanceDest",
    # Gateway Metadata (Passed directly from FastAPI payload)
    "txn_type",
    "is_geo_mismatch",  # Derived from sender_country != receiver_country
    "is_web_channel",  # Derived from channel == "web"
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features from raw PaySim data, synthesizing Gateway schemas."""

    # --- CRITICAL FIX: Standardize PaySim column names ---
    # This maps the lowercase 'b' in your CSV to the names used in FEATURES
    df = df.rename(
        columns={
            "oldbalanceOrg": "oldBalanceOrig",
            "newbalanceOrig": "newBalanceOrig",
            "oldbalanceDest": "oldBalanceDest",
            "newbalanceDest": "newBalanceDest",
        }
    )

    # 1. Per-sender stats (simulates historical lookup via Redis)
    sender_stats = (
        df.groupby("nameOrig")
        .agg(
            sender_txn_count=("amount", "count"),
            sender_total_volume=("amount", "sum"),
            sender_avg_amount=("amount", "mean"),
            sender_max_amount=("amount", "max"),
            account_age_hours=("step", "min"),
        )
        .reset_index()
    )
    df = df.merge(sender_stats, on="nameOrig", how="left")

    df["amount_vs_avg_ratio"] = (
        df["amount"] / df["sender_avg_amount"].clip(lower=1)
    ).clip(upper=50)

    # Now this will find 'oldBalanceDest' correctly after the rename
    df["is_new_account"] = (df["account_age_hours"] < 24).astype(float)
    df["is_new_receiver"] = (df["oldBalanceDest"] == 0).astype(float)

    # 2. Balance discrepancies
    df["balance_diff_orig"] = (
        df["oldBalanceOrig"] - df["newBalanceOrig"] - df["amount"]
    ).clip(-1e6, 1e6)
    df["balance_diff_dest"] = (
        df["newBalanceDest"] - df["oldBalanceDest"] - df["amount"]
    ).clip(-1e6, 1e6)

    # 3. Transaction type mapping
    type_map = {"PAYMENT": 0, "TRANSFER": 1, "CASH_OUT": 2, "CASH_IN": 3, "DEBIT": 4}
    df["txn_type"] = df["type"].map(type_map).fillna(0)

    # 4. Velocity
    df["txn_count_1h"] = df.groupby(["nameOrig", "step"])["amount"].transform("count")
    df["velocity_score"] = (df["txn_count_1h"] / 10).clip(upper=1.0)

    # 5. Synthetic Gateway Features
    np.random.seed(42)
    df["is_geo_mismatch"] = np.where(
        df["isFraud"] == 1,
        np.random.choice([1, 0], size=len(df), p=[0.75, 0.25]),
        np.random.choice([1, 0], size=len(df), p=[0.05, 0.95]),
    )
    df["is_web_channel"] = np.where(
        (df["isFraud"] == 1) & (df["type"].isin(["CASH_OUT", "TRANSFER"])),
        np.random.choice([1, 0], size=len(df), p=[0.85, 0.15]),
        np.random.choice([1, 0], size=len(df), p=[0.40, 0.60]),
    )

    return df


def train(
    data_path: str = settings.PAYSIM_DATA_PATH,
    model_path: str = settings.MODEL_PATH,
    feature_names_path: str = settings.FEATURE_NAMES_PATH,
    threshold_path: str = settings.THRESHOLD_PATH,
    model_version: str = settings.MODEL_VERSION,
) -> dict:
    """Train XGBoost fraud detection model on PaySim data."""
    logger.info(f"training_started | data_path={data_path}")

    df = pd.read_csv(data_path)
    logger.info(f"data_loaded | rows={len(df)} | fraud_rate={df['isFraud'].mean():.4f}")

    # Focus only on high-risk transaction types mapped in Pydantic
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])].copy()
    logger.info(f"filtered_to_fraud_types | rows={len(df)}")

    df = build_features(df)

    # Ensure columns match FEATURES exactly to prevent inference shape errors
    X = df[FEATURES].fillna(0)
    y = df["isFraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Handle class imbalance heavily
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    logger.info(f"class_balance | scale_pos_weight={float(scale_pos_weight):.2f}")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        random_state=42,
        n_jobs=-1,
    )

    # ---------------------------------------------------------
    # CRITICAL FIX: Convert to raw numpy arrays for ONNX safety
    # ---------------------------------------------------------
    X_train_np = X_train.to_numpy()
    X_test_np = X_test.to_numpy()
    y_train_np = y_train.to_numpy()
    y_test_np = y_test.to_numpy()

    model.fit(
        X_train_np,
        y_train_np,
        eval_set=[(X_test_np, y_test_np)],
        verbose=False,
    )

    # 1. Convert to ONNX
    initial_type = [('float_input', FloatTensorType([None, len(FEATURES)]))]
    onx = onnxmltools.convert_xgboost(model, initial_types=initial_type)
    
    # Save ONNX dynamically
    onnx_path = Path(model_path)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())
        
    logger.info(f"Artifacts saved | ONNX model ready at {onnx_path}")

    # 2. CRITICAL FIX: Use the Numpy arrays for evaluation!
    y_pred_proba = model.predict_proba(X_test_np)[:, 1]
    auc = roc_auc_score(y_test_np, y_pred_proba)
    logger.info(f"model_trained | auc={round(auc, 4)}")

    # 3. Optimal threshold for F1 Score
    thresholds = np.arange(0.1, 0.9, 0.01)
    f1_scores = []
    for t in thresholds:
        preds = (y_pred_proba >= t).astype(int)
        tp = ((preds == 1) & (y_test_np == 1)).sum()
        fp = ((preds == 1) & (y_test_np == 0)).sum()
        fn = ((preds == 0) & (y_test_np == 1)).sum()
        precision = tp / (tp + fp + 1e-9)
        recall = tp / (tp + fn + 1e-9)
        f1 = 2 * precision * recall / (precision + recall + 1e-9)
        f1_scores.append(f1)

    optimal_threshold = float(thresholds[np.argmax(f1_scores)])
    logger.info(f"optimal_threshold | threshold={optimal_threshold:.2f}")

    # 4. Save JSON Metadata
    with open(feature_names_path, "w") as f:
        json.dump(FEATURES, f)
    
    with open(threshold_path, "w") as f:
        json.dump(
            {
                "threshold": optimal_threshold,
                "auc": round(auc, 4),
                "model_version": model_version,
            },
            f,
        )

    logger.info(f"artifacts_saved | metadata ready in {Path(threshold_path).parent}")

    report = classification_report(
        y_test_np,  # Use Numpy array here too!
        (y_pred_proba >= optimal_threshold).astype(int),
        output_dict=True,
    )

    return {
        "auc": round(auc, 4),
        "threshold": optimal_threshold,
        "model_version": model_version,
        "classification_report": report,
    }

if __name__ == "__main__":
    # Use settings for standardized paths
    train()
