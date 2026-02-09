import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceDetector:
    """
    Tasks API BlazeFace version.
    Returns Face Boxes along with confidence.
    """
    def __init__(self, model_path: str, min_conf: float = 0.5):
        base = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceDetectorOptions(
            base_options=base,
            min_detection_confidence=min_conf,
        )
        self.engine = vision.FaceDetector.create_from_options(options)

    def detect(self, crop):
        if crop is None or crop.size == 0:
            return []

        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        res = self.engine.detect(mp_image)
        faces = []

        if res.detections:
            for d in res.detections:
                bbox = d.bounding_box
                faces.append({
                    "confidence": d.categories[0].score,
                    # Save local coordinates (relative to the person crop)
                    "box": [bbox.origin_x, bbox.origin_y, bbox.width, bbox.height]
                })
        return faces