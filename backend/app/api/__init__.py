"""
API Routes Package for Smart Gate Monitoring System.
"""
from fastapi import APIRouter
from backend.app.api.camera import router as camera_router
from backend.app.api.video import router as video_router
from backend.app.api.monitoring import router as monitoring_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(camera_router)
api_router.include_router(video_router)
api_router.include_router(monitoring_router)
api_router.include_router(analytics_router)
api_router.include_router(alerts_router)
