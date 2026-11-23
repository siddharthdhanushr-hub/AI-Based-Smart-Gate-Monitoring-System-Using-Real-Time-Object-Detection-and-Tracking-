"""
Unit tests for database models and CRUD persistence repository.
"""

from datetime import datetime, timezone
from backend.app.database import crud
from backend.app.database.models import MonitoringEvent, GateTrafficStats


def test_record_crossing_event(db_session):
    event = crud.record_crossing_event(
        db=db_session,
        track_id=10,
        class_id=2,
        class_name="car",
        direction="ENTRY",
        confidence=0.93,
        bbox=[100, 150, 300, 350],
        centroid=[200, 350]
    )

    assert event.id is not None
    assert event.track_id == 10
    assert event.class_name == "car"
    assert event.direction == "ENTRY"

    # Verify that daily stats record was updated
    stats = crud.get_realtime_stats(db_session)
    assert stats["total_entries"] == 1
    assert stats["today"]["entries"] == 1
    assert stats["today"]["vehicle_entries"] == 1
    assert stats["today"]["people_entries"] == 0
    assert stats["by_class"]["car"]["entry"] == 1


def test_get_events_pagination_and_filtering(db_session):
    # Insert multiple events
    for i in range(10):
        cls_name = "person" if i % 2 == 0 else "car"
        direction = "ENTRY" if i < 7 else "EXIT"
        crud.record_crossing_event(
            db=db_session,
            track_id=i + 1,
            class_id=0 if cls_name == "person" else 2,
            class_name=cls_name,
            direction=direction,
            confidence=0.85,
            bbox=[10, 10, 50, 50],
            centroid=[30, 50]
        )

    # Test limit and offset
    total, events_page1 = crud.get_events(db=db_session, limit=5, offset=0)
    assert total == 10
    assert len(events_page1) == 5

    total, events_page2 = crud.get_events(db=db_session, limit=5, offset=5)
    assert len(events_page2) == 5

    # Test direction filter
    _, exit_events = crud.get_events(db=db_session, direction="EXIT")
    assert len(exit_events) == 3

    # Test class filter
    _, person_events = crud.get_events(db=db_session, class_name="person")
    assert len(person_events) == 5


def test_analytics_and_alerts(db_session):
    # Insert sample event
    crud.record_crossing_event(
        db=db_session,
        track_id=99,
        class_id=0,
        class_name="person",
        direction="ENTRY",
        confidence=0.91,
        bbox=[10, 10, 50, 50],
        centroid=[30, 50]
    )

    # Test daily analytics
    daily = crud.get_daily_analytics(db=db_session, days=7)
    assert len(daily) >= 1
    assert daily[0]["entries"] >= 1

    # Test hourly analytics
    hourly = crud.get_hourly_analytics(db=db_session)
    assert len(hourly) == 24

    # Test system alert logging
    alert = crud.log_system_alert(
        db=db_session,
        alert_type="TEST_ALERT",
        message="Test alert message",
        severity="WARNING"
    )
    assert alert.id is not None
    assert alert.severity == "WARNING"

    alerts = crud.get_alerts(db=db_session, limit=10)
    assert len(alerts) >= 1
    assert alerts[0].alert_type == "TEST_ALERT"
