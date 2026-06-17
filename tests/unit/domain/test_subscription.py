from uuid import uuid4

import pytest
from pydantic import ValidationError

from domain.shared.errors import DomainStateError, DomainValidationError
from domain.subscriptions.enums import SubscriptionStatus
from domain.subscriptions.subscription import Subscription, SubscriptionRevisionCreated


def test_subscription_rejects_shared_public_id_and_token_hash() -> None:
    with pytest.raises(ValidationError):
        Subscription(
            client_id=uuid4(),
            public_id="shared-value",
            access_token_hash="shared-value",
            name="Starter",
        )


def test_subscription_bump_revision_records_revision_event(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"revision": 7})

    event = sub.bump_revision("added a new access grant")

    assert sub.revision == 8
    assert isinstance(event, SubscriptionRevisionCreated)
    assert event.subscription_id == sub.id
    assert event.revision == 8
    assert event.safe_change_summary == "added a new access grant"
    assert sub.pull_domain_events() == (event,)


def test_subscription_suspend_resume_and_revoke_flow(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.ACTIVE})

    sub.suspend()
    assert sub.status == SubscriptionStatus.SUSPENDED

    sub.resume()
    assert sub.status == SubscriptionStatus.ACTIVE

    sub.revoke()
    assert sub.status == SubscriptionStatus.REVOKED


def test_subscription_revoke_is_idempotent(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.ACTIVE})

    sub.revoke()
    revoked_at = sub.revoked_at

    sub.revoke()

    assert sub.status == SubscriptionStatus.REVOKED
    assert sub.revoked_at == revoked_at


def test_subscription_rejects_resume_after_revocation(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.REVOKED})

    with pytest.raises(DomainStateError):
        sub.resume()


def test_subscription_rotate_token_updates_hash_and_bumps_revision(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.ACTIVE, "revision": 3})

    event = sub.rotate_token("routestack-sha256$def456")

    assert sub.access_token_hash == "routestack-sha256$def456"
    assert sub.revision == 4
    assert isinstance(event, SubscriptionRevisionCreated)
    assert event.safe_change_summary == "rotated access token"


def test_subscription_rotate_token_rejects_same_hash(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.ACTIVE})

    with pytest.raises(DomainStateError):
        sub.rotate_token("hash-abc")


def test_subscription_rotate_token_rejects_hash_matching_public_id(subscription: Subscription) -> None:
    sub = subscription.model_copy(update={"status": SubscriptionStatus.ACTIVE})

    with pytest.raises(DomainValidationError):
        sub.rotate_token("public-id-test")
