import uvicorn
from pydantic import BaseModel

from config import Config
from containers import create_container


class UvicornConfig(BaseModel):
    app: str = "api.rest.app:create_app"
    factory: bool = True
    host: str
    port: int

    @classmethod
    def from_settings(cls, settings: Config) -> "UvicornConfig":
        return cls(
            host=settings.SERVER.HOST,
            port=settings.SERVER.PORT,
        )


def run_server() -> None:
    settings = create_container().settings()
    uvicorn.run(**UvicornConfig.from_settings(settings).model_dump())


if __name__ == "__main__":
    run_server()
