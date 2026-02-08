import os
import json
import time

from .runner import ChangeDetectionRunner


class ThresholdBenchmark:
    def __init__(
        self,
        input_dir: str,
        output_base_dir: str,
        method: str = "ssim",
        thresholds: list = None
    ):
        self.input_dir = input_dir
        self.output_base_dir = output_base_dir
        self.method = method
        self.thresholds = thresholds or [5, 10, 15, 20]

        os.makedirs(self.output_base_dir, exist_ok=True)

    def run(self):
        results = []

        for threshold in self.thresholds:
            print(f"\nRunning threshold benchmark: {threshold}%")

            output_dir = os.path.join(
                self.output_base_dir,
                f"threshold_{threshold}"
            )

            start_time = time.time()

            runner = ChangeDetectionRunner(
                input_dir=self.input_dir,
                output_dir=output_dir,
                method=self.method,
                threshold=threshold
            )

            runner.run()

            elapsed_time = round(time.time() - start_time, 3)

            metadata_path = os.path.join(output_dir, "metadata.json")
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            results.append({
                "threshold": threshold,
                "method": self.method,
                "input_frames": metadata["total_input_frames"],
                "kept_frames": metadata["total_kept_frames"],
                "dropped_frames": metadata["total_input_frames"] - metadata["total_kept_frames"],
                "processing_time_sec": elapsed_time
            })

        benchmark_path = os.path.join(self.output_base_dir, "benchmark_results.json")
        with open(benchmark_path, "w") as f:
            json.dump(results, f, indent=2)

        print("\nThreshold benchmarking completed")
        print(f"Results saved to: {benchmark_path}")
