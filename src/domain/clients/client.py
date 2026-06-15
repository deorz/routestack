from dataclasses import dataclass, field
from datetime import datetime

from domain.shared.entity import Entity
from domain.shared.errors import DomainStateError, DomainValidationError
from domain.shared.time import ensure_optional_utc, ensure_utc, utc_now
from domain.shared.validation import (
    normalize_optional_text,
    normalize_required_text,
    normalize_tags,
)


@dataclass(slots=True, kw_only=True, eq=False)
class Client(Entity):
    display_name: str
    email: str | None = None
    comment: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True
    deleted_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.display_name = normalize_required_text(self.display_name, "display_name")
        self.email = normalize_optional_text(self.email, "email")
        self.comment = normalize_optional_text(self.comment, "comment")
        self.tags = normalize_tags(self.tags)
        self.deleted_at = ensure_optional_utc(self.deleted_at, "deleted_at")
        self.created_at = ensure_utc(self.created_at, "created_at")
        self.updated_at = ensure_utc(self.updated_at, "updated_at")

        if not isinstance(self.enabled, bool):
            raise DomainValidationError("enabled must be a boolean")

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
