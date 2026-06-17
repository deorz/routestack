from typing import Any

from arq.connections import RedisSettings

from config import Config
from containers import Container
from outbox import tasks

_settings = Config()


async def startup(ctx: dict[str, Any]) -> None:
    container = Container()
    await container.init_resources()  # type: ignore[misc]
    ctx["container"] = container


async def shutdown(ctx: dict[str, Any]) -> None:
    await ctx["container"].shutdown_resources()  # type: ignore[misc]


class WorkerSettings:
    functions: list = [tasks.process_outbox_operation]  # noqa: RUF012
    redis_settings: RedisSettings = RedisSettings.from_dsn(_settings.REDIS.URL)
    on_startup = startup
    on_shutdown = shutdown
    max_tries = 5
