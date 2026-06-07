from typing import Literal
from pydantic import BaseModel, Field


class FraudInvestigationReport(BaseModel):
    """Structured output of a fraud investigation.

    Returned by every LLM provider via instructor or native structured output.
    No regex parsing ever touches this — the model validates the shape.
    """

    summary: str = Field(
        description="2-3 sentence professional narrative explaining key findings"
    )
    risk_factors: list[str] = Field(
        description="Specific risk signals identified, one per list item"
    )
    verdict: Literal["FRAUDULENT", "SUSPICIOUS", "LEGITIMATE"] = Field(
        description="Overall assessment of the transaction"
    )
    recommendation: Literal["BLOCK", "REVIEW", "ALLOW"] = Field(
        description="Recommended action"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the verdict: 0.0 = uncertain, 1.0 = certain",
    )

    def confidence_label(self) -> str:
        if self.confidence >= 0.8:
            return "HIGH"
        if self.confidence >= 0.5:
            return "MEDIUM"
        return "LOW"
