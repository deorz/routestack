from typing import Any, Self

from pydantic import AwareDatetime, Field, NonNegativeInt, PositiveInt, model_validator

from domain.operations.enums import OperationStatus, OperationType
from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import utc_now
from domain.shared.types import OptionalText, RequiredText


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
    def validate_attempt_limit(self) -> Self:
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
        self._ensure_claimed()
        now = utc_now()
        self.status = OperationStatus.SUCCEEDED
        self.finished_at = now
        self.last_error = None
        self.updated_at = now

    def fail_retryable(self, error_message: str | None = None) -> None:
        self._ensure_claimed()
        now = utc_now()
        self.last_error = error_message
        self.finished_at = now
        attempts_exhausted = self.attempts >= self.max_attempts
        self.status = OperationStatus.FAILED if attempts_exhausted else OperationStatus.PENDING
        self.updated_at = now

    def fail_terminal(self, error_message: str | None = None) -> None:
        self._ensure_claimed()
        now = utc_now()
        self.status = OperationStatus.FAILED
        self.finished_at = now
        self.last_error = error_message
        self.updated_at = now

    def _ensure_claimed(self) -> None:
        if self.status != OperationStatus.CLAIMED:
            raise DomainStateError("operation must be CLAIMED")
