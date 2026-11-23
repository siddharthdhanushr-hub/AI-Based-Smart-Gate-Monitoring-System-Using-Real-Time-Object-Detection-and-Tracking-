"""
Pydantic schemas for gate crossing events.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class GateCrossingEventCreate(BaseModel):
    track_id: int
    class_id: int
    class_name: str
    direction: str  # ENTRY or EXIT
    confidence: float
    bbox: List[int]
    centroid: List[int]
    timestamp: Optional[datetime] = None
    snapshot_path: Optional[str] = None


class GateCrossingEventResponse(BaseModel):
    id: int
    event_id: str
    track_id: int
    class_id: int
    class_name: str
    direction: str
    confidence: float
    bbox: List[int]
    centroid: List[int]
    timestamp: datetime
    snapshot_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEventsResponse(BaseModel):
    total_count: int
    limit: int
    offset: int
    events: List[GateCrossingEventResponse]
