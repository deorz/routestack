from typing import Any

from dependency_injector.wiring import Provide, inject

from containers import Container


@inject
async def process_outbox_operation(
    _ctx: dict[str, Any],
    operation_id: str,
    unit_of_work: Any = Provide[Container.unit_of_work],
) -> None:
    with unit_of_work() as uow:
        operation = uow.operations.get(operation_id)
        if operation is None:
            return

        operation.claim()
        uow.operations.add(operation)

        operation.succeed()
        uow.operations.add(operation)

        uow.commit()
