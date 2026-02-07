import os
import sys


SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv"}
SUPPORTED_ENGINES = {"ffmpeg", "opencv"}
SUPPORTED_IMAGE_FORMATS = {"jpg", "png"}


def validate_video_path(video_path: str) -> None:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    _, ext = os.path.splitext(video_path.lower())
    if ext not in SUPPORTED_VIDEO_FORMATS:
        raise ValueError(
            f"Unsupported video format: {ext}. "
            f"Supported formats: {SUPPORTED_VIDEO_FORMATS}"
        )


def validate_fps(fps: float) -> None:
    if fps <= 0:
        raise ValueError("FPS must be greater than 0")


def validate_engine(engine: str) -> None:
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unsupported engine: {engine}. "
            f"Supported engines: {SUPPORTED_ENGINES}"
        )


def validate_image_format(image_format: str) -> None:
    if image_format not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported image format: {image_format}. "
            f"Supported formats: {SUPPORTED_IMAGE_FORMATS}"
        )


def validate_output_dir(output_dir: str) -> None:
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        raise PermissionError(
            f"Cannot create or write to output directory '{output_dir}': {e}"
        )
