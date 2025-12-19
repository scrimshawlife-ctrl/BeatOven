from __future__ import annotations
from typing import Optional

from beatoven.dspcoffee_bridge.schema import ResonanceFrame, ResonanceMetrics, RhythmTokens
from .schema import MediaFrame

def media_to_resonance(m: MediaFrame) -> ResonanceFrame:
    """
    Converts MediaFrame → ResonanceFrame.
    Rhythm tokens may be absent; BeatOven can later generate patterns from affect.
    """
    a = m.affect
    # Map affect → resonance metrics (deterministic)
    metrics = ResonanceMetrics(
        complexity=float(min(1.0, 0.25 + 0.5*m.physical.get("edge_density", 0.1) + 0.3*m.physical.get("luma_var", 0.1))),
        emotional_intensity=float(a.get("arousal", 0.5)),
        groove=float(min(1.0, 0.35 + 0.45*a.get("dominance", 0.5) + 0.20*(1.0 - m.physical.get("jitter", 0.0)))),
        energy=float(min(1.0, 0.40 + 0.60*a.get("arousal", 0.5))),
        density=float(min(1.0, 0.30 + 0.45*m.physical.get("edge_density", 0.1) + 0.25*m.physical.get("motion_energy", 0.0))),
        swing=float(min(1.0, 0.25 + 0.65*m.physical.get("jitter", 0.0))),  # shaky cam → swing bias (tunable)
        brightness=float(m.physical.get("luma_mean", 0.5)),
        tension=float(min(1.0, 0.20 + 0.65*a.get("dread", 0.2) + 0.15*m.physical.get("luma_var", 0.1))),
    ).clamp01()

    extras = {
        "media_kind": m.kind,
        "media_path": m.path,
        "affect": m.affect,
        "affect_conf": m.confidence.get("affect_confidence", 0.0),
        "perceived_era": m.perceived_era,
        "era_conf": m.era_confidence,
        "physical": m.physical,
        "semantic": m.semantic,
    }

    return ResonanceFrame.new(
        source="beatoven_render",
        genre=None,        # can be inferred later (or user-provided)
        subgenre=None,
        metrics=metrics,
        rhythm=None,
        extras=extras,
        beatoven_version="beatoven-media-intel-v1",
    )
