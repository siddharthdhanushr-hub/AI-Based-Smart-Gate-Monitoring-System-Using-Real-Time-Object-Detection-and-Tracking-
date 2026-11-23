"""
Pydantic schemas for telemetry, statistics, and historical analytics.
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class TodayStats(BaseModel):
    entries: int
    exits: int
    people_entries: int
    people_exits: int
    vehicle_entries: int
    vehicle_exits: int


class ClassDirectionStats(BaseModel):
    entry: int
    exit: int


class RealtimeStatsResponse(BaseModel):
    timestamp: str
    is_active: bool
    total_entries: int
    total_exits: int
    net_inside: int
    today: TodayStats
    by_class: Dict[str, ClassDirectionStats]


class DailyDataPoint(BaseModel):
    date: str
    entries: int
    exits: int
    people: int
    vehicles: int


class DailyAnalyticsResponse(BaseModel):
    days: int
    data: List[DailyDataPoint]


class HourlyDataPoint(BaseModel):
    hour: str
    entries: int
    exits: int
    people: int
    vehicles: int


class HourlyAnalyticsResponse(BaseModel):
    date: str
    hourly_distribution: List[HourlyDataPoint]
