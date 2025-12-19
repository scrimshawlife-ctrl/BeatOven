"""
BeatOven Media Intelligence

Analyzes images and videos to extract ResonanceFrames for driving dsp.coffee presets.

Architecture:
- Physical features: color, texture, composition, motion (deterministic, explainable)
- Semantic features: objects, scenes, actions, audio (optional, upgradeable)
- Affect models: valence/arousal/dominance + emotion blends
- Temporal awareness: trajectory analysis + era inference

Pipeline:
  Media (image/video) → MediaFrame → ResonanceFrame → dsp.coffee bridge

Design principles:
- Deterministic and explainable
- Confidence tracking at all levels
- Stable contracts, upgradeable models
- Conservative estimates that can be calibrated

Usage:
    from beatoven.media_intel import analyze_image, analyze_video, media_to_resonance

    # Analyze media
    media_frame = analyze_image("photo.jpg", media_id="img_001")

    # Convert to ResonanceFrame
    resonance_frame = media_to_resonance(media_frame)

    # Feed to bridge
    bridge_runtime.on_frame(resonance_frame)
"""

from .schema import MediaFrame
from .analyzer import analyze_image, analyze_video
from .to_resonance import media_to_resonance

__all__ = [
    "MediaFrame",
    "analyze_image",
    "analyze_video",
    "media_to_resonance",
]
