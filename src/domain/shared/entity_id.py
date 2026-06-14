from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.shared.errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class EntityId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise DomainValidationError("value must be a UUID")

    @classmethod
    def new(cls) -> EntityId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> EntityId:
        try:
            parsed = UUID(value)
        except (TypeError, ValueError) as exc:
            raise DomainValidationError("invalid entity id") from exc

        return cls(parsed)

    def __str__(self) -> str:
        return str(self.value)
