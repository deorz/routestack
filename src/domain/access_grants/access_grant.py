from datetime import datetime
from enum import auto

from pydantic import Field, field_validator

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
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("subscription_id", "service_instance_id", mode="before")
    @classmethod
    def validate_entity_reference(cls, value: object, info) -> EntityId:
        return ensure_entity_id(value, info.field_name)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: object) -> AccessGrantType:
        return ensure_enum(value, AccessGrantType, "type")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> AccessGrantStatus:
        return ensure_enum(value, AccessGrantStatus, "status")

    @field_validator("desired_state", "actual_state", mode="before")
    @classmethod
    def validate_state(cls, value: object, info) -> AccessGrantState:
        return ensure_enum(value, AccessGrantState, info.field_name)

    @field_validator("display_name", mode="before")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return normalize_required_text(value, "display_name")

    @field_validator("external_reference", "last_error", mode="before")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str | None:
        return normalize_optional_text(value, info.field_name)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def validate_timestamp(cls, value: datetime, info) -> datetime:
        return ensure_utc(value, info.field_name)

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
