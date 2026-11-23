"""
Historical and peak hour analytics API routes.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.schemas.stats import DailyAnalyticsResponse, HourlyAnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Traffic Analytics"])


@router.get("/daily", response_model=DailyAnalyticsResponse)
def get_daily_analytics(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Returns daily traffic totals over the past N days."""
    data = crud.get_daily_analytics(db=db, days=days)
    return DailyAnalyticsResponse(days=days, data=data)


@router.get("/hourly", response_model=HourlyAnalyticsResponse)
def get_hourly_analytics(
    date: Optional[str] = Query(None, description="Format YYYY-MM-DD (defaults to today)"),
    db: Session = Depends(get_db)
):
    """Returns 24-hour distribution of movements for a given date."""
    distribution = crud.get_hourly_analytics(db=db, query_date=date)
    return HourlyAnalyticsResponse(
        date=date or "today",
        hourly_distribution=distribution
    )
