from enum import StrEnum, auto


class AccessGrantType(StrEnum):
    VLESS_REALITY = auto()
    AMNEZIAWG = auto()
    HYSTERIA = auto()
    TELEGRAM_PROXY = auto()
    SOCKS5 = auto()


class AccessGrantStatus(StrEnum):
    PENDING = auto()
    PROVISIONING = auto()
    ACTIVE = auto()
    DISABLING = auto()
    DISABLED = auto()
    FAILED = auto()
    REVOKED = auto()


class AccessGrantState(StrEnum):
    PENDING = auto()
    ENABLED = auto()
    DISABLED = auto()
    FAILED = auto()
    REVOKED = auto()
