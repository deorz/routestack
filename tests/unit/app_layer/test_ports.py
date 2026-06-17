from app_layer.ports.repositories import AdminUserRepository, ClientRepository, SubscriptionRevisionRepository
from app_layer.ports.unit_of_work import UnitOfWork
from domain.clients.client import Client
from domain.shared.time import utc_now
from domain.subscriptions.revision import SubscriptionRevision
from tests.fakes import FakeUnitOfWork, InMemoryAdminUserRepository, InMemoryRepository


def test_repository_and_unit_of_work_ports_accept_in_memory_implementations() -> None:
    repository = InMemoryRepository()
    admin_repository = InMemoryAdminUserRepository()
    uow = FakeUnitOfWork(admins=admin_repository, clients=repository)
    client = Client(display_name="Ada Lovelace")

    assert isinstance(repository, ClientRepository)

    revision_repo = InMemoryRepository()
    uow_2 = FakeUnitOfWork(admins=admin_repository, clients=repository, subscription_revisions=revision_repo)
    revision = SubscriptionRevision(
        subscription_id=client.id,
        revision=1,
        safe_change_summary="test",
        created_at=utc_now(),
    )
    assert isinstance(revision_repo, SubscriptionRevisionRepository)

    with uow_2:
        uow_2.subscription_revisions.add(revision)

    assert revision_repo.get(revision.id) == revision
    assert isinstance(admin_repository, AdminUserRepository)
    assert isinstance(uow, UnitOfWork)

    with uow:
        uow.clients.add(client)

    assert repository.get(client.id) == client
    assert uow.commits == 1
    assert uow.shutdowns == 1
