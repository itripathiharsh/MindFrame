import os
import sys
import json
import pandas as pd

# ---------------------------------------------------------
# PATH SETUP (Crucial for running inside tests/ folder)
# ---------------------------------------------------------
# 1. Get the folder where this script lives (tests/)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the project root (one level up)
project_root = os.path.dirname(current_script_dir)

# 3. Add project root to Python path so we can import 'src'
if project_root not in sys.path:
    sys.path.append(project_root)

# Now we can safely import from src
from src.detectors.change_detector import ChangeDetector

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# We look for 'output' in the PROJECT ROOT, not inside tests/
INPUT_DIR = os.path.join(project_root, "extracted_frames") 

# We will save benchmarks in the PROJECT ROOT
BASE_OUTPUT_DIR = os.path.join(project_root, "benchmarks")

# Define the Test Cases (MSE %, SSIM %)
TEST_CASES = [
    {"name": "Sensitive (Keep Most)",   "mse": 0.1,  "ssim": 5.0},
    {"name": "Balanced (Recommended)",  "mse": 0.5,  "ssim": 15.0},
    {"name": "Strict (Drops Minor)",    "mse": 0.5,  "ssim": 25.0},
    {"name": "Very Strict (Highlights)", "mse": 1.0, "ssim": 35.0},
]

def run_benchmark():
    # Verify input exists
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Input directory not found at: {INPUT_DIR}")
        print("   Did you run Stage 1 (run.py) yet?")
        return

    results_summary = []

    print(f"\n🚀 Starting Benchmark (Script: nikhil_test.py)")
    print(f"   Input:  {INPUT_DIR}")
    print(f"   Output: {BASE_OUTPUT_DIR}")
    print(f"{'='*60}")

    for case in TEST_CASES:
        name = case["name"]
        mse = case["mse"]
        ssim = case["ssim"]
        
        # Create a unique output folder for this run
        run_output_dir = os.path.join(BASE_OUTPUT_DIR, f"mse{mse}_ssim{ssim}")
        
        print(f"\n🔹 Testing: {name}")
        print(f"   Config: MSE > {mse}% | SSIM > {ssim}%")
        
        try:
            # Initialize and Run Detector
            detector = ChangeDetector(INPUT_DIR, run_output_dir)
            detector.process_single_pass(mse_threshold=mse, ssim_threshold=ssim)
            
            # Read stats
            report_path = os.path.join(run_output_dir, "detection_report.json")
            with open(report_path, 'r') as f:
                data = json.load(f)
                stats = data["stats"]
                
                results_summary.append({
                    "Config Name": name,
                    "MSE Thresh": mse,
                    "SSIM Thresh": ssim,
                    "Total Frames": stats["total"],
                    "Kept": stats["kept"],
                    "Dropped": stats["dropped_total"],
                    "Reduction %": f"{stats['reduction_percent']}%",
                    "Time (s)": stats["duration_sec"]
                })
                
        except Exception as e:
            print(f"❌ Failed: {e}")

    # ---------------------------------------------------------
    # PRINT RESULTS
    # ---------------------------------------------------------
    print(f"\n\n🏆 BENCHMARK RESULTS")
    print(f"{'='*80}")
    
    df = pd.DataFrame(results_summary)
    
    # Reorder columns
    cols = ["Config Name", "MSE Thresh", "SSIM Thresh", "Kept", "Dropped", "Reduction %", "Time (s)"]
    print(df[cols].to_markdown(index=False))
    
    # Save to CSV in the project root
    csv_path = os.path.join(project_root, "benchmark_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n✅ Results saved to {csv_path}")

if __name__ == "__main__":
    try:
        import pandas
    except ImportError:
        print("Please install pandas: pip install pandas tabulate")
    else:
        run_benchmark()