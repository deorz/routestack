from enum import auto

from domain.shared.value_enums import AutoNameStrEnum


class OperationType(AutoNameStrEnum):
    INSTALL_COMPONENT = auto()
    APPLY_SERVICE_REVISION = auto()
    START_SERVICE = auto()
    STOP_SERVICE = auto()
    RESTART_SERVICE = auto()
    APPLY_FIREWALL_REVISION = auto()
    CREATE_TUNNEL = auto()
    REMOVE_TUNNEL = auto()
    COLLECT_STATUS = auto()
    COLLECT_LOGS = auto()
    RUN_HEALTH_CHECK = auto()
    MANAGE_CERTIFICATE = auto()


class OperationStatus(AutoNameStrEnum):
    PENDING = auto()
    CLAIMED = auto()
    SUCCEEDED = auto()
    FAILED = auto()
