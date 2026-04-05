from fastapi import APIRouter

from . import health

__all__ = ("router",)

router = APIRouter()

router.include_router(health.router)
