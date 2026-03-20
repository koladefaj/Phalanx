"""Risk score calculation and categorization."""

from aegis_shared.enums import RiskLevel, RiskDecision
from aegis_shared.utils.logging import get_logger

logger = get_logger("scorer")


class RiskScorer:
    """Calculates final risk scores from rule and ML inputs.

    Score formula:
        final_score = (rule_score * rule_weight) + (ml_score * 100 * ml_weight)

    Risk categories (relaxed for low‑risk transactions):
        LOW:      0–30
        MEDIUM:   30–50
        HIGH:     50–75
        CRITICAL: 75–100
    """

    def calculate_rule_score(self, rule_results: list[dict]) -> float:
        """Calculate aggregate score from rule evaluations with severity weighting."""
        if not rule_results:
            return 0.0

        triggered = [r for r in rule_results if r.get("triggered", False)]

        if not triggered:
            return 0.0

        
        weighted_total = 0.0
        for r in triggered:
            base_score = r.get("score", 0.0)
            severity = r.get("severity", "MEDIUM")
            
            # Severity multipliers (reduced)
            if severity == "HIGH":
                weighted_total += base_score * 2.5   
            elif severity == "MEDIUM":
                weighted_total += base_score * 1.2
            else:  # LOW
                weighted_total += base_score * 0.7

        # Additional boost for multiple HIGH severity rules (reduced)
        high_count = sum(1 for r in triggered if r.get("severity") == "HIGH")
        if high_count >= 2:
            weighted_total *= 1.2                   
        elif high_count == 1:
            weighted_total *= 1.08                      

        # Normalize against TOTAL rules
        max_possible = len(rule_results)
        normalized = (weighted_total / max_possible) * 100

        logger.debug(
            "rule_score_calculation",
            triggered_count=len(triggered),
            high_count=high_count,
            total_rules=max_possible,
            weighted_total=weighted_total,
            normalized=normalized,
        )

        return min(100.0, max(0.0, normalized))

    def calculate_final_score(
        self,
        rule_score: float,
        ml_score: float,
        rule_weight: float = 0.6,
        ml_weight: float = 0.4,
    ) -> float:
        """Calculate weighted final risk score."""
        if abs((rule_weight + ml_weight) - 1.0) > 0.001:
            logger.warning(
                "score_weights_dont_sum_to_one",
                rule_weight=rule_weight,
                ml_weight=ml_weight,
            )

        if ml_score == 0.0:
            return min(100.0, max(0.0, rule_score))

        ml_contribution = ml_score * 100 * ml_weight
        rule_contribution = rule_score * rule_weight
        final_score = rule_contribution + ml_contribution

        logger.debug(
            "final_score_calculation",
            rule_score=rule_score,
            ml_score=ml_score,
            rule_contribution=rule_contribution,
            ml_contribution=ml_contribution,
            final_score=final_score,
        )

        return min(100.0, max(0.0, final_score))

    def categorize_risk(self, score: float) -> RiskLevel:
        """Categorize risk score into levels (thresholds raised)."""
        EPSILON = 0.0001
        pct_score = score * 100 if score < 1 else score

        if pct_score >= 75 - EPSILON:
            return RiskLevel.CRITICAL
        if pct_score >= 45 - EPSILON:      
            return RiskLevel.HIGH
        if pct_score >= 25 - EPSILON:    
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def make_decision(self, risk_level: RiskLevel) -> RiskDecision:
        """Map a RiskLevel to a RiskDecision."""
        return {
            RiskLevel.LOW:      RiskDecision.APPROVE,
            RiskLevel.MEDIUM:   RiskDecision.REVIEW,
            RiskLevel.HIGH:     RiskDecision.BLOCK,
            RiskLevel.CRITICAL: RiskDecision.BLOCK,
        }.get(risk_level, RiskDecision.REVIEW)