
# 📌 Project Overview – MindFrame (Behavior Analysis Pipeline)

MindFrame is a modular video-based behavior analysis system designed to process long video streams and extract only behaviorally meaningful visual data. The system follows a multi-stage pipeline where each stage refines the video information before it is passed to the next analysis module.

The primary goal is to reduce redundant data while preserving temporal and behavioral integrity.

---

## 🔹 Ticket-1: Frame Extraction (Brief Workflow Overview)

The first stage of the pipeline converts video input into structured frame data.

### Workflow:

1. A video file (MP4 / AVI / MOV) is provided as input.
2. Frames are extracted at a configurable frame rate (e.g., 1 FPS, 5 FPS, 10 FPS).
3. Each extracted frame is saved as an image file.
4. Accurate timestamps are generated and stored in a metadata file.
5. The output is a standardized directory containing:

   * `images/`
   * `metadata.json`

This stage ensures all downstream modules operate on uniform, time-aligned visual data.

---

## 🔹 Ticket-2: Pixel Difference Detection (Core Focus)

### 🎯 Objective

Ticket-2 is designed to **eliminate visually redundant frames** by detecting meaningful visual changes between frames. Instead of processing every extracted frame, only frames that exhibit sufficient structural difference are retained for further analysis.

This stage acts as a **data reduction and signal enhancement layer** in the pipeline.

---

## 🔍 Why Ticket-2 Is Necessary

After frame extraction, many frames are nearly identical:

* Static background
* Minimal facial movement
* Small posture shifts
* Idle frames during pauses

Processing these frames:

* Wastes compute
* Slows down pose and face detection
* Introduces noise into behavioral analysis

Ticket-2 solves this by **keeping only frames that show meaningful visual change**.

---

## 🧠 Core Concept: Visual Change Detection

Ticket-2 compares frames based on **perceptual similarity** rather than raw pixel differences.

The system answers one key question:

> “Is this frame visually different enough from the last retained frame to matter?”

---

## 🧪 Two Change Detection Approaches

Ticket-2 supports **two complementary approaches** for measuring visual change:

---

### 1️⃣ Structural Similarity Index (SSIM)

#### What it is:

SSIM measures how similar two images appear **to the human eye**, rather than comparing exact pixel values.

#### What SSIM evaluates:

* Luminance (brightness)
* Contrast
* Structural information (edges, shapes)

#### SSIM output:

* Range: `0 → 1`
* `1.0` → images are identical
* Lower values indicate increasing visual difference

#### Conversion to change percentage:

```
change % = (1 - SSIM) × 100
```

This conversion allows intuitive thresholding.

#### Why SSIM is preferred:

* Robust to lighting changes
* Sensitive to posture and movement
* Matches human visual perception

SSIM is the **default and recommended method**.

---

### 2️⃣ Mean Squared Error (MSE)

#### What it is:

MSE calculates the average squared difference between corresponding pixels in two frames.

#### Characteristics:

* Fast computation
* Sensitive to noise and lighting changes
* Less perceptually meaningful than SSIM

#### Use case:

MSE is useful in controlled environments or when performance is prioritized over perceptual accuracy.

---

## 🎚️ Threshold Mechanism

The **threshold** defines the minimum percentage of visual change required for a frame to be retained.

### Decision rule:

```
if change_percentage ≥ threshold:
    keep frame
else:
    drop frame
```

### Interpretation:

* Low threshold (e.g., 10%) → highly sensitive
* Medium threshold (15–20%) → balanced
* High threshold (25–30%) → strict filtering

---

## 🔁 Comparison Strategy (Critical Design Choice)

Frames are **not** compared sequentially.

Instead, each new frame is compared against the **last retained frame**.

### Why this matters:

* Prevents accumulation of tiny changes
* Avoids keeping near-identical frames
* Ensures only meaningful transitions survive

This approach dramatically improves frame reduction efficiency while preserving behavioral transitions.

---

## 📂 Input and Output Flow

### Input:

* `images/` from Ticket-1
* `metadata.json` containing timestamps and frame order

### Output:

* Filtered `images/` directory
* Updated `metadata.json` (kept frames only)
* `dropped_frames.json` (discarded frames with change scores)

All timestamps remain unchanged.

---

## 🧮 Example Behavior (Real Data)

For a 2:22 minute video at 5 FPS:

* Total extracted frames: `712`

### Threshold = 10%

* Frames retained: ~650
* Minimal reduction
* Captures micro movements

### Threshold = 20%

* Frames retained: `420`
* ~41% reduction
* Preserves visible posture and motion changes

This demonstrates how threshold selection directly impacts data density.

---

## 🧑‍💻 Workflow – How to Run Ticket-2

1. Ensure Ticket-1 output exists:

```
outputs/extraction/
 ├── images/
 └── metadata.json
```

2. Run the interactive CLI:

```bash
python -m ticket2
```

3. Provide:

* Input directory
* Change detection method (SSIM / MSE)
* Threshold value
* Output directory

4. Processed results are saved to:

```
outputs/change_detection/
```

---

## 🚀 Impact on the Overall System

Ticket-2:

* Reduces redundant frames
* Improves downstream accuracy
* Lowers compute cost
* Preserves temporal integrity

It acts as a **behavior-aware filter** before face and pose analysis.

---

## 🏁 Final Summary

Ticket-2 is the most critical preprocessing stage in MindFrame. By combining perceptual similarity metrics with configurable thresholds and a robust comparison strategy, the system effectively balances data reduction and behavioral fidelity. This ensures that downstream analysis operates only on frames that carry meaningful behavioral information.
