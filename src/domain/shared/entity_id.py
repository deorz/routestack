from typing import NewType
from uuid import UUID, uuid4

from domain.shared.errors import DomainValidationError

EntityId = NewType("EntityId", UUID)


def new_entity_id() -> EntityId:
    return EntityId(uuid4())


def ensure_entity_id(value: object, field_name: str) -> EntityId:
    if not isinstance(value, UUID):
        raise DomainValidationError(f"{field_name} must be a UUID")

    return EntityId(value)
