from dependency_injector import containers, providers

from application.settings import AppSettings
from infrastructure.db import SqlAlchemyUnitOfWork, create_session_factory, create_sqlite_engine
from infrastructure.security.password_hasher import BcryptPasswordHasher


class Container(containers.DeclarativeContainer):
    """Application composition root."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "presentation.http.routes.auth",
            "presentation.http.routes.health",
        ],
    )

    settings = providers.Singleton(AppSettings)
    password_hasher = providers.Singleton(BcryptPasswordHasher)
    db_engine = providers.Singleton(
        create_sqlite_engine,
        url=settings.provided.database_url,
    )
    session_factory = providers.Singleton(
        create_session_factory,
        engine=db_engine,
    )
    unit_of_work = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
    )


def create_container() -> Container:
    return Container()
