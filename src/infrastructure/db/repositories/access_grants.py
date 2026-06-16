from sqlalchemy.orm import Session

from domain.access_grants.access_grant import AccessGrant
from domain.access_grants.enums import AccessGrantState, AccessGrantStatus, AccessGrantType
from infrastructure.db.models import AccessGrantOrm
from infrastructure.db.repositories.base import SqlAlchemyRepository, entity_id, utc


class SqlAlchemyAccessGrantRepository(SqlAlchemyRepository[AccessGrant, AccessGrantOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AccessGrantOrm, self._to_orm, self._from_orm)

    @staticmethod
    def _to_orm(access_grant: AccessGrant) -> AccessGrantOrm:
        return AccessGrantOrm(
            id=str(access_grant.id),
            subscription_id=str(access_grant.subscription_id),
            service_instance_id=str(access_grant.service_instance_id),
            type=access_grant.type.value,
            display_name=access_grant.display_name,
            status=access_grant.status.value,
            desired_state=access_grant.desired_state.value,
            actual_state=access_grant.actual_state.value,
            external_reference=access_grant.external_reference,
            last_error=access_grant.last_error,
            created_at=access_grant.created_at,
            updated_at=access_grant.updated_at,
        )

    @staticmethod
    def _from_orm(orm: AccessGrantOrm) -> AccessGrant:
        return AccessGrant(
            id=entity_id(orm.id),
            subscription_id=entity_id(orm.subscription_id),
            service_instance_id=entity_id(orm.service_instance_id),
            type=AccessGrantType(orm.type),
            display_name=orm.display_name,
            status=AccessGrantStatus(orm.status),
            desired_state=AccessGrantState(orm.desired_state),
            actual_state=AccessGrantState(orm.actual_state),
            external_reference=orm.external_reference,
            last_error=orm.last_error,
            created_at=utc(orm.created_at),
            updated_at=utc(orm.updated_at),
        )
