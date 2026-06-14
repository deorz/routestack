from fastapi import FastAPI

from infrastructure.container import Container, create_container


def create_app(container: Container | None = None) -> FastAPI:
    app_container = container or create_container()
    app_settings = app_container.settings()
    app = FastAPI(title=app_settings.app_name)
    app.state.container = app_container

    @app.get("/healthz", include_in_schema=False)
    def healthcheck() -> dict[str, str]:
        settings = app_container.settings()
        return {"status": "ok", "service": settings.app_name}

    return app
