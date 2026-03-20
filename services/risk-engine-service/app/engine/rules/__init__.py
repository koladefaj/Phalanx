"""Rule engine package — all configurable detection rules."""

from app.engine.rules.base_rule import BaseRule
from app.engine.rules.high_value import HighValueRule
from app.engine.rules.velocity import VelocitySpikeRule
from app.engine.rules.geo_mismatch import GeoMismatchRule
from app.engine.rules.device_fingerprint import DeviceFingerprintRule
from app.engine.rules.unusual_hour import UnusualHourRule
from app.engine.rules.account_age import AccountAgeRule
from app.engine.rules.failed_burst import FailedBurstRule


from app.engine.rules.new_receiver_rule import NewReceiverRule

def get_all_rules() -> list[BaseRule]:
    """Get all configured risk evaluation rules.

    Returns:
        List of rule instances.
    """
    return [
        HighValueRule(),
        VelocitySpikeRule(),
        GeoMismatchRule(),
        DeviceFingerprintRule(),
        UnusualHourRule(),
        AccountAgeRule(),
        FailedBurstRule(),
        NewReceiverRule(),
    ]


__all__ = [
    "BaseRule",
    "HighValueRule",
    "VelocitySpikeRule",
    "GeoMismatchRule",
    "DeviceFingerprintRule",
    "UnusualHourRule",
    "AccountAgeRule",
    "FailedBurstRule",
    "NewReceiverRule",
    "get_all_rules",
]
