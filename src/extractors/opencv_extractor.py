import os
import cv2
from typing import List, Dict


def extract_frames_opencv(
    video_path: str,
    output_dir: str,
    fps: float,
    image_format: str,
    original_fps: float,
) -> List[Dict]:
    """
    Extract frames using OpenCV.

    Returns:
        List of frame metadata dictionaries
    """

    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")

    # Calculate frame interval
    frame_interval = max(int(round(original_fps / fps)), 1)

    extracted_frames = []
    frame_index = 0
    saved_frame_id = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index % frame_interval == 0:
            timestamp_sec = round(frame_index / original_fps, 3)

            filename = f"frame_{saved_frame_id:06d}.{image_format}"
            output_path = os.path.join(output_dir, filename)

            success = cv2.imwrite(output_path, frame)
            if not success:
                cap.release()
                raise IOError(f"Failed to write frame: {output_path}")

            extracted_frames.append({
                "frame_id": saved_frame_id,
                "filename": filename,
                "timestamp_sec": timestamp_sec,
            })

            saved_frame_id += 1

        frame_index += 1

    cap.release()

    return extracted_frames
