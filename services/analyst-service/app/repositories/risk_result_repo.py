"""Write-back repository for the analyst-service.

The agent service reads from the DB via read-only models, but writes the
investigation result back to the risk_results table that is owned by
the risk-engine-service. Both services share the same Postgres instance
(aegis_risk DB), which makes this safe and avoids adding gRPC surface.
"""

import uuid
from typing import Optional
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.read_only import RiskResultReadOnly
from aegis_shared.utils.logging import get_logger

logger = get_logger("analyst_risk_result_repo")


class AnalystRiskResultRepository:
    """Write-back operations for analyst investigation results in risk_results."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
    ) -> bool:
        """Atomically update risk_results with analyst investigation fields.

        Returns True if the row was found and updated, False otherwise.
        """
        try:
            stmt = (
                update(RiskResultReadOnly)
                .where(RiskResultReadOnly.transaction_id == uuid.UUID(transaction_id))
                .values(
                    agent_summary=agent_summary,
                    agent_risk_factors=agent_risk_factors,
                    agent_recommendation=agent_recommendation,
                    agent_confidence=agent_confidence,
                    agent_model=agent_model,
                    agent_latency_ms=agent_latency_ms,
                    agent_fallback_used=agent_fallback_used,
                    version=RiskResultReadOnly.version + 1,
                )
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            rows_affected = result.rowcount
            logger.info(
                "analyst_investigation_written_back",
                transaction_id=transaction_id,
                rows_affected=rows_affected,
            )
            return rows_affected > 0
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "analyst_writeback_failed",
                transaction_id=transaction_id,
                error=str(e),
            )
            raise

    async def is_already_investigated(self, transaction_id: str) -> bool:
        """Check if a transaction already has an analyst summary (idempotency guard)."""
        stmt = (
            select(RiskResultReadOnly.agent_summary)
            .where(RiskResultReadOnly.transaction_id == uuid.UUID(transaction_id))
            .where(RiskResultReadOnly.agent_summary.is_not(None))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
