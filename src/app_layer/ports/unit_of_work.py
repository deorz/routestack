from types import TracebackType
from typing import Protocol, Self, runtime_checkable

from app_layer.ports.repositories import (
    AccessGrantRepository,
    AdminUserRepository,
    AuditRecordRepository,
    ClientRepository,
    OperationRepository,
    OutboxMessageRepository,
    SubscriptionRepository,
    SubscriptionRevisionRepository,
)
from domain.shared.entity import Entity


@runtime_checkable
class UnitOfWork(Protocol):
    admins: AdminUserRepository
    clients: ClientRepository
    subscriptions: SubscriptionRepository
    access_grants: AccessGrantRepository
    operations: OperationRepository
    subscription_revisions: SubscriptionRevisionRepository
    audit_records: AuditRecordRepository
    outbox_messages: OutboxMessageRepository

    def track(self, entity: Entity) -> None: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def shutdown(self) -> None: ...
