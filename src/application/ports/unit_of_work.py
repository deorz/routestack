from types import TracebackType
from typing import Protocol, Self, runtime_checkable

from application.ports.repositories import (
    AccessGrantRepository,
    ClientRepository,
    OperationRepository,
    SubscriptionRepository,
)


@runtime_checkable
class UnitOfWork(Protocol):
    clients: ClientRepository
    subscriptions: SubscriptionRepository
    access_grants: AccessGrantRepository
    operations: OperationRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
