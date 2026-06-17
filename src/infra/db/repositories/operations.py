from sqlalchemy.orm import Session

from domain.operations.enums import OperationStatus, OperationType
from domain.operations.operation import Operation
from infra.db.models import OperationOrm
from infra.db.repositories.base import SqlAlchemyRepository, entity_id, utc, utc_or_none


class SqlAlchemyOperationRepository(SqlAlchemyRepository[Operation, OperationOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OperationOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(operation: Operation) -> OperationOrm:
        return OperationOrm(
            id=str(operation.id),
            type=operation.type.value,
            node_id=str(operation.node_id),
            payload=dict(operation.payload),
            idempotency_key=operation.idempotency_key,
            status=operation.status.value,
            attempts=operation.attempts,
            max_attempts=operation.max_attempts,
            started_at=operation.started_at,
            finished_at=operation.finished_at,
            last_error=operation.last_error,
            created_at=operation.created_at,
            updated_at=operation.updated_at,
        )

    @staticmethod
    def _from_orm(orm: OperationOrm) -> Operation:
        return Operation(
            id=entity_id(orm.id),
            type=OperationType(orm.type),
            node_id=entity_id(orm.node_id),
            payload=dict(orm.payload or {}),
            idempotency_key=orm.idempotency_key,
            status=OperationStatus(orm.status),
            attempts=orm.attempts,
            max_attempts=orm.max_attempts,
            started_at=utc_or_none(orm.started_at),
            finished_at=utc_or_none(orm.finished_at),
            last_error=orm.last_error,
            created_at=utc(orm.created_at),
            updated_at=utc(orm.updated_at),
        )
