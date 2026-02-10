import cv2
import yaml
import os
import sys
import shutil
import csv
import urllib.request
import argparse  # CLI ke liye zaroori library
from ultralytics import YOLO

# --- IMPORTS ---
# Ensure these modules are present in your 'srj' folder
from detectors.person_detector import PersonDetector
from detectors.face_detector import FaceDetector
from detectors.pose_estimator import PoseEstimator
from quality.scorer import QualityScorer
from quality.policy import FramePolicy
from pipeline.frame_analyzer import FrameAnalyzer

# --- PATH SETUP ---
# Gets the current directory of the script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "quality.yaml")

# 1. Pose Model Paths (MediaPipe Heavy)
POSE_MODEL_FILENAME = "pose_landmarker.task"
POSE_MODEL_PATH = os.path.join(BASE_DIR, POSE_MODEL_FILENAME)
# Official Google URL for the Heavy model (best accuracy)
POSE_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"

# 2. Face Model Paths (MediaPipe BlazeFace)
# Note: MTCNN use karte waqt iski zaroorat nahi padti, par MediaPipe mode ke liye ye chahiye.
FACE_MODEL_FILENAME = "blaze_face_short_range.tflite"
FACE_MODEL_PATH = os.path.join(BASE_DIR, FACE_MODEL_FILENAME)
FACE_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"

# --- UTILITY: AUTO-DOWNLOAD MODELS ---
def check_and_download(url, path, name):
    """
    Checks if a model file exists. If not, downloads it with a progress bar.
    """
    if os.path.exists(path):
        # File exists, no need to download
        return

    print(f"[INFO] '{name}' not found at {path}")
    print(f"[INFO] Downloading {name} from Google servers...")
    
    try:
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\rDownloading {name}: {percent:.1f}%", end="")
        
        urllib.request.urlretrieve(url, path, progress)
        print(f"\n[SUCCESS] {name} Download Complete!")
    except Exception as e:
        print(f"\n[ERROR] Download failed for {name}: {e}")
        print("Please check internet connection or download manually.")
        sys.exit(1)

# --- CLI ARGUMENT PARSER ---
def parse_arguments():
    """
    Defines command-line arguments for flexible usage.
    """
    parser = argparse.ArgumentParser(description="MindFrame Quality Filter & Analytics")
    
    # Detector Selection
    parser.add_argument("-d", "--detector", type=str, default=None, choices=["mtcnn", "mediapipe"],
                        help="Choose Face Detector: 'mtcnn' (Accurate) or 'mediapipe' (Fast)")

    # Input/Output Paths
    parser.add_argument("-i", "--input", type=str, default=None, 
                        help="Path to input folder containing frames (Default: ../output)")
    parser.add_argument("-o", "--output", type=str, default=None, 
                        help="Path to save filtered frames (Default: ../filtered_data)")

    # Threshold Overrides
    parser.add_argument("-s", "--score", type=int, default=None, 
                        help="Minimum Score per Person (0-100). Overrides config.")
    parser.add_argument("-r", "--ratio", type=float, default=None, 
                        help="Minimum Ratio of Good People (0.0-1.0). Overrides config.")

    return parser.parse_args()

