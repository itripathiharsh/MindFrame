
# 🧠 MindFrame

**Video Frame Extraction Module (Ticket-1)**

MindFrame is a modular, production-ready video preprocessing system designed for **behavior analysis pipelines**.
This module focuses on **robust frame extraction with accurate timestamps**, forming the foundation for downstream tasks such as change detection, face/pose analysis, and behavior scoring.

---

## 📌 What This Module Does

MindFrame takes a video file as input and:

* Extracts frames using **FFmpeg** or **OpenCV**
* Supports **configurable frame rates** (1 FPS, 10 FPS, etc.)
* Preserves **timestamp metadata** for each frame
* Handles common video formats (MP4, AVI, MOV, MKV)
* Provides **two execution modes**:

  * Interactive (human-friendly)
  * CLI-based (automation-friendly)

This module is **Stage-1** of the overall behavior analysis pipeline.

---

## 🧩 High-Level Workflow

```
Video Input
   ↓
Video Metadata Reader
   ↓
Frame Extraction Engine (FFmpeg / OpenCV)
   ↓
Timestamp Mapping
   ↓
Structured Output (Images + metadata.json)
```

---

## 📁 Project Structure

```
MindFrame/
│
├── run.py                      # Interactive entry point (recommended for demos)
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   │
│   ├── cli.py                  # CLI entry point (scripted / automation)
│   ├── main.py                 # Core orchestration logic
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── ffmpeg_extractor.py # FFmpeg-based frame extraction
│   │   └── opencv_extractor.py # OpenCV-based frame extraction
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── video_info.py       # Reads FPS, duration, total frames
│   │   ├── metadata_writer.py  # Writes metadata.json
│   │   └── validators.py       # Input validation utilities
│
├── samples/
│   └── sample_video.mp4        # Test video
│
├── tests/
│   └── test_extraction.py      # Pytest-based validation
│
└── output/                     # Generated outputs (ignored in git)
```

---

## 🧠 File Responsibilities (Important)

### `main.py` – **Core Orchestrator**

* Reads video metadata
* Chooses extraction engine
* Calls extractor modules
* Builds standardized metadata
* Saves outputs

> This file contains **no user interaction logic**.

---

### `ffmpeg_extractor.py`

* Fast, time-based frame extraction
* Uses FFmpeg’s `fps` filter
* Best for production and long videos

---

### `opencv_extractor.py`

* Frame-accurate extraction
* Reads video frame-by-frame
* Useful for debugging and variable-FPS videos

---

### `cli.py`

* Script-based execution using flags
* Designed for automation and batch jobs

---

### `run.py`

* Interactive execution mode
* Asks user for inputs step-by-step
* Designed for demos, judges, and non-technical users

---

## ▶️ How to Run (Recommended – Interactive Mode)

### Use case

* First-time users
* Demos
* Manual testing
* Judges / evaluators

### Command

```powershell
python run.py
```

### Example interaction

```
Enter video path:
> samples/sample_video.mp4

Choose engine (ffmpeg/opencv) [ffmpeg]:
> opencv

Enter FPS (e.g., 1, 5, 10):
> 10

Enter output directory [output]:
> output_demo

Save metadata? (y/n) [y]:
> y
```

### Result

```
output_demo/
 ├── images/
 │    ├── frame_000001.jpg
 │    ├── frame_000002.jpg
 │    └── ...
 └── metadata.json
```

---

## ▶️ How to Run (CLI Mode – Automation)

### Use case

* Scripts
* CI/CD
* Batch processing
* Advanced users

### Command

```powershell
python -m src.cli --video samples/sample_video.mp4 --fps 1 --engine ffmpeg --output output --save-metadata
```

### Flags

| Flag              | Description          |
| ----------------- | -------------------- |
| `--video`         | Path to input video  |
| `--fps`           | Frames per second    |
| `--engine`        | `ffmpeg` or `opencv` |
| `--output`        | Output directory     |
| `--save-metadata` | Save metadata.json   |

---

## 📄 Output Format

### Directory

```
output/
 ├── images/
 │    ├── frame_000001.jpg
 │    ├── frame_000002.jpg
 │    └── ...
 └── metadata.json
```

### Metadata (`metadata.json`)

```json
{
  "project": "MindFrame",
  "source_video": "sample_video.mp4",
  "engine": "ffmpeg",
  "requested_fps": 1,
  "original_video_fps": 25,
  "total_frames_extracted": 100,
  "extraction_time": "2026-02-07T07:17:42Z",
  "frames": [
    {
      "frame_id": 1,
      "filename": "frame_000001.jpg",
      "timestamp_sec": 0.0
    }
  ]
}
```

---

## 🧪 Testing & Validation

Automated tests ensure:

* FFmpeg extraction works
* OpenCV extraction works
* Metadata integrity is preserved

### Run tests

```powershell
python -m pytest
```

---

## 🎯 About “Sample Output with 100 Frames”

The requirement to provide **100 frames** is a **demonstration artifact**, not a hardcoded rule.

Example:

* 100-second video @ 1 FPS → 100 frames
* 10-second video @ 10 FPS → 100 frames

This proves:

* FPS logic works
* System scales beyond toy examples

---

## 🏆 Design Decisions Summary

| Decision                     | Reason                   |
| ---------------------------- | ------------------------ |
| Dual engine support          | Flexibility & robustness |
| FFmpeg as default            | Speed & time accuracy    |
| OpenCV as fallback           | Frame-level precision    |
| Separate `run.py` & `cli.py` | Usability + automation   |
| Central `main.py`            | Clean orchestration      |
| Metadata JSON                | Downstream compatibility |

---
