from sqlalchemy.orm import Session

from domain.operations.audit import AuditRecord
from infra.db.models import AuditRecordOrm
from infra.db.repositories.base import SqlAlchemyRepository, entity_id, utc


class SqlAlchemyAuditRecordRepository(SqlAlchemyRepository[AuditRecord, AuditRecordOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AuditRecordOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(audit: AuditRecord) -> AuditRecordOrm:
        return AuditRecordOrm(
            id=str(audit.id),
            actor_id=str(audit.actor_id) if audit.actor_id else None,
            action=audit.action,
            entity_type=audit.entity_type,
            entity_id=str(audit.entity_id),
            audit_metadata=audit.metadata,
            source_ip=audit.source_ip,
            created_at=audit.created_at,
        )

    @staticmethod
    def _from_orm(orm: AuditRecordOrm) -> AuditRecord:
        return AuditRecord(
            id=entity_id(orm.id),
            actor_id=entity_id(orm.actor_id) if orm.actor_id else None,
            action=orm.action,
            entity_type=orm.entity_type,
            entity_id=entity_id(orm.entity_id),
            metadata=orm.audit_metadata,
            source_ip=orm.source_ip,
            created_at=utc(orm.created_at),
        )
