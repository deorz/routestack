from datetime import datetime
from enum import auto

from pydantic import Field, field_validator, model_validator

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId, ensure_entity_id
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.events import DomainEvent
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import (
    ensure_enum,
    ensure_non_negative_int,
    ensure_positive_int,
    normalize_required_text,
)
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


class SubscriptionRevisionCreated(DomainEvent):
    subscription_id: EntityId
    revision: int
    safe_change_summary: str

    @field_validator("subscription_id", mode="before")
    @classmethod
    def validate_subscription_id(cls, value: object) -> EntityId:
        return ensure_entity_id(value, "subscription_id")

    @field_validator("revision", mode="before")
    @classmethod
    def validate_revision(cls, value: int) -> int:
        return ensure_positive_int(value, "revision")

    @field_validator("safe_change_summary", mode="before")
    @classmethod
    def validate_safe_change_summary(cls, value: str) -> str:
        return normalize_required_text(value, "safe_change_summary")


class Subscription(Entity):
    public_id: str
    access_token_hash: str
    client_id: EntityId
    name: str
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    revision: int = 0
    expires_at: datetime | None = None
    suspended_at: datetime | None = None
    revoked_at: datetime | None = None
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("public_id", "access_token_hash", "name", mode="before")
    @classmethod
    def validate_required_text(cls, value: str, info) -> str:
        return normalize_required_text(value, info.field_name)

    @field_validator("client_id", mode="before")
    @classmethod
    def validate_client_id(cls, value: object) -> EntityId:
        return ensure_entity_id(value, "client_id")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> SubscriptionStatus:
        return ensure_enum(value, SubscriptionStatus, "status")

    @field_validator("revision", mode="before")
    @classmethod
    def validate_non_negative_revision(cls, value: int) -> int:
        return ensure_non_negative_int(value, "revision")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def validate_timestamp(cls, value: datetime, info) -> datetime:
        return ensure_utc(value, info.field_name)

    @field_validator("expires_at", "suspended_at", "revoked_at", "deleted_at", mode="before")
    @classmethod
    def validate_optional_timestamp(cls, value: datetime | None, info) -> datetime | None:
        return ensure_optional_utc(value, info.field_name)

    @model_validator(mode="after")
    def validate_public_token_split(self) -> "Subscription":
        if self.public_id == self.access_token_hash:
            raise DomainValidationError("public_id must differ from access_token_hash")
        return self

    def bump_revision(self, summary: str) -> SubscriptionRevisionCreated:
        event = SubscriptionRevisionCreated(
            subscription_id=self.id,
            revision=self.revision + 1,
            safe_change_summary=summary,
        )
        self.revision += 1
        self.updated_at = utc_now()
        self.record_domain_event(event)
        return event

    def suspend(self) -> None:
        self._ensure_active_lifecycle("suspend")
        self.status = SubscriptionStatus.SUSPENDED
        self.suspended_at = utc_now()
        self.updated_at = utc_now()

    def resume(self) -> None:
        if self.status != SubscriptionStatus.SUSPENDED:
            raise DomainStateError("subscription can only be resumed from SUSPENDED")

        self.status = SubscriptionStatus.ACTIVE
        self.suspended_at = None
        self.updated_at = utc_now()

    def revoke(self) -> None:
        if self.status == SubscriptionStatus.REVOKED:
            return

        if self.status == SubscriptionStatus.DELETED:
            raise DomainStateError("subscription is deleted")

        self.status = SubscriptionStatus.REVOKED
        self.revoked_at = utc_now()
        self.suspended_at = None
        self.updated_at = utc_now()

    def _ensure_active_lifecycle(self, action: str) -> None:
        if self.status in {SubscriptionStatus.REVOKED, SubscriptionStatus.DELETED}:
            raise DomainStateError(f"subscription cannot {action} after terminal lifecycle state")

        if self.status == SubscriptionStatus.SUSPENDED:
            raise DomainStateError("subscription is already suspended")
