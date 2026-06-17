from enum import StrEnum, auto


class SubscriptionStatus(StrEnum):
    PENDING = auto()
    PROVISIONING = auto()
    ACTIVE = auto()
    UPDATING = auto()
    DEGRADED = auto()
    SUSPENDED = auto()
    EXPIRED = auto()
    REVOKED = auto()
    DELETED = auto()
