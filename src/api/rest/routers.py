from fastapi import FastAPI

from api.rest.admin.routers import admin_router
from api.rest.healthcheck import router as healthcheck_router
from config import Config


def init_rest_api(app: FastAPI, config: Config) -> FastAPI:
    app.include_router(healthcheck_router)
    app.include_router(admin_router, prefix=config.API.ROOT_PREFIX)
    return app
