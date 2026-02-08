import os
import cv2
import json
import time
from tqdm import tqdm
from .metrics import calculate_mse, calculate_ssim, convert_to_percentage

class ChangeDetector:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.images_dir = os.path.join(input_dir, "images")
        self.output_dir = output_dir
        self.viz_dir = os.path.join(output_dir, "visualization")
        self.metadata_path = os.path.join(input_dir, "metadata.json")
        
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"No metadata found in {input_dir}")
            
        with open(self.metadata_path, 'r') as f:
            self.meta = json.load(f)

    def process_single_pass(self, mse_threshold=0.5, ssim_threshold=15.0):
        """
        Optimized Single-Pass Pipeline.
        Checks MSE first (fast). If passed, checks SSIM (slow).
        """
        os.makedirs(self.viz_dir, exist_ok=True)
        
        frames = sorted(self.meta['frames'], key=lambda x: x['frame_id'])
        if not frames:
            print("No frames to process.")
            return

        print(f"\n🚀 Running Single-Pass Detection")
        print(f"   [Gate 1] MSE  > {mse_threshold}% (Fast Reject)")
        print(f"   [Gate 2] SSIM > {ssim_threshold}% (Structural Check)")
        
        start_time = time.time()
        
        # Stats counters
        stats = {
            "total": len(frames),
            "kept": 0,
            "dropped_mse": 0,
            "dropped_ssim": 0
        }
        
        results = []

        # --- Initialize with First Frame ---
        first_meta = frames[0]
        first_img_path = os.path.join(self.images_dir, first_meta['filename'])
        prev_kept_img = cv2.imread(first_img_path)
        
        if prev_kept_img is None:
            print(f"❌ Error reading first frame: {first_meta['filename']}")
            return

        # Always keep 1st frame
        stats["kept"] += 1
        results.append({
            "frame_id": first_meta['frame_id'],
            "filename": first_meta['filename'],
            "status": "kept",
            "reason": "First Frame",
            "mse_diff": 100.0,
            "ssim_diff": 100.0
        })
        
        self._save_viz(prev_kept_img, first_meta['filename'], "kept", 100, 100)

        # --- Main Loop (Start from 2nd frame) ---
        pbar = tqdm(frames[1:], desc="Processing", unit="frame")
        
        for frame_meta in pbar:
            img_path = os.path.join(self.images_dir, frame_meta['filename'])
            curr_img = cv2.imread(img_path)
            
            if curr_img is None:
                continue

            # 1. MSE CHECK (Fast Gate)
            raw_mse = calculate_mse(prev_kept_img, curr_img)
            mse_diff = convert_to_percentage(raw_mse, "mse")
            
            if mse_diff <= mse_threshold:
                # Dropped by MSE
                stats["dropped_mse"] += 1
                results.append({
                    "frame_id": frame_meta['frame_id'],
                    "filename": frame_meta['filename'],
                    "status": "dropped",
                    "reason": "MSE Low",
                    "mse_diff": round(mse_diff, 4),
                    "ssim_diff": 0.0 # Skipped
                })
                self._save_viz(curr_img, frame_meta['filename'], "dropped", mse_diff, 0.0, "MSE Low")
                continue # Skip to next frame (prev_kept_img DOES NOT change)

            # 2. SSIM CHECK (Slow Gate - only runs if MSE passed)
            raw_ssim = calculate_ssim(prev_kept_img, curr_img)
            ssim_diff = convert_to_percentage(raw_ssim, "ssim")

            if ssim_diff <= ssim_threshold:
                # Dropped by SSIM
                stats["dropped_ssim"] += 1
                results.append({
                    "frame_id": frame_meta['frame_id'],
                    "filename": frame_meta['filename'],
                    "status": "dropped",
                    "reason": "SSIM Low",
                    "mse_diff": round(mse_diff, 4),
                    "ssim_diff": round(ssim_diff, 4)
                })
                self._save_viz(curr_img, frame_meta['filename'], "dropped", mse_diff, ssim_diff, "SSIM Low")
                continue # Skip (prev_kept_img DOES NOT change)

            # 3. KEEP FRAME (Passed both)
            stats["kept"] += 1
            results.append({
                "frame_id": frame_meta['frame_id'],
                "filename": frame_meta['filename'],
                "status": "kept",
                "reason": "Significant Change",
                "mse_diff": round(mse_diff, 4),
                "ssim_diff": round(ssim_diff, 4)
            })
            self._save_viz(curr_img, frame_meta['filename'], "kept", mse_diff, ssim_diff)
            
            # Update Reference Frame
            prev_kept_img = curr_img

        # --- Final Report ---
        end_time = time.time()
        duration = end_time - start_time
        dropped_total = stats["dropped_mse"] + stats["dropped_ssim"]
        reduction = (dropped_total / stats["total"]) * 100.0
        
        print("\n📊 Final Results")
        print(f" - Processed: {stats['total']}")
        print(f" - Kept:      {stats['kept']}")
        print(f" - Dropped:   {dropped_total} (MSE: {stats['dropped_mse']}, SSIM: {stats['dropped_ssim']})")
        print(f" - Reduction: {reduction:.1f}%")
        print(f" - Time:      {duration:.2f}s ({stats['total']/duration:.1f} fps)")

        self._write_report(mse_threshold, ssim_threshold, stats, results, duration, reduction)

    def _save_viz(self, img, filename, status, mse, ssim, reason=""):
        """Helper to draw and save visualization images"""
        viz_img = img.copy()
        color = (0, 255, 0) if status == "kept" else (0, 0, 255)
        
        cv2.rectangle(viz_img, (0, 0), (viz_img.shape[1]-1, viz_img.shape[0]-1), color, 10)
        
        label = f"{status.upper()}"
        if reason: label += f" ({reason})"
        
        info = f"MSE: {mse:.2f}% | SSIM: {ssim:.2f}%"
        
        cv2.putText(viz_img, label, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(viz_img, info, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imwrite(os.path.join(self.viz_dir, filename), viz_img)

    def _write_report(self, mse_th, ssim_th, stats, frames, duration, reduction):
        report = {
            "config": {"mse_threshold": mse_th, "ssim_threshold": ssim_th},
            "stats": {
                "total": stats['total'],
                "kept": stats['kept'],
                "dropped_total": stats['dropped_mse'] + stats['dropped_ssim'],
                "dropped_mse": stats['dropped_mse'],
                "dropped_ssim": stats['dropped_ssim'],
                "reduction_percent": round(reduction, 2),
                "duration_sec": round(duration, 2)
            },
            "frames": frames
        }
        with open(os.path.join(self.output_dir, "detection_report.json"), "w") as f:
            json.dump(report, f, indent=4)