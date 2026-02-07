import os
import json
import shutil
import pytest

from src.main import run_extraction



# -------------------------
# Test Configuration
# -------------------------
TEST_VIDEO = "samples/sample_video.mp4"
OUTPUT_DIR = "test_output"


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """
    Setup before tests and cleanup after tests.
    """
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    yield

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)


# -------------------------
# FFmpeg Extraction Test
# -------------------------
def test_ffmpeg_frame_extraction():
    run_extraction(
        video_path=TEST_VIDEO,
        fps=1,
        engine="ffmpeg",
        output_dir=OUTPUT_DIR,
        image_format="jpg",
        save_metadata=True,
    )

    images_dir = os.path.join(OUTPUT_DIR, "images")
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.json")

    assert os.path.isdir(images_dir), "Images directory not created"
    assert os.path.isfile(metadata_path), "metadata.json not created"

    images = os.listdir(images_dir)
    assert len(images) > 0, "No frames extracted using FFmpeg"

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["engine"] == "ffmpeg"
    assert metadata["requested_fps"] == 1
    assert metadata["total_frames_extracted"] == len(images)
    assert len(metadata["frames"]) == len(images)


# -------------------------
# OpenCV Extraction Test
# -------------------------
def test_opencv_frame_extraction():
    # Clear output directory before OpenCV test
    shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    run_extraction(
        video_path=TEST_VIDEO,
        fps=1,
        engine="opencv",
        output_dir=OUTPUT_DIR,
        image_format="jpg",
        save_metadata=True,
    )

    images_dir = os.path.join(OUTPUT_DIR, "images")
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.json")

    assert os.path.isdir(images_dir), "Images directory not created"
    assert os.path.isfile(metadata_path), "metadata.json not created"

    images = os.listdir(images_dir)
    assert len(images) > 0, "No frames extracted using OpenCV"

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    assert metadata["engine"] == "opencv"
    assert metadata["requested_fps"] == 1
    assert metadata["total_frames_extracted"] == len(images)
    assert len(metadata["frames"]) == len(images)


# -------------------------
# Metadata Integrity Test
# -------------------------
def test_metadata_integrity():
    metadata_path = os.path.join(OUTPUT_DIR, "metadata.json")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    required_keys = [
        "project",
        "source_video",
        "engine",
        "requested_fps",
        "original_video_fps",
        "total_frames_extracted",
        "frames",
    ]

    for key in required_keys:
        assert key in metadata, f"Missing metadata key: {key}"

    for frame in metadata["frames"]:
        assert "frame_id" in frame
        assert "filename" in frame
        assert "timestamp_sec" in frame
