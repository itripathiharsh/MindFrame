import cv2
import yaml
import os
import sys
import shutil
import csv
import urllib.request
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
FACE_MODEL_FILENAME = "blaze_face_short_range.tflite"
FACE_MODEL_PATH = os.path.join(BASE_DIR, FACE_MODEL_FILENAME)
# Official Google URL for the Face model
FACE_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"

# Folders Configuration
# Note: Checks 'output' folder parallel to 'srj'
INPUT_FOLDER = os.path.join(BASE_DIR, "..", "output_frames/images")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "..", "filtered_data")
CSV_FILE_PATH = os.path.join(OUTPUT_FOLDER, "annotations.csv")

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

# --- MAIN EXECUTION ---
def main():
    # 1. Ensure Models Exist (Auto-Download Step)
    check_and_download(POSE_URL, POSE_MODEL_PATH, "Pose Model")
    check_and_download(FACE_URL, FACE_MODEL_PATH, "Face Model")

    # 2. Load Configuration File
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] Config not found at: {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, 'r') as f:
        cfg = yaml.safe_load(f)

    # 3. Initialize All Analytics Modules
    print("[INFO] Loading YOLO (Person Detector)...")
    yolo = YOLO("yolov8n.pt")
    
    print("[INFO] Initializing Analytics Modules...")
    # Initialize detectors with their respective models
    person_detector = PersonDetector(yolo)
    face_detector = FaceDetector(model_path=FACE_MODEL_PATH)
    pose_estimator = PoseEstimator(model_path=POSE_MODEL_PATH)
    
    # Initialize Logic Modules
    scorer = QualityScorer(cfg)
    policy = FramePolicy(cfg["min_frame_score"], cfg["min_ratio"])

    # Build the Analysis Pipeline
    analyzer = FrameAnalyzer(person_detector, face_detector, pose_estimator, scorer)

    # 4. Prepare Output Directories
    if not os.path.exists(INPUT_FOLDER):
        print(f"[ERROR] Input folder '{INPUT_FOLDER}' does not exist.")
        print("Make sure you have run Ticket 1 code and have frames in 'output' folder.")
        return

    if os.path.exists(OUTPUT_FOLDER):
        print(f"[INFO] Cleaning old output folder: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER) # Clear old results to avoid mix-up
    os.makedirs(OUTPUT_FOLDER)

    # 5. Prepare CSV Writer (For Client Deliverables)
    print(f"[INFO] Creating Annotation CSV at: {CSV_FILE_PATH}")
    csv_file = open(CSV_FILE_PATH, mode='w', newline='')
    writer = csv.writer(csv_file)
    
    # Write the Header row for the CSV
    writer.writerow(["Filename", "Decision", "Person_Count", "Orientations", "Avg_Score"])

    # 6. Process Images Loop
    # Get all images from input folder
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
        # Decide based on Policy (e.g., "Are 60% of people facing front?")
        keep, ratio = policy.decide(persons)

        # --- DATA LOGGING STEP ---
        # Extract orientations for CSV (e.g., ['Frontal', 'Back-Facing'])
        orientations_list = [p.get("orientation", "Unknown") for p in persons]
        
        # Calculate Average Score of the frame
        if persons:
            avg_score = sum(p["score"] for p in persons) / len(persons)
        else:
            avg_score = 0
            
        status_str = "KEPT" if keep else "DROPPED"
        
        # Write row to CSV
        writer.writerow([img_name, status_str, len(persons), str(orientations_list), f"{avg_score:.2f}"])

        # --- VISUALIZATION & SAVING STEP ---
        # Only save the frame if it passes the policy (keep=True)
        if keep:
            display_frame = frame.copy()
            
            # Loop through each person to draw details
            for p in persons:
                bx, by, bw, bh = map(int, p["bbox"])
                ori_text = p.get("orientation", "N/A")
                score_val = int(p["score"])

                # --- COLOR CODING LOGIC ---
                # Green: High Score (Frontal)
                # Yellow: Medium Score (Semi-Profile)
                # Red: Low Score (Back/Profile)
                
                if score_val >= 90:
                    color = (0, 255, 0) # Green (Frontal)
                elif score_val >= 50:
                    color = (0, 255, 255) # Yellow (Semi/Profile)
                else:
                    color = (0, 0, 255) # Red (Back)

                # 1. Draw Green Box on Face (if a face was detected)
                if p["faces"]:
                    for fbox in p["faces"]:
                        fx, fy, fw, fh = map(int, fbox)
                        # Box color matches the quality score
                        cv2.rectangle(display_frame, (fx, fy), (fx+fw, fy+fh), color, 2)
                
                # 2. Draw Orientation Text (e.g., "Frontal (100)")
                # Place text slightly above the Person's Bounding Box
                label = f"{ori_text} ({score_val})"
                cv2.putText(display_frame, label, (bx, by - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Save the annotated image to the filtered folder
            save_path = os.path.join(OUTPUT_FOLDER, img_name)
            cv2.imwrite(save_path, display_frame)
            print(f"[✓] {img_name} : KEPT (Ratio: {ratio:.2f}) -> {orientations_list}")
        else:
            # If dropped, just print to console
            print(f"[X] {img_name} : DROPPED (Ratio: {ratio:.2f}) -> {orientations_list}")

    # 7. Cleanup & Finish
    csv_file.close()
    print("------------------------------------------------")
    print(f"[DONE] Analysis Complete.")
    print(f"[OUTPUT] Filtered Images saved to: {OUTPUT_FOLDER}")
    print(f"[OUTPUT] CSV Data saved to: {CSV_FILE_PATH}")

if __name__ == "__main__":
    main()