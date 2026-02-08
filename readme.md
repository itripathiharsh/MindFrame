🧠 MindFrame

Video Preprocessing & Behavior Analysis Pipeline

MindFrame is a modular, production-ready system designed for behavior analysis pipelines. It processes raw video into meaningful data by extracting frames and intelligently filtering out redundant or static content.

Instead of flooding downstream AI models with thousands of identical frames (e.g., an empty room), MindFrame uses a hybrid dual-pass filter to keep only the moments where meaningful motion or structural changes occur.

🚀 Quick Start (The "I just want to run it" guide)

1. Install Dependencies

pip install -r requirements.txt
pip install matplotlib pandas tabulate scikit-image


2. Run Stage 1 (Extract Frames)

Turn video into images.

python run.py
# Follow prompts: Select video -> ffmpeg -> 1 FPS


3. Run Stage 2 (Filter Duplicates)

Remove boring frames using default settings.

python run_detection.py
# Follow prompts: Select output folder -> MSE 0.5 -> SSIM 15.0


🧩 The Pipeline: How it Works

We process video in two distinct stages. This modular approach allows you to re-run analysis without re-extracting frames (which is slow).

graph TD
    A[Video File] -->|Stage 1: Extraction| B(Raw Frames Folder)
    B -->|Stage 2: Gate 1| C{MSE Check}
    C -- High Diff --> D{SSIM Check}
    C -- Low Diff --> E[Drop Frame]
    D -- High Diff --> F[Keep Frame]
    D -- Low Diff --> E
    F --> G[Final Dataset]


📚 Step-by-Step Guide

Step 1: Frame Extraction (Ticket-1)

Goal: Convert a video file into a folder of individual images with accurate timestamps.

Why? Machine learning models (like DeepFace or YOLO) cannot read videos directly; they need images.

Tool: run.py

How to run:

python run.py


Video Path: Enter the path to your video (e.g., samples/sample_video.mp4).

Engine: Choose ffmpeg (Recommended for speed/accuracy) or opencv (Good for debugging).

FPS: Enter 1 (Extract 1 frame every second).

Output:

A folder named output/images containing frame_000001.jpg, etc.

A metadata.json file containing the exact timestamp of every frame.

Step 2: Threshold Analysis (Recommended)

Goal: Scientifically determine "What is noise?" vs. "What is a real movement?"

Why? Guessing thresholds (e.g., "10% change") is dangerous. If you guess too high, you lose data. If too low, you keep garbage.

Tool: analyze_thresholds.py

How to run:

python analyze_thresholds.py


Input: Enter the folder from Step 1 (usually output).

Output:

It generates a graph: threshold_analysis.png.

Look at the graph: The flat, wiggly line at the bottom is sensor noise. The spikes are actual movement.

Pick numbers: Choose an MSE and SSIM value that is above the noise but below the spikes.

Step 3: Change Detection (Ticket-2)

Goal: Filter the raw frames to keep only "meaningful" content.

Why? 90% of security footage or behavioral observation is static (nothing happening). We remove those frames to save storage and processing time.

Tool: run_detection.py

How to run:

python run_detection.py


Input: Enter the folder from Step 1 (output).

Output: Enter a name for the new results folder (e.g., output_analyzed).

MSE Threshold: Enter 0.5 (Removes exact duplicates/noise).

SSIM Threshold: Enter 15.0 (Removes small lighting shifts/wind).

What happens inside?

Gate 1 (Fast): It calculates MSE (Pixel Difference). If Diff < 0.5%, the frame is dropped immediately.

Gate 2 (Smart): If it passes Gate 1, it calculates SSIM (Structural Similarity). If Structure Change < 15%, it is dropped.

Output:

Check output_analyzed/visualization/.

You will see frames with Green Borders (Kept) and Red Borders (Dropped).

Step 4: Verification & Benchmarking

Goal: Prove that your system is efficient.

Why? You need to report "We reduced data volume by 60%."

Tool: tests/nikhil_test.py

How to run:

python tests/nikhil_test.py


Output:
It runs the detector 4 times with different strictness levels and prints a table:

Config Name

MSE

SSIM

Kept

Dropped

Reduction %

Sensitive

0.1

5.0

85

15

15.0%

Balanced

0.5

15.0

42

58

58.0%

Strict

0.5

25.0

20

80

80.0%

This confirms your logic is working and helps you choose the best configuration for production.

📁 Project Structure

MindFrame/
│
├── run.py                      # Step 1: Extraction Script
├── run_detection.py            # Step 3: Detection Script
├── analyze_thresholds.py       # Step 2: Analysis Tool
│
├── src/
│   ├── extractors/             # (Core) FFmpeg & OpenCV logic
│   ├── detectors/              # (Core) Change detection logic
│   └── utils/                  # Helpers for JSON/Files
│
├── tests/
│   ├── test_extraction.py      # Automated checks
│   └── nikhil_test.py          # Step 4: Benchmark Tool
│
└── output/                     # (Generated) Raw frames


🏆 Key Design Decisions

Hybrid Filter (MSE + SSIM):

We don't just use one. MSE is fast but "dumb." SSIM is smart but slow.

By using MSE as a "Gatekeeper," we filter 50% of frames instantly, making the system 2x faster than using SSIM alone.

Single-Pass Processing:

We optimized the loop to read images only once. This allows MindFrame to process hours of video without crashing your computer's memory (RAM).

Visualization-First Debugging:

Instead of just giving you a CSV file, we generate images with colored borders. This allows you to visually verify exactly why a frame was dropped.

📄 Deliverables Summary

Feature

Status

Frame Extraction

✅ FFmpeg & OpenCV Engines

Pixel Diff Detection

✅ MSE Implementation

Structural Detection

✅ SSIM Implementation

Threshold System

✅ Configurable (0-100%)

Benchmarks

✅ Auto-generated CSV Reports

Visualization

✅ Green/Red Overlay System