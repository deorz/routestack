from dataclasses import dataclass

from application.ports.repositories import (
    AccessGrantRepository,
    ClientRepository,
    OperationRepository,
    SubscriptionRepository,
)
from application.ports.unit_of_work import UnitOfWork
from domain.clients.client import Client
from domain.shared.entity_id import EntityId


class InMemoryClientRepository:
    def __init__(self) -> None:
        self.clients: dict[EntityId, Client] = {}

    def add(self, client: Client) -> None:
        self.clients[client.id] = client

    def get(self, client_id: EntityId) -> Client | None:
        return self.clients.get(client_id)


@dataclass
class FakeUnitOfWork:
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
    unit_of_work = FakeUnitOfWork(
        clients=repository,
        subscriptions=repository,
        access_grants=repository,
        operations=repository,
    )
    client = Client(display_name="Ada Lovelace")

    assert isinstance(repository, ClientRepository)
    assert isinstance(unit_of_work, UnitOfWork)

    with unit_of_work as transaction:
        transaction.clients.add(client)
        transaction.commit()

    assert repository.get(client.id) == client
    assert unit_of_work.committed is True
