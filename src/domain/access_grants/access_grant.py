from pydantic import AwareDatetime, Field

from domain.access_grants.enums import AccessGrantState, AccessGrantStatus, AccessGrantType
from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError
from domain.shared.time import utc_now
from domain.shared.types import OptionalText, RequiredText


class AccessGrant(Entity):
    subscription_id: EntityId
    service_instance_id: EntityId
    type: AccessGrantType
    display_name: RequiredText
    status: AccessGrantStatus = AccessGrantStatus.PENDING
    desired_state: AccessGrantState = AccessGrantState.ENABLED
    actual_state: AccessGrantState = AccessGrantState.PENDING
    external_reference: OptionalText = None
    last_error: OptionalText = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    def succeed(self) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.ACTIVE
        self.desired_state = AccessGrantState.ENABLED
        self.actual_state = AccessGrantState.ENABLED
        self.last_error = None
        self.updated_at = utc_now()

    def disable(self) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.DISABLED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.DISABLED
        self.updated_at = utc_now()

    def fail(self, error_message: str | None = None) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.FAILED
        self.actual_state = AccessGrantState.FAILED
        self.last_error = error_message
        self.updated_at = utc_now()

    def revoke(self) -> None:
        if self.status == AccessGrantStatus.REVOKED:
            return

        self.status = AccessGrantStatus.REVOKED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.REVOKED
        self.updated_at = utc_now()

    def _ensure_not_terminal(self) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant is in terminal state {self.status}")
