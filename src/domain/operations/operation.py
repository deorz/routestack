from enum import auto
from typing import Annotated, Any

from pydantic import AwareDatetime, Field, NonNegativeInt, PositiveInt, StringConstraints, model_validator

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import utc_now
from domain.shared.validation import normalize_optional_text
from domain.shared.value_enums import AutoNameStrEnum

RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionalText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None


class OperationType(AutoNameStrEnum):
    INSTALL_COMPONENT = auto()
    APPLY_SERVICE_REVISION = auto()
    START_SERVICE = auto()
    STOP_SERVICE = auto()
    RESTART_SERVICE = auto()
    APPLY_FIREWALL_REVISION = auto()
    CREATE_TUNNEL = auto()
    REMOVE_TUNNEL = auto()
    COLLECT_STATUS = auto()
    COLLECT_LOGS = auto()
    RUN_HEALTH_CHECK = auto()
    MANAGE_CERTIFICATE = auto()


class OperationStatus(AutoNameStrEnum):
    PENDING = auto()
    CLAIMED = auto()
    SUCCEEDED = auto()
    FAILED = auto()


class Operation(Entity):
    type: OperationType
    node_id: EntityId
    payload: dict[str, Any]
    idempotency_key: RequiredText
    status: OperationStatus = OperationStatus.PENDING
    attempts: NonNegativeInt = 0
    max_attempts: PositiveInt = 3
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    last_error: OptionalText = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_attempt_limit(self) -> "Operation":
        if self.attempts > self.max_attempts:
            raise DomainValidationError("attempts cannot exceed max_attempts")
        return self

    def claim(self) -> None:
        if self.status != OperationStatus.PENDING:
            raise DomainStateError("operation can only be claimed from PENDING")

        if self.attempts >= self.max_attempts:
            raise DomainStateError("operation has exhausted its attempts")

        self.attempts += 1
        self.status = OperationStatus.CLAIMED
        now = utc_now()
        self.started_at = now
        self.finished_at = None
        self.last_error = None
        self.updated_at = now

    def succeed(self) -> None:
        self._ensure_claimed("succeed")
        now = utc_now()
        self.status = OperationStatus.SUCCEEDED
        self.finished_at = now
        self.last_error = None
        self.updated_at = now

    def fail_retryable(self, error_message: str | None = None) -> None:
        self._ensure_claimed("fail")
        now = utc_now()
        self.last_error = normalize_optional_text(error_message, "error_message")
        self.finished_at = now
        attempts_exhausted = self.attempts >= self.max_attempts
        self.status = OperationStatus.FAILED if attempts_exhausted else OperationStatus.PENDING
        self.updated_at = now

    def fail_terminal(self, error_message: str | None = None) -> None:
        self._ensure_claimed("fail")
        now = utc_now()
        self.status = OperationStatus.FAILED
        self.finished_at = now
        self.last_error = normalize_optional_text(error_message, "error_message")
        self.updated_at = now

    def _ensure_claimed(self, action: str) -> None:
        if self.status != OperationStatus.CLAIMED:
            raise DomainStateError(f"operation can only {action} while CLAIMED")
