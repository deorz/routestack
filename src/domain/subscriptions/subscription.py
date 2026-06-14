from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.events import DomainEvent
from domain.shared.time import ensure_utc, utc_now
from domain.shared.validation import normalize_required_text


class SubscriptionStatus(StrEnum):
    PENDING = "PENDING"
    PROVISIONING = "PROVISIONING"
    ACTIVE = "ACTIVE"
    UPDATING = "UPDATING"
    DEGRADED = "DEGRADED"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    DELETED = "DELETED"


@dataclass(frozen=True, slots=True)
class SubscriptionRevisionCreated(DomainEvent):
    subscription_id: EntityId
    revision: int
    safe_change_summary: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.subscription_id, EntityId):
            raise DomainValidationError("subscription_id must be an EntityId")

        if (
            not isinstance(self.revision, int)
            or isinstance(self.revision, bool)
            or self.revision < 1
        ):
            raise DomainValidationError("revision must be a positive integer")

        object.__setattr__(
            self,
            "safe_change_summary",
            normalize_required_text(self.safe_change_summary, "safe_change_summary"),
        )


@dataclass(slots=True, kw_only=True, eq=False)
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
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.public_id = normalize_required_text(self.public_id, "public_id")
        self.access_token_hash = normalize_required_text(
            self.access_token_hash,
            "access_token_hash",
        )
        self.name = normalize_required_text(self.name, "name")

        if self.public_id == self.access_token_hash:
            raise DomainValidationError("public_id must differ from access_token_hash")

        if not isinstance(self.client_id, EntityId):
            raise DomainValidationError("client_id must be an EntityId")

        if not isinstance(self.status, SubscriptionStatus):
            raise DomainValidationError("status must be a SubscriptionStatus")

        self.revision = self._validate_revision(self.revision)
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.updated_at = ensure_utc(self.updated_at, "updated_at")
        self.expires_at = self._normalize_optional_timestamp(self.expires_at, "expires_at")
        self.suspended_at = self._normalize_optional_timestamp(self.suspended_at, "suspended_at")
        self.revoked_at = self._normalize_optional_timestamp(self.revoked_at, "revoked_at")
        self.deleted_at = self._normalize_optional_timestamp(self.deleted_at, "deleted_at")

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

    @staticmethod
    def _validate_revision(value: int) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise DomainValidationError("revision must be a non-negative integer")
        return value

    @staticmethod
    def _normalize_optional_timestamp(value: datetime | None, field_name: str) -> datetime | None:
        if value is None:
            return None
        return ensure_utc(value, field_name)
