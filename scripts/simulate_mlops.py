"""
MLOps Hot-Swapping Simulation Script
------------------------------------
This script acts as the "External Airflow/SageMaker Pipeline".
It demonstrates replacing the ML Service's prediction model securely
in production with zero downtime by exploiting Localstack S3 and gRPC.
"""

import os
import sys
import json
import uuid
import boto3
import subprocess
from pathlib import Path

# Fix module resolution to allow imports
sys.path.insert(0, str(Path(os.path.abspath(__file__)).parent.parent / "services" / "ml-service"))
sys.path.insert(0, str(Path(os.path.abspath(__file__)).parent.parent / "shared"))

import grpc
from aegis_shared.generated import ml_service_pb2, ml_service_pb2_grpc

BUCKET_NAME = "aegis-models"
MODELS_DIR = Path(__file__).parent.parent / "services" / "ml-service" / "models"

def get_s3_client():
    """Initializes Boto3 targeting localstack."""
    return boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1"
    )

def ensure_bucket_exists(s3):
    """Ensures the S3 bucket is instantiated on Localstack."""
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"[+] Bucket '{BUCKET_NAME}' already exists.")
    except Exception:
        print(f"[*] Creating bucket '{BUCKET_NAME}'...")
        s3.create_bucket(Bucket=BUCKET_NAME)

def prepare_artifacts():
    """Extracts base artifacts from the live container to simulate new files."""
    if not MODELS_DIR.exists():
        print("[*] Extracting base artifacts from live Docker container for the simulation...")
        subprocess.run([
            "docker", "cp", "aegis-risk-ml-service-1:/app/models", str(MODELS_DIR.parent)
        ], check=True)
    
    # Mutate the metadata to mathematically "prove" the hot-swap worked
    metadata_path = MODELS_DIR / "metadata.json"
    with open(metadata_path, "r") as f:
        meta = json.load(f)
    
    # We alter the version string so the grpc response logs visually change
    new_version = f"v2.0-{str(uuid.uuid4())[:4]}"
    meta["model_version"] = new_version
    
    with open(metadata_path, "w") as f:
        json.dump(meta, f)
        
    print(f"[+] Synthesized new model iteration: {new_version}")

def upload_to_s3(s3):
    """Uploads the ONNX weights, features, and metadata to object storage."""
    print("[*] Simulating pipeline artifact deployment to S3...")
    for artifact in ["risk_model.onnx", "features.json", "metadata.json"]:
        local_path = MODELS_DIR / artifact
        s3.upload_file(str(local_path), BUCKET_NAME, artifact)
        print(f"  -> Uploaded: {artifact}")

def trigger_hot_swap():
    """Uses gRPC to tell the production inference cluster to pull from S3."""
    print("[*] Triggering Zero-Downtime Pipeline Swap via gRPC...")
    channel = grpc.insecure_channel("localhost:50053")
    stub = ml_service_pb2_grpc.MLServiceStub(channel)
    
    req = ml_service_pb2.ReloadModelRequest(
        s3_bucket=BUCKET_NAME,
        s3_prefix=""
    )
    
    response = stub.ReloadModel(req)
    if response.success:
        print(f"\n[SUCCESS] Production Model Hot-Swapped Safely!")
        print(f"[INFO] New Engine Brain Registered: {response.new_version}")
    else:
        print(f"\n[ERROR] Pipeline Swap Failed: {response.message}")

if __name__ == "__main__":
    print("========================================")
    print(" AEGIS RISK - MLOPS PIPELINE SIMULATION ")
    print("========================================")
    
    s3 = get_s3_client()
    ensure_bucket_exists(s3)
    prepare_artifacts()
    upload_to_s3(s3)
    trigger_hot_swap()
    print("========================================\n")
