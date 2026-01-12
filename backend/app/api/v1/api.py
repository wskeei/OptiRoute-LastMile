from fastapi import APIRouter
from app.api.v1.endpoints import utils, delivery, dispatch, stats

api_router = APIRouter()
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(delivery.router, prefix="/delivery", tags=["delivery"])
api_router.include_router(dispatch.router, prefix="/dispatch", tags=["dispatch"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
