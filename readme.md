
# MindFrame

**AI-Powered Video-Based Human Behavior Analysis System**

InsightLens is a modular computer vision system designed to analyze human behavior from video data. The project processes video streams to extract meaningful frames, detect visual changes, analyze face and pose orientation, and filter frames based on behavioral quality metrics.

The system is built as a **multi-stage pipeline**, where each module is independently configurable and scalable.

---

## 🚀 Key Features

* Multi-format video support (MP4, AVI, MOV)
* Configurable frame extraction with accurate timestamps
* Pixel-level change detection to reduce redundant frames
* Face detection and pose estimation for behavior filtering
* Modular, pipeline-based architecture
* CLI-driven execution for easy testing and integration

---

## 🧩 System Architecture

```
Video Input
   ↓
Frame Extraction Module
   ↓
Pixel Difference Detection
   ↓
Face & Pose Detection Filter
   ↓
Behavior-Ready Frame Dataset
```

Each stage operates independently and passes structured output to the next module.

---

## 📦 Project Modules

### 1️⃣ Frame Extraction Module

**Purpose:**
Extract frames from video files at a configurable rate while preserving timestamp metadata.

**Key Capabilities:**

* FPS-based or frame-interval-based extraction
* Timestamp generation for each frame
* Supports multiple video formats
* CLI-based execution

---

### 2️⃣ Pixel Difference Detection Module

**Purpose:**
Identify significant visual changes between consecutive frames and drop redundant frames.

**Techniques Used:**

* Mean Squared Error (MSE)
* Structural Similarity Index (SSIM)
* Configurable change thresholds (5%, 10%, 15%, 20%)

---

### 3️⃣ Face & Pose Detection Filter

**Purpose:**
Ensure extracted frames contain usable human presence and orientation.

**Capabilities:**

* Face detection using CV/ML models
* Pose estimation to identify back-facing or profile views
* Quality scoring for face visibility
* Multi-participant handling

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **OpenCV**
* **FFmpeg**
* **MediaPipe**
* **NumPy**
* **scikit-image**
* **CLI (argparse / typer)**

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/insightlens.git
cd insightlens
pip install -r requirements.txt
```

---

## ▶️ Usage (Example)

```bash
python extract_frames.py \
  --video sample.mp4 \
  --fps 1 \
  --output frames/
```

Each module can be run independently or chained together as part of the full pipeline.

---

## 📁 Sample Output Structure

```
output/
 ├── frames/
 │    ├── frame_000001.jpg
 │    ├── frame_000002.jpg
 │    └── ...
 ├── metadata.json
 └── logs/
```

---

## 🎯 Use Cases

* Interview and assessment analysis
* Human attention and engagement tracking
* Behavioral research and studies
* Video data preprocessing for ML pipelines
* Remote proctoring and monitoring systems

---

## 🧠 Future Enhancements

* Emotion and sentiment detection
* Gaze tracking
* Audio-visual behavior fusion
* Real-time video stream support
* Dashboard-based analytics

---

## 👥 Contributors

* **Harsh** – Frame Extraction Module
* **Nikhil** – Pixel Difference Detection
* **Jithin** – Face & Pose Detection

---

## 📜 License

MIT License

---

If you want next, I can:

* Make it **shorter (1-page README)**
* Add **diagrams**
* Split README per module
* Rewrite this to sound more **research-paper style**
* Tailor it for **resume / GitHub showcase**

Just say the word 🚀
