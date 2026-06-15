import uvicorn
from pydantic import BaseModel

from application.settings import AppSettings
from infrastructure.container import create_container


class UvicornConfig(BaseModel):
    app: str = "presentation.http.app:create_app"
    factory: bool = True
    host: str
    port: int

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "UvicornConfig":
        return cls(
            host=settings.server.host,
            port=settings.server.port,
        )


def run_server() -> None:
    settings = create_container().settings()
    uvicorn.run(**UvicornConfig.from_settings(settings).model_dump())


def main() -> None:
    run_server()
