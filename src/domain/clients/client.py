from pydantic import AwareDatetime, Field

from domain.shared.entity import Entity
from domain.shared.errors import DomainStateError
from domain.shared.time import utc_now
from domain.shared.types import OptionalText, RequiredText


class Client(Entity):
    display_name: RequiredText
    email: OptionalText = None
    comment: OptionalText = None
    tags: tuple[str, ...] = Field(default_factory=tuple)
    enabled: bool = True
    deleted_at: AwareDatetime | None = None
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)

    def rename(self, display_name: str) -> None:
        self._ensure_mutable("rename")
        self.display_name = display_name
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
