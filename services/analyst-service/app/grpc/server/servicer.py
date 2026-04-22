import grpc
from aegis_shared.utils.logging import get_logger
from aegis_shared.generated import analyst_service_pb2, analyst_service_pb2_grpc, common_pb2
from app.services.base import BaseAgentService

logger = get_logger("analyst_servicer")

class AnalystServicer(analyst_service_pb2_grpc.AnalystServiceServicer):
    """gRPC servicer for AI Analyst investigations."""

    def __init__(self, analyst_service: BaseAgentService):
        self.analyst_service = analyst_service

    async def InvestigateTransaction(self, request, context):
        """Run a full fraud investigation on a transaction."""
        transaction_id = request.transaction_id
        sender_id = request.sender_id
        
        logger.info("received_investigation_request", transaction_id=transaction_id, sender_id=sender_id)

        try:
            # The analyst returns a string report. 
            report = await self.analyst_service.investigate_transaction(transaction_id, sender_id)
            
            # Basic parsing of the report to extract verdict and recommendation
            verdict = "SUSPICIOUS"
            confidence = "MEDIUM"
            recommendation = "REVIEW"
            
            if "VERDICT: LEGITIMATE" in report.upper():
                verdict = "LEGITIMATE"
                recommendation = "ALLOW"
            elif "VERDICT: FRAUDULENT" in report.upper():
                verdict = "FRAUDULENT"
                recommendation = "BLOCK"
                
            if "CONFIDENCE: HIGH" in report.upper():
                confidence = "HIGH"
            elif "CONFIDENCE: LOW" in report.upper():
                confidence = "LOW"
            
            return analyst_service_pb2.InvestigateResponse(
                transaction_id=transaction_id,
                verdict=verdict,
                confidence=confidence,
                summary=report,
                recommendation=recommendation,
                agent_name=self.analyst_service.get_agent_name()
            )
            
        except Exception as e:
            logger.error("investigation_failed", transaction_id=transaction_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Investigation failed: {str(e)}")
            return analyst_service_pb2.InvestigateResponse()

    async def HealthCheck(self, request, context):
        """Standard health check."""
        return common_pb2.HealthCheckResponse(
            status="SERVING",
            service_name="analyst-service",
            version="0.1.0"
        )
