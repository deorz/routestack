from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import ensure_utc, utc_now
from domain.shared.validation import normalize_optional_text, normalize_required_text


class AccessGrantType(StrEnum):
    VLESS_REALITY = "VLESS_REALITY"
    AMNEZIAWG = "AMNEZIAWG"
    HYSTERIA = "HYSTERIA"
    TELEGRAM_PROXY = "TELEGRAM_PROXY"
    SOCKS5 = "SOCKS5"


class AccessGrantStatus(StrEnum):
    PENDING = "PENDING"
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    DISABLING = "DISABLING"
    DISABLED = "DISABLED"
    FAILED = "FAILED"
    REVOKED = "REVOKED"


@dataclass(slots=True, kw_only=True, eq=False)
class AccessGrant(Entity):
    subscription_id: EntityId
    service_instance_id: EntityId
    type: AccessGrantType
    display_name: str
    status: AccessGrantStatus = AccessGrantStatus.PENDING
    desired_state: str = "enabled"
    actual_state: str = "pending"
    external_reference: str | None = None
    last_error: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.subscription_id, EntityId):
            raise DomainValidationError("subscription_id must be an EntityId")
        if not isinstance(self.service_instance_id, EntityId):
            raise DomainValidationError("service_instance_id must be an EntityId")
        if not isinstance(self.type, AccessGrantType):
            raise DomainValidationError("type must be an AccessGrantType")
        if not isinstance(self.status, AccessGrantStatus):
            raise DomainValidationError("status must be an AccessGrantStatus")

        self.display_name = normalize_required_text(self.display_name, "display_name")
        self.desired_state = normalize_required_text(self.desired_state, "desired_state")
        self.actual_state = normalize_required_text(self.actual_state, "actual_state")
        self.external_reference = normalize_optional_text(
            self.external_reference,
            "external_reference",
        )
        self.last_error = normalize_optional_text(self.last_error, "last_error")
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.updated_at = ensure_utc(self.updated_at, "updated_at")

    def succeed(self) -> None:
        self._ensure_mutable("succeed")
        self.status = AccessGrantStatus.ACTIVE
        self.desired_state = "enabled"
        self.actual_state = "enabled"
        self.last_error = None
        self.updated_at = utc_now()

    def disable(self) -> None:
        self._ensure_not_terminal("disable")
        self.status = AccessGrantStatus.DISABLED
        self.desired_state = "disabled"
        self.actual_state = "disabled"
        self.updated_at = utc_now()

    def fail(self, error_message: str | None = None) -> None:
        self._ensure_not_terminal("fail")
        self.status = AccessGrantStatus.FAILED
        self.actual_state = "failed"
        self.last_error = normalize_optional_text(error_message, "error_message")
        self.updated_at = utc_now()

    def revoke(self) -> None:
        if self.status == AccessGrantStatus.REVOKED:
            return

        self.status = AccessGrantStatus.REVOKED
        self.desired_state = "disabled"
        self.actual_state = "revoked"
        self.updated_at = utc_now()

    def _ensure_mutable(self, action: str) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant cannot {action} from {self.status}")

    def _ensure_not_terminal(self, action: str) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant cannot {action} from {self.status}")
