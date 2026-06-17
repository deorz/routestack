from fastapi import FastAPI

from api.rest.routers import init_rest_api
from containers import Container, create_container


def create_app(container: Container | None = None) -> FastAPI:
    app_container = container or create_container()
    app_settings = app_container.settings()
    app = FastAPI(title=app_settings.APP.NAME)
    app.state.container = app_container
    init_rest_api(app, app_settings)

    return app
