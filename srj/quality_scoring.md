# 📘 MindFrame: Quality Scoring & Face Detection Module
**Version:** 1.0.0  
**Module:** Frame face Analytics Pipeline

---

## 1. 🌟 Overview
The **Quality Scoring Module** is an intelligent filter designed to evaluate participant engagement in video frames. Unlike simple face detection, this system determines **"Quality"** based on:
1.  **Face Visibility:** Whether a face is detected.
2.  **Orientation:** Where the person is looking (Frontal vs. Side vs. Back).
3.  **Group Consensus:** Whether the majority of the group is attentive.

It utilizes a **Hybrid Architecture** combining:
* **Face Detection:** Options for **MTCNN** (High Accuracy) or **MediaPipe** (High Speed).
* **Pose Estimation:** **MediaPipe Pose Landmarks** to detect head orientation via geometric analysis.

---

## 2. 🚀 How to Run the Code
This module supports a **Command Line Interface (CLI)**, allowing you to choose models and paths dynamically.

### 📦 Prerequisites
Ensure all dependencies are installed:
```bash
pip install opencv-python mediapipe mtcnn ultralytics pyyaml



🏃‍♂️ Execution Methods
Method A: Interactive Mode (Recommended)
Simply run the script, and it will ask for the input folder and model choice.

Bash
python srj/main.py
Prompts you will see:

Enter Input Images Folder Path: (Press Enter for default)

Choose Face Detector Model: (Select 1 for MTCNN, 2 for MediaPipe)

Method B: Command Line Arguments (For Automation)
You can pass arguments directly to skip prompts.

1. Run with Default Settings (MTCNN):

Bash
python srj/main.py
2. Run with MediaPipe (Faster):

Bash
python srj/main.py -d mediapipe
3. Custom Input/Output Folders:

Bash
python srj/main.py -i "C:/MyImages" -o "C:/MyResults"
4. Strict Mode (High Quality Filter):

Bash
python srj/main.py -d mtcnn --score 80 --ratio 0.6
3. 🧠 Logic Breakdown: Orientation & Scoring
A. Orientation Detection (Geometric Analysis)
The system calculates the orientation by analyzing the horizontal distance between the Nose and Ears landmarks.

Orientation Label,Condition / Logic,Quality Score,Status
Frontal,Both ears visible. Nose is centrally located (Ratio 0.4 - 0.6).,100,✅ Excellent
Slight-Left/Right,"Both ears visible, nose slightly off-center.",80,✅ Good
Semi-Profile,"Both ears visible, but nose is close to one ear.",60-70,⚠️ Average
Profile (Side),One ear is hidden (< 30% visibility).,45-50,⚠️ Poor
Indistinct,"Face detector failed, but Pose detected a body/head.",45,⚠️ Poor
Back-Facing,No face detected AND No nose landmarks visible.,0-20,❌ Reject


B. The Ratio Formula 📐
To mathematically distinguish between Frontal and Semi-Profile views, we calculate:

Code snippet
Ratio = Distance(Nose to Left Ear) / Total Width(Left Ear to Right Ear)
Ratio ≈ 0.50: Perfect Frontal (Nose is in the center).

Ratio < 0.40: Looking Left.

Ratio > 0.60: Looking Right.

4. ⚖️ Frame Selection Policy (Group Logic)
Since frames contain multiple people, we use a Majority Consensus Policy instead of a simple average score.

Step 1: Individual Check 👤
Each person is marked as "PASS" if their score meets the threshold:

Condition: Person Score >= min_frame_score (Default: 50)

Step 2: Frame Ratio Calculation 📊
Code snippet
Frame Ratio = (Count of PASS People) / (Total People in Frame)
Step 3: Final Decision ✅/❌
KEEP Frame: If Frame Ratio >= min_ratio (Default: 0.40).

DROP Frame: If ratio is lower.

Reasoning: This logic preserves frames where a significant portion (e.g., 40%) of the group is visible and engaged, even if 1 or 2 individuals are looking away or undetected.

5. ⚙️ Configuration Parameters
The system behavior is controlled via srj/config/quality.yaml:

Parameter,Default,Description
min_frame_score,50,"The minimum score for a person to be considered ""Valid"". • Set to 40: Includes side-profiles/blurry faces.• Set to 80: Strictly frontal faces only."
min_ratio,0.40,The percentage of the group required to save the frame.• Set to 0.4: Keeps frame if 40% of people are valid.• Set to 0.8: Very strict group requirement.


6. 📂 Deliverables & Outputs
1. Processed Images (filtered_data/) 🖼️
Images are saved with color-coded bounding boxes for easy debugging:

🟢 Green: High Confidence (Frontal/Slight).

🟡 Yellow: Medium Confidence (Semi-Profile).

🔴 Red: Low Confidence (Back/Profile).

2. Data Logs (filtered_data/annotations.csv) 📝
A CSV file containing detailed analytics for every frame:

Filename: Name of the image.

Decision: KEPT or DROPPED.

Person_Count: Number of people detected.

Orientations: List of directions (e.g., ['Frontal', 'Back']).

Avg_Score: Average quality score of the frame.