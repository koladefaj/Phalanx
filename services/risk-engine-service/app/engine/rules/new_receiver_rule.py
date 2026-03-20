"""New receiver detection rule."""

from app.engine.rules.base_rule import BaseRule


class NewReceiverRule(BaseRule):
    """Flags transactions to a receiver the sender has never used before.

    A sender transacting with a brand new receiver is a meaningful fraud
    signal — especially combined with high value or high-risk corridor.
    
    Score: 0.5 — meaningful signal but not blocking on its own.
    """

    @property
    def name(self) -> str:
        return "NEW_RECEIVER"

    def evaluate(self, transaction: dict) -> dict:
        metadata = transaction.get("metadata") or {}
        is_new_receiver = metadata.get("is_new_receiver", True)
        account_age_days = metadata.get("account_age_days", 0)

        if is_new_receiver:
            # Higher score for very new accounts sending to new receivers
            score = 0.7 if account_age_days < 1 else 0.5
            
            # Determine severity based on score
            if score >= 0.8:
                severity = "HIGH"
            elif score >= 0.5:
                severity = "MEDIUM"
            else:
                severity = "LOW"
                
            return self._result(
                triggered=True,
                score=score,
                reason="Sender has never transacted with this receiver before",
                severity=severity,
            )
        return self._result(
            triggered=False,
            score=0.0,
            reason="Known receiver — previously transacted successfully",
            severity="LOW",
        )