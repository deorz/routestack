from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from domain.access_grants.access_grant import AccessGrant
from domain.access_grants.enums import AccessGrantState, AccessGrantStatus, AccessGrantType
from domain.clients.client import Client
from domain.operations.enums import OperationStatus, OperationType
from domain.operations.operation import Operation
from domain.subscriptions.enums import SubscriptionStatus
from domain.subscriptions.subscription import Subscription
from infrastructure.db import Base, create_session_factory, create_sqlite_engine
from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def test_repositories_round_trip_domain_entities(tmp_path: Path) -> None:
    session_factory = _session_factory(tmp_path)
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
        deleted_at=datetime(2026, 2, 4, 4, 5, 8, tzinfo=UTC),
        created_at=datetime(2026, 2, 3, 4, 5, 9, tzinfo=UTC),
        updated_at=datetime(2026, 2, 3, 4, 5, 10, tzinfo=UTC),
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
    operation = Operation(
        id=UUID("00000000-0000-0000-0000-000000000030"),
        type=OperationType.RUN_HEALTH_CHECK,
        node_id=UUID("00000000-0000-0000-0000-000000000031"),
        payload={"check": "health", "targets": ["core", "edge"], "limits": {"retries": 2}},
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

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.clients.add(client)
        unit_of_work.subscriptions.add(subscription)
        unit_of_work.access_grants.add(access_grant)
        unit_of_work.operations.add(operation)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        assert unit_of_work.clients.get(client.id).model_dump() == client.model_dump()
        assert unit_of_work.subscriptions.get(subscription.id).model_dump() == subscription.model_dump()
        assert unit_of_work.access_grants.get(access_grant.id).model_dump() == access_grant.model_dump()
        assert unit_of_work.operations.get(operation.id).model_dump() == operation.model_dump()


def _session_factory(tmp_path: Path):
    engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'repositories.db'}")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)
