from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from domain.shared.entity_id import EntityId


class SqlAlchemyRepository[DomainEntity, Orm]:
    def __init__(
        self,
        session: Session,
        orm_type: type[Orm],
        to_orm: Callable[[DomainEntity], Orm],
        from_orm: Callable[[Orm], DomainEntity],
    ) -> None:
        self._session = session
        self._orm_type = orm_type
        self._to_orm_fn = to_orm
        self._from_orm_fn = from_orm

    def add(self, entity: DomainEntity) -> None:
        self._session.merge(self._to_orm_fn(entity))

    def get(self, entity_id: EntityId) -> DomainEntity | None:
        orm = self._session.get(self._orm_type, str(entity_id))
        if orm is None:
            return None

        return self._from_orm_fn(orm)


def entity_id(value: str) -> EntityId:
    return EntityId(UUID(value))


def utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


def utc_or_none(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    return utc(value)
