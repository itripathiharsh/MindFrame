import cv2
import sys

# Try importing libraries to avoid crashes if one is missing
try:
    from mtcnn import MTCNN
except ImportError:
    MTCNN = None

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except ImportError:
    mp = None

class FaceDetector:
    """
    Hybrid Face Detector.
    Supports: 'mtcnn' (Default) OR 'mediapipe'
    """
    def __init__(self, method="mtcnn", model_path=None, min_conf=0.5):
        self.method = method.lower()
        self.min_conf = min_conf
        
        # --- MTCNN INIT ---
        if self.method == "mtcnn":
            if MTCNN is None:
                print("[ERROR] MTCNN not installed. Run: pip install mtcnn tensorflow")
                sys.exit(1)
            self.engine = MTCNN()
            print("[INFO] Initialized MTCNN Detector")
            
        # --- MEDIAPIPE INIT ---
        elif self.method == "mediapipe":
            if mp is None:
                print("[ERROR] MediaPipe not installed.")
                sys.exit(1)
            if not model_path:
                print("[ERROR] Model path required for MediaPipe.")
                sys.exit(1)
                
            base = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceDetectorOptions(
                base_options=base,
                min_detection_confidence=min_conf,
            )
            self.engine = vision.FaceDetector.create_from_options(options)
            print("[INFO] Initialized MediaPipe Face Detector")
        
        else:
            print(f"[ERROR] Unknown detector method: {self.method}")
            sys.exit(1)

    def detect(self, crop):
        if crop is None or crop.size == 0:
            return []
        
        faces = []
        
        # --- LOGIC FOR MTCNN ---
        if self.method == "mtcnn":
            rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            results = self.engine.detect_faces(rgb)
            
            for res in results:
                if res['confidence'] > self.min_conf:
                    faces.append({
                        "box": res['box'], # [x, y, w, h]
                        "confidence": res['confidence']
                    })

        # --- LOGIC FOR MEDIAPIPE ---
        elif self.method == "mediapipe":
            rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            res = self.engine.detect(mp_image)
            
            if res.detections:
                for d in res.detections:
                    bbox = d.bounding_box
                    faces.append({
                        # Convert MediaPipe bbox object to list [x, y, w, h]
                        "box": [bbox.origin_x, bbox.origin_y, bbox.width, bbox.height],
                        "confidence": d.categories[0].score
                    })
                    
        return faces