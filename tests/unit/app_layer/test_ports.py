from app_layer.ports.repositories import AdminUserRepository, ClientRepository
from app_layer.ports.unit_of_work import UnitOfWork
from domain.clients.client import Client
from tests.fakes import FakeUnitOfWork, InMemoryAdminUserRepository, InMemoryRepository


def test_repository_and_unit_of_work_ports_accept_in_memory_implementations() -> None:
    repository = InMemoryRepository()
    admin_repository = InMemoryAdminUserRepository()
    uow = FakeUnitOfWork(admins=admin_repository, clients=repository)
    client = Client(display_name="Ada Lovelace")

    assert isinstance(repository, ClientRepository)
    assert isinstance(admin_repository, AdminUserRepository)
    assert isinstance(uow, UnitOfWork)

    with uow:
        uow.clients.add(client)

    assert repository.get(client.id) == client
    assert uow.commits == 1
    assert uow.shutdowns == 1
