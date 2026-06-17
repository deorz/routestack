from pathlib import Path

import pytest

from app_layer.ports.unit_of_work import UnitOfWork
from domain.clients.client import Client
from infra.db import Base, create_session_factory, create_sqlite_engine
from infra.db.unit_of_work import SqlAlchemyUnitOfWork


def test_unit_of_work_commits_client_to_new_transaction(tmp_path: Path) -> None:
    session_factory = _session_factory(tmp_path)
    client = Client(display_name="Grace Hopper", tags=("admin",))

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        assert isinstance(unit_of_work, UnitOfWork)
        unit_of_work.clients.add(client)

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        loaded = unit_of_work.clients.get(client.id)

    assert loaded is not None
    assert loaded.model_dump() == client.model_dump()


def test_unit_of_work_rolls_back_uncommitted_changes_on_exception(tmp_path: Path) -> None:
    session_factory = _session_factory(tmp_path)
    client = Client(display_name="Rollback Candidate")

    with pytest.raises(RuntimeError, match="abort"), SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.clients.add(client)
        raise RuntimeError("abort")

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        loaded = unit_of_work.clients.get(client.id)

    assert loaded is None


def _session_factory(tmp_path: Path):
    engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'uow.db'}")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)
