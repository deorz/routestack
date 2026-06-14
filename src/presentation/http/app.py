from fastapi import FastAPI

from infrastructure.container import Container, create_container
from presentation.http.routes.health import router as health_router


def create_app(container: Container | None = None) -> FastAPI:
    app_container = container or create_container()
    app_settings = app_container.settings()
    app = FastAPI(title=app_settings.app_name)
    app.state.container = app_container
    app.include_router(health_router)

    return app
