import json
import os
from typing import Dict, Any


def write_metadata(metadata: Dict[str, Any], output_path: str) -> None:
    """
    Writes metadata dictionary to a JSON file.

    Args:
        metadata (dict): Metadata content
        output_path (str): Path to metadata.json
    """

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")

    # Basic sanity checks
    required_keys = [
        "project",
        "source_video",
        "engine",
        "requested_fps",
        "original_video_fps",
        "total_frames_extracted",
        "frames",
    ]

    missing_keys = [key for key in required_keys if key not in metadata]
    if missing_keys:
        raise KeyError(f"Missing required metadata keys: {missing_keys}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Failed to write metadata file: {e}")
