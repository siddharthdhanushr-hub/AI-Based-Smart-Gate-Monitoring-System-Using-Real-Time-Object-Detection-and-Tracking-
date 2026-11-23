"""
Monitoring stats and events API routes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.schemas.stats import RealtimeStatsResponse
from backend.app.schemas.event import PaginatedEventsResponse, GateCrossingEventResponse

router = APIRouter(prefix="/monitoring", tags=["Monitoring & Events"])


@router.get("/stats", response_model=RealtimeStatsResponse)
def get_monitoring_stats(db: Session = Depends(get_db)):
    """Returns real-time cumulative, today, and per-class traffic statistics."""
    stats = crud.get_realtime_stats(db)
    return stats


@router.get("/events", response_model=PaginatedEventsResponse)
def get_monitoring_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    direction: Optional[str] = Query(None, pattern="^(ENTRY|EXIT|entry|exit)$"),
    class_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns paginated gate crossing event records."""
    total, events = crud.get_events(
        db=db,
        limit=limit,
        offset=offset,
        direction=direction,
        class_name=class_name
    )

    formatted_events = []
    for ev in events:
        formatted_events.append(GateCrossingEventResponse(
            id=ev.id,
            event_id=ev.event_id,
            track_id=ev.track_id,
            class_id=ev.class_id,
            class_name=ev.class_name,
            direction=ev.direction,
            confidence=ev.confidence,
            bbox=[ev.bbox_x1, ev.bbox_y1, ev.bbox_x2, ev.bbox_y2],
            centroid=[ev.centroid_x, ev.centroid_y],
            timestamp=ev.timestamp,
            snapshot_path=ev.snapshot_path
        ))

    return PaginatedEventsResponse(
        total_count=total,
        limit=limit,
        offset=offset,
        events=formatted_events
    )
