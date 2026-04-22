"""Risk result repository — persist and retrieve risk evaluation results."""

from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy import update

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models.risk_result import RiskResult
from aegis_shared.utils.logging import get_logger

logger = get_logger("risk_result_repo")


class RiskResultRepository:
    """Database operations for RiskResult model."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(
        self,
        assessment,
        transaction_data: dict,
        rule_flags: list[dict],
        rule_score: float,              
        ml_anomaly_score: Optional[float],
        ml_model_version: Optional[str],
        ml_fallback_used: bool,
        ml_features_used: Optional[dict],
        correlation_id: Optional[str] = None,
    ) -> None:
        """Atomic upsert for risk results to ensure idempotency."""
        
        stmt = insert(RiskResult).values(
            transaction_id=UUID(assessment.transaction_id),
            amount=Decimal(str(transaction_data.get("amount", 0))),
            currency=transaction_data.get("currency"),
            sender_id=transaction_data.get("sender_id"),
            receiver_id=transaction_data.get("receiver_id"),
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level.value,
            decision=assessment.decision,
            confidence=assessment.confidence,
            rule_score=rule_score,       
            triggered_rules=transaction_data.get("triggered_rules", []),  # from payload
            rule_flags=rule_flags,
            ml_anomaly_score=ml_anomaly_score,
            ml_model_version=ml_model_version,
            ml_fallback_used=ml_fallback_used,
            ml_features_used=ml_features_used,
            processing_time_ms=assessment.processing_time_ms,
            worker_id=str(transaction_data.get("worker_id", "")),
            correlation_id=correlation_id,
            version=1
        ).on_conflict_do_nothing(index_elements=['transaction_id']) 
            
            
        await self.session.execute(stmt)

    async def update_analyst_investigation(
        self,
        transaction_id: str,
        agent_summary: str,
        agent_risk_factors: list[str],
        agent_recommendation: str,
        agent_confidence: float,
        agent_model: str,
        agent_latency_ms: float,
        agent_fallback_used: bool = False,
    ) -> None:
        """Direct Update pattern (Atomic) to avoid SELECT FOR UPDATE overhead."""
        stmt = (
            update(RiskResult)
            .where(RiskResult.transaction_id == UUID(transaction_id))
            .values(
                agent_summary=agent_summary,
                agent_risk_factors=agent_risk_factors,
                agent_recommendation=agent_recommendation,
                agent_confidence=agent_confidence,
                agent_model=agent_model,
                agent_latency_ms=agent_latency_ms,
                agent_fallback_used=agent_fallback_used,
                version=RiskResult.version + 1,
            )
        )
        await self.session.execute(stmt)
            
        logger.info("analyst_investigation_updated_atomically", transaction_id=transaction_id)

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[RiskResult]:
        """Fetch a risk result by its transaction UUID."""
        from sqlalchemy import select
        
        stmt = select(RiskResult).where(RiskResult.transaction_id == UUID(transaction_id))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()