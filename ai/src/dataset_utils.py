"""
Dataset preparation, validation, and frame sampling utilities for YOLOv8.
Enforces non-overlapping recording splits and Darknet label format validation.
"""

from typing import Dict, List, Tuple, Any, Optional
import os
import glob
import shutil
import random
import yaml


def extract_frames_from_video(
    video_path: str,
    output_dir: str,
    stride: int = 30,
    prefix: Optional[str] = None
) -> List[str]:
    """
    Extracts frames from a video file at a fixed stride.
    Stride of 30 at 30fps corresponds to 1 frame per second.
    """
    import cv2

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Could not open video: {video_path}")

    base_name = prefix or os.path.splitext(os.path.basename(video_path))[0]
    frame_idx = 0
    saved_frames: List[str] = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % stride == 0:
            filename = f"{base_name}_frame_{frame_idx:06d}.jpg"
            out_path = os.path.join(output_dir, filename)
            cv2.imwrite(out_path, frame)
            saved_frames.append(out_path)

        frame_idx += 1

    cap.release()
    return saved_frames


def validate_yolo_labels(
    images_dir: str,
    labels_dir: str,
    num_classes: int = 6
) -> Dict[str, Any]:
    """
    Validates YOLO Darknet annotations:
    1. Checks that corresponding .txt file exists for each .jpg image.
    2. Validates format: <class_id> <x_center> <y_center> <width> <height>.
    3. Asserts normalized values in [0.0, 1.0].
    4. Asserts 0 <= class_id < num_classes.
    """
    image_extensions = ("*.jpg", "*.jpeg", "*.png")
    image_paths: List[str] = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(images_dir, ext)))

    stats = {
        "total_images": len(image_paths),
        "valid_images": 0,
        "missing_labels": 0,
        "corrupted_labels": 0,
        "total_boxes": 0,
        "boxes_per_class": {i: 0 for i in range(num_classes)},
        "issues": []
    }

    for img_path in image_paths:
        base = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(labels_dir, f"{base}.txt")

        if not os.path.exists(lbl_path):
            stats["missing_labels"] += 1
            stats["issues"].append(f"Missing label for image: {os.path.basename(img_path)}")
            continue

        valid_file = True
        try:
            with open(lbl_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            for line_no, line in enumerate(lines, 1):
                parts = line.split()
                if len(parts) != 5:
                    valid_file = False
                    stats["issues"].append(
                        f"{base}.txt L{line_no}: Expected 5 fields, got {len(parts)}"
                    )
                    break

                cls_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])

                if cls_id < 0 or cls_id >= num_classes:
                    valid_file = False
                    stats["issues"].append(
                        f"{base}.txt L{line_no}: Invalid class {cls_id} (allowed 0-{num_classes-1})"
                    )
                    break

                for val, name in [(xc, "xc"), (yc, "yc"), (w, "w"), (h, "h")]:
                    if not (0.0 <= val <= 1.0):
                        valid_file = False
                        stats["issues"].append(
                            f"{base}.txt L{line_no}: {name}={val} out of bounds [0, 1]"
                        )
                        break

                if not valid_file:
                    break

                stats["total_boxes"] += 1
                stats["boxes_per_class"][cls_id] = stats["boxes_per_class"].get(cls_id, 0) + 1

        except Exception as e:
            valid_file = False
            stats["corrupted_labels"] += 1
            stats["issues"].append(f"Error reading {base}.txt: {str(e)}")

        if valid_file:
            stats["valid_images"] += 1

    return stats


def split_dataset_by_recording(
    recording_to_frames: Dict[str, List[str]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Dict[str, List[str]]:
    """
    Partitions whole video recordings into train, val, and test splits.
    Guarantees zero frame overlap from the same recording across splits!
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"

    recordings = list(recording_to_frames.keys())
    random.seed(seed)
    random.shuffle(recordings)

    n_total = len(recordings)
    n_train = max(1, int(round(n_total * train_ratio)))
    n_val = max(1, int(round(n_total * val_ratio))) if n_total >= 3 else 1

    train_recs = recordings[:n_train]
    val_recs = recordings[n_train:n_train + n_val]
    test_recs = recordings[n_train + n_val:]

    # Fallback if too few recordings
    if not test_recs and len(val_recs) > 1:
        test_recs = [val_recs.pop()]

    splits = {"train": [], "val": [], "test": []}
    for rec in train_recs:
        splits["train"].extend(recording_to_frames[rec])
    for rec in val_recs:
        splits["val"].extend(recording_to_frames[rec])
    for rec in test_recs:
        splits["test"].extend(recording_to_frames[rec])

    return splits


def create_data_yaml(
    output_path: str,
    dataset_root: str,
    train_rel: str = "images/train",
    val_rel: str = "images/val",
    test_rel: str = "images/test",
    class_names: Optional[Dict[int, str]] = None
) -> None:
    """Creates a YOLOv8 data.yaml file."""
    if class_names is None:
        class_names = {
            0: "person",
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            4: "bus",
            5: "truck"
        }

    config = {
        "path": dataset_root,
        "train": train_rel,
        "val": val_rel,
        "test": test_rel,
        "nc": len(class_names),
        "names": class_names
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
