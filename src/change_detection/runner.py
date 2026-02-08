import os
import json
import shutil
import cv2
from tqdm import tqdm

from .detector import ChangeDetector


class ChangeDetectionRunner:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        method: str = "ssim",
        threshold: float = 10.0
    ):
        self.input_images = os.path.join(input_dir, "images")
        self.input_metadata = os.path.join(input_dir, "metadata.json")

        self.output_images = os.path.join(output_dir, "images")
        self.output_metadata = os.path.join(output_dir, "metadata.json")
        self.output_dropped = os.path.join(output_dir, "dropped_frames.json")

        self.threshold = threshold
        self.detector = ChangeDetector(method=method)

        os.makedirs(self.output_images, exist_ok=True)

    def _load_metadata(self):
        with open(self.input_metadata, "r") as f:
            return json.load(f)

    def _load_frame(self, filename: str):
        path = os.path.join(self.input_images, filename)
        return cv2.imread(path)

    def run(self):
        metadata = self._load_metadata()
        frames_meta = metadata.get("frames", [])

        if len(frames_meta) < 2:
            raise RuntimeError("Not enough frames for change detection")

        kept_frames = []
        dropped_frames = []

        prev_meta = frames_meta[0]
        prev_frame = self._load_frame(prev_meta["filename"])

        # Always keep the first frame
        shutil.copy(
            os.path.join(self.input_images, prev_meta["filename"]),
            os.path.join(self.output_images, prev_meta["filename"])
        )

        prev_meta["change_score"] = 0.0
        prev_meta["status"] = "kept"
        kept_frames.append(prev_meta)

        for current_meta in tqdm(frames_meta[1:], desc="Running Change Detection"):
            curr_frame = self._load_frame(current_meta["filename"])

            change_score = self.detector.compute_change(prev_frame, curr_frame)
            current_meta["change_score"] = round(change_score, 4)

            if change_score >= self.threshold:
                current_meta["status"] = "kept"

                shutil.copy(
                    os.path.join(self.input_images, current_meta["filename"]),
                    os.path.join(self.output_images, current_meta["filename"])
                )

                kept_frames.append(current_meta)
                prev_frame = curr_frame
                prev_meta = current_meta
            else:
                current_meta["status"] = "dropped"
                dropped_frames.append(current_meta)

        # Write metadata
        final_metadata = {
            "source": "extraction",
            "change_method": self.detector.method,
            "threshold": self.threshold,
            "total_input_frames": len(frames_meta),
            "total_kept_frames": len(kept_frames),
            "frames": kept_frames
        }

        with open(self.output_metadata, "w") as f:
            json.dump(final_metadata, f, indent=2)

        with open(self.output_dropped, "w") as f:
            json.dump(dropped_frames, f, indent=2)

        print(f"Change detection completed")
        print(f"Kept frames: {len(kept_frames)}")
        print(f"Dropped frames: {len(dropped_frames)}")
