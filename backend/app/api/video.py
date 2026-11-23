"""
Video streaming API route serving live MJPEG stream.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.app.services.camera_service import camera_service

router = APIRouter(prefix="/video", tags=["Video Stream"])


@router.get("/stream")
def get_video_stream():
    """
    Streams multipart MJPEG annotated video feed for embedding in the React dashboard.
    """
    if not camera_service.is_running:
        camera_service.start()

    return StreamingResponse(
        camera_service.get_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
