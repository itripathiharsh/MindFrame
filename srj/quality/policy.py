class FramePolicy:
    def __init__(self, min_score, min_ratio):
        self.min_score = min_score
        self.min_ratio = min_ratio

    def decide(self, persons):
        if not persons:
            return False, 0

        good = [p for p in persons if p["score"] >= self.min_score]
        ratio = len(good) / len(persons)

        return ratio >= self.min_ratio, ratio
