import cv2
import numpy as np

from backend.app.services.camera_service import CameraService


def _read_stream_frame(service):
    service.is_running = True
    stream = service.get_mjpeg_stream()
    try:
        part = next(stream)
    finally:
        stream.close()
        service.is_running = False

    image_bytes = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
    return cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)


def test_mjpeg_stream_prefers_annotated_frames():
    service = CameraService()
    service.current_frame = np.zeros((16, 16, 3), dtype=np.uint8)
    annotated_frame = np.zeros((16, 16, 3), dtype=np.uint8)
    annotated_frame[:, :, 1] = 255
    service.set_annotated_frame(annotated_frame)

    frame = _read_stream_frame(service)

    assert frame[8, 8, 1] > 200
    assert frame[8, 8, 0] < 50
    assert frame[8, 8, 2] < 50


def test_mjpeg_stream_uses_raw_frame_until_annotation_is_available():
    service = CameraService()
    raw_frame = np.zeros((16, 16, 3), dtype=np.uint8)
    raw_frame[:, :, 2] = 255
    service.current_frame = raw_frame

    frame = _read_stream_frame(service)

    assert frame[8, 8, 2] > 200
    assert frame[8, 8, 0] < 50
    assert frame[8, 8, 1] < 50
