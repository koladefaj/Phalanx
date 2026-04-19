import json
import pickle
import onnxruntime as rt
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np

import logging
import threading
from app.config import settings

logger = logging.getLogger("ml_predictor")

class RiskPredictor:
    """Singleton class to hold the model and artifacts in memory."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super(RiskPredictor, cls).__new__(cls)
                    cls._instance._swap_lock = threading.Lock()
                    cls._instance._initialize()
        return cls._instance

    def reload(self):
        """Thread-safe reload of model parameters via hot-swapping."""
        logger.info("Hot-swapping ML model artifacts...")
        self._initialize()

    def _initialize(self):
        # Load ONNX session from config path
        model_path = settings.MODEL_PATH
        new_session = rt.InferenceSession(model_path)
        new_input_name = new_session.get_inputs()[0].name
        
        # Load feature names from config path
        with open(settings.FEATURE_NAMES_PATH, "r") as f:
            new_feature_names = json.load(f)
        
        # Load metadata/threshold from config path
        with open(settings.THRESHOLD_PATH, "r") as f:
            metadata = json.load(f)
            new_threshold = metadata["threshold"]
            new_model_version = metadata.get("model_version", settings.MODEL_VERSION)
        
        # Atomic swap
        with self._swap_lock:
            self.session = new_session
            self.input_name = new_input_name
            self.feature_names = new_feature_names
            self.threshold = new_threshold
            self.model_version = new_model_version

        logger.info(
            "predictor_initialized_or_reloaded",
            model_version=self.model_version,
            num_features=len(self.feature_names),
            threshold=self.threshold,
        )

    def _assemble_features(self, req: Any) -> np.ndarray:
        """
        Calculates state changes and maps the gRPC request to the exact 
        18-feature array expected by the model.
        """
        # Calculate intermediate/state-change variables
        amount_vs_avg_ratio = min(req.amount / max(req.sender_avg_amount, 1), 50.0)
        is_new_account = 1.0 if req.account_age_hours < 24 else 0.0
        is_new_receiver = 1.0 if req.old_balance_dest == 0 else 0.0
        velocity_score = min(req.txn_count_1h / 10.0, 1.0)
        
        # Calculate expected new balances (simulating ledger math)
        new_balance_orig = req.old_balance_orig - req.amount
        new_balance_dest = req.old_balance_dest + req.amount
        
        balance_diff_orig = max(min(req.old_balance_orig - new_balance_orig - req.amount, 1e6), -1e6)
        balance_diff_dest = max(min(new_balance_dest - req.old_balance_dest - req.amount, 1e6), -1e6)

        # Map Categoricals
        type_map = {"PAYMENT": 0, "TRANSFER": 1, "CASH_OUT": 2, "CASH_IN": 3, "DEBIT": 4}
        txn_type = type_map.get(req.transaction_type.upper(), 0)
        is_geo_mismatch = 1.0 if req.sender_country != req.receiver_country else 0.0
        is_web_channel = 1.0 if req.channel.lower() == "web" else 0.0

        # Build Dictionary (Unordered)
        feature_dict = {
            "amount": req.amount,
            "amount_vs_avg_ratio": amount_vs_avg_ratio,
            "sender_txn_count": req.sender_txn_count,
            "sender_avg_amount": req.sender_avg_amount,
            "sender_max_amount": req.sender_max_amount,
            "sender_total_volume": req.sender_total_volume,
            "account_age_hours": req.account_age_hours,
            "txn_count_1h": req.txn_count_1h,
            "velocity_score": velocity_score,
            "is_new_account": is_new_account,
            "is_new_receiver": is_new_receiver,
            "balance_diff_orig": balance_diff_orig,
            "balance_diff_dest": balance_diff_dest,
            "oldBalanceOrig": req.old_balance_orig,
            "newBalanceOrig": new_balance_orig,
            "oldBalanceDest": req.old_balance_dest,
            "newBalanceDest": new_balance_dest,
            "txn_type": txn_type,
            "is_geo_mismatch": is_geo_mismatch,
            "is_web_channel": is_web_channel
        }

        # ENFORCEMENT: Build array in the EXACT order of self.feature_names
        try:
            ordered_features = [feature_dict[fname] for fname in self.feature_names]
            return np.array([ordered_features]) # 2D array for XGBoost predict
        except KeyError as e:
            logger.error(f"Missing required feature for model inference: {e}")
            raise ValueError(f"Feature assembly failed. Missing: {e}")

    def predict(self, grpc_request):
        """Runs the inference and applies business logic thresholds."""
        X_infer = self._assemble_features(grpc_request).astype(np.float32)  # Ensure correct dtype for ONNX
        
        # ONNX inference
        onnx_pred = self.session.run(None, {self.input_name: X_infer})
        risk_score = float(onnx_pred[1][0][1]) # Get probability of class 1 (fraud)
        
        # Business Logic Decision Tree
        if risk_score >= 0.90:
            decision = "BLOCK"
        elif risk_score >= self.threshold:
            decision = "REVIEW"
        else:
            decision = "APPROVE"
            
        return risk_score, decision