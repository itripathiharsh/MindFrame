import os
import sys
import json
from datetime import datetime

from src.utils.video_info import get_video_info
from src.utils.metadata_writer import write_metadata
from src.extractors.ffmpeg_extractor import extract_frames_ffmpeg
from src.extractors.opencv_extractor import extract_frames_opencv


def run_extraction(
    video_path: str,
    fps: float,
    engine: str,
    output_dir: str,
    image_format: str = "jpg",
    save_metadata: bool = True,
):
    """
    Main orchestration function for MindFrame frame extraction.
    """

    # -------------------------
    # Prepare output directories
    # -------------------------
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # -------------------------
    # Read video information
    # -------------------------
    video_info = get_video_info(video_path)
    original_fps = video_info["fps"]
    total_frames = video_info["total_frames"]
    duration = video_info["duration"]

    print("\n[MindFrame] Video Information")
    print(f" - Source: {video_path}")
    print(f" - Duration: {duration:.2f} seconds")
    print(f" - Original FPS: {original_fps}")
    print(f" - Total Frames: {total_frames}")
    print(f" - Extraction FPS: {fps}")
    print(f" - Engine: {engine}\n")

    # -------------------------
    # Frame extraction
    # -------------------------
    if engine == "ffmpeg":
        extracted_frames = extract_frames_ffmpeg(
            video_path=video_path,
            output_dir=images_dir,
            fps=fps,
            image_format=image_format,
            original_fps=original_fps,
        )
    elif engine == "opencv":
        extracted_frames = extract_frames_opencv(
            video_path=video_path,
            output_dir=images_dir,
            fps=fps,
            image_format=image_format,
            original_fps=original_fps,
        )
    else:
        print(f"[ERROR] Unsupported engine: {engine}")
        sys.exit(1)

    if not extracted_frames:
        print("[ERROR] No frames were extracted.")
        sys.exit(1)

    print(f"[MindFrame] Extracted {len(extracted_frames)} frames")

    # -------------------------
    # Metadata generation
    # -------------------------
    if save_metadata:
        metadata_path = os.path.join(output_dir, "metadata.json")

        metadata = {
            "project": "MindFrame",
            "source_video": os.path.basename(video_path),
            "engine": engine,
            "requested_fps": fps,
            "original_video_fps": original_fps,
            "total_frames_extracted": len(extracted_frames),
            "extraction_time": datetime.utcnow().isoformat() + "Z",
            "frames": extracted_frames,
        }

        write_metadata(metadata, metadata_path)

        print(f"[MindFrame] Metadata saved to {metadata_path}")

    print("\n[MindFrame] Frame extraction completed successfully.\n")
