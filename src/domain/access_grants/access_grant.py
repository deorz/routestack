from enum import auto
from typing import Annotated

from pydantic import AwareDatetime, Field, StringConstraints

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError
from domain.shared.time import utc_now
from domain.shared.validation import normalize_optional_text
from domain.shared.value_enums import AutoNameStrEnum

RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None


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
    display_name: RequiredText
    status: AccessGrantStatus = AccessGrantStatus.PENDING
    desired_state: AccessGrantState = AccessGrantState.ENABLED
    actual_state: AccessGrantState = AccessGrantState.PENDING
    external_reference: OptionalText = None
    last_error: OptionalText = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

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
