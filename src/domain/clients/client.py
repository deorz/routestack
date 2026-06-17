from pydantic import AwareDatetime, Field

from domain.shared.entity import Entity
from domain.shared.errors import DomainStateError
from domain.shared.time import utc_now
from domain.shared.timestamps import TimestampedMixin
from domain.shared.types import OptionalText, RequiredText


class Client(Entity, TimestampedMixin):
    display_name: RequiredText
    email: OptionalText = None
    comment: OptionalText = None
    tags: tuple[str, ...] = Field(default_factory=tuple)
    enabled: bool = True
    deleted_at: AwareDatetime | None = None

    def rename(self, display_name: str) -> None:
        self._ensure_mutable()
        self.display_name = display_name
        self._touch()

    def soft_delete(self) -> None:
        if self.deleted_at is not None:
            return

        self.enabled = False
        self.deleted_at = utc_now()
        self._touch()

    def _ensure_mutable(self) -> None:
        if self.deleted_at is not None:
            raise DomainStateError("client was soft-deleted")
