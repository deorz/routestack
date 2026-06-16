from enum import auto

from domain.shared.value_enums import AutoNameStrEnum


class AccessGrantType(AutoNameStrEnum):
    VLESS_REALITY = auto()
    AMNEZIAWG = auto()
    HYSTERIA = auto()
    TELEGRAM_PROXY = auto()
    SOCKS5 = auto()


class AccessGrantStatus(AutoNameStrEnum):
    PENDING = auto()
    PROVISIONING = auto()
    ACTIVE = auto()
    DISABLING = auto()
    DISABLED = auto()
    FAILED = auto()
    REVOKED = auto()


class AccessGrantState(AutoNameStrEnum):
    PENDING = auto()
    ENABLED = auto()
    DISABLED = auto()
    FAILED = auto()
    REVOKED = auto()
