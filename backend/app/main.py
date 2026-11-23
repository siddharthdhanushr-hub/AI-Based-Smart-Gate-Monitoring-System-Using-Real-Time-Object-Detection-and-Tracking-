"""
FastAPI Application Entrypoint for AI-Based Smart Gate Monitoring System.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.session import init_db
from backend.app.api import api_router
from backend.app.api.websocket import router as ws_router
from backend.app.services.camera_service import camera_service
from backend.app.services.event_processor import monitoring_processor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    # Startup: Initialize database schema
    init_db()
    yield
    # Shutdown: Stop monitoring and release camera resources
    if monitoring_processor.is_running:
        await monitoring_processor.stop()
    if camera_service.is_running:
        camera_service.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-time object detection, tracking, and directional gate counting API",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS) for React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST and WebSocket routers
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(ws_router)


@app.get("/", tags=["Health & Status"])
def root_status():
    """System health and gateway metadata."""
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": "/docs",
        "endpoints": {
            "camera_start": f"{settings.API_PREFIX}/camera/start",
            "camera_stop": f"{settings.API_PREFIX}/camera/stop",
            "camera_source": f"{settings.API_PREFIX}/camera/source",
            "video_stream": f"{settings.API_PREFIX}/video/stream",
            "monitoring_stats": f"{settings.API_PREFIX}/monitoring/stats",
            "monitoring_events": f"{settings.API_PREFIX}/monitoring/events",
            "analytics_daily": f"{settings.API_PREFIX}/analytics/daily",
            "analytics_hourly": f"{settings.API_PREFIX}/analytics/hourly",
            "alerts": f"{settings.API_PREFIX}/alerts",
            "websocket": "/ws/monitoring"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
