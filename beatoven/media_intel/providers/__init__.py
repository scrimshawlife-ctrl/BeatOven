"""
Semantic Providers: Hot-swappable analyzers with availability reporting

Each provider:
- Reports availability (installed libs, model weights)
- Analyzes media when available
- Returns structured semantic data
- Gracefully degrades if dependencies missing

Providers:
- CLIP: Scene/object tags, era inference, aesthetic scores
- Action: Video action recognition (torchvision R3D)
- AudioMood: Tempo, energy, brightness from audio tracks
- Speech: (Future) Speech detection, transcription, sentiment
"""

from .base import MediaKind, ProviderStatus, SemanticProvider

__all__ = [
    "MediaKind",
    "ProviderStatus",
    "SemanticProvider",
]
