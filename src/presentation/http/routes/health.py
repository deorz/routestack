from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from application.settings import AppSettings
from infrastructure.container import Container

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
@inject
def healthcheck(
    settings: Annotated[AppSettings, Depends(Provide[Container.settings])],
) -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
