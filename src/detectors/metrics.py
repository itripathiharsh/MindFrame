import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_mse(imageA, imageB):
    """
    Compute the Mean Squared Error between two images.
    Returns the raw MSE value.
    """
    # Convert to float to avoid overflow
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def calculate_ssim(imageA, imageB):
    """
    Compute Structural Similarity Index.
    Returns a score between -1.0 and 1.0.
    """
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
    
    score, _ = ssim(grayA, grayB, full=True)
    return score

def convert_to_percentage(score, method="mse"):
    """
    Normalize scores to a strict 0-100% difference scale.
    0% = Identical
    100% = Maximum possible difference
    """
    if method == "ssim":
        # SSIM is 1.0 (match) to -1.0 (inverse). 
        # (1 - 1) * 100 = 0%
        # (1 - 0) * 100 = 100% (Very different)
        return (1.0 - score) * 100.0
    
    elif method == "mse":
        # Max possible MSE for 8-bit images is 255^2 = 65025.
        # We normalize to this max value.
        normalized = (score / 65025.0) * 100.0
        # Clamp just in case
        return min(max(normalized, 0.0), 100.0)