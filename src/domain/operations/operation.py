from datetime import datetime
from enum import auto
from typing import Any

from pydantic import Field, field_validator, model_validator

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId, ensure_entity_id
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import (
    ensure_enum,
    ensure_non_negative_int,
    ensure_positive_int,
    normalize_optional_text,
    normalize_required_text,
)
from domain.shared.value_enums import AutoNameStrEnum


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
    idempotency_key: str
    status: OperationStatus = OperationStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value: object) -> OperationType:
        return ensure_enum(value, OperationType, "type")

    @field_validator("node_id", mode="before")
    @classmethod
    def validate_node_id(cls, value: object) -> EntityId:
        return ensure_entity_id(value, "node_id")

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> OperationStatus:
        return ensure_enum(value, OperationStatus, "status")

    @field_validator("payload", mode="before")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        return cls._normalize_payload(value)

    @field_validator("idempotency_key", mode="before")
    @classmethod
    def validate_idempotency_key(cls, value: str) -> str:
        return normalize_required_text(value, "idempotency_key")

    @field_validator("attempts", mode="before")
    @classmethod
    def validate_attempts(cls, value: int) -> int:
        return ensure_non_negative_int(value, "attempts")

    @field_validator("max_attempts", mode="before")
    @classmethod
    def validate_max_attempts(cls, value: int) -> int:
        return ensure_positive_int(value, "max_attempts")

    @field_validator("started_at", "finished_at", mode="before")
    @classmethod
    def validate_optional_timestamp(cls, value: datetime | None, info) -> datetime | None:
        return ensure_optional_utc(value, info.field_name)

    @field_validator("last_error", mode="before")
    @classmethod
    def validate_last_error(cls, value: str | None) -> str | None:
        return normalize_optional_text(value, "last_error")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def validate_timestamp(cls, value: datetime, info) -> datetime:
        return ensure_utc(value, info.field_name)

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

    @staticmethod
    def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            try:
                payload = dict(payload)
            except (TypeError, ValueError) as exc:
                raise DomainValidationError("payload must be a mapping") from exc

        return dict(payload)
