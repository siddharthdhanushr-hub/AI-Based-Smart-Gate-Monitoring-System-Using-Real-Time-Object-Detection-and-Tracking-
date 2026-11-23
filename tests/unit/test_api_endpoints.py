"""
Unit tests for FastAPI REST API endpoints using TestClient.
"""

from fastapi.testclient import TestClient


def test_root_status(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_camera_start_and_stop(client: TestClient):
    # Test camera start
    start_resp = client.post("/api/camera/start", json={"source": "0"})
    assert start_resp.status_code == 200
    start_data = start_resp.json()
    assert start_data["status"] == "success"
    assert start_data["is_running"] is True

    # Test camera stop
    stop_resp = client.post("/api/camera/stop")
    assert stop_resp.status_code == 200
    stop_data = stop_resp.json()
    assert stop_data["status"] == "success"
    assert stop_data["is_running"] is False


def test_camera_source_switch(client: TestClient):
    resp = client.post("/api/camera/source", json={
        "source_type": "file",
        "source_value": "sample_video.mp4"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["source_value"] == "sample_video.mp4"


def test_monitoring_stats_endpoint(client: TestClient):
    response = client.get("/api/monitoring/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_entries" in data
    assert "total_exits" in data
    assert "today" in data
    assert "by_class" in data


def test_monitoring_events_endpoint(client: TestClient):
    response = client.get("/api/monitoring/events?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "events" in data
    assert isinstance(data["events"], list)


def test_analytics_endpoints(client: TestClient):
    # Test daily analytics
    resp_daily = client.get("/api/analytics/daily?days=7")
    assert resp_daily.status_code == 200
    daily_data = resp_daily.json()
    assert "data" in daily_data

    # Test hourly analytics
    resp_hourly = client.get("/api/analytics/hourly")
    assert resp_hourly.status_code == 200
    hourly_data = resp_hourly.json()
    assert "hourly_distribution" in hourly_data


def test_alerts_endpoint(client: TestClient):
    response = client.get("/api/alerts?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "alerts" in data
