from enum import auto
from typing import Annotated

from pydantic import AwareDatetime, Field, NonNegativeInt, PositiveInt, StringConstraints, model_validator

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.events import DomainEvent
from domain.shared.time import utc_now
from domain.shared.value_enums import AutoNameStrEnum

RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


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
    revision: PositiveInt
    safe_change_summary: RequiredText


class Subscription(Entity):
    public_id: RequiredText
    access_token_hash: RequiredText
    client_id: EntityId
    name: RequiredText
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    revision: NonNegativeInt = 0
    expires_at: AwareDatetime | None = None
    suspended_at: AwareDatetime | None = None
    revoked_at: AwareDatetime | None = None
    deleted_at: AwareDatetime | None = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

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
