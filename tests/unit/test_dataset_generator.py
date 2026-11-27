"""
Unit tests for the automated Colab surveillance dataset generator and negative background sampler.
"""

import os
import shutil
import tempfile
import pytest
import yaml

from ai.src.dataset_utils import prepare_colab_surveillance_dataset, validate_yolo_labels


def test_prepare_colab_surveillance_dataset():
    sample_video = "ai/dataset/sample_gate.mp4"
    if not os.path.exists(sample_video):
        pytest.skip("ai/dataset/sample_gate.mp4 not found for testing.")

    with tempfile.TemporaryDirectory() as temp_dir:
        yaml_path = prepare_colab_surveillance_dataset(
            video_path=sample_video,
            output_root=temp_dir,
            stride=30,
            max_frames=10,
            include_background_negatives=True
        )

        assert os.path.exists(yaml_path), f"data.yaml not created at {yaml_path}"

        # Verify YAML structure
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        assert "path" in config
        assert "train" in config
        assert "val" in config
        assert "test" in config
        assert config["nc"] == 6
        assert config["names"][4] == "bus"

        # Verify image and label directories
        train_img_dir = os.path.join(temp_dir, "images", "train")
        train_lbl_dir = os.path.join(temp_dir, "labels", "train")
        assert os.path.exists(train_img_dir)
        assert os.path.exists(train_lbl_dir)

        # Verify negative background files are created with empty labels (0-byte)
        bg_negative_lbl = os.path.join(train_lbl_dir, "bg_negative_scene_train_0.txt")
        assert os.path.exists(bg_negative_lbl), "Negative background label file not found"
        assert os.path.getsize(bg_negative_lbl) == 0, "Negative background label file must be empty (0 bytes)"

        # Validate label format
        stats = validate_yolo_labels(train_img_dir, train_lbl_dir, num_classes=6)
        assert stats["corrupted_labels"] == 0, f"Corrupted labels found: {stats['issues']}"
        assert stats["valid_images"] > 0
