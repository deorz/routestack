from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from domain.admins.admin_user import AdminUser
from infrastructure.db import (
    Base,
    create_session_factory,
    create_sqlite_engine,
)
from infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def test_admin_user_round_trip_persistence(tmp_path: Path) -> None:
    admin_user = AdminUser(
        id=UUID("00000000-0000-0000-0000-000000000101"),
        login="root",
        password_hash="hash-123",
        last_login_at=datetime(2026, 6, 15, 10, 0, 0, tzinfo=UTC),
        disabled_at=datetime(2026, 6, 15, 11, 0, 0, tzinfo=UTC),
        created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
    )
    session_factory = _session_factory(tmp_path)

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.admins.add(admin_user)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        loaded_admin_user = unit_of_work.admins.get(admin_user.id)

    assert loaded_admin_user is not None
    assert loaded_admin_user.model_dump() == admin_user.model_dump()


def test_admin_user_repository_looks_up_by_login(tmp_path: Path) -> None:
    admin_user = AdminUser(login="root", password_hash="hash-123")
    session_factory = _session_factory(tmp_path)

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.admins.add(admin_user)
        unit_of_work.commit()

    with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        loaded_admin_user = unit_of_work.admins.get_by_login("root")

    assert loaded_admin_user is not None
    assert loaded_admin_user.model_dump() == admin_user.model_dump()


def _session_factory(tmp_path: Path):
    engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'uow-admin.db'}")
    Base.metadata.create_all(engine)
    return create_session_factory(engine)
