import cv2
import time
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO

# --- IMPORTS FROM YOUR PROJECT ---
try:
    from detectors.face_detector import FaceDetector
except ImportError:
    print("[ERROR] Could not import FaceDetector. Make sure this script is in the 'srj' folder.")
    sys.exit(1)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "..", "output/images") 
OUTPUT_GRAPH = os.path.join(BASE_DIR, "..", "filtered_data", "comparison_result.png")
FACE_MODEL_PATH = os.path.join(BASE_DIR, "blaze_face_short_range.tflite")

def main():
    # 1. Setup Input
    if not os.path.exists(INPUT_FOLDER):
        print(f"[ERROR] Input folder not found: {INPUT_FOLDER}")
        return

    images = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.jpg', '.png'))]
    if not images:
        print("[ERROR] No images found to test.")
        return

    # Optional: Limit images for faster testing
    # images = images[:30] 
    print(f"[INFO] Benchmarking on {len(images)} images...")

    # 2. Initialize Detectors
    print("[INFO] Loading MTCNN...")
    mtcnn_detector = FaceDetector(method="mtcnn")

    print("[INFO] Loading MediaPipe (Low Confidence)...")
    # Confidence gira di hai taaki kuch toh detect ho
    mp_detector = FaceDetector(method="mediapipe", model_path=FACE_MODEL_PATH, min_conf=0.1)

    # --- TEST 1: MTCNN ---
    print("\n--- Running MTCNN ---")
    start_time = time.time()
    mtcnn_faces_count = 0
    
    for img_name in images:
        frame = cv2.imread(os.path.join(INPUT_FOLDER, img_name))
        if frame is None: continue
        faces = mtcnn_detector.detect(frame)
        mtcnn_faces_count += len(faces)
        print(f"\rProcessing: {img_name} | Faces: {len(faces)}", end="")

    mtcnn_total_time = time.time() - start_time
    mtcnn_fps = len(images) / mtcnn_total_time if mtcnn_total_time > 0 else 0
    print(f"\n[RESULT] MTCNN: {mtcnn_total_time:.2f}s | FPS: {mtcnn_fps:.2f} | Total Faces: {mtcnn_faces_count}")

    # --- TEST 2: MEDIAPIPE ---
    print("\n--- Running MediaPipe ---")
    start_time = time.time()
    mp_faces_count = 0

    for img_name in images:
        frame = cv2.imread(os.path.join(INPUT_FOLDER, img_name))
        if frame is None: continue
        faces = mp_detector.detect(frame)
        mp_faces_count += len(faces)
        print(f"\rProcessing: {img_name} | Faces: {len(faces)}", end="")

    mp_total_time = time.time() - start_time
    mp_fps = len(images) / mp_total_time if mp_total_time > 0 else 0
    print(f"\n[RESULT] MediaPipe: {mp_total_time:.2f}s | FPS: {mp_fps:.2f} | Total Faces: {mp_faces_count}")

    # --- 3. VISUALIZATION ---
    print("\n[INFO] Generating Dual-Axis Graph...")
    create_comparison_chart(mtcnn_fps, mp_fps, mtcnn_faces_count, mp_faces_count)

def create_comparison_chart(mtcnn_fps, mp_fps, mtcnn_count, mp_count):
    models = ['MTCNN', 'MediaPipe']
    
    # Data Setup
    fps_values = [mtcnn_fps, mp_fps]
    count_values = [mtcnn_count, mp_count]
    
    x = np.arange(len(models))  # Label locations
    width = 0.35  # Width of the bars

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # --- BAR 1: FPS (Left Axis) ---
    color1 = '#66b3ff' # Blue
    rects1 = ax1.bar(x - width/2, fps_values, width, label='Speed (FPS)', color=color1, alpha=0.7)
    ax1.set_xlabel('Models', fontweight='bold')
    ax1.set_ylabel('Speed (FPS)', color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, max(fps_values) * 1.2) # Thoda upar jagah chhodna

    # --- BAR 2: Accuracy (Right Axis) ---
    ax2 = ax1.twinx()  # Doosra Y-axis banaya
    color2 = '#ff9999' # Red
    rects2 = ax2.bar(x + width/2, count_values, width, label='Accuracy (Face Count)', color=color2, alpha=0.7)
    ax2.set_ylabel('Total Faces Detected', color=color2, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, max(count_values) * 1.2) # Thoda upar jagah chhodna

    # Labels add karna (Bar ke upar value likhna)
    def autolabel(rects, ax):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold')

    autolabel(rects1, ax1)
    autolabel(rects2, ax2)

    # Title & Legend
    plt.title('Comparison: Speed vs Accuracy (Dual Axis)', fontweight='bold')
    
    # Saving
    output_dir = os.path.dirname(OUTPUT_GRAPH)
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    plt.savefig(OUTPUT_GRAPH)
    print(f"[SUCCESS] Graph saved at: {OUTPUT_GRAPH}")

    # --- AUTO CLOSE LOGIC (Let it down) ---
    print("[INFO] Showing graph for 5 seconds...")
    plt.show(block=False)  # Script ko rokega nahi
    plt.pause(5)           # 5 second wait karega
    plt.close()            # Window band kar dega
    print("[INFO] Visualization closed.")

if __name__ == "__main__":
    main()