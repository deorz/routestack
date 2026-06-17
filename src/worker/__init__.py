from arq import Worker
from arq.connections import RedisSettings as ArqRedisSettings

from containers import create_container
from worker.tasks import FUNCTIONS


async def _on_startup(ctx: dict[str, object]) -> None:
    ctx["container"] = create_container()


def run_worker(redis_url: str) -> None:
    settings = ArqRedisSettings.from_dsn(redis_url)
    worker = Worker(
        functions=FUNCTIONS,
        redis_settings=settings,
        on_startup=_on_startup,
    )
    worker.run()
