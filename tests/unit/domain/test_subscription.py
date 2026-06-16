from uuid import uuid4

import pytest
from pydantic import ValidationError

from domain.shared.errors import DomainStateError
from domain.subscriptions.enums import SubscriptionStatus
from domain.subscriptions.subscription import (
    Subscription,
    SubscriptionRevisionCreated,
)


def test_subscription_rejects_shared_public_id_and_token_hash() -> None:
    with pytest.raises(ValidationError):
        Subscription(
            client_id=uuid4(),
            public_id="shared-value",
            access_token_hash="shared-value",
            name="Starter",
        )


def test_subscription_bump_revision_records_revision_event() -> None:
    subscription = Subscription(
        client_id=uuid4(),
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKX4",
        access_token_hash="hash-abc",
        name="Starter",
        revision=7,
    )

    event = subscription.bump_revision("added a new access grant")

    assert subscription.revision == 8
    assert isinstance(event, SubscriptionRevisionCreated)
    assert event.subscription_id == subscription.id
    assert event.revision == 8
    assert event.safe_change_summary == "added a new access grant"
    assert subscription.pull_domain_events() == (event,)


def test_subscription_suspend_resume_and_revoke_flow() -> None:
    subscription = Subscription(
        client_id=uuid4(),
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKX4",
        access_token_hash="hash-abc",
        name="Starter",
        status=SubscriptionStatus.ACTIVE,
    )

    subscription.suspend()
    assert subscription.status == SubscriptionStatus.SUSPENDED

    subscription.resume()
    assert subscription.status == SubscriptionStatus.ACTIVE

    subscription.revoke()
    assert subscription.status == SubscriptionStatus.REVOKED


def test_subscription_revoke_is_idempotent() -> None:
    subscription = Subscription(
        client_id=uuid4(),
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKX4",
        access_token_hash="hash-abc",
        name="Starter",
        status=SubscriptionStatus.ACTIVE,
    )

    subscription.revoke()
    revoked_at = subscription.revoked_at

    subscription.revoke()

    assert subscription.status == SubscriptionStatus.REVOKED
    assert subscription.revoked_at == revoked_at


def test_subscription_rejects_resume_after_revocation() -> None:
    subscription = Subscription(
        client_id=uuid4(),
        public_id="SUB-01JXYZ8DQ7YQ8S3H63HPS6TKX4",
        access_token_hash="hash-abc",
        name="Starter",
        status=SubscriptionStatus.REVOKED,
    )

    with pytest.raises(DomainStateError):
        subscription.resume()
