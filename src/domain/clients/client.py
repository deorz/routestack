from datetime import datetime

from pydantic import Field, field_validator

from domain.shared.entity import Entity
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import (
    normalize_optional_text,
    normalize_required_text,
    normalize_tags,
)


class Client(Entity):
    display_name: str
    email: str | None = None
    comment: str | None = None
    tags: tuple[str, ...] = Field(default_factory=tuple)
    enabled: bool = True
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("display_name", mode="before")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return normalize_required_text(value, "display_name")

    @field_validator("email", "comment", mode="before")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str | None:
        return normalize_optional_text(value, info.field_name)

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: object) -> tuple[str, ...]:
        return normalize_tags(value)

    @field_validator("enabled", mode="before")
    @classmethod
    def validate_enabled(cls, value: object) -> bool:
        if not isinstance(value, bool):
            raise DomainValidationError("enabled must be a boolean")
        return value

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def validate_timestamp(cls, value: datetime, info) -> datetime:
        return ensure_utc(value, info.field_name)

    @field_validator("deleted_at", mode="before")
    @classmethod
    def validate_deleted_at(cls, value: datetime | None) -> datetime | None:
        return ensure_optional_utc(value, "deleted_at")

    def rename(self, display_name: str) -> None:
        self._ensure_mutable("rename")
        self.display_name = normalize_required_text(display_name, "display_name")
        self.updated_at = utc_now()

    def soft_delete(self) -> None:
        if self.deleted_at is not None:
            return

        self.enabled = False
        self.deleted_at = utc_now()
        self.updated_at = utc_now()

    def _ensure_mutable(self, action: str) -> None:
        if self.deleted_at is not None:
            raise DomainStateError(f"client cannot {action} after soft delete")
