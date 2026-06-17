from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from api.rest.app import create_app
from config import Config
from containers import create_container


@pytest.fixture
def app_client_factory() -> Callable[[Config | None], TestClient]:
    def factory(settings: Config | None = None) -> TestClient:
        container = create_container()
        if settings is not None:
            container.settings.override(settings)

        return TestClient(create_app(container=container))

    return factory
