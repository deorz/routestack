from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from config import Config
from containers import Container

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
@inject
def healthcheck(settings: Annotated[Config, Depends(Provide[Container.settings])]) -> dict[str, str]:
    return {"status": "ok", "service": settings.APP.NAME}
