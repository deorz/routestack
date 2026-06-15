from dataclasses import dataclass

from application.ports.repositories import (
    AccessGrantRepository,
    AdminUserRepository,
    ClientRepository,
    OperationRepository,
    SubscriptionRepository,
)
from application.ports.unit_of_work import UnitOfWork
from domain.admins.admin_user import AdminUser
from domain.clients.client import Client
from domain.shared.entity_id import EntityId


class InMemoryClientRepository:
    def __init__(self) -> None:
        self.clients: dict[EntityId, Client] = {}

    def add(self, client: Client) -> None:
        self.clients[client.id] = client

    def get(self, client_id: EntityId) -> Client | None:
        return self.clients.get(client_id)


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


@dataclass
class FakeUnitOfWork:
    admins: AdminUserRepository
    clients: ClientRepository
    subscriptions: SubscriptionRepository
    access_grants: AccessGrantRepository
    operations: OperationRepository
    committed: bool = False
    rolled_back: bool = False

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc is not None:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def test_repository_and_unit_of_work_ports_accept_in_memory_implementations() -> None:
    repository = InMemoryClientRepository()
    admin_repository = InMemoryAdminUserRepository()
    unit_of_work = FakeUnitOfWork(
        admins=admin_repository,
        clients=repository,
        subscriptions=repository,
        access_grants=repository,
        operations=repository,
    )
    client = Client(display_name="Ada Lovelace")

    assert isinstance(repository, ClientRepository)
    assert isinstance(admin_repository, AdminUserRepository)
    assert isinstance(unit_of_work, UnitOfWork)

    with unit_of_work as transaction:
        transaction.clients.add(client)
        transaction.commit()

    assert repository.get(client.id) == client
    assert unit_of_work.committed is True
