"""
Database package for Smart Gate Monitoring System.
"""
from backend.app.database.session import Base, engine, SessionLocal, get_db, init_db
from backend.app.database.models import MonitoringEvent, GateTrafficStats, SystemAlert, CameraConfig
