from sqlalchemy.orm import Session

from domain.operations.outbox import OutboxMessage
from infra.db.models import OutboxMessageOrm
from infra.db.repositories.base import SqlAlchemyRepository, entity_id, utc


class SqlAlchemyOutboxMessageRepository(SqlAlchemyRepository[OutboxMessage, OutboxMessageOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OutboxMessageOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(message: OutboxMessage) -> OutboxMessageOrm:
        return OutboxMessageOrm(
            id=str(message.id),
            event_type=message.event_type,
            payload=message.payload,
            created_at=message.created_at,
        )

    @staticmethod
    def _from_orm(orm: OutboxMessageOrm) -> OutboxMessage:
        return OutboxMessage(
            id=entity_id(orm.id),
            event_type=orm.event_type,
            payload=orm.payload,
            created_at=utc(orm.created_at),
        )
