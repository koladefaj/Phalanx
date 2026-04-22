"""Account age risk detection rule."""

from app.config import settings
from app.engine.rules.base_rule import BaseRule


class AccountAgeRule(BaseRule):
    """Flags transactions from recently created accounts.

    New accounts (< ACCOUNT_AGE_RISK_DAYS old) are considered higher risk.
    In production, this would query the user profile service.
    """

    @property
    def name(self) -> str:
        return "ACCOUNT_AGE_RISK"

    def evaluate(self, transaction: dict) -> dict:
        metadata = transaction.get("metadata") or {}
        account_age_days = metadata.get("account_age_days")

        if account_age_days is None:
            return self._result(
                triggered=False,
                score=0.0,
                reason="Account age information not available",
                severity="LOW",
            )

        threshold = settings.ACCOUNT_AGE_RISK_DAYS

        # format as hours if less than 1 day, else days rounded to 1dp
        if account_age_days < 1:
            age_display = f"{account_age_days * 24:.1f} hours"
        else:
            age_display = f"{account_age_days:.1f} days"

        if account_age_days < threshold:
            amount = float(transaction.get("amount", 0))
            
            # THE FIX: Grace period for onboarding transactions
            if amount <= 250.0:
                return self._result(
                    triggered=True,
                    score=0.1, # Negligible penalty
                    reason=f"New account ({age_display}), but low amount (${amount})",
                    severity="LOW",
                )

            if amount <= 500.0:
                return self._result(
                    triggered=True,
                    score=0.3, # Mild penalty
                    reason=f"New account ({age_display}), medium amount (${amount})",
                    severity="MEDIUM",
                )

            # Otherwise, apply normal strict scoring for larger amounts
            score = min(1.0, 1.0 - (account_age_days / threshold))
            
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
                reason=(
                    f"Account is {age_display} old "
                    f"(risk threshold: {threshold} days)"
                ),
                severity=severity,
            )

        return self._result(
            triggered=False,
            score=0.0,
            reason=f"Account is {account_age_days:.1f} days old (mature account)",
            severity="LOW",
        )