"""
Schemas package for Smart Gate Monitoring System.
"""
from backend.app.schemas.detection import DetectionItem, TrackTrajectory
from backend.app.schemas.event import (
    GateCrossingEventCreate,
    GateCrossingEventResponse,
    PaginatedEventsResponse
)
from backend.app.schemas.stats import (
    TodayStats,
    ClassDirectionStats,
    RealtimeStatsResponse,
    DailyAnalyticsResponse,
    HourlyAnalyticsResponse
)
from backend.app.schemas.alert import AlertResponse, AlertListResponse
from backend.app.schemas.camera import (
    GateLinePoints,
    CameraStartRequest,
    CameraStartResponse,
    CameraStopResponse,
    CameraSourceSwitchRequest,
    CameraSourceResponse
)
