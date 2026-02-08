import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


class ChangeDetector:
    """
    Computes visual difference between two frames using SSIM or MSE.
    Returns normalized percentage change.
    """

    def __init__(self, method: str = "ssim"):
        """
        method: 'ssim' or 'mse'
        """
        method = method.lower()
        if method not in ["ssim", "mse"]:
            raise ValueError("method must be either 'ssim' or 'mse'")

        self.method = method

    @staticmethod
    def _preprocess(frame: np.ndarray) -> np.ndarray:
        """
        Convert frame to grayscale for comparison.
        """
        if frame is None:
            raise ValueError("Invalid frame received for processing")

        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return frame

    @staticmethod
    def _compute_mse(frame_a: np.ndarray, frame_b: np.ndarray) -> float:
        """
        Compute Mean Squared Error between two frames.
        """
        err = np.mean((frame_a.astype("float") - frame_b.astype("float")) ** 2)
        return err

    @staticmethod
    def _normalize_mse(mse_value: float) -> float:
        """
        Normalize MSE to percentage scale (0–100).
        """
        # Max possible MSE for 8-bit grayscale image
        max_mse = 255.0 ** 2
        normalized = (mse_value / max_mse) * 100.0
        return float(normalized)

    @staticmethod
    def _compute_ssim(frame_a: np.ndarray, frame_b: np.ndarray) -> float:
        """
        Compute Structural Similarity Index.
        """
        score, _ = ssim(frame_a, frame_b, full=True)
        return score

    @staticmethod
    def _normalize_ssim(ssim_score: float) -> float:
        """
        Convert SSIM similarity score to percentage change.
        """
        # SSIM = 1 → identical → 0% change
        # SSIM = 0 → completely different → 100% change
        change_percent = (1.0 - ssim_score) * 100.0
        return float(change_percent)

    def compute_change(self, frame_a: np.ndarray, frame_b: np.ndarray) -> float:
        """
        Public API: compute percentage change between two frames.
        """
        frame_a = self._preprocess(frame_a)
        frame_b = self._preprocess(frame_b)

        if frame_a.shape != frame_b.shape:
            raise ValueError("Frame dimensions do not match")

        if self.method == "mse":
            mse_value = self._compute_mse(frame_a, frame_b)
            return self._normalize_mse(mse_value)

        ssim_score = self._compute_ssim(frame_a, frame_b)
        return self._normalize_ssim(ssim_score)
