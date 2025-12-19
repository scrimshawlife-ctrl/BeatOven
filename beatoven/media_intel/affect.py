from __future__ import annotations
from typing import Dict, Tuple

def affect_from_features(physical: Dict[str, float], semantic: Dict[str, object]) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Deterministic affect estimate from features.
    Replace/augment later with learned models; keep output contract stable.

    Returns:
      affect: dict (valence/arousal/dominance + blends)
      conf: dict (affect_confidence)
    """
    # Physical cues
    brightness = float(physical.get("luma_mean", 0.5))
    contrast = float(physical.get("luma_var", 0.1))
    sat = float(physical.get("sat_mean", 0.4))
    edge = float(physical.get("edge_density", 0.1))
    motion = float(physical.get("motion_energy", 0.0))

    # Core dimensions
    arousal = min(1.0, max(0.0, 0.25 + 0.35*contrast + 0.25*edge + 0.35*motion))
    valence = min(1.0, max(0.0, 0.55 + 0.30*(brightness - 0.5) + 0.15*(sat - 0.4) - 0.10*contrast))
    dominance = min(1.0, max(0.0, 0.50 + 0.25*(edge - 0.2) + 0.20*(brightness - 0.5)))

    # Blends (examples)
    awe = min(1.0, max(0.0, 0.25 + 0.50*arousal + 0.15*(1.0 - edge)))
    dread = min(1.0, max(0.0, 0.20 + 0.45*arousal + 0.35*(0.55 - valence)))
    nostalgia = min(1.0, max(0.0, 0.20 + 0.35*(0.6 - contrast) + 0.25*(0.55 - sat)))
    tenderness = min(1.0, max(0.0, 0.15 + 0.45*valence + 0.10*(1.0 - arousal)))

    affect = {
        "valence": float(valence),
        "arousal": float(arousal),
        "dominance": float(dominance),
        "awe": float(awe),
        "dread": float(dread),
        "nostalgia": float(nostalgia),
        "tenderness": float(tenderness),
    }

    # Confidence: conservative unless semantics corroborate (placeholder for now)
    # Use peakiness of blends to avoid flat "shrug" outputs.
    peak = max(affect.values()) - (sum(affect.values())/len(affect))
    conf = {"affect_confidence": float(max(0.15, min(0.75, 0.25 + 0.8*peak)))}
    return affect, conf
