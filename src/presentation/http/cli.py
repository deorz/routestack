import uvicorn

from infrastructure.container import create_container


def run() -> None:
    container = create_container()
    settings = container.settings()

    uvicorn.run(
        "presentation.http.app:create_app",
        factory=True,
        host=settings.server_host,
        port=settings.server_port,
    )
