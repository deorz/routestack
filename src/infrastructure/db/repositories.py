from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

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

OrmRecord = Mapping[str, Any]


class SqlAlchemyRepository[DomainEntity]:
    def __init__(
        self,
        session: Session,
        table: Table,
        to_values: Callable[[DomainEntity], dict[str, Any]],
        from_record: Callable[[OrmRecord], DomainEntity],
    ) -> None:
        self._session = session
        self._table = table
        self._to_values = to_values
        self._from_record = from_record

    def add(self, entity: DomainEntity) -> None:
        values = self._to_values(entity)
        update_values = {key: value for key, value in values.items() if key != "id"}
        statement = sqlite_insert(self._table).values(**values)
        self._session.execute(
            statement.on_conflict_do_update(
                index_elements=[self._table.c.id],
                set_=update_values,
            )
        )

    def get(self, entity_id: EntityId) -> DomainEntity | None:
        record = self._session.execute(select(self._table).where(self._table.c.id == str(entity_id))).mappings().first()
        if record is None:
            return None

        return self._from_record(record)


class SqlAlchemyClientRepository(SqlAlchemyRepository[Client]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ClientOrm, self._to_values, self._from_record)

    @staticmethod
    def _to_values(client: Client) -> dict[str, Any]:
        return {
            "id": str(client.id),
            "display_name": client.display_name,
            "email": client.email,
            "comment": client.comment,
            "tags": list(client.tags),
            "enabled": client.enabled,
            "deleted_at": client.deleted_at,
            "created_at": client.created_at,
            "updated_at": client.updated_at,
        }

    @staticmethod
    def _from_record(record: OrmRecord) -> Client:
        return Client(
            id=_entity_id(record["id"]),
            display_name=record["display_name"],
            email=record["email"],
            comment=record["comment"],
            tags=tuple(record["tags"] or ()),
            enabled=record["enabled"],
            deleted_at=_utc_or_none(record["deleted_at"]),
            created_at=_utc(record["created_at"]),
            updated_at=_utc(record["updated_at"]),
        )


class SqlAlchemyAdminUserRepository(SqlAlchemyRepository[AdminUser]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AdminUserOrm, self._to_values, self._from_record)

    def get_by_login(self, login: str) -> AdminUser | None:
        normalized_login = normalize_required_text(login, "login")
        record = (
            self._session.execute(select(self._table).where(self._table.c.login == normalized_login)).mappings().first()
        )
        if record is None:
            return None

        return self._from_record(record)

    @staticmethod
    def _to_values(admin_user: AdminUser) -> dict[str, Any]:
        return {
            "id": str(admin_user.id),
            "login": admin_user.login,
            "password_hash": admin_user.password_hash,
            "last_login_at": admin_user.last_login_at,
            "disabled_at": admin_user.disabled_at,
            "created_at": admin_user.created_at,
        }

    @staticmethod
    def _from_record(record: OrmRecord) -> AdminUser:
        return AdminUser(
            id=_entity_id(record["id"]),
            login=record["login"],
            password_hash=record["password_hash"],
            last_login_at=_utc_or_none(record["last_login_at"]),
            disabled_at=_utc_or_none(record["disabled_at"]),
            created_at=_utc(record["created_at"]),
        )


class SqlAlchemySubscriptionRepository(SqlAlchemyRepository[Subscription]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, SubscriptionOrm, self._to_values, self._from_record)

    @staticmethod
    def _to_values(subscription: Subscription) -> dict[str, Any]:
        return {
            "id": str(subscription.id),
            "public_id": subscription.public_id,
            "access_token_hash": subscription.access_token_hash,
            "client_id": str(subscription.client_id),
            "name": subscription.name,
            "status": subscription.status.value,
            "revision": subscription.revision,
            "expires_at": subscription.expires_at,
            "suspended_at": subscription.suspended_at,
            "revoked_at": subscription.revoked_at,
            "deleted_at": subscription.deleted_at,
            "created_at": subscription.created_at,
            "updated_at": subscription.updated_at,
        }

    @staticmethod
    def _from_record(record: OrmRecord) -> Subscription:
        return Subscription(
            id=_entity_id(record["id"]),
            public_id=record["public_id"],
            access_token_hash=record["access_token_hash"],
            client_id=_entity_id(record["client_id"]),
            name=record["name"],
            status=SubscriptionStatus(record["status"]),
            revision=record["revision"],
            expires_at=_utc_or_none(record["expires_at"]),
            suspended_at=_utc_or_none(record["suspended_at"]),
            revoked_at=_utc_or_none(record["revoked_at"]),
            deleted_at=_utc_or_none(record["deleted_at"]),
            created_at=_utc(record["created_at"]),
            updated_at=_utc(record["updated_at"]),
        )


class SqlAlchemyAccessGrantRepository(SqlAlchemyRepository[AccessGrant]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AccessGrantOrm, self._to_values, self._from_record)

    @staticmethod
    def _to_values(access_grant: AccessGrant) -> dict[str, Any]:
        return {
            "id": str(access_grant.id),
            "subscription_id": str(access_grant.subscription_id),
            "service_instance_id": str(access_grant.service_instance_id),
            "type": access_grant.type.value,
            "display_name": access_grant.display_name,
            "status": access_grant.status.value,
            "desired_state": access_grant.desired_state.value,
            "actual_state": access_grant.actual_state.value,
            "external_reference": access_grant.external_reference,
            "last_error": access_grant.last_error,
            "created_at": access_grant.created_at,
            "updated_at": access_grant.updated_at,
        }

    @staticmethod
    def _from_record(record: OrmRecord) -> AccessGrant:
        return AccessGrant(
            id=_entity_id(record["id"]),
            subscription_id=_entity_id(record["subscription_id"]),
            service_instance_id=_entity_id(record["service_instance_id"]),
            type=AccessGrantType(record["type"]),
            display_name=record["display_name"],
            status=AccessGrantStatus(record["status"]),
            desired_state=AccessGrantState(record["desired_state"]),
            actual_state=AccessGrantState(record["actual_state"]),
            external_reference=record["external_reference"],
            last_error=record["last_error"],
            created_at=_utc(record["created_at"]),
            updated_at=_utc(record["updated_at"]),
        )


class SqlAlchemyOperationRepository(SqlAlchemyRepository[Operation]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, OperationOrm, self._to_values, self._from_record)

    @staticmethod
    def _to_values(operation: Operation) -> dict[str, Any]:
        return {
            "id": str(operation.id),
            "type": operation.type.value,
            "node_id": str(operation.node_id),
            "payload": dict(operation.payload),
            "idempotency_key": operation.idempotency_key,
            "status": operation.status.value,
            "attempts": operation.attempts,
            "max_attempts": operation.max_attempts,
            "started_at": operation.started_at,
            "finished_at": operation.finished_at,
            "last_error": operation.last_error,
            "created_at": operation.created_at,
            "updated_at": operation.updated_at,
        }

    @staticmethod
    def _from_record(record: OrmRecord) -> Operation:
        return Operation(
            id=_entity_id(record["id"]),
            type=OperationType(record["type"]),
            node_id=_entity_id(record["node_id"]),
            payload=dict(record["payload"] or {}),
            idempotency_key=record["idempotency_key"],
            status=OperationStatus(record["status"]),
            attempts=record["attempts"],
            max_attempts=record["max_attempts"],
            started_at=_utc_or_none(record["started_at"]),
            finished_at=_utc_or_none(record["finished_at"]),
            last_error=record["last_error"],
            created_at=_utc(record["created_at"]),
            updated_at=_utc(record["updated_at"]),
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
