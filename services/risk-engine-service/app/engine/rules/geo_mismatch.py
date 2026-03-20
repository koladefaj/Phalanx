"""Geo-location mismatch detection rule."""

from app.engine.rules.base_rule import BaseRule

# High-risk country pairs
HIGH_RISK_CORRIDORS = {
    ("US", "NG"), ("US", "GH"), ("GB", "NG"),
    ("US", "RU"), ("GB", "RU"), ("US", "KP"),
}


class GeoMismatchRule(BaseRule):
    """Flags transactions where sender and receiver are in different countries,
    especially high-risk corridors.

    Score:
    - Same country: 0.0
    - Different country: 0.3
    - High-risk corridor: 0.4-1.0 based on amount
    """

    @property
    def name(self) -> str:
        return "GEO_MISMATCH"

    def evaluate(self, transaction: dict) -> dict:
        sender_country = transaction.get("sender_country", "").upper()
        receiver_country = transaction.get("receiver_country", "").upper()
        amount = float(transaction.get("amount", 0))

        if not sender_country or not receiver_country:
            return self._result(
                triggered=False,
                score=0.0,
                reason="Country information not available",
                severity="LOW",
            )

        # Same country — no risk
        if sender_country == receiver_country:
            return self._result(
                triggered=False,
                score=0.0,
                reason=f"Domestic transaction ({sender_country})",
                severity="LOW",
            )

        # Check high-risk corridor
        pair = (sender_country, receiver_country)
        reverse_pair = (receiver_country, sender_country)

        if pair in HIGH_RISK_CORRIDORS or reverse_pair in HIGH_RISK_CORRIDORS:
            # Amount-based scoring for high-risk corridors
            if amount < 200:
                score = 0.4  # Small amount - lower score
                severity = "MEDIUM"
                detail = f"Small transaction (${amount:.2f}) to high-risk corridor: {sender_country} → {receiver_country}"
            elif amount < 1000:
                score = 0.7  # Medium amount
                severity = "HIGH"
                detail = f"Medium amount (${amount:.2f}) to high-risk corridor: {sender_country} → {receiver_country}"
            else:
                score = 0.9  # Large amount - very high score
                severity = "HIGH"
                detail = f"Large amount (${amount:.2f}) to high-risk corridor: {sender_country} → {receiver_country}"
            
            return self._result(
                triggered=True,
                score=score,
                reason=detail,
                severity=severity,
            )

        # Cross-border but not high-risk
        # Also amount-based, but lower baseline
        if amount < 1000:
            score = 0.2
            severity = "LOW"
        else:
            score = 0.3
            severity = "MEDIUM"
            
        return self._result(
            triggered=True,
            score=score,
            reason=f"Cross-border transaction: {sender_country} → {receiver_country}",
            severity=severity,
        )