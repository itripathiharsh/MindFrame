class PersonDetector:
    def __init__(self, model):
        self.model = model

    def detect(self, frame):
        """
        Returns list of bounding boxes for PERSONS only.
        [[x1,y1,x2,y2], ...]
        """
        # Change 1: classes=0 (Sirf Person detect karega)
        # Change 2: verbose=False (Faltu logs "suitcases/tv" band karega)
        results = self.model(frame, classes=0, verbose=False)

        boxes = []
        for r in results:
            for b in r.boxes:
                # Ab humein check karne ki zaroorat nahi ki cls == 0 hai, 
                # kyunki YOLO ab sirf person hi dhundega.
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                boxes.append([x1, y1, x2, y2])

        return boxes