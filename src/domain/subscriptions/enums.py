from enum import auto

from domain.shared.value_enums import AutoNameStrEnum


class SubscriptionStatus(AutoNameStrEnum):
    PENDING = auto()
    PROVISIONING = auto()
    ACTIVE = auto()
    UPDATING = auto()
    DEGRADED = auto()
    SUSPENDED = auto()
    EXPIRED = auto()
    REVOKED = auto()
    DELETED = auto()
