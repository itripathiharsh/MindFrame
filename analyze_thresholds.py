import os
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.detectors.metrics import calculate_mse, calculate_ssim, convert_to_percentage

def analyze_video_noise(input_dir):
    """
    Scans all frames to calculate the 'Noise Floor' of the video.
    Helps the user pick perfect thresholds.
    """
    images_dir = os.path.join(input_dir, "images")
    metadata_path = os.path.join(input_dir, "metadata.json")
    
    if not os.path.exists(metadata_path):
        print("❌ Metadata not found. Run Stage 1 extraction first.")
        return

    with open(metadata_path, 'r') as f:
        meta = json.load(f)
        
    frames = sorted(meta['frames'], key=lambda x: x['frame_id'])
    
    print(f"📊 Analyzing {len(frames)} frames to find optimal thresholds...")
    
    mse_scores = []
    ssim_scores = []
    frame_indices = []
    
    # Read first frame
    prev_img = cv2.imread(os.path.join(images_dir, frames[0]['filename']))
    
    # Loop through all frames (Frame N vs Frame N+1)
    for i in tqdm(range(1, len(frames))):
        curr_meta = frames[i]
        curr_img = cv2.imread(os.path.join(images_dir, curr_meta['filename']))
        
        if curr_img is None:
            continue
            
        # Calculate raw differences
        raw_mse = calculate_mse(prev_img, curr_img)
        raw_ssim = calculate_ssim(prev_img, curr_img)
        
        # Convert to percentages
        mse_p = convert_to_percentage(raw_mse, "mse")
        ssim_p = convert_to_percentage(raw_ssim, "ssim")
        
        mse_scores.append(mse_p)
        ssim_scores.append(ssim_p)
        frame_indices.append(i)
        
        # Update previous frame (Strict N vs N+1 comparison for analysis)
        prev_img = curr_img

    # --- Statistical Analysis ---
    mse_scores = np.array(mse_scores)
    ssim_scores = np.array(ssim_scores)
    
    print("\n📈 Statistical Analysis (The 'Noise Floor')")
    print("-" * 40)
    
    # Calculate percentiles
    mse_90 = np.percentile(mse_scores, 90)
    ssim_90 = np.percentile(ssim_scores, 90)
    
    print(f"MSE Average:    {np.mean(mse_scores):.4f}%")
    print(f"MSE Peak:       {np.max(mse_scores):.4f}%")
    print(f"MSE 90% floor:  {mse_90:.4f}%  (90% of frames are below this)")
    
    print("-" * 40)
    print(f"SSIM Average:   {np.mean(ssim_scores):.4f}%")
    print(f"SSIM Peak:      {np.max(ssim_scores):.4f}%")
    print(f"SSIM 90% floor: {ssim_90:.4f}% (90% of frames are below this)")
    print("-" * 40)
    
    # Recommendations
    rec_mse = mse_90 * 1.5  # Safety margin above noise
    rec_ssim = ssim_90 * 1.5
    
    print("\n💡 RECOMMENDED THRESHOLDS:")
    print(f"   MSE Threshold:  {rec_mse:.2f}")
    print(f"   SSIM Threshold: {rec_ssim:.2f}")
    print("(These values filter out 90% of the noise + a safety margin)")

    # --- Plotting ---
    plt.figure(figsize=(12, 6))
    
    # Plot MSE
    plt.subplot(2, 1, 1)
    plt.plot(frame_indices, mse_scores, color='blue', label='MSE (Pixel Diff)')
    plt.axhline(y=rec_mse, color='r', linestyle='--', label=f'Recommended Thresh ({rec_mse:.2f})')
    plt.title("MSE Difference per Frame (Pixel Noise)")
    plt.ylabel("Difference %")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot SSIM
    plt.subplot(2, 1, 2)
    plt.plot(frame_indices, ssim_scores, color='green', label='SSIM (Structural Diff)')
    plt.axhline(y=rec_ssim, color='r', linestyle='--', label=f'Recommended Thresh ({rec_ssim:.2f})')
    plt.title("SSIM Difference per Frame (Structural Change)")
    plt.xlabel("Frame ID")
    plt.ylabel("Difference %")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_plot = "threshold_analysis.png"
    plt.savefig(output_plot)
    print(f"\n✅ Graph saved to: {output_plot}")
    print("Open this image to visually see where the 'spikes' (action) are.")

if __name__ == "__main__":
    folder = input("Enter Stage 1 output directory [output]: ").strip() or "output"
    analyze_video_noise(folder)