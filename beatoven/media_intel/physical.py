from __future__ import annotations
import numpy as np
import cv2
from typing import Any, Dict, Tuple

def _hist_stats(gray: np.ndarray) -> Dict[str, float]:
    hist = cv2.calcHist([gray],[0],None,[256],[0,256]).flatten()
    hist = hist / (hist.sum() + 1e-9)
    idx = np.arange(256, dtype=np.float32)
    mean = float((hist * idx).sum())
    var = float((hist * (idx - mean) ** 2).sum())
    return {"luma_mean": mean/255.0, "luma_var": var/(255.0**2)}

def analyze_image_physical(bgr: np.ndarray) -> Dict[str, Any]:
    """
    Explainable, deterministic physical features.
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # brightness/contrast
    stats = _hist_stats(gray)

    # saturation proxy via HSV
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:,:,1].astype(np.float32) / 255.0
    stats["sat_mean"] = float(sat.mean())
    stats["sat_var"] = float(sat.var())

    # edge density (composition/clutter proxy)
    edges = cv2.Canny(gray, 80, 160)
    stats["edge_density"] = float((edges > 0).mean())

    # sharpness (Laplacian variance)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    stats["sharpness"] = float(lap.var())

    # symmetry proxy: compare left/right halves
    left = gray[:, :w//2]
    right = cv2.flip(gray[:, w - w//2:], 1)
    if left.shape == right.shape:
        diff = np.abs(left.astype(np.float32) - right.astype(np.float32)).mean() / 255.0
        stats["symmetry_inv"] = float(1.0 - min(1.0, diff))
    else:
        stats["symmetry_inv"] = 0.0

    stats["resolution_mp"] = float((h*w)/1e6)
    return stats

def analyze_video_motion(frames_gray: list[np.ndarray]) -> Dict[str, Any]:
    """
    Motion descriptors: optical flow energy, jitter proxy.
    """
    if len(frames_gray) < 2:
        return {"motion_energy": 0.0, "jitter": 0.0}

    energies = []
    jitters = []

    prev = frames_gray[0]
    for cur in frames_gray[1:]:
        flow = cv2.calcOpticalFlowFarneback(prev, cur, None, 0.5, 2, 15, 3, 5, 1.2, 0)
        mag = np.sqrt(flow[...,0]**2 + flow[...,1]**2)
        energies.append(float(np.mean(mag)))

        # jitter proxy: flow variance (handheld shaky vs smooth)
        jitters.append(float(np.var(mag)))
        prev = cur

    # Normalize with gentle squashing so it behaves across content
    me = float(np.tanh(np.mean(energies) / 2.0))
    ji = float(np.tanh(np.mean(jitters) / 10.0))
    return {"motion_energy": me, "jitter": ji}
