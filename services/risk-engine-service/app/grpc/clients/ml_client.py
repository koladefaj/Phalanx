"""gRPC client for ML Service."""

import grpc
from aegis_shared.generated import ml_service_pb2_grpc
from app.mappers.ml_client_mapper import MLClientMapper
from app.config import settings
from aegis_shared.utils.logging import get_logger

logger = get_logger("ml_grpc_client")


class MLGRPCClient:
    """gRPC client for the ML anomaly detection service.

    Used by the RiskOrchestrator to get anomaly scores.
    Falls back gracefully if the ML service is unavailable.
    """

    def __init__(self, channel: grpc.aio.Channel):
        self.channel = channel
        self.stub = ml_service_pb2_grpc.MLServiceStub(self.channel)

    async def score_transaction(
        self,
        transaction_data: dict,
        features: dict | None = None,
    ) -> dict:
        """Score a transaction for anomalies via gRPC.

        Args:
            transaction_data: Transaction event data from EvaluateRiskRequest.
            features: Enrichment features from account profile.

        Returns:
            Dict with anomaly_score, model_version, fallback_used.
        """
        transaction_id = transaction_data.get("transaction_id", "unknown")

        try:
            # Merge enrichment features into data for the mapper
            enriched_data = {**transaction_data}
            if features:
                enriched_data.update(features)

            # 1. Map internal enriched dict to Protobuf request
            request = MLClientMapper.to_score_proto(enriched_data)

            # 2. Call ML Service via gRPC
            response = await self.stub.ScoreTransaction(
                request, timeout=settings.GRPC_TIMEOUT,
            )

            logger.info(
                "ml_response_received",
                transaction_id=transaction_id,
                anomaly_score=response.anomaly_score,
                decision=response.decision,
                latency_ms=round(response.processing_time_ms, 2),
            )

            # 3. Return mapped dictionary for business logic
            return {
                "anomaly_score": response.anomaly_score,
                "decision": response.decision,
                "model_version": response.model_version,
                "fallback_used": response.fallback_used,
            }

        except grpc.RpcError as e:
            logger.error(
                "grpc_score_transaction_failed",
                transaction_id=transaction_id,
                code=str(e.code()),
                details=e.details(),
            )
            raise

    async def close(self) -> None:
        """Close the gRPC channel. Call during app shutdown."""
        await self.channel.close()
