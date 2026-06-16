from sqlalchemy.orm import Session

from domain.clients.client import Client
from infrastructure.db.models import ClientOrm
from infrastructure.db.repositories.base import SqlAlchemyRepository, entity_id, utc, utc_or_none


class SqlAlchemyClientRepository(SqlAlchemyRepository[Client, ClientOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ClientOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(client: Client) -> ClientOrm:
        return ClientOrm(
            id=str(client.id),
            display_name=client.display_name,
            email=client.email,
            comment=client.comment,
            tags=list(client.tags),
            enabled=client.enabled,
            deleted_at=client.deleted_at,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    @staticmethod
    def _from_orm(orm: ClientOrm) -> Client:
        return Client(
            id=entity_id(orm.id),
            display_name=orm.display_name,
            email=orm.email,
            comment=orm.comment,
            tags=tuple(orm.tags or ()),
            enabled=orm.enabled,
            deleted_at=utc_or_none(orm.deleted_at),
            created_at=utc(orm.created_at),
            updated_at=utc(orm.updated_at),
        )
