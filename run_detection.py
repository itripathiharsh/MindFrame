import os
import argparse
from src.detectors.change_detector import ChangeDetector

def prompt_input(prompt_text, default=None):
    value = input(prompt_text).strip()
    return value if value else default

def main():
    print("\n🧠 MindFrame – Stage 2: Dual-Pass Difference Detection\n")

    # 1. Input/Output
    default_input = "output"
    input_dir = prompt_input(f"Enter input directory (Stage 1 output) [{default_input}]: ", default_input)
    
    if not os.path.exists(input_dir):
        print(f"❌ Error: Directory '{input_dir}' not found.")
        return

    default_output = f"{input_dir}_analyzed"
    output_dir = prompt_input(f"Enter output directory [{default_output}]: ", default_output)

    print("\n--- Configuration (Tuned for Real-World Video) ---")
    
    # 2. MSE Threshold (Pass 1)
    # PROBLEM SOLVED: 10% MSE is too high. 
    # Real-world duplicate detection uses 0.1% to 1.0%.
    # We default to 0.5% which removes exact duplicates and sensor noise.
    mse_input = prompt_input("Enter MSE Threshold % (removes identical frames) [0.5]: ", "0.5")
    mse_thresh = float(mse_input)

    # 3. SSIM Threshold (Pass 2)
    # PROBLEM SOLVED: 10% SSIM can be too sensitive (keeps too much).
    # We raised default to 15% to ensure we only keep meaningful structural changes.
    ssim_input = prompt_input("Enter SSIM Threshold % (removes similar content) [15.0]: ", "15.0")
    ssim_thresh = float(ssim_input)

  
    
    # 4. Run (Updated Method Name)
    detector = ChangeDetector(input_dir, output_dir)
    # Changed from process_two_stage to process_single_pass
    detector.process_single_pass(mse_threshold=mse_thresh, ssim_threshold=ssim_thresh)

if __name__ == "__main__":
    main()