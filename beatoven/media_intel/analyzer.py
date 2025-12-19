from __future__ import annotations
import os
import cv2
import numpy as np
from typing import Optional

from .schema import MediaFrame
from .physical import analyze_image_physical, analyze_video_motion
from .affect import affect_from_features
from .temporal import summarize_emotion_trajectory, infer_era_from_heuristics

def analyze_image(path: str, media_id: str) -> MediaFrame:
    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Could not read image: {path}")

    physical = analyze_image_physical(bgr)
    semantic = {}  # plug in CLIP/scene models later, keep contract stable

    affect, conf = affect_from_features(physical, semantic)
    era_dist, era_conf = infer_era_from_heuristics(physical, semantic)

    return MediaFrame(
        media_id=media_id,
        kind="image",
        path=path,
        physical=physical,
        semantic=semantic,
        affect=affect,
        confidence={**conf},
        perceived_era=era_dist,
        era_confidence=era_conf,
        model_versions={"physical": "v1", "affect": "v1", "era": "v1"},
    )

def analyze_video(path: str, media_id: str, sample_fps: float = 2.0, max_seconds: float = 60.0) -> MediaFrame:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration_s = float(total_frames / fps) if total_frames > 0 else None

    step = max(1, int(round(fps / sample_fps)))
    max_frames = int(sample_fps * max_seconds)

    frames_gray = []
    arousal_series = []
    valence_series = []

    idx = 0
    kept = 0
    while kept < max_frames:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames_gray.append(gray)

            physical = analyze_image_physical(frame)
            # motion computed after loop; here we get affect per sampled frame
            affect, _conf = affect_from_features(physical, {})
            arousal_series.append(float(affect["arousal"]))
            valence_series.append(float(affect["valence"]))
            kept += 1
        idx += 1

    cap.release()

    motion = analyze_video_motion(frames_gray)
    # Aggregate physical from a representative frame (middle) + motion
    physical_agg = {}
    if frames_gray:
        # Re-open to grab middle frame for color-based stats
        cap2 = cv2.VideoCapture(path)
        mid = max(0, int((total_frames or 0) * 0.5))
        cap2.set(cv2.CAP_PROP_POS_FRAMES, mid)
        ok, frame_mid = cap2.read()
        cap2.release()
        if ok and frame_mid is not None:
            physical_agg = analyze_image_physical(frame_mid)
    physical_agg.update(motion)

    semantic = {}
    affect, conf = affect_from_features(physical_agg, semantic)
    traj = summarize_emotion_trajectory(arousal_series, valence_series)
    era_dist, era_conf = infer_era_from_heuristics(physical_agg, semantic)

    return MediaFrame(
        media_id=media_id,
        kind="video",
        path=path,
        duration_s=duration_s,
        physical={**physical_agg, **traj},
        semantic=semantic,
        affect=affect,
        confidence={**conf},
        perceived_era=era_dist,
        era_confidence=era_conf,
        model_versions={"physical": "v1", "affect": "v1", "temporal": "v1", "era": "v1"},
    )
