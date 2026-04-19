"""ML gRPC servicer — implements high-speed ONNX inference."""

import grpc
import time
from aegis_shared.generated import ml_service_pb2
from aegis_shared.generated import ml_service_pb2_grpc
from aegis_shared.utils.logging import get_logger

from app.core.predictor import RiskPredictor

logger = get_logger("ml_servicer")


class MLServicer(ml_service_pb2_grpc.MLServiceServicer):
    """gRPC servicer implementing the ML Prediction Service."""

    def __init__(self, predictor: RiskPredictor):
        # Initialize the Singleton predictor so the ONNX model stays in memory
        self.predictor = predictor
        logger.info("ml_servicer_initialized", status="ready")

    async def ScoreTransaction(
        self, request, context
    ) -> ml_service_pb2.ScoreTransactionResponse:
        """Evaluate a transaction using the ONNX model."""
        start_time = time.time()

        logger.info(
            "score_transaction_rpc",
            transaction_id=request.transaction_id,
            amount=request.amount,
        )

        try:
            # 1. Run inference (Predictor handles assembly and ONNX execution)
            anomaly_score, decision = self.predictor.predict(request)

            processing_time_ms = (time.time() - start_time) * 1000

            logger.info(
                "prediction_complete",
                transaction_id=request.transaction_id,
                anomaly_score=anomaly_score,
                decision=decision,
                latency_ms=round(processing_time_ms, 2),
            )

            # 2. Return Proto Response — fields match ml_service.proto
            return ml_service_pb2.ScoreTransactionResponse(
                transaction_id=request.transaction_id,
                anomaly_score=anomaly_score,
                decision=decision,
                model_version=self.predictor.model_version,
                fallback_used=False,
                processing_time_ms=processing_time_ms,
            )

        except ValueError as e:
            # Caught an assembly/feature mapping error
            logger.warning("invalid_inference_features", error=str(e))
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error("inference_failed", error=str(e))
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal model inference failure"
            )

    async def ReloadModel(
        self, request, context
    ) -> ml_service_pb2.ReloadModelResponse:
        """Trigger S3 Sync and Swap Predictor Engine Brain."""
        logger.info(
            "reload_model_requested",
            bucket=request.s3_bucket,
            prefix=request.s3_prefix,
        )

        from app.core.s3_client import S3Client

        s3_client = S3Client()
        success, message = s3_client.download_artifacts(
            bucket=request.s3_bucket, prefix=request.s3_prefix
        )

        if not success:
            logger.warning("reload_model_download_failed", error=message)
            return ml_service_pb2.ReloadModelResponse(
                success=False,
                message=message,
                new_version=self.predictor.model_version
            )

        try:
            self.predictor.reload()
            return ml_service_pb2.ReloadModelResponse(
                success=True,
                message="Model hot-swapped successfully.",
                new_version=self.predictor.model_version,
            )
        except Exception as e:
            logger.error("reload_model_swap_failed", error=str(e))
            return ml_service_pb2.ReloadModelResponse(
                success=False,
                message=f"Failed to hot-swap singleton: {str(e)}",
                new_version=self.predictor.model_version,
            )
