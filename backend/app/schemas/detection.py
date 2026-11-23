"""
Pydantic schemas for detection and tracking data contracts.
Matches the contract required by Siddharth Chandrashekar.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DetectionItem(BaseModel):
    """
    Contract for detected and tracked objects.
    Matches Chandrashekar's required interface.
    """
    track_id: int = Field(..., description="Unique persistent tracking ID (or -1 if raw detection)")
    class_id: int = Field(..., ge=0, le=5, description="Category index 0 to 5")
    class_name: str = Field(..., description="Canonical class name: person, bicycle, car, motorcycle, bus, truck")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    bbox: List[int] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2]")
    center: List[int] = Field(..., min_length=2, max_length=2, description="Centroid coordinate [cx, cy]")


class TrackTrajectory(BaseModel):
    """Stores spatial history for a tracked object."""
    track_id: int
    class_name: str
    points: List[List[int]]  # History of [cx, cy] points
    last_seen_frame: int
