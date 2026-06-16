from uuid import uuid4

import pytest

from domain.operations.enums import OperationStatus, OperationType
from domain.operations.operation import Operation
from domain.shared.errors import DomainStateError


@pytest.fixture
def operation() -> Operation:
    return Operation(
        type=OperationType.RUN_HEALTH_CHECK,
        node_id=uuid4(),
        payload={"check": "health"},
        idempotency_key="op-123",
        max_attempts=2,
    )


def test_operation_claim_succeed_and_retry_flow(operation: Operation) -> None:
    operation.claim()
    assert operation.status == OperationStatus.CLAIMED
    assert operation.attempts == 1

    operation.fail_retryable("temporary network failure")
    assert operation.status == OperationStatus.PENDING

    operation.claim()
    operation.succeed()

    assert operation.status == OperationStatus.SUCCEEDED


def test_operation_retryable_failure_exhausts_attempts(operation: Operation) -> None:
    operation.claim()
    operation.fail_retryable("temporary network failure")

    operation.claim()
    operation.fail_retryable("temporary network failure")

    assert operation.status == OperationStatus.FAILED
    assert operation.attempts == 2


def test_operation_rejects_claim_after_terminal_failure(operation: Operation) -> None:
    operation.claim()
    operation.fail_terminal("permanent payload error")

    assert operation.status == OperationStatus.FAILED

    with pytest.raises(DomainStateError):
        operation.claim()
