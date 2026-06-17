from typing import Protocol, runtime_checkable

from domain.access_grants.access_grant import AccessGrant
from domain.admins.admin_user import AdminUser
from domain.clients.client import Client
from domain.operations.audit import AuditRecord
from domain.operations.operation import Operation
from domain.shared.entity_id import EntityId
from domain.subscriptions.revision import SubscriptionRevision
from domain.subscriptions.subscription import Subscription


@runtime_checkable
class ClientRepository(Protocol):
    def add(self, client: Client) -> None: ...

    def get(self, client_id: EntityId) -> Client | None: ...


@runtime_checkable
class AdminUserRepository(Protocol):
    def add(self, admin_user: AdminUser) -> None: ...

    def get(self, admin_user_id: EntityId) -> AdminUser | None: ...

    def get_by_login(self, login: str) -> AdminUser | None: ...


@runtime_checkable
class SubscriptionRepository(Protocol):
    def add(self, subscription: Subscription) -> None: ...

    def get(self, subscription_id: EntityId) -> Subscription | None: ...


@runtime_checkable
class AccessGrantRepository(Protocol):
    def add(self, access_grant: AccessGrant) -> None: ...

    def get(self, access_grant_id: EntityId) -> AccessGrant | None: ...


@runtime_checkable
class OperationRepository(Protocol):
    def add(self, operation: Operation) -> None: ...

    def get(self, operation_id: EntityId) -> Operation | None: ...

    def find_claimable(self, *, limit: int = 10) -> list[Operation]: ...

    def find_by_idempotency_key(self, key: str) -> Operation | None: ...


@runtime_checkable
class SubscriptionRevisionRepository(Protocol):
    def add(self, revision: SubscriptionRevision) -> None: ...

    def get(self, revision_id: EntityId) -> SubscriptionRevision | None: ...


@runtime_checkable
class AuditRecordRepository(Protocol):
    def add(self, audit_record: AuditRecord) -> None: ...

    def get(self, audit_record_id: EntityId) -> AuditRecord | None: ...
