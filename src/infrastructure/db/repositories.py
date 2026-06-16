from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.access_grants.access_grant import AccessGrant, AccessGrantState, AccessGrantStatus, AccessGrantType
from domain.admins.admin_user import AdminUser
from domain.clients.client import Client
from domain.operations.operation import Operation, OperationStatus, OperationType
from domain.shared.entity_id import EntityId
from domain.shared.validation import normalize_required_text
from domain.subscriptions.subscription import Subscription, SubscriptionStatus
from infrastructure.db.models import (
    AccessGrantOrm,
    AdminUserOrm,
    ClientOrm,
    OperationOrm,
    SubscriptionOrm,
)


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
        self._to_orm = to_orm
        self._from_orm = from_orm

    def add(self, entity: DomainEntity) -> None:
        self._session.merge(self._to_orm(entity))

    def get(self, entity_id: EntityId) -> DomainEntity | None:
        orm = self._session.get(self._orm_type, str(entity_id))
        if orm is None:
            return None

        return self._from_orm(orm)


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
            id=_entity_id(orm.id),
            display_name=orm.display_name,
            email=orm.email,
            comment=orm.comment,
            tags=tuple(orm.tags or ()),
            enabled=orm.enabled,
            deleted_at=_utc_or_none(orm.deleted_at),
            created_at=_utc(orm.created_at),
            updated_at=_utc(orm.updated_at),
        )


class SqlAlchemyAdminUserRepository(SqlAlchemyRepository[AdminUser, AdminUserOrm]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AdminUserOrm, self._to_orm, self._from_orm)

    def get_by_login(self, login: str) -> AdminUser | None:
        normalized_login = normalize_required_text(login, "login")
        orm = self._session.scalar(select(self._orm_type).where(self._orm_type.login == normalized_login))
        if orm is None:
            return None

        return self._from_orm(orm)

    @staticmethod
    def _to_orm(admin_user: AdminUser) -> AdminUserOrm:
        return AdminUserOrm(
            id=str(admin_user.id),
            login=admin_user.login,
            password_hash=admin_user.password_hash,
            last_login_at=admin_user.last_login_at,
            disabled_at=admin_user.disabled_at,
            created_at=admin_user.created_at,
        )

    @staticmethod
    def _from_orm(orm: AdminUserOrm) -> AdminUser:
        return AdminUser(
            id=_entity_id(orm.id),
            login=orm.login,
            password_hash=orm.password_hash,
            last_login_at=_utc_or_none(orm.last_login_at),
            disabled_at=_utc_or_none(orm.disabled_at),
            created_at=_utc(orm.created_at),
        )


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
            id=_entity_id(orm.id),
            public_id=orm.public_id,
            access_token_hash=orm.access_token_hash,
            client_id=_entity_id(orm.client_id),
            name=orm.name,
            status=SubscriptionStatus(orm.status),
            revision=orm.revision,
            expires_at=_utc_or_none(orm.expires_at),
            suspended_at=_utc_or_none(orm.suspended_at),
            revoked_at=_utc_or_none(orm.revoked_at),
            deleted_at=_utc_or_none(orm.deleted_at),
            created_at=_utc(orm.created_at),
            updated_at=_utc(orm.updated_at),
        )


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
            id=_entity_id(orm.id),
            subscription_id=_entity_id(orm.subscription_id),
            service_instance_id=_entity_id(orm.service_instance_id),
            type=AccessGrantType(orm.type),
            display_name=orm.display_name,
            status=AccessGrantStatus(orm.status),
            desired_state=AccessGrantState(orm.desired_state),
            actual_state=AccessGrantState(orm.actual_state),
            external_reference=orm.external_reference,
            last_error=orm.last_error,
            created_at=_utc(orm.created_at),
            updated_at=_utc(orm.updated_at),
        )


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
            id=_entity_id(orm.id),
            type=OperationType(orm.type),
            node_id=_entity_id(orm.node_id),
            payload=dict(orm.payload or {}),
            idempotency_key=orm.idempotency_key,
            status=OperationStatus(orm.status),
            attempts=orm.attempts,
            max_attempts=orm.max_attempts,
            started_at=_utc_or_none(orm.started_at),
            finished_at=_utc_or_none(orm.finished_at),
            last_error=orm.last_error,
            created_at=_utc(orm.created_at),
            updated_at=_utc(orm.updated_at),
        )


def _entity_id(value: str) -> EntityId:
    return EntityId(UUID(value))


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)


def _utc_or_none(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    return _utc(value)
