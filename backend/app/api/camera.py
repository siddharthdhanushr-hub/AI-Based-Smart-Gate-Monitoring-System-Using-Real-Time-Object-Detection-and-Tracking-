"""
Camera control API routes: Start, Stop, and Switch Source.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.camera import (
    CameraStartRequest,
    CameraStartResponse,
    CameraStopResponse,
    CameraSourceSwitchRequest,
    CameraSourceResponse
)
from backend.app.services.event_processor import monitoring_processor
from backend.app.services.camera_service import camera_service

router = APIRouter(prefix="/camera", tags=["Camera Controls"])


@router.post("/start", response_model=CameraStartResponse)
async def start_camera(request: CameraStartRequest = CameraStartRequest()):
    """Starts video ingestion and the monitoring processing loop."""
    try:
        if request.gate_line:
            monitoring_processor.set_gate_line(request.gate_line.p1, request.gate_line.p2)

        if request.source:
            camera_service.source_value = request.source

        await monitoring_processor.start()
        return CameraStartResponse(
            status="success",
            message="Camera monitoring loop started",
            active_source=camera_service.source_value,
            is_running=True,
            started_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start camera: {str(e)}")


@router.post("/stop", response_model=CameraStopResponse)
async def stop_camera():
    """Stops video ingestion and monitoring loop."""
    try:
        await monitoring_processor.stop()
        return CameraStopResponse(
            status="success",
            message="Camera monitoring loop stopped",
            is_running=False,
            stopped_at=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop camera: {str(e)}")


@router.post("/source", response_model=CameraSourceResponse)
async def switch_camera_source(request: CameraSourceSwitchRequest):
    """Dynamically switches active video stream source."""
    try:
        success = camera_service.switch_source(request.source_type, request.source_value)
        if not success:
            raise HTTPException(status_code=400, detail="Could not initialize requested video source")

        return CameraSourceResponse(
            status="success",
            source_type=request.source_type,
            source_value=request.source_value,
            message="Camera source switched successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch camera source: {str(e)}")
