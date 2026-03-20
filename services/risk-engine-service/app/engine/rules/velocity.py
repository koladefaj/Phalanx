"""Velocity spike detection rule."""

from app.config import settings
from app.engine.rules.base_rule import BaseRule


class VelocitySpikeRule(BaseRule):
    """Detects unusually high transaction frequency for a sender.

    Checks if the number of recent transactions from the same sender
    exceeds a configurable threshold within a time window.
    """

    @property
    def name(self) -> str:
        return "VELOCITY_SPIKE"

    def evaluate(self, transaction: dict) -> dict:
        metadata = transaction.get("metadata") or {}
        recent_count = metadata.get("recent_transaction_count", 0)
        max_allowed = settings.VELOCITY_MAX_TRANSACTIONS
        window = settings.VELOCITY_WINDOW_MINUTES

        if recent_count > max_allowed:
            excess = recent_count - max_allowed
            if excess >= 2:
                score = 1.0
                severity = "HIGH"
            else:
                score = 0.8
                severity = "MEDIUM"
                
            return self._result(
                triggered=True,
                score=score,
                reason=(
                    f"Sender has {recent_count} transactions in the last "
                    f"{window} minutes (threshold: {max_allowed})"
                ),
                severity=severity,
            )

        return self._result(
            triggered=False,
            score=0.0,
            reason=f"Transaction velocity within normal range ({recent_count}/{max_allowed})",
            severity="LOW",
        )