from sqlalchemy.orm import Session

from domain.subscriptions.enums import SubscriptionStatus
from domain.subscriptions.subscription import Subscription
from infrastructure.db.models import SubscriptionOrm
from infrastructure.db.repositories.base import SqlAlchemyRepository, entity_id, utc, utc_or_none


class SqlAlchemySubscriptionRepository(SqlAlchemyRepository[Subscription, SubscriptionOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SubscriptionOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(subscription: Subscription) -> SubscriptionOrm:
        return SubscriptionOrm(
            id=str(subscription.id),
            public_id=subscription.public_id,
            access_token_hash=subscription.access_token_hash,
            client_id=str(subscription.client_id),
            name=subscription.name,
            status=subscription.status.value,
            revision=subscription.revision,
            expires_at=subscription.expires_at,
            suspended_at=subscription.suspended_at,
            revoked_at=subscription.revoked_at,
            deleted_at=subscription.deleted_at,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )

    @staticmethod
    def _from_orm(orm: SubscriptionOrm) -> Subscription:
        return Subscription(
            id=entity_id(orm.id),
            public_id=orm.public_id,
            access_token_hash=orm.access_token_hash,
            client_id=entity_id(orm.client_id),
            name=orm.name,
            status=SubscriptionStatus(orm.status),
            revision=orm.revision,
            expires_at=utc_or_none(orm.expires_at),
            suspended_at=utc_or_none(orm.suspended_at),
            revoked_at=utc_or_none(orm.revoked_at),
            deleted_at=utc_or_none(orm.deleted_at),
            created_at=utc(orm.created_at),
            updated_at=utc(orm.updated_at),
        )
