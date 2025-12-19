from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .base import MediaKind, ProviderStatus, SemanticProvider

@dataclass
class AudioMoodProvider(SemanticProvider):
    """
    Audio-derived mood + tempo-ish features (for videos with sound, or uploaded audio).
    Requires: librosa, numpy, soundfile
    """
    name: str = "audio_mood"

    def status(self) -> ProviderStatus:
        try:
            import librosa  # noqa
            import soundfile  # noqa
            import numpy  # noqa
            return ProviderStatus(name=self.name, available=True, version="librosa-basic")
        except Exception as e:
            return ProviderStatus(name=self.name, available=False, reason=str(e))

    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # If kind is video, you'll typically extract audio to a temp wav before calling this.
        # The UI can make that explicit.
        import librosa
        import numpy as np

        y, sr = librosa.load(path, sr=None, mono=True)
        if y.size < sr * 0.5:
            return {}

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        rms = float(np.sqrt(np.mean(y**2)))
        centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

        # Simple normalized proxies (not "truth", but useful control signals)
        energy = float(min(1.0, rms * 10.0))
        brightness = float(min(1.0, centroid / 4000.0))
        percussive = float(min(1.0, zcr * 5.0))

        return {
            "tempo_bpm": float(tempo),
            "rms": rms,
            "centroid": centroid,
            "rolloff": rolloff,
            "zcr": zcr,
            "energy_proxy": energy,
            "brightness_proxy": brightness,
            "percussive_proxy": percussive,
        }
