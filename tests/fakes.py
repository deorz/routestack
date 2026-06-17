from types import TracebackType
from typing import Any

from app_layer.exceptions import IdempotencyConflictError
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
from domain.admins.admin_user import AdminUser
from domain.operations.enums import OperationStatus
from domain.operations.operation import Operation
from domain.shared.entity import Entity
from domain.shared.entity_id import EntityId


class FakePasswordHasher:
    def hash_password(self, password: str) -> str:
        return f"hashed::{password}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash_password(password)


class InMemoryRepository:
    def __init__(self) -> None:
        self.records: dict[EntityId, Any] = {}

    def add(self, entity: Any) -> None:
        self.records[entity.id] = entity

    def get(self, entity_id: EntityId) -> Any | None:
        return self.records.get(entity_id)


class InMemoryOperationRepository:
    def __init__(self) -> None:
        self.records: dict[EntityId, Operation] = {}

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


class InMemoryAdminUserRepository:
    def __init__(self) -> None:
        self.admins: dict[EntityId, AdminUser] = {}

    def add(self, admin_user: AdminUser) -> None:
        self.admins[admin_user.id] = admin_user

    def get(self, admin_user_id: EntityId) -> AdminUser | None:
        return self.admins.get(admin_user_id)

    def get_by_login(self, login: str) -> AdminUser | None:
        for admin_user in self.admins.values():
            if admin_user.login == login:
                return admin_user
        return None


class FakeUnitOfWork:
    def __init__(
        self,
        *,
        admins: AdminUserRepository | None = None,
        clients: ClientRepository | None = None,
        subscriptions: SubscriptionRepository | None = None,
        access_grants: AccessGrantRepository | None = None,
        operations: OperationRepository | None = None,
        subscription_revisions: SubscriptionRevisionRepository | None = None,
        audit_records: AuditRecordRepository | None = None,
        outbox_messages: OutboxMessageRepository | None = None,
    ) -> None:
        self.admins = admins or InMemoryAdminUserRepository()
        self.clients = clients or InMemoryRepository()
        self.subscriptions = subscriptions or InMemoryRepository()
        self.access_grants = access_grants or InMemoryRepository()
        self.operations = operations or InMemoryOperationRepository()
        self.subscription_revisions = subscription_revisions or InMemoryRepository()
        self.audit_records = audit_records or InMemoryRepository()
        self.outbox_messages = outbox_messages or InMemoryRepository()
        self.commits = 0
        self.rollbacks = 0
        self.shutdowns = 0

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

    def track(self, entity: Entity) -> None:
        pass

    def ensure_idempotent(self, key: str) -> None:
        existing = self.operations.find_by_idempotency_key(key)
        if existing is not None:
            raise IdempotencyConflictError(key)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def shutdown(self) -> None:
        self.shutdowns += 1
