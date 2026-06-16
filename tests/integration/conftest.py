from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from application.settings import Config
from infrastructure.container import create_container
from presentation.http.app import create_app


@pytest.fixture
def app_client_factory() -> Callable[[Config | None], TestClient]:
    def factory(settings: Config | None = None) -> TestClient:
        container = create_container()
        if settings is not None:
            container.settings.override(settings)

        return TestClient(create_app(container=container))

    return factory
