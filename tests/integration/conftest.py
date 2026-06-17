from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from api.rest.app import create_app
from config import Config
from containers import create_container
from infra.db import Base


@pytest.fixture
def app_client_factory() -> Callable[[Config | None], TestClient]:
    def factory(settings: Config | None = None) -> TestClient:
        container = create_container()
        if settings is not None:
            container.settings.override(settings)
        return TestClient(create_app(container=container))

    return factory


@pytest.fixture
def seeded_app_client(tmp_path) -> TestClient:
    """TestClient with temp SQLite DB created and admin user bootstrapped."""
    settings = Config()
    settings.DATABASE.URL = f"sqlite:///{tmp_path}/integration-test.db"
    container = create_container()
    container.settings.override(settings)
    Base.metadata.create_all(container.db_engine())
    client = TestClient(create_app(container=container))
    container.admin_auth_service().bootstrap_user(login="root", password="secret-123")
    return client
