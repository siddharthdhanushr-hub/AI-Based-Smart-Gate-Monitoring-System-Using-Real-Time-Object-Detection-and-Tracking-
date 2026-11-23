"""
System and security alerts API routes.
"""

import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.schemas.alert import AlertListResponse, AlertResponse

router = APIRouter(prefix="/alerts", tags=["System Alerts"])


@router.get("", response_model=AlertListResponse)
def get_alerts(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Retrieves operational, congestion, and security alerts."""
    alerts = crud.get_alerts(db=db, limit=limit, unread_only=unread_only)
    formatted = []
    for a in alerts:
        meta = None
        if a.metadata_json:
            try:
                meta = json.loads(a.metadata_json)
            except Exception:
                meta = None
        formatted.append(AlertResponse(
            id=a.id,
            alert_type=a.alert_type,
            severity=a.severity,
            message=a.message,
            timestamp=a.timestamp,
            is_resolved=a.is_resolved,
            metadata=meta
        ))
    return AlertListResponse(total=len(formatted), alerts=formatted)