# --- MAIN EXECUTION ---
def main():
    # 1. Parse CLI Arguments
    args = parse_arguments()

    # --- INTERACTIVE INPUT LOGIC ---
    # Agar argument CLI mein nahi diya, toh user se input maango
    
    # Input Path Logic
    if args.input:
        INPUT_FOLDER = args.input
    else:
        user_input = input("Enter Input Images Folder Path (Press Enter for default '../output/images'): ").strip()
        if user_input:
            INPUT_FOLDER = user_input
        else:
            INPUT_FOLDER = os.path.join(BASE_DIR, "..", "output/images")

    # Model Selection Logic
    if args.detector:
        detector_choice = args.detector
    else:
        print("\nChoose Face Detector Model:")
        print("1. MTCNN (More Accurate, Slower)")
        print("2. MediaPipe (Faster, Less Accurate)")
        choice = input("Enter choice (1 or 2) [Default: 1]: ").strip()
        
        if choice == "2":
            detector_choice = "mediapipe"
        else:
            detector_choice = "mtcnn"

    # Output Path Logic (Optional, keep default or arg)
    if args.output:
        OUTPUT_FOLDER = args.output
    else:
        OUTPUT_FOLDER = os.path.join(BASE_DIR, "..", "filtered_data")
        
    CSV_FILE_PATH = os.path.join(OUTPUT_FOLDER, "annotations.csv")

    print(f"\n[CONFIG] Input: {INPUT_FOLDER}")
    print(f"[CONFIG] Output: {OUTPUT_FOLDER}")
    print(f"[CONFIG] Model: {detector_choice.upper()}\n")

    # 3. Ensure Models Exist
    # Always download Pose Model
    check_and_download(POSE_URL, POSE_MODEL_PATH, "Pose Model")
    
    # Download Face Model only if MediaPipe detector is chosen
    if detector_choice == "mediapipe":
        check_and_download(FACE_URL, FACE_MODEL_PATH, "Face Model")

    # 4. Load Configuration File
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Config not found at: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, 'r') as f:
        cfg = yaml.safe_load(f)

    # ** Override Config with CLI Args if provided **
    if args.score is not None:
        print(f"[CLI] Overriding Min Score: {args.score}")
        cfg["min_frame_score"] = args.score
        
    if args.ratio is not None:
        print(f"[CLI] Overriding Min Ratio: {args.ratio}")
        cfg["min_ratio"] = args.ratio

    # 5. Initialize All Analytics Modules
    print(f"[INFO] Initializing Pipeline using Detector: {detector_choice.upper()}")
    print("[INFO] Loading YOLO (Person Detector)...")
    yolo = YOLO("yolov8n.pt")
    
    # Initialize Detectors
    person_detector = PersonDetector(yolo)
    
    # Hybrid Face Detector Initialization
    # We pass both method and model_path so it can handle either choice
    face_detector = FaceDetector(method=detector_choice, model_path=FACE_MODEL_PATH)
    
    pose_estimator = PoseEstimator(model_path=POSE_MODEL_PATH)
    
    # Initialize Logic Modules
    scorer = QualityScorer(cfg)
    policy = FramePolicy(cfg["min_frame_score"], cfg["min_ratio"])

    # Build the Analysis Pipeline
    analyzer = FrameAnalyzer(person_detector, face_detector, pose_estimator, scorer)

    # 6. Prepare Output Directories
    if not os.path.exists(INPUT_FOLDER):
        print(f"[ERROR] Input folder '{INPUT_FOLDER}' does not exist.")
        return

    if os.path.exists(OUTPUT_FOLDER):
        print(f"[INFO] Cleaning old output folder: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER) # Clear old results
    os.makedirs(OUTPUT_FOLDER)

    # 7. Prepare CSV Writer
    print(f"[INFO] Creating Annotation CSV at: {CSV_FILE_PATH}")
    csv_file = open(CSV_FILE_PATH, mode='w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(["Filename", "Decision", "Person_Count", "Orientations", "Avg_Score"])

    # 8. Process Images Loop
    images = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    images.sort()

    print(f"[INFO] Starting analysis on {len(images)} frames...")
    print("------------------------------------------------")

    for img_name in images:
        img_path = os.path.join(INPUT_FOLDER, img_name)
        frame = cv2.imread(img_path)

        if frame is None:
            print(f"[WARNING] Could not read {img_name}. Skipping.")
            continue

        # --- ANALYSIS STEP ---
        # 1. Detect Persons -> 2. Detect Faces -> 3. Estimate Pose -> 4. Calculate Score
        persons = analyzer.analyze(frame)
        
        # --- DECISION STEP ---
        keep, ratio = policy.decide(persons)

        # --- DATA LOGGING STEP ---
        orientations_list = [p.get("orientation", "Unknown") for p in persons]
        
        if persons:
            avg_score = sum(p["score"] for p in persons) / len(persons)
        else:
            avg_score = 0
            
        status_str = "KEPT" if keep else "DROPPED"
        
        # Write row to CSV
        writer.writerow([img_name, status_str, len(persons), str(orientations_list), f"{avg_score:.2f}"])

        # --- VISUALIZATION & SAVING STEP ---
        if keep:
            display_frame = frame.copy()
            
            for p in persons:
                bx, by, bw, bh = map(int, p["bbox"])
                score_val = int(p["score"])
                ori_text = p.get("orientation", "N/A")

                # --- COLOR CODING LOGIC ---
                # Green: High Score (Frontal)
                # Yellow: Medium Score (Semi-Profile)
                # Red: Low Score (Back/Profile)
                if score_val >= 90:
                    color = (0, 255, 0) # Green
                elif score_val >= 50:
                    color = (0, 255, 255) # Yellow
                else:
                    color = (0, 0, 255) # Red

                # 1. Draw Face Box (Matches Detector Output)
                if p["faces"]:
                    for fbox in p["faces"]:
                        fx, fy, fw, fh = map(int, fbox)
                        cv2.rectangle(display_frame, (fx, fy), (fx+fw, fy+fh), color, 2)
                
                # 2. Draw Orientation Text
                label = f"{ori_text} ({score_val})"
                cv2.putText(display_frame, label, (bx, by - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Save the annotated image
            save_path = os.path.join(OUTPUT_FOLDER, img_name)
            cv2.imwrite(save_path, display_frame)
            print(f"[✓] {img_name} : KEPT (Ratio: {ratio:.2f}) -> {orientations_list}")
        else:
            print(f"[X] {img_name} : DROPPED (Ratio: {ratio:.2f}) -> {orientations_list}")

    # 9. Cleanup & Finish
    csv_file.close()
    print("------------------------------------------------")
    print(f"[DONE] Analysis Complete.")
    print(f"[OUTPUT] Filtered Images saved to: {OUTPUT_FOLDER}")
    print(f"[OUTPUT] CSV Data saved to: {CSV_FILE_PATH}")

if __name__ == "__main__":
    main()