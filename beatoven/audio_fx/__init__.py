"""
BeatOven Audio FX

User-tunable audio processing stages:
- Binaural beats: Frequency entrainment with per-channel carrier offsets
- (Future) Spatial audio, reverb, harmonic enhancement

All FX are spec-driven and deterministic.
"""

from .binaural import BinauralSpec, apply_binaural

__all__ = [
    "BinauralSpec",
    "apply_binaural",
]
