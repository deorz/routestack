from arq.connections import ArqRedis


class OperationQueue:
    def __init__(self, redis: ArqRedis) -> None:
        self._redis = redis

    async def enqueue(self, operation_id: str, *, idempotency_key: str | None = None) -> None:
        await self._redis.enqueue_job(
            "process_operation",
            str(operation_id),
            _job_id=idempotency_key,
        )
