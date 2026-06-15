from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from domain.access_grants.access_grant import (
    AccessGrant,
    AccessGrantState,
    AccessGrantStatus,
    AccessGrantType,
)
from domain.clients.client import Client
from domain.operations.operation import Operation, OperationStatus, OperationType
from domain.subscriptions.subscription import Subscription, SubscriptionStatus
from infrastructure.db import (
    AccessGrantRow,
    Base,
    ClientRow,
    OperationRow,
    SubscriptionRow,
    access_grant_from_row,
    access_grant_to_row,
    client_from_row,
    client_to_row,
    create_session_factory,
    create_sqlite_engine,
    operation_from_row,
    operation_to_row,
    subscription_from_row,
    subscription_to_row,
)


def test_client_round_trip_mapping(tmp_path: Path) -> None:
    client = Client(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        display_name="Primary Client",
        email="client@example.test",
        comment="Stored in SQLite",
        tags=("alpha", "beta"),
        enabled=False,
        deleted_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        created_at=datetime(2026, 1, 2, 3, 4, 6, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, 3, 4, 7, tzinfo=UTC),
    )

    loaded = _persist_round_trip(
        tmp_path,
        client_to_row(client),
        ClientRow,
        client_from_row,
    )

    assert asdict(loaded) == asdict(client)


def test_subscription_round_trip_mapping(tmp_path: Path) -> None:
    client = Client(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        display_name="Parent Client",
        created_at=datetime(2026, 2, 3, 4, 5, 6, tzinfo=UTC),
        updated_at=datetime(2026, 2, 3, 4, 5, 7, tzinfo=UTC),
    )
    subscription = Subscription(
        id=UUID("00000000-0000-0000-0000-000000000011"),
        client_id=client.id,
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKX4",
        access_token_hash="hash-abc",
        name="Starter",
        status=SubscriptionStatus.DEGRADED,
        revision=7,
        expires_at=datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC),
        suspended_at=datetime(2026, 2, 3, 4, 5, 8, tzinfo=UTC),
        revoked_at=None,
        deleted_at=datetime(2026, 2, 4, 4, 5, 8, tzinfo=UTC),
        created_at=datetime(2026, 2, 3, 4, 5, 9, tzinfo=UTC),
        updated_at=datetime(2026, 2, 3, 4, 5, 10, tzinfo=UTC),
    )

    loaded = _persist_round_trip(
        tmp_path,
        subscription_to_row(subscription),
        SubscriptionRow,
        subscription_from_row,
        parent_rows=[client_to_row(client)],
    )

    assert asdict(loaded) == asdict(subscription)


def test_access_grant_round_trip_mapping(tmp_path: Path) -> None:
    client = Client(
        id=UUID("00000000-0000-0000-0000-000000000020"),
        display_name="Parent Client",
        created_at=datetime(2026, 3, 4, 5, 6, 7, tzinfo=UTC),
        updated_at=datetime(2026, 3, 4, 5, 6, 8, tzinfo=UTC),
    )
    subscription = Subscription(
        id=UUID("00000000-0000-0000-0000-000000000021"),
        client_id=client.id,
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKY0",
        access_token_hash="hash-def",
        name="Pro",
        status=SubscriptionStatus.ACTIVE,
        revision=1,
        created_at=datetime(2026, 3, 4, 5, 6, 9, tzinfo=UTC),
        updated_at=datetime(2026, 3, 4, 5, 6, 10, tzinfo=UTC),
    )
    access_grant = AccessGrant(
        id=UUID("00000000-0000-0000-0000-000000000022"),
        subscription_id=subscription.id,
        service_instance_id=UUID("00000000-0000-0000-0000-000000000023"),
        type=AccessGrantType.VLESS_REALITY,
        display_name="Primary VLESS",
        status=AccessGrantStatus.FAILED,
        desired_state=AccessGrantState.ENABLED,
        actual_state=AccessGrantState.FAILED,
        external_reference="backend:node-1",
        last_error="backend rejected configuration",
        created_at=datetime(2026, 3, 4, 5, 6, 11, tzinfo=UTC),
        updated_at=datetime(2026, 3, 4, 5, 6, 12, tzinfo=UTC),
    )

    loaded = _persist_round_trip(
        tmp_path,
        access_grant_to_row(access_grant),
        AccessGrantRow,
        access_grant_from_row,
        parent_rows=[
            client_to_row(client),
            subscription_to_row(subscription),
        ],
    )

    assert asdict(loaded) == asdict(access_grant)


def test_operation_round_trip_mapping(tmp_path: Path) -> None:
    operation = Operation(
        id=UUID("00000000-0000-0000-0000-000000000030"),
        type=OperationType.RUN_HEALTH_CHECK,
        node_id=UUID("00000000-0000-0000-0000-000000000031"),
        payload={
            "check": "health",
            "targets": ["core", "edge"],
            "limits": {"retries": 2},
        },
        idempotency_key="op-123",
        status=OperationStatus.FAILED,
        attempts=2,
        max_attempts=3,
        started_at=datetime(2026, 4, 5, 6, 7, 8, tzinfo=UTC),
        finished_at=datetime(2026, 4, 5, 6, 7, 9, tzinfo=UTC),
        last_error="temporary network failure",
        created_at=datetime(2026, 4, 5, 6, 7, 10, tzinfo=UTC),
        updated_at=datetime(2026, 4, 5, 6, 7, 11, tzinfo=UTC),
    )

    loaded = _persist_round_trip(
        tmp_path,
        operation_to_row(operation),
        OperationRow,
        operation_from_row,
    )

    assert asdict(loaded) == asdict(operation)


def _persist_round_trip(
    tmp_path: Path,
    row: object,
    row_type: type[object],
    from_row: Callable[[object], object],
    *,
    parent_rows: list[object] | None = None,
) -> object:
    database_path = tmp_path / "persistence.db"
    engine = create_sqlite_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        for parent_row in parent_rows or []:
            session.add(parent_row)
            session.commit()

    with session_factory() as session:
        session.add(row)
        session.commit()

    with session_factory() as session:
        loaded_row = session.get(row_type, row.id)
        assert loaded_row is not None

    try:
        return from_row(loaded_row)
    finally:
        engine.dispose()
