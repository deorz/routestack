from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import ensure_utc, utc_now
from domain.shared.validation import (
    ensure_non_negative_int,
    ensure_positive_int,
    normalize_optional_text,
    normalize_required_text,
)


class OperationType(StrEnum):
    INSTALL_COMPONENT = "INSTALL_COMPONENT"
    APPLY_SERVICE_REVISION = "APPLY_SERVICE_REVISION"
    START_SERVICE = "START_SERVICE"
    STOP_SERVICE = "STOP_SERVICE"
    RESTART_SERVICE = "RESTART_SERVICE"
    APPLY_FIREWALL_REVISION = "APPLY_FIREWALL_REVISION"
    CREATE_TUNNEL = "CREATE_TUNNEL"
    REMOVE_TUNNEL = "REMOVE_TUNNEL"
    COLLECT_STATUS = "COLLECT_STATUS"
    COLLECT_LOGS = "COLLECT_LOGS"
    RUN_HEALTH_CHECK = "RUN_HEALTH_CHECK"
    MANAGE_CERTIFICATE = "MANAGE_CERTIFICATE"


class OperationStatus(StrEnum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


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
        super().__post_init__()
        if not isinstance(self.type, OperationType):
            raise DomainValidationError("type must be an OperationType")
        if not isinstance(self.node_id, EntityId):
            raise DomainValidationError("node_id must be an EntityId")
        if not isinstance(self.status, OperationStatus):
            raise DomainValidationError("status must be an OperationStatus")

        self.payload = self._normalize_payload(self.payload)
        self.idempotency_key = normalize_required_text(self.idempotency_key, "idempotency_key")
        self.attempts = ensure_non_negative_int(self.attempts, "attempts")
        self.max_attempts = ensure_positive_int(self.max_attempts, "max_attempts")

        if self.attempts > self.max_attempts:
            raise DomainValidationError("attempts cannot exceed max_attempts")

        self.started_at = self._normalize_optional_timestamp(self.started_at, "started_at")
        self.finished_at = self._normalize_optional_timestamp(self.finished_at, "finished_at")
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
        self.status = (
            OperationStatus.FAILED
            if self.attempts >= self.max_attempts
            else OperationStatus.PENDING
        )
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

    @staticmethod
    def _normalize_optional_timestamp(value: datetime | None, field_name: str) -> datetime | None:
        if value is None:
            return None
        return ensure_utc(value, field_name)
