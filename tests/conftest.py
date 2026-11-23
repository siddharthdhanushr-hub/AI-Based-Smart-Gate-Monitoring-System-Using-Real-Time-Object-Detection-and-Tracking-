"""
Pytest configuration, fixtures, and in-memory test database setup.
Uses StaticPool to ensure all connections in a test share the in-memory database.
"""

import pytest
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.database.session import Base, get_db
from backend.app.main import app

# In-memory SQLite with StaticPool so all threads/sessions share the same DB in test
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a clean in-memory database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_frame():
    """Returns a synthetic 720p BGR frame."""
    return np.zeros((720, 1280, 3), dtype=np.uint8)


@pytest.fixture
def sample_detection_payload():
    """Returns a valid detection/tracking dictionary matching the contract."""
    return {
        "track_id": 12,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.92,
        "bbox": [100, 120, 240, 400],
        "center": [170, 400]
    }
