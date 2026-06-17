from enum import StrEnum, auto


class OperationType(StrEnum):
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


class OperationStatus(StrEnum):
    PENDING = auto()
    CLAIMED = auto()
    SUCCEEDED = auto()
    FAILED = auto()
