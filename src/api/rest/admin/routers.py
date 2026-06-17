from fastapi import APIRouter

from api.rest.admin.v1.routers import v1_router

admin_router = APIRouter(tags=["admin"])
admin_router.include_router(v1_router)
