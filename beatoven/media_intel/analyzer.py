from __future__ import annotations
import os
import numpy as np
from typing import Optional

from .schema import MediaFrame
from .affect import affect_from_features
from .temporal import summarize_emotion_trajectory, infer_era_from_heuristics

# Optional opencv dependency
try:
    import cv2
    from .physical import analyze_image_physical, analyze_video_motion
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False
    cv2 = None  # type: ignore

# Optional semantic engine
try:
    from .semantic_engine import SemanticEngine
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False
    SemanticEngine = None  # type: ignore

def analyze_image(path: str, media_id: str, semantic_engine: Optional["SemanticEngine"] = None) -> MediaFrame:
    if not _CV2_AVAILABLE:
        raise ImportError(
            "opencv-python is required for media analysis. "
            "Install with: pip install beatoven[media]"
        )

    bgr = cv2.imread(path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"Could not read image: {path}")

    physical = analyze_image_physical(bgr)

    # Use semantic engine if provided
    if semantic_engine is not None and _SEMANTIC_AVAILABLE:
        semantic = semantic_engine.analyze(kind="image", path=path, context={"hint": "music-control"})
    else:
        semantic = {}

    affect, conf = affect_from_features(physical, semantic)

    # Merge CLIP era if available
    if "clip" in semantic and "era_dist" in semantic["clip"]:
        era_dist = semantic["clip"]["era_dist"]
        era_conf = float(max(era_dist.values())) if era_dist else 0.5
    else:
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

def analyze_video(path: str, media_id: str, sample_fps: float = 2.0, max_seconds: float = 60.0, semantic_engine: Optional["SemanticEngine"] = None) -> MediaFrame:
    if not _CV2_AVAILABLE:
        raise ImportError(
            "opencv-python is required for media analysis. "
            "Install with: pip install beatoven[media]"
        )

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

    # Use semantic engine if provided
    if semantic_engine is not None and _SEMANTIC_AVAILABLE:
        semantic = semantic_engine.analyze(kind="video", path=path, context={"hint": "music-control"})
    else:
        semantic = {}

    affect, conf = affect_from_features(physical_agg, semantic)
    traj = summarize_emotion_trajectory(arousal_series, valence_series)

    # Merge CLIP era if available
    if "clip" in semantic and "era_dist" in semantic["clip"]:
        era_dist = semantic["clip"]["era_dist"]
        era_conf = float(max(era_dist.values())) if era_dist else 0.5
    else:
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
