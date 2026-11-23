"""
Database Repository (CRUD operations) for the Gate Monitoring System.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from backend.app.database.models import MonitoringEvent, GateTrafficStats, SystemAlert, CameraConfig


def record_crossing_event(
    db: Session,
    track_id: int,
    class_id: int,
    class_name: str,
    direction: str,
    confidence: float,
    bbox: List[int],
    centroid: List[int],
    timestamp: Optional[datetime] = None,
    snapshot_path: Optional[str] = None
) -> MonitoringEvent:
    """Inserts a new gate crossing event and updates daily aggregate statistics."""
    ts = timestamp or datetime.now(timezone.utc)
    event = MonitoringEvent(
        track_id=track_id,
        class_id=class_id,
        class_name=class_name.lower(),
        direction=direction.upper(),
        confidence=confidence,
        bbox_x1=bbox[0],
        bbox_y1=bbox[1],
        bbox_x2=bbox[2],
        bbox_y2=bbox[3],
        centroid_x=centroid[0],
        centroid_y=centroid[1],
        timestamp=ts,
        snapshot_path=snapshot_path
    )
    db.add(event)
    
    # Update or insert daily stats
    today_str = ts.strftime("%Y-%m-%d")
    stats = db.query(GateTrafficStats).filter(GateTrafficStats.date == today_str).first()
    if not stats:
        stats = GateTrafficStats(
            date=today_str,
            total_entries=0,
            total_exits=0,
            people_entries=0,
            people_exits=0,
            vehicle_entries=0,
            vehicle_exits=0
        )
        db.add(stats)

    is_entry = direction.upper() == "ENTRY"
    is_person = class_name.lower() == "person"

    if is_entry:
        stats.total_entries = (stats.total_entries or 0) + 1
        if is_person:
            stats.people_entries = (stats.people_entries or 0) + 1
        else:
            stats.vehicle_entries = (stats.vehicle_entries or 0) + 1
    else:
        stats.total_exits = (stats.total_exits or 0) + 1
        if is_person:
            stats.people_exits = (stats.people_exits or 0) + 1
        else:
            stats.vehicle_exits = (stats.vehicle_exits or 0) + 1

    stats.last_updated = ts
    db.commit()
    db.refresh(event)
    return event


def get_events(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    direction: Optional[str] = None,
    class_name: Optional[str] = None
) -> Tuple[int, List[MonitoringEvent]]:
    """Returns paginated events matching optional filters."""
    query = db.query(MonitoringEvent)
    if direction:
        query = query.filter(MonitoringEvent.direction == direction.upper())
    if class_name:
        query = query.filter(MonitoringEvent.class_name == class_name.lower())

    total = query.count()
    events = query.order_by(desc(MonitoringEvent.timestamp)).offset(offset).limit(limit).all()
    return total, events


def get_realtime_stats(db: Session) -> Dict[str, Any]:
    """Calculates overall and today's cumulative stats with per-class breakdown."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_stats = db.query(GateTrafficStats).filter(GateTrafficStats.date == today_str).first()

    # Totals across all time
    all_time_entries = db.query(func.count(MonitoringEvent.id)).filter(MonitoringEvent.direction == "ENTRY").scalar() or 0
    all_time_exits = db.query(func.count(MonitoringEvent.id)).filter(MonitoringEvent.direction == "EXIT").scalar() or 0

    # Per-class counts for today
    today_events = db.query(
        MonitoringEvent.class_name,
        MonitoringEvent.direction,
        func.count(MonitoringEvent.id)
    ).group_by(MonitoringEvent.class_name, MonitoringEvent.direction).all()

    by_class: Dict[str, Dict[str, int]] = {
        "person": {"entry": 0, "exit": 0},
        "bicycle": {"entry": 0, "exit": 0},
        "car": {"entry": 0, "exit": 0},
        "motorcycle": {"entry": 0, "exit": 0},
        "bus": {"entry": 0, "exit": 0},
        "truck": {"entry": 0, "exit": 0}
    }

    for c_name, dir_name, count in today_events:
        c_name = c_name.lower()
        dir_name = dir_name.lower()
        if c_name in by_class and dir_name in by_class[c_name]:
            by_class[c_name][dir_name] = count

    today_entries = today_stats.total_entries if today_stats else 0
    today_exits = today_stats.total_exits if today_stats else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
        "total_entries": all_time_entries,
        "total_exits": all_time_exits,
        "net_inside": max(0, all_time_entries - all_time_exits),
        "today": {
            "entries": today_entries,
            "exits": today_exits,
            "people_entries": today_stats.people_entries if today_stats else 0,
            "people_exits": today_stats.people_exits if today_stats else 0,
            "vehicle_entries": today_stats.vehicle_entries if today_stats else 0,
            "vehicle_exits": today_stats.vehicle_exits if today_stats else 0
        },
        "by_class": by_class
    }


def get_daily_analytics(db: Session, days: int = 7) -> List[Dict[str, Any]]:
    """Returns aggregated traffic across the past N days."""
    stats = db.query(GateTrafficStats).order_by(desc(GateTrafficStats.date)).limit(days).all()
    res = []
    for s in reversed(stats):
        res.append({
            "date": s.date,
            "entries": s.total_entries or 0,
            "exits": s.total_exits or 0,
            "people": (s.people_entries or 0) + (s.people_exits or 0),
            "vehicles": (s.vehicle_entries or 0) + (s.vehicle_exits or 0)
        })
    return res


def get_hourly_analytics(db: Session, query_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns 24-hour distribution of movements for peak hour analysis."""
    d_str = query_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    events = db.query(MonitoringEvent).all()
    # Group by hour for the date
    hourly_map = {f"{h:02d}:00": {"entries": 0, "exits": 0, "people": 0, "vehicles": 0} for h in range(24)}
    
    for ev in events:
        if ev.timestamp.strftime("%Y-%m-%d") == d_str:
            hour_key = ev.timestamp.strftime("%H:00")
            is_entry = ev.direction == "ENTRY"
            is_person = ev.class_name == "person"
            if hour_key in hourly_map:
                if is_entry:
                    hourly_map[hour_key]["entries"] += 1
                else:
                    hourly_map[hour_key]["exits"] += 1
                if is_person:
                    hourly_map[hour_key]["people"] += 1
                else:
                    hourly_map[hour_key]["vehicles"] += 1

    return [{"hour": k, **v} for k, v in hourly_map.items()]


def log_system_alert(
    db: Session,
    alert_type: str,
    message: str,
    severity: str = "INFO",
    metadata_json: Optional[str] = None
) -> SystemAlert:
    """Creates a system alert log."""
    alert = SystemAlert(
        alert_type=alert_type,
        severity=severity.upper(),
        message=message,
        timestamp=datetime.now(timezone.utc),
        metadata_json=metadata_json
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alerts(db: Session, limit: int = 20, unread_only: bool = False) -> List[SystemAlert]:
    """Retrieves recent system alerts."""
    q = db.query(SystemAlert)
    if unread_only:
        q = q.filter(SystemAlert.is_resolved == False)
    return q.order_by(desc(SystemAlert.timestamp)).limit(limit).all()
