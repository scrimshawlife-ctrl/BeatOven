from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

@dataclass(frozen=True)
class BinauralSpec:
    carrier_hz: float          # e.g. 200.0
    beat_hz: float             # e.g. 6.0  (theta-ish)
    mix: float = 0.15          # 0..1
    ramp_s: float = 2.0        # fade in/out to avoid clicks
    phase_deg: float = 0.0     # phase offset
    pan: float = 0.0           # -1..1 (bias L/R if desired)

def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else float(x)

def apply_binaural(stereo: np.ndarray, sr: int, spec: BinauralSpec) -> np.ndarray:
    """
    Apply binaural beats to stereo audio.

    Args:
        stereo: shape (N,2), float32 in range [-1,1]
        sr: sample rate (Hz)
        spec: BinauralSpec with carrier, beat freq, mix, etc.

    Returns:
        stereo audio with binaural beats mixed in, shape (N,2)

    The binaural effect:
        Left channel:  sin(2π × (carrier - beat/2) × t)
        Right channel: sin(2π × (carrier + beat/2) × t)

    The brain perceives a "beat" at beat_hz due to the frequency difference.
    """
    if stereo.ndim != 2 or stereo.shape[1] != 2:
        raise ValueError("stereo must be (N,2)")

    mix = _clamp(spec.mix, 0.0, 1.0)
    if mix <= 1e-6:
        return stereo

    carrier = _clamp(spec.carrier_hz, 80.0, 1000.0)
    beat = _clamp(spec.beat_hz, 0.5, 40.0)

    n = stereo.shape[0]
    t = np.arange(n, dtype=np.float32) / float(sr)

    # Binaural: left = carrier - beat/2, right = carrier + beat/2
    wL = 2.0 * np.pi * (carrier - beat * 0.5)
    wR = 2.0 * np.pi * (carrier + beat * 0.5)

    ph = (np.deg2rad(spec.phase_deg)).astype(np.float32) if hasattr(np, "deg2rad") else (spec.phase_deg * np.pi / 180.0)
    left = np.sin(wL * t + ph).astype(np.float32)
    right = np.sin(wR * t + ph).astype(np.float32)

    # pan bias: -1 favors left, +1 favors right
    pan = _clamp(spec.pan, -1.0, 1.0)
    panL = 0.5 * (1.0 - pan)
    panR = 0.5 * (1.0 + pan)

    bb = np.stack([left * panL, right * panR], axis=1)

    # ramp envelope
    ramp = int(max(0, spec.ramp_s) * sr)
    if ramp > 0 and 2 * ramp < n:
        env = np.ones((n,), dtype=np.float32)
        up = np.linspace(0.0, 1.0, ramp, dtype=np.float32)
        dn = np.linspace(1.0, 0.0, ramp, dtype=np.float32)
        env[:ramp] = up
        env[-ramp:] = dn
        bb *= env[:, None]

    out = (1.0 - mix) * stereo + mix * bb
    # soft clip safeguard
    out = np.tanh(out).astype(np.float32)
    return out
