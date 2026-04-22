"""Mapper to convert between internal models and gRPC protobuf messages."""

from datetime import datetime
from uuid import UUID
from decimal import Decimal

from aegis_shared.generated.risk_engine_pb2 import (
    EvaluateRiskRequest, 
    EvaluateRiskResponse,
    GetRiskResultResponse,
    GetRiskResultRequest
)
from aegis_shared.schemas.risk import RiskAssessment, RiskFactor, RiskResultResponse, AnalystInvestigation
from aegis_shared.enums import RiskDecision, RiskLevel


class RiskClientMapper:
    """Centralized mapping between business models and Risk Engine protobuf messages."""

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
    def to_evaluate_proto(
        cls,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        sender_id: str,
        receiver_id: str,
        sender_country: str,
        receiver_country: str,
        device_fingerprint: str = "",
        ip_address: str = "",
        channel: str = "web",
        created_at: datetime | None = None,
    ) -> EvaluateRiskRequest:
        """Build EvaluateRiskRequest proto from explicit fields.
        
        Takes explicit kwargs — no magic dict unpacking so the interface
        is clear and type-checkable.
        """
        return EvaluateRiskRequest(
            transaction_id=cls._fmt(transaction_id),
            amount=float(amount),           # proto field is double
            currency=currency,
            sender_id=sender_id,
            receiver_id=receiver_id,
            sender_country=sender_country or "",
            receiver_country=receiver_country or "",
            device_fingerprint=device_fingerprint or "",
            ip_address=ip_address or "",
            channel=channel or "web",
            created_at=cls._fmt(created_at) if created_at else "",
        )

    @classmethod
    def from_evaluate_proto(cls, proto: EvaluateRiskResponse) -> RiskAssessment:
        """Convert EvaluateRiskResponse proto → RiskAssessment Pydantic model."""
        risk_factors = [
            RiskFactor(
                factor=rf.factor,
                severity=rf.severity,
                detail=rf.detail,
            )
            for rf in proto.risk_factors
        ]

        return RiskAssessment(
            transaction_id=proto.transaction_id,
            decision=RiskDecision(proto.decision),
            risk_score=float(proto.risk_score),
            risk_level=RiskLevel(proto.risk_level),
            confidence=proto.confidence or "MEDIUM",
            risk_factors=risk_factors,
            rule_score=float(proto.rule_score) if hasattr(proto, "rule_score") else 0.0,
            processing_time_ms=float(proto.processing_time_ms),
            model_version=proto.model_version or "1.0.0",
        )

    @classmethod
    def from_get_proto(cls, proto: GetRiskResultResponse) -> RiskResultResponse:
        """Convert GetRiskResultResponse proto → RiskResultResponse Pydantic model."""
        risk_factors = [
            RiskFactor(
                factor=rf.factor,
                severity=rf.severity,
                detail=rf.detail,
            )
            for rf in proto.risk_factors
        ]

        analyst = None
        if proto.agent_summary:
            analyst = AnalystInvestigation(
                agent_summary=proto.agent_summary,
                agent_risk_factors=list(proto.agent_risk_factors),
                agent_recommendation=proto.agent_recommendation,
                agent_confidence=0.8, # Proto doesn't have it yet, using default
                agent_fallback_used=proto.agent_fallback_used
            )

        return RiskResultResponse(
            transaction_id=proto.transaction_id,
            risk_score=float(proto.risk_score),
            risk_level=RiskLevel(proto.risk_level),
            decision=RiskDecision(proto.decision),
            triggered_rules=list(proto.agent_risk_factors),
            risk_factors=risk_factors,
            analyst_investigation=analyst,
            evaluated_at=datetime.fromisoformat(proto.evaluated_at) if proto.evaluated_at else datetime.now()
        )