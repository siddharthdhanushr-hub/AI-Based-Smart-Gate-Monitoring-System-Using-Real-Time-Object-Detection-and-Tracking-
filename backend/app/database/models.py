"""
SQLAlchemy ORM models for monitoring events, traffic aggregates, alerts, and camera settings.
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from backend.app.database.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class MonitoringEvent(Base):
    """Stores individual gate line crossing events."""
    __tablename__ = "monitoring_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    track_id = Column(Integer, nullable=False, index=True)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(32), nullable=False, index=True)
    direction = Column(String(16), nullable=False, index=True)  # ENTRY or EXIT
    confidence = Column(Float, nullable=False)
    
    # Bounding box coordinates in frame space
    bbox_x1 = Column(Integer, nullable=False)
    bbox_y1 = Column(Integer, nullable=False)
    bbox_x2 = Column(Integer, nullable=False)
    bbox_y2 = Column(Integer, nullable=False)
    
    # Bottom-center centroid
    centroid_x = Column(Integer, nullable=False)
    centroid_y = Column(Integer, nullable=False)
    
    timestamp = Column(DateTime, default=utc_now, index=True)
    snapshot_path = Column(String(256), nullable=True)


class GateTrafficStats(Base):
    """Daily cumulative traffic aggregates for historical analysis."""
    __tablename__ = "gate_traffic_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True)  # YYYY-MM-DD
    total_entries = Column(Integer, default=0, nullable=False)
    total_exits = Column(Integer, default=0, nullable=False)
    people_entries = Column(Integer, default=0, nullable=False)
    people_exits = Column(Integer, default=0, nullable=False)
    vehicle_entries = Column(Integer, default=0, nullable=False)
    vehicle_exits = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=utc_now, onupdate=utc_now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_entries = kwargs.get("total_entries", 0)
        self.total_exits = kwargs.get("total_exits", 0)
        self.people_entries = kwargs.get("people_entries", 0)
        self.people_exits = kwargs.get("people_exits", 0)
        self.vehicle_entries = kwargs.get("vehicle_entries", 0)
        self.vehicle_exits = kwargs.get("vehicle_exits", 0)


class SystemAlert(Base):
    """Operational and security alerts."""
    __tablename__ = "system_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(32), nullable=False, index=True)
    severity = Column(String(16), default="INFO")  # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=utc_now, index=True)
    is_resolved = Column(Boolean, default=False)
    metadata_json = Column(Text, nullable=True)


class CameraConfig(Base):
    """Persisted camera and gate line configurations."""
    __tablename__ = "camera_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), default="Primary Gate Camera")
    source_type = Column(String(32), default="webcam")  # webcam, file, rtsp
    source_value = Column(String(256), default="0")
    gate_line_p1_x = Column(Integer, default=100)
    gate_line_p1_y = Column(Integer, default=360)
    gate_line_p2_x = Column(Integer, default=1180)
    gate_line_p2_y = Column(Integer, default=360)
    is_active = Column(Boolean, default=True)
