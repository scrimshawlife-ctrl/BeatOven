from __future__ import annotations
from typing import Dict, List
import math

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def compute_gsi(payload: Dict) -> Dict:
    """
    Groove Stability Index (0..1)
    onsets_ms: list of onset times in ms
    grid_ms: expected grid spacing in ms (e.g. 125ms for 1/16 at 120bpm)
    """
    onsets: List[float] = payload["onsets_ms"]
    grid: float = float(payload["grid_ms"])
    if grid <= 0 or len(onsets) < 2:
        return {"gsi": 0.0, "timing_error_ms_mean": None, "timing_error_ms_p95": None}

    # Error = distance to nearest gridline
    errs = []
    for t in onsets:
        nearest = round(t / grid) * grid
        errs.append(abs(t - nearest))

    errs_sorted = sorted(errs)
    mean = sum(errs_sorted) / len(errs_sorted)
    p95 = errs_sorted[int(0.95 * (len(errs_sorted) - 1))]

    # Convert error to score: 0 error -> 1.0, large error -> 0.0
    # scale: 1 grid = terrible
    score = 1.0 - _clamp01(mean / grid)
    return {"gsi": float(score), "timing_error_ms_mean": float(mean), "timing_error_ms_p95": float(p95)}

def compute_swr(payload: Dict) -> Dict:
    """
    Spectral Warmth Ratio = low_mid / max(high, eps)
    """
    band = payload["band_energy"]
    low_mid = float(band["low_mid"])
    high = float(band["high"])
    eps = 1e-9
    swr = low_mid / max(high, eps)
    return {"swr": float(swr)}

def compute_drs(payload: Dict) -> Dict:
    """
    Dynamic Range Score proxy.
    drs = clamp01(1 - (rms/peak))
    """
    rms = float(payload["rms"])
    peak = float(payload["peak"])
    if peak <= 0:
        return {"drs": 0.0}
    drs = 1.0 - (rms / peak)
    return {"drs": float(_clamp01(drs))}

def compute_afs(payload: Dict) -> Dict:
    """
    Archetype Fit Score via cosine similarity mapped to 0..1.
    """
    a = [float(x) for x in payload["intent_vector"]]
    b = [float(x) for x in payload["audio_vector"]]
    if len(a) != len(b) or len(a) == 0:
        return {"afs": 0.0}

    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return {"afs": 0.0}

    cos = dot / (na * nb)  # [-1, 1]
    afs = (cos + 1.0) / 2.0
    return {"afs": float(_clamp01(afs))}
