from typing import Self

from pydantic import AwareDatetime, NonNegativeInt, PositiveInt, model_validator

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.events import DomainEvent
from domain.shared.time import utc_now
from domain.shared.timestamps import DatetimeMixin
from domain.shared.types import RequiredText
from domain.subscriptions.enums import SubscriptionStatus


class SubscriptionRevisionCreated(DomainEvent):
    subscription_id: EntityId
    revision: PositiveInt
    safe_change_summary: RequiredText


class Subscription(Entity, DatetimeMixin):
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

    @model_validator(mode="after")
    def validate_public_token_split(self) -> Self:
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
        self._record_update()
        self.record_domain_event(event)
        return event

    def suspend(self) -> None:
        self._ensure_active_lifecycle()
        self.status = SubscriptionStatus.SUSPENDED
        self.suspended_at = utc_now()
        self._record_update()

    def resume(self) -> None:
        if self.status != SubscriptionStatus.SUSPENDED:
            raise DomainStateError("subscription can only be resumed from SUSPENDED")

        self.status = SubscriptionStatus.ACTIVE
        self.suspended_at = None
        self._record_update()

    def revoke(self) -> None:
        if self.status == SubscriptionStatus.REVOKED:
            return

        if self.status == SubscriptionStatus.DELETED:
            raise DomainStateError("subscription is deleted")

        self.status = SubscriptionStatus.REVOKED
        self.revoked_at = utc_now()
        self.suspended_at = None
        self._record_update()

    def _ensure_active_lifecycle(self) -> None:
        if self.status in {SubscriptionStatus.REVOKED, SubscriptionStatus.DELETED}:
            raise DomainStateError("subscription is in a terminal lifecycle state")

        if self.status == SubscriptionStatus.SUSPENDED:
            raise DomainStateError("subscription is already suspended")
