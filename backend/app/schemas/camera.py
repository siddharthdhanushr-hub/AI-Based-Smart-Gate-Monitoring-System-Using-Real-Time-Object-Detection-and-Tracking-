"""
Pydantic schemas for camera requests and responses.
"""

from typing import Optional, Tuple
from pydantic import BaseModel, Field


class GateLinePoints(BaseModel):
    p1: Tuple[int, int] = Field(..., description="Start point [x1, y1]")
    p2: Tuple[int, int] = Field(..., description="End point [x2, y2]")


class CameraStartRequest(BaseModel):
    source: Optional[str] = Field("0", description="Webcam device index or video file path")
    gate_line: Optional[GateLinePoints] = None


class CameraStartResponse(BaseModel):
    status: str
    message: str
    active_source: str
    is_running: bool
    started_at: str


class CameraStopResponse(BaseModel):
    status: str
    message: str
    is_running: bool
    stopped_at: str


class CameraSourceSwitchRequest(BaseModel):
    source_type: str = Field(..., description="webcam or file")
    source_value: str = Field(..., description="Device index or filepath")


class CameraSourceResponse(BaseModel):
    status: str
    source_type: str
    source_value: str
    message: str
