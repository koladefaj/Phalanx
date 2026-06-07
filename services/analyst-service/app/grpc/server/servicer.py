import grpc

from aegis_shared.generated import analyst_service_pb2, analyst_service_pb2_grpc, common_pb2
from aegis_shared.utils.logging import get_logger
from app.services.base import BaseAgentService

logger = get_logger("analyst_servicer")


class AnalystServicer(analyst_service_pb2_grpc.AnalystServiceServicer):

    def __init__(self, analyst_service: BaseAgentService):
        self.analyst_service = analyst_service

    async def InvestigateTransaction(self, request, context):
        transaction_id = request.transaction_id
        sender_id = request.sender_id

        logger.info(
            "received_investigation_request",
            transaction_id=transaction_id,
            sender_id=sender_id,
        )

        try:
            report = await self.analyst_service.investigate_transaction(
                transaction_id, sender_id
            )

            return analyst_service_pb2.InvestigateResponse(
                transaction_id=transaction_id,
                verdict=report.verdict,
                confidence=report.confidence_label(),
                summary=report.summary,
                recommendation=report.recommendation,
                agent_name=self.analyst_service.get_agent_name(),
            )

        except Exception as e:
            logger.error("investigation_failed", transaction_id=transaction_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Investigation failed: {str(e)}")
            return analyst_service_pb2.InvestigateResponse()

    async def HealthCheck(self, request, context):
        return common_pb2.HealthCheckResponse(
            status="SERVING",
            service_name="analyst-service",
            version="0.1.0",
        )
