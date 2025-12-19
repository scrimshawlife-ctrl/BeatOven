from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .semantic_engine import SemanticEngine

@dataclass(frozen=True)
class BeatOvenCapabilities:
    semantic: Dict[str, Any]
    binaural: Dict[str, Any]

def compute_capabilities(sem: SemanticEngine) -> BeatOvenCapabilities:
    """
    Always show controls; report install/availability truthfully.
    UI can render all options and gray out unavailable ones with reasons.
    """
    binaural = {
        "available": True,
        "modes": ["render_fx", "stream_fx"],
        "params": ["carrier_hz", "beat_hz", "mix", "ramp_s", "phase_deg", "pan", "automation"],
        "safety": {
            "min_carrier_hz": 80.0,
            "max_carrier_hz": 1000.0,
            "min_beat_hz": 0.5,
            "max_beat_hz": 40.0,
            "min_mix": 0.0,
            "max_mix": 1.0,
        }
    }
    return BeatOvenCapabilities(semantic=sem.capabilities(), binaural=binaural)
