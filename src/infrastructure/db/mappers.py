from datetime import UTC, datetime
from uuid import UUID

from domain.access_grants.access_grant import (
    AccessGrant,
    AccessGrantState,
    AccessGrantStatus,
    AccessGrantType,
)
from domain.clients.client import Client
from domain.operations.operation import Operation, OperationStatus, OperationType
from domain.shared.entity_id import EntityId
from domain.subscriptions.subscription import Subscription, SubscriptionStatus
from infrastructure.db.models import AccessGrantRow, ClientRow, OperationRow, SubscriptionRow


def client_to_row(client: Client) -> ClientRow:
    return ClientRow(
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


def client_from_row(row: ClientRow) -> Client:
    return Client(
        id=_entity_id(row.id),
        display_name=row.display_name,
        email=row.email,
        comment=row.comment,
        tags=tuple(row.tags or ()),
        enabled=row.enabled,
        deleted_at=_utc_or_none(row.deleted_at),
        created_at=_utc(row.created_at),
        updated_at=_utc(row.updated_at),
    )


def subscription_to_row(subscription: Subscription) -> SubscriptionRow:
    return SubscriptionRow(
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


def subscription_from_row(row: SubscriptionRow) -> Subscription:
    return Subscription(
        id=_entity_id(row.id),
        public_id=row.public_id,
        access_token_hash=row.access_token_hash,
        client_id=_entity_id(row.client_id),
        name=row.name,
        status=SubscriptionStatus(row.status),
        revision=row.revision,
        expires_at=_utc_or_none(row.expires_at),
        suspended_at=_utc_or_none(row.suspended_at),
        revoked_at=_utc_or_none(row.revoked_at),
        deleted_at=_utc_or_none(row.deleted_at),
        created_at=_utc(row.created_at),
        updated_at=_utc(row.updated_at),
    )


def access_grant_to_row(access_grant: AccessGrant) -> AccessGrantRow:
    return AccessGrantRow(
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


def access_grant_from_row(row: AccessGrantRow) -> AccessGrant:
    return AccessGrant(
        id=_entity_id(row.id),
        subscription_id=_entity_id(row.subscription_id),
        service_instance_id=_entity_id(row.service_instance_id),
        type=AccessGrantType(row.type),
        display_name=row.display_name,
        status=AccessGrantStatus(row.status),
        desired_state=AccessGrantState(row.desired_state),
        actual_state=AccessGrantState(row.actual_state),
        external_reference=row.external_reference,
        last_error=row.last_error,
        created_at=_utc(row.created_at),
        updated_at=_utc(row.updated_at),
    )


def operation_to_row(operation: Operation) -> OperationRow:
    return OperationRow(
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


def operation_from_row(row: OperationRow) -> Operation:
    return Operation(
        id=_entity_id(row.id),
        type=OperationType(row.type),
        node_id=_entity_id(row.node_id),
        payload=dict(row.payload or {}),
        idempotency_key=row.idempotency_key,
        status=OperationStatus(row.status),
        attempts=row.attempts,
        max_attempts=row.max_attempts,
        started_at=_utc_or_none(row.started_at),
        finished_at=_utc_or_none(row.finished_at),
        last_error=row.last_error,
        created_at=_utc(row.created_at),
        updated_at=_utc(row.updated_at),
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
