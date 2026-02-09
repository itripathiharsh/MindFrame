class FrameAnalyzer:
    def __init__(self, person_detector, face_detector, pose_estimator, scorer):
        self.person_detector = person_detector
        self.face_detector = face_detector
        self.pose_estimator = pose_estimator
        self.scorer = scorer

    def analyze(self, frame):
        persons = []
        boxes = self.person_detector.detect(frame)

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            crop = frame[y1:y2, x1:x2]

            if crop.size == 0: continue

            faces = self.face_detector.detect(crop)
            
            # Global Face Coordinates
            global_faces = []
            for f in faces:
                fx, fy, fw, fh = f["box"]
                global_faces.append([x1 + fx, y1 + fy, fw, fh])

            pose = self.pose_estimator.estimate(crop)
            
            # Get Score AND Orientation
            final_score, orientation = self.scorer.score(faces, pose)

            persons.append({
                "bbox": box,
                "faces": global_faces,
                "score": final_score,
                "orientation": orientation  # New Field
            })

        return persons