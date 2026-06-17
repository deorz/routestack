from arq.worker import func as arq_func


@arq_func
async def process_operation(ctx: dict[str, object], operation_id: str) -> None:
    container = ctx["container"]
    uow_factory = container.unit_of_work  # type: ignore[union-attr]

    with uow_factory() as uow:
        operation = uow.operations.get(operation_id)  # type: ignore[arg-type]
        if operation is None:
            return

        operation.claim()
        uow.operations.add(operation)

        operation.succeed()
        uow.operations.add(operation)


FUNCTIONS = [process_operation]
