import asyncio
import logging
from collections.abc import Callable

from app_layer.ports.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

_POLL_INTERVAL_SECONDS = 5
_BATCH_LIMIT = 10


class OperationWorker:
    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = unit_of_work_factory
        self._running = False
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self._process_batch()
            except Exception:
                logger.exception("Operation worker iteration failed")

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)

    async def _process_batch(self) -> None:
        with self._uow_factory() as uow:
            claimable = uow.operations.find_claimable(limit=_BATCH_LIMIT)
            if not claimable:
                return

            operation = claimable[0]
            operation.claim()
            uow.operations.add(operation)

            operation.succeed()
            uow.operations.add(operation)
