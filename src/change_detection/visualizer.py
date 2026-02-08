import json
import matplotlib.pyplot as plt


class ChangeDetectionVisualizer:
    def __init__(self, metadata_path: str):
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()

    def _load_metadata(self):
        with open(self.metadata_path, "r") as f:
            return json.load(f)

    def plot_change_scores(self):
        frames = self.metadata["frames"]
        threshold = self.metadata["threshold"]

        frame_ids = [f["frame_id"] for f in frames]
        change_scores = [f["change_score"] for f in frames]

        plt.figure()
        plt.plot(frame_ids, change_scores, marker='o')
        plt.axhline(
            y=threshold,
            linestyle='--',
            label=f"Threshold = {threshold}%"
        )

        plt.xlabel("Frame ID")
        plt.ylabel("Change Score (%)")
        plt.title("Frame Change Detection Analysis")
        plt.legend()
        plt.grid(True)
        plt.show()
