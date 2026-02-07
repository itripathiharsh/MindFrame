# Extraction Engines: Conceptual Difference

### OpenCV-Based Extraction

**Methodology**

OpenCV performs frame extraction by:

* Reading the video sequentially frame-by-frame

* Selecting frames based on a fixed frame interval derived from:

  ```
  frame_interval = original_fps / requested_fps
  ```

* Computing timestamps using frame index arithmetic:

  ```
  timestamp = frame_index / original_fps
  ```

**Characteristics**

* Assumes a constant frame rate
* Stops extraction strictly at end-of-stream
* Produces a frame count closely matching:

  ```
  ceil(video_duration × requested_fps)
  ```

**Advantages**

* Predictable frame counts
* Intuitive one-frame-per-second behavior
* Useful for debugging and controlled experiments

**Limitations**

* Ignores presentation timestamps
* Sensitive to variable frame rate (VFR) videos
* May silently discard encoder padding frames

---

### FFmpeg-Based Extraction

**Methodology**

FFmpeg performs frame extraction by:

* Sampling frames according to **presentation timestamps (PTS)**
* Selecting frames that occur at regular time intervals on the video timeline
* Respecting all encoded timestamps, including padding and delay frames

**Characteristics**

* Timestamp-driven rather than frame-count-driven
* May extract frames beyond the visually perceived duration
* Frame count may exceed `duration × FPS`

**Advantages**

* Preserves true temporal alignment
* Handles variable frame rate and encoder padding correctly
* Reflects the actual encoded video timeline

**Limitations**

* Frame counts may appear unintuitive
* Requires understanding of timestamp-based sampling

---

## Presentation Timestamp (PTS) Explanation

Each video frame carries a presentation timestamp indicating **when that frame should be displayed on the playback timeline**.

Key points:

* PTS values define the true temporal structure of a video
* Container-reported duration is an approximation
* Encoders may introduce leading or trailing frames with valid timestamps
* FFmpeg respects these timestamps
* OpenCV does not use PTS for sampling

As a result, FFmpeg may extract frames at timestamps that extend beyond the reported duration, while OpenCV does not.

---

## Observed Behavior Example

| Engine | Requested FPS | Reported Duration | Frames Extracted |
| ------ | ------------- | ----------------- | ---------------- |
| OpenCV | 1 FPS         | ~142 seconds      | 143 frames       |
| FFmpeg | 1 FPS         | ~142 seconds      | 150 frames       |

This difference reflects the underlying sampling strategy, not an error.

---

## Design Decision Rationale

MindFrame uses **FFmpeg as the default engine** and **OpenCV as a fallback**.

Justification:

* Behavior analysis relies on accurate temporal alignment
* Timestamp-based sampling is more robust for real-world videos
* OpenCV remains valuable for strict FPS expectations and validation

---

## Summary

* OpenCV provides deterministic, frame-count-based sampling
* FFmpeg provides temporally accurate, timestamp-based sampling
* Both engines are correct within their respective models
* Supporting both enables robustness across diverse video sources

---

## Conclusion

The inclusion of both FFmpeg and OpenCV is a deliberate architectural decision.
It allows MindFrame to balance intuitive sampling behavior with accurate temporal fidelity, ensuring reliability for downstream behavior analysis tasks.


