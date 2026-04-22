"""Risk Engine Servicer Mapper — converts internal models to proto responses."""

from datetime import datetime
from uuid import UUID
from decimal import Decimal

from aegis_shared.generated.risk_engine_pb2 import (
    EvaluateRiskResponse,
    GetRiskResultResponse,
    RiskFactor,
    RuleFlagResult,
)
from aegis_shared.schemas.risk import RiskAssessment, RiskResult


class RiskServicerMapper:
    """Maps RiskAssessment / RiskResult → proto response messages."""

    @staticmethod
    def _fmt(value) -> str:
        """Convert any value to a proto-safe string."""
        if value is None:
            return ""
        if isinstance(value, (UUID, Decimal)):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "value"):  # Enum
            return str(value.value)
        return str(value)

    @classmethod
    def to_create_proto(cls, result: RiskAssessment) -> EvaluateRiskResponse:
        """Convert RiskAssessment → EvaluateRiskResponse.

        This is the SYNC response — only decision + score + risk_factors.
        No LLM fields, no rule flags, no ML detail.
        """
        return EvaluateRiskResponse(
            transaction_id=cls._fmt(result.transaction_id),
            decision=result.decision.value if hasattr(result.decision, "value") else str(result.decision),
            risk_score=float(result.risk_score),
            risk_level=result.risk_level.value if hasattr(result.risk_level, "value") else str(result.risk_level),
            confidence=result.confidence or "MEDIUM",
            risk_factors=[
                RiskFactor(
                    factor=rf.factor,
                    severity=rf.severity,
                    detail=rf.detail or "",
                )
                for rf in (result.risk_factors or [])
            ],
            processing_time_ms=float(result.processing_time_ms),
            model_version=result.model_version or "1.0.0",
        )

    @classmethod
    def to_get_result_proto(cls, result) -> GetRiskResultResponse:
        """Convert RiskResult (SQLAlchemy model) → GetRiskResultResponse.

        This is the ASYNC response — full detail including Agent investigation,
        rule flags, and ML score. Fetched by client after webhook notification.
        """
        # Note: 'result' is typically the SQLAlchemy model instance here,
        # which has flat columns rather than nested MLScore/AgentInvestigation objects.
        
        # Safely extract agent fields
        agent_summary = getattr(result, "agent_summary", "")
        agent_factors = getattr(result, "agent_risk_factors", [])
        agent_rec = getattr(result, "agent_recommendation", "")
        agent_fallback = getattr(result, "agent_fallback_used", True)

        return GetRiskResultResponse(
            transaction_id=cls._fmt(result.transaction_id),
            decision=result.decision.value if hasattr(result.decision, "value") else str(result.decision),
            risk_score=float(result.risk_score),
            risk_level=result.risk_level.value if hasattr(result.risk_level, "value") else str(result.risk_level),

            # Inline risk factors summary
            risk_factors=[
                RiskFactor(
                    factor=rf.factor,
                    severity=rf.severity,
                    detail=rf.detail or "",
                )
                for rf in (getattr(result, "risk_factors", []) or [])
            ],

            # Rule engine detail
            rule_flags=[
                RuleFlagResult(
                    rule_name=rf.get("rule", ""),
                    triggered=rf.get("triggered", False),
                    score=float(rf.get("score", 0.0)),
                    reason=rf.get("reason", ""),
                )
                for rf in (result.rule_flags or [])
            ] if isinstance(result.rule_flags, list) else [],

            # ML detail
            ml_anomaly_score=float(getattr(result, "ml_anomaly_score", 0.0) or 0.0),
            ml_fallback_used=getattr(result, "ml_fallback_used", True),
            ml_model_version=getattr(result, "ml_model_version", ""),

            # Agent investigation — may be empty if async job not complete yet
            agent_summary=agent_summary or "",
            agent_risk_factors=agent_factors or [],
            agent_recommendation=agent_rec or "",
            agent_fallback_used=agent_fallback,

            # Metadata
            processing_time_ms=float(getattr(result, "processing_time_ms", 0.0) or 0.0),
            worker_id=cls._fmt(getattr(result, "worker_id", "")),
            evaluated_at=cls._fmt(result.evaluated_at),
        )