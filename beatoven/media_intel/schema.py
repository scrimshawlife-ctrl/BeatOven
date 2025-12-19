from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

MediaKind = Literal["image", "video"]

@dataclass(frozen=True)
class MediaFrame:
    media_id: str
    kind: MediaKind
    path: str

    # Temporal
    duration_s: Optional[float] = None          # video
    perceived_era: Optional[Dict[str, float]] = None  # {"1990s":0.3,"2000s":0.5,...}
    era_confidence: float = 0.0

    # Features (explainable)
    physical: Dict[str, Any] = field(default_factory=dict)
    semantic: Dict[str, Any] = field(default_factory=dict)
    affect: Dict[str, float] = field(default_factory=dict)  # valence/arousal/dominance + blends
    confidence: Dict[str, float] = field(default_factory=dict)

    # Provenance
    model_versions: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
