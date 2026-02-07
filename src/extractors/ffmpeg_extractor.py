import os
import subprocess
from typing import List, Dict


def extract_frames_ffmpeg(
    video_path: str,
    output_dir: str,
    fps: float,
    image_format: str,
    original_fps: float,
) -> List[Dict]:
    """
    Extract frames using FFmpeg.

    Returns:
        List of frame metadata dictionaries
    """

    os.makedirs(output_dir, exist_ok=True)

    frame_pattern = os.path.join(
        output_dir, f"frame_%06d.{image_format}"
    )

    # FFmpeg command
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"fps={fps}",
        frame_pattern,
    ]

    try:
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError("FFmpeg is not installed or not in PATH")

    if process.returncode != 0:
        raise RuntimeError(
            f"FFmpeg extraction failed:\n{process.stderr}"
        )

    # Collect extracted frames
    frame_files = sorted(
        f for f in os.listdir(output_dir)
        if f.endswith(f".{image_format}")
    )

    extracted_frames = []

    for idx, filename in enumerate(frame_files, start=1):
        timestamp_sec = round((idx - 1) / fps, 3)

        extracted_frames.append({
            "frame_id": idx,
            "filename": filename,
            "timestamp_sec": timestamp_sec,
        })

    return extracted_frames
