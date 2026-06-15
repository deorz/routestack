from dataclasses import dataclass, field
from datetime import datetime
from enum import auto
from typing import Any

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


@dataclass(slots=True, kw_only=True, eq=False)
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
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        Entity.__post_init__(self)
        self.type = ensure_enum(self.type, OperationType, "type")
        self.node_id = ensure_entity_id(self.node_id, "node_id")
        self.status = ensure_enum(self.status, OperationStatus, "status")
        self.payload = self._normalize_payload(self.payload)
        self.idempotency_key = normalize_required_text(self.idempotency_key, "idempotency_key")
        self.attempts = ensure_non_negative_int(self.attempts, "attempts")
        self.max_attempts = ensure_positive_int(self.max_attempts, "max_attempts")

        if self.attempts > self.max_attempts:
            raise DomainValidationError("attempts cannot exceed max_attempts")

        self.started_at = ensure_optional_utc(self.started_at, "started_at")
        self.finished_at = ensure_optional_utc(self.finished_at, "finished_at")
        self.last_error = normalize_optional_text(self.last_error, "last_error")
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.updated_at = ensure_utc(self.updated_at, "updated_at")

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
