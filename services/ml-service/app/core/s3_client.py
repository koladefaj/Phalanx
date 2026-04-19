"""S3 client for hot-swapping ML artifacts."""

import boto3
import botocore
from pathlib import Path
from typing import Tuple
from app.config import settings
import logging

logger = logging.getLogger("ml_s3_client")

class S3Client:
    """Handles S3 synchronization for hot-swapping ML models without downtime."""
    
    def __init__(self):
        # Configure Boto3, utilizing Localstack if running locally
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_ENDPOINT_URL if settings.AWS_ENDPOINT_URL else None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
    def download_artifacts(self, bucket: str, prefix: str = "") -> Tuple[bool, str]:
        """Download model artifacts from S3 to the local models directory."""
        try:
            # Ensure models directory exists
            Path("models").mkdir(parents=True, exist_ok=True)
            
            artifacts = ["risk_model.onnx", "features.json", "metadata.json"]
            
            for file in artifacts:
                s3_key = f"{prefix}/{file}" if prefix else file
                local_path = f"models/{file}"
                logger.info(f"Downloading {s3_key} from {bucket} to {local_path}...")
                
                self.s3.download_file(bucket, s3_key, local_path)
                
            return True, "Artifacts synchronized successfully."
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            msg = f"S3 Client Error: {error_code} - {str(e)}"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Unexpected error syncing artifacts: {str(e)}"
            logger.error(msg)
            return False, msg
