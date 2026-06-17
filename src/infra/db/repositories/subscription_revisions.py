from sqlalchemy.orm import Session

from domain.subscriptions.revision import SubscriptionRevision
from infra.db.models import SubscriptionRevisionOrm
from infra.db.repositories.base import SqlAlchemyRepository, entity_id, utc


class SqlAlchemySubscriptionRevisionRepository(SqlAlchemyRepository[SubscriptionRevision, SubscriptionRevisionOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SubscriptionRevisionOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(revision: SubscriptionRevision) -> SubscriptionRevisionOrm:
        return SubscriptionRevisionOrm(
            id=str(revision.id),
            subscription_id=str(revision.subscription_id),
            revision=revision.revision,
            safe_change_summary=revision.safe_change_summary,
            created_at=revision.created_at,
            created_by=revision.created_by,
        )

    @staticmethod
    def _from_orm(orm: SubscriptionRevisionOrm) -> SubscriptionRevision:
        return SubscriptionRevision(
            id=entity_id(orm.id),
            subscription_id=entity_id(orm.subscription_id),
            revision=orm.revision,
            safe_change_summary=orm.safe_change_summary,
            created_at=utc(orm.created_at),
            created_by=orm.created_by,
        )
