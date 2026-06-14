from dataclasses import dataclass, field
from datetime import datetime
from enum import auto

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId, ensure_entity_id
from domain.shared.errors import DomainStateError
from domain.shared.time import ensure_utc, utc_now
from domain.shared.validation import (
    ensure_enum,
    normalize_optional_text,
    normalize_required_text,
)
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


@dataclass(slots=True, kw_only=True, eq=False)
class AccessGrant(Entity):
    subscription_id: EntityId
    service_instance_id: EntityId
    type: AccessGrantType
    display_name: str
    status: AccessGrantStatus = AccessGrantStatus.PENDING
    desired_state: AccessGrantState = AccessGrantState.ENABLED
    actual_state: AccessGrantState = AccessGrantState.PENDING
    external_reference: str | None = None
    last_error: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.subscription_id = ensure_entity_id(self.subscription_id, "subscription_id")
        self.service_instance_id = ensure_entity_id(self.service_instance_id, "service_instance_id")
        self.type = ensure_enum(self.type, AccessGrantType, "type")
        self.status = ensure_enum(self.status, AccessGrantStatus, "status")
        self.display_name = normalize_required_text(self.display_name, "display_name")
        self.desired_state = ensure_enum(self.desired_state, AccessGrantState, "desired_state")
        self.actual_state = ensure_enum(self.actual_state, AccessGrantState, "actual_state")
        self.external_reference = normalize_optional_text(self.external_reference, "external_reference")
        self.last_error = normalize_optional_text(self.last_error, "last_error")
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.updated_at = ensure_utc(self.updated_at, "updated_at")

    def succeed(self) -> None:
        self._ensure_mutable("succeed")
        self.status = AccessGrantStatus.ACTIVE
        self.desired_state = AccessGrantState.ENABLED
        self.actual_state = AccessGrantState.ENABLED
        self.last_error = None
        self.updated_at = utc_now()

    def disable(self) -> None:
        self._ensure_not_terminal("disable")
        self.status = AccessGrantStatus.DISABLED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.DISABLED
        self.updated_at = utc_now()

    def fail(self, error_message: str | None = None) -> None:
        self._ensure_not_terminal("fail")
        self.status = AccessGrantStatus.FAILED
        self.actual_state = AccessGrantState.FAILED
        self.last_error = normalize_optional_text(error_message, "error_message")
        self.updated_at = utc_now()

    def revoke(self) -> None:
        if self.status == AccessGrantStatus.REVOKED:
            return

        self.status = AccessGrantStatus.REVOKED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.REVOKED
        self.updated_at = utc_now()

    def _ensure_mutable(self, action: str) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant cannot {action} from {self.status}")

    def _ensure_not_terminal(self, action: str) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant cannot {action} from {self.status}")
