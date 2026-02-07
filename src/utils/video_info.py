import cv2
import os


def get_video_info(video_path: str) -> dict:
    """
    Extract basic information from a video file.

    Returns:
        dict with keys:
            fps
            total_frames
            duration
    """

    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps <= 0:
        cap.release()
        raise ValueError("Invalid FPS detected in video metadata")

    duration = total_frames / fps

    cap.release()

    return {
        "fps": round(fps, 3),
        "total_frames": total_frames,
        "duration": round(duration, 3),
    }
