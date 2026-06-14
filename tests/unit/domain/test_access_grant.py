from uuid import uuid4

import pytest

from domain.access_grants.access_grant import (
    AccessGrant,
    AccessGrantStatus,
    AccessGrantType,
)
from domain.shared.errors import DomainStateError


@pytest.fixture
def grant() -> AccessGrant:
    return AccessGrant(
        subscription_id=uuid4(),
        service_instance_id=uuid4(),
        type=AccessGrantType.VLESS_REALITY,
        display_name="Primary VLESS",
    )


def test_access_grant_transitions_through_enable_disable_and_revoke(grant: AccessGrant) -> None:
    grant.succeed()
    assert grant.status == AccessGrantStatus.ACTIVE

    grant.disable()
    assert grant.status == AccessGrantStatus.DISABLED

    grant.revoke()
    assert grant.status == AccessGrantStatus.REVOKED


def test_access_grant_records_failure(grant: AccessGrant) -> None:
    grant.fail("backend rejected configuration")

    assert grant.status == AccessGrantStatus.FAILED
    assert grant.last_error == "backend rejected configuration"


def test_access_grant_rejects_success_after_revocation(grant: AccessGrant) -> None:
    grant.revoke()

    with pytest.raises(DomainStateError):
        grant.succeed()


def test_access_grant_revoke_is_idempotent(grant: AccessGrant) -> None:
    grant.revoke()

    grant.revoke()

    assert grant.status == AccessGrantStatus.REVOKED
