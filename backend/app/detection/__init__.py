"""
Detection and tracking package for Smart Gate Monitoring System.
"""
from backend.app.detection.model_loader import ModelLoader
from backend.app.detection.kalman_filter import KalmanFilter
from backend.app.detection.tracker_deepsort import DeepSortTracker, Track, TrackState
from backend.app.detection.detector import SimpleCentroidTracker, DetectionPipeline
