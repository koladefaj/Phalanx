"""gRPC client for Analyst Investigation Service."""

import grpc
from aegis_shared.generated import analyst_service_pb2, analyst_service_pb2_grpc, common_pb2
from aegis_shared.utils.logging import get_logger

logger = get_logger("analyst_grpc_client")

class AnalystClient:
    """gRPC client for the Analyst investigation service."""

    def __init__(self, channel: grpc.aio.Channel):
        self.channel = channel
        self.stub = analyst_service_pb2_grpc.AnalystServiceStub(self.channel)

    async def investigate_transaction(
        self,
        transaction_id: str,
        sender_id: str,
        correlation_id: str = "",
    ) -> dict:
        """Request a full AI analyst investigation via gRPC."""
        try:
            metadata = common_pb2.RequestMetadata(
                correlation_id=correlation_id,
                timestamp="",
            )
            request = analyst_service_pb2.InvestigateRequest(
                metadata=metadata,
                transaction_id=transaction_id,
                sender_id=sender_id,
            )

            response = await self.stub.InvestigateTransaction(
                request, 
                timeout=120.0 # Analysts can take a while
            )

            return {
                "summary": response.summary,
                "verdict": response.verdict,
                "confidence": response.confidence,
                "recommendation": response.recommendation,
                "agent_name": response.agent_name,
                "fallback_used": False,
            }
        except grpc.RpcError as e:
            logger.warning("analyst_service_unavailable", error=str(e))
            # Return a fallback response
            return {
                "summary": f"Investigation unavailable for {transaction_id}.",
                "verdict": "SUSPICIOUS",
                "confidence": "LOW",
                "recommendation": "REVIEW",
                "agent_name": "fallback-logic",
                "fallback_used": True,
            }
