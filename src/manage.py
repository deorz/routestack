import sys

import uvicorn
from pydantic import BaseModel

from config import Config
from containers import create_container
from worker import run_worker


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


def run_operation_worker() -> None:
    settings = create_container().settings()
    run_worker(settings.REDIS.URL)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"
    if mode == "worker":
        run_operation_worker()
    else:
        run_server()
