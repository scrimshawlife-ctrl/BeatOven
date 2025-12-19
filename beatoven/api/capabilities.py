"""
BeatOven Capabilities API

System-wide capabilities reporting endpoint.

Reports ALL available features with honest availability status:
- Available: feature is ready to use
- Disabled: feature installed but disabled (with reason)
- Unavailable: missing dependencies (with install instructions)

UI uses this to show all options, graying out unavailable ones with reasons.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class FeatureCapability(BaseModel):
    """Single feature capability."""
    feature_id: str
    name: str
    available: bool
    reason: Optional[str] = None  # Why unavailable/disabled
    install_hint: Optional[str] = None  # How to enable
    version: Optional[str] = None


class CapabilitiesResponse(BaseModel):
    """System-wide capabilities response."""
    version: str
    features: List[FeatureCapability]
    available_count: int
    unavailable_count: int


def get_capabilities() -> CapabilitiesResponse:
    """
    Get system-wide capabilities.

    Returns comprehensive list of ALL features, showing what's available,
    what's disabled, and what's missing.
    """
    features = []

    # Core features (always available)
    features.append(FeatureCapability(
        feature_id="core.rhythm",
        name="Rhythm Generation",
        available=True,
        version="1.0.0"
    ))

    features.append(FeatureCapability(
        feature_id="core.harmony",
        name="Harmonic Progression",
        available=True,
        version="1.0.0"
    ))

    features.append(FeatureCapability(
        feature_id="core.timbre",
        name="Timbre Synthesis",
        available=True,
        version="1.0.0"
    ))

    features.append(FeatureCapability(
        feature_id="core.drums",
        name="Equipment-Aware Drums",
        available=True,
        version="1.0.0"
    ))

    # Hardware bridge
    try:
        import cbor2
        import serial
        features.append(FeatureCapability(
            feature_id="hardware.dspcoffee",
            name="dsp.coffee Hardware Bridge",
            available=True,
            version="1.0.0"
        ))
    except ImportError:
        features.append(FeatureCapability(
            feature_id="hardware.dspcoffee",
            name="dsp.coffee Hardware Bridge",
            available=False,
            reason="Missing dependencies: pyserial, cbor2",
            install_hint="pip install beatoven[hardware]"
        ))

    # Media intelligence (basic)
    try:
        import cv2
        features.append(FeatureCapability(
            feature_id="media.basic",
            name="Media Intelligence (Basic CV)",
            available=True,
            version="1.0.0"
        ))
    except ImportError:
        features.append(FeatureCapability(
            feature_id="media.basic",
            name="Media Intelligence (Basic CV)",
            available=False,
            reason="Missing opencv-python",
            install_hint="pip install beatoven[media]"
        ))

    # Media intelligence (semantic)
    try:
        import transformers
        import torch
        features.append(FeatureCapability(
            feature_id="media.semantic.clip",
            name="CLIP Scene Analysis",
            available=True,
            version="1.0.0"
        ))
    except ImportError:
        features.append(FeatureCapability(
            feature_id="media.semantic.clip",
            name="CLIP Scene Analysis",
            available=False,
            reason="Missing transformers, torch",
            install_hint="pip install transformers torch pillow"
        ))

    # Audio FX
    features.append(FeatureCapability(
        feature_id="fx.binaural",
        name="Binaural Audio FX",
        available=True,
        version="1.0.0"
    ))

    # Signals intake
    try:
        import feedparser
        import requests
        features.append(FeatureCapability(
            feature_id="signals.feeds",
            name="RSS/Feed Signal Intake",
            available=True,
            version="1.0.0"
        ))
    except ImportError:
        features.append(FeatureCapability(
            feature_id="signals.feeds",
            name="RSS/Feed Signal Intake",
            available=False,
            reason="Missing feedparser or requests",
            install_hint="Already in core dependencies (should be installed)"
        ))

    # Stem extraction
    features.append(FeatureCapability(
        feature_id="audio.stems",
        name="Audio Stem Extraction",
        available=True,
        version="1.0.0"
    ))

    # Ringtone generation
    features.append(FeatureCapability(
        feature_id="mobile.ringtones",
        name="Ringtone Generation",
        available=True,
        version="1.0.0"
    ))

    # Count
    available_count = sum(1 for f in features if f.available)
    unavailable_count = len(features) - available_count

    return CapabilitiesResponse(
        version="1.0.0",
        features=features,
        available_count=available_count,
        unavailable_count=unavailable_count
    )


__all__ = ["get_capabilities", "CapabilitiesResponse", "FeatureCapability"]
