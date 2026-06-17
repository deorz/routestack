from dataclasses import dataclass, field
from types import TracebackType
from typing import Any

from app_layer.ports.repositories import (
    AccessGrantRepository,
    AdminUserRepository,
    AuditRecordRepository,
    ClientRepository,
    OperationRepository,
    SubscriptionRepository,
    SubscriptionRevisionRepository,
)
from domain.admins.admin_user import AdminUser
from domain.operations.enums import OperationStatus
from domain.operations.operation import Operation
from domain.shared.entity_id import EntityId


@dataclass
class InMemoryRepository:
    records: dict[EntityId, Any] = field(default_factory=dict)

    def add(self, entity: Any) -> None:
        self.records[entity.id] = entity

    def get(self, entity_id: EntityId) -> Any | None:
        return self.records.get(entity_id)


@dataclass
class InMemoryOperationRepository:
    records: dict[EntityId, Operation] = field(default_factory=dict)

    def add(self, operation: Operation) -> None:
        self.records[operation.id] = operation

    def get(self, operation_id: EntityId) -> Operation | None:
        return self.records.get(operation_id)

    def find_claimable(self, *, limit: int = 10) -> list[Operation]:
        claimable = [
            op for op in self.records.values() if op.status == OperationStatus.PENDING and op.attempts < op.max_attempts
        ]
        return sorted(claimable, key=lambda op: op.created_at)[:limit]

    def find_by_idempotency_key(self, key: str) -> Operation | None:
        for op in self.records.values():
            if op.idempotency_key == key:
                return op
        return None


@dataclass
class InMemoryAdminUserRepository:
    admins: dict[EntityId, AdminUser] = field(default_factory=dict)

    def add(self, admin_user: AdminUser) -> None:
        self.admins[admin_user.id] = admin_user

    def get(self, admin_user_id: EntityId) -> AdminUser | None:
        return self.admins.get(admin_user_id)

    def get_by_login(self, login: str) -> AdminUser | None:
        for admin_user in self.admins.values():
            if admin_user.login == login:
                return admin_user

        return None


@dataclass
class FakeUnitOfWork:
    admins: AdminUserRepository = field(default_factory=InMemoryAdminUserRepository)
    clients: ClientRepository = field(default_factory=InMemoryRepository)
    subscriptions: SubscriptionRepository = field(default_factory=InMemoryRepository)
    access_grants: AccessGrantRepository = field(default_factory=InMemoryRepository)
    operations: OperationRepository = field(default_factory=InMemoryOperationRepository)
    subscription_revisions: SubscriptionRevisionRepository = field(default_factory=InMemoryRepository)
    audit_records: AuditRecordRepository = field(default_factory=InMemoryRepository)
    commits: int = 0
    rollbacks: int = 0
    shutdowns: int = 0

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.shutdown()

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def shutdown(self) -> None:
        self.shutdowns += 1
