import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class PoseEstimator:
    """
    Returns landmarks with (x, y) coordinates for geometry logic.
    """
    def __init__(self, model_path: str, min_confidence: float = 0.3):
        base = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base,
            num_poses=1,
            min_pose_detection_confidence=min_confidence,
        )
        self.engine = vision.PoseLandmarker.create_from_options(options)

    def estimate(self, crop):
        if crop is None or crop.size == 0:
            return None

        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        res = self.engine.detect(mp_image)

        if not res.pose_landmarks:
            return None

        lm = res.pose_landmarks[0]
        
        # Return strict coordinates needed for orientation logic
        # Landmark 0: Nose, 7: Left Ear, 8: Right Ear
        return {
            "nose": {"x": lm[0].x, "vis": lm[0].visibility},
            "left_ear": {"x": lm[7].x, "vis": lm[7].visibility},
            "right_ear": {"x": lm[8].x, "vis": lm[8].visibility},
            "left_shoulder": {"vis": lm[11].visibility},
            "right_shoulder": {"vis": lm[12].visibility},
        }