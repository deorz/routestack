from domain.access_grants.enums import AccessGrantState, AccessGrantStatus, AccessGrantType
from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError
from domain.shared.timestamps import DatetimeMixin
from domain.shared.types import OptionalText, RequiredText


class AccessGrant(Entity, DatetimeMixin):
    subscription_id: EntityId
    service_instance_id: EntityId
    type: AccessGrantType
    display_name: RequiredText
    status: AccessGrantStatus = AccessGrantStatus.PENDING
    desired_state: AccessGrantState = AccessGrantState.ENABLED
    actual_state: AccessGrantState = AccessGrantState.PENDING
    external_reference: OptionalText = None
    last_error: OptionalText = None

    def succeed(self) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.ACTIVE
        self.desired_state = AccessGrantState.ENABLED
        self.actual_state = AccessGrantState.ENABLED
        self.last_error = None
        self._record_update()

    def disable(self) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.DISABLED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.DISABLED
        self._record_update()

    def fail(self, error_message: str | None = None) -> None:
        self._ensure_not_terminal()
        self.status = AccessGrantStatus.FAILED
        self.actual_state = AccessGrantState.FAILED
        self.last_error = error_message
        self._record_update()

    def revoke(self) -> None:
        if self.status == AccessGrantStatus.REVOKED:
            return

        self.status = AccessGrantStatus.REVOKED
        self.desired_state = AccessGrantState.DISABLED
        self.actual_state = AccessGrantState.REVOKED
        self._record_update()

    def _ensure_not_terminal(self) -> None:
        if self.status in {AccessGrantStatus.REVOKED, AccessGrantStatus.DISABLED}:
            raise DomainStateError(f"access grant is in terminal state {self.status}")
