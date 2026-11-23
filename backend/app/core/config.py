"""
Application Configuration settings for Smart Gate Monitoring System.
Uses pydantic_settings with environment variable overrides.
"""

from typing import List, Tuple
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Based Smart Gate Monitoring System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("GATE_DATABASE_URL", "sqlite:///backend/app/gate_monitoring.db")
    
    # AI & Model Inference
    MODEL_PATH: str = os.getenv("GATE_MODEL_PATH", "yolov8n.pt")
    CONFIDENCE_THRESHOLD: float = 0.40
    IOU_THRESHOLD: float = 0.50
    INFERENCE_DEVICE: str = os.getenv("GATE_INFERENCE_DEVICE", "cpu")
    
    # Camera & Ingestion
    DEFAULT_CAMERA_SOURCE: str = os.getenv("GATE_CAMERA_SOURCE", "0")
    FRAME_WIDTH: int = 1280
    FRAME_HEIGHT: int = 720
    
    # Virtual Gate Line Coordinates (P1, P2) in [x, y]
    GATE_LINE_P1: Tuple[int, int] = (100, 360)
    GATE_LINE_P2: Tuple[int, int] = (1180, 360)
    
    # Debounce / Crossing Settings
    DEBOUNCE_SECONDS: float = 3.0
    TRACK_MAX_AGE_FRAMES: int = 30
    MIN_CROSSING_DISTANCE_PX: float = 15.0
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
