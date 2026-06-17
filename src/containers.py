from dependency_injector import containers, providers

from app_layer.admins import AdminAuthService
from app_layer.operations import OperationQueue
from config import Config
from infra.db import SqlAlchemyUnitOfWork, create_session_factory, create_sqlite_engine
from infra.queue import create_redis_pool
from infra.security import BcryptPasswordHasher, Sha256AccessTokenGenerator


class Container(containers.DeclarativeContainer):
    """Application composition root."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.rest.admin.v1.auth",
            "api.rest.dependencies.auth",
            "api.rest.dependencies.idempotency",
            "api.rest.healthcheck",
        ],
    )

    settings = providers.Singleton(Config)
    password_hasher = providers.Singleton(BcryptPasswordHasher)
    token_generator = providers.Singleton(Sha256AccessTokenGenerator)

    redis_pool = providers.Resource(
        create_redis_pool,
        redis_url=settings.provided.REDIS.URL,
    )

    operation_queue = providers.Factory(
        OperationQueue,
        redis=redis_pool,
    )

    db_engine = providers.Singleton(
        create_sqlite_engine,
        url=settings.provided.DATABASE.URL,
    )
    session_factory = providers.Singleton(
        create_session_factory,
        engine=db_engine,
    )
    unit_of_work = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_factory=session_factory,
    )
    admin_auth_service = providers.Factory(
        AdminAuthService,
        unit_of_work=unit_of_work,
        password_hasher=password_hasher,
    )


def create_container() -> Container:
    return Container()
