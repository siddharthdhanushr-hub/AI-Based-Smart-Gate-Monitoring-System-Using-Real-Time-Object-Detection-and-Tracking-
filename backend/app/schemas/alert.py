"""
Pydantic schemas for alerts and camera controls.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# --- Alerts Schemas ---
class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    is_resolved: bool
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertResponse]


# --- Camera Control Schemas ---
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
