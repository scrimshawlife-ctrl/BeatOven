"""
BeatOven Input Module

Handles text intent, mood tags, ABX-Runes seed, and optional audio-style extraction.
Normalizes all inputs into symbolic vectors for downstream processing.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class MoodTag:
    """Represents a mood tag with intensity."""
    name: str
    intensity: float = 1.0  # 0.0 to 1.0

    def __post_init__(self):
        self.intensity = max(0.0, min(1.0, self.intensity))


@dataclass
class ABXRunesSeed:
    """ABX-Runes seed for deterministic generation."""
    seed_string: str
    numeric_seed: int = field(init=False)
    rune_vector: np.ndarray = field(init=False)

    def __post_init__(self):
        # Derive numeric seed from string hash
        hash_bytes = hashlib.sha256(self.seed_string.encode()).digest()
        self.numeric_seed = int.from_bytes(hash_bytes[:8], 'big')
        # Generate 64-dimensional rune vector from seed
        rng = np.random.default_rng(self.numeric_seed)
        self.rune_vector = rng.uniform(-1.0, 1.0, 64).astype(np.float32)


@dataclass
class AudioStyleFeatures:
    """Extracted audio style features from reference audio."""
    spectral_centroid: float = 0.5
    spectral_rolloff: float = 0.5
    tempo_estimate: float = 120.0
    rms_energy: float = 0.5
    zero_crossing_rate: float = 0.1
    mfcc_mean: np.ndarray = field(default_factory=lambda: np.zeros(13, dtype=np.float32))

    def to_vector(self) -> np.ndarray:
        """Convert to normalized feature vector."""
        base = np.array([
            self.spectral_centroid,
            self.spectral_rolloff,
            self.tempo_estimate / 200.0,  # Normalize tempo
            self.rms_energy,
            self.zero_crossing_rate
        ], dtype=np.float32)
        return np.concatenate([base, self.mfcc_mean])


@dataclass
class SymbolicVector:
    """Normalized symbolic vector output from input processing."""
    intent_embedding: np.ndarray  # 128-dim intent vector
    mood_vector: np.ndarray  # 32-dim mood vector
    rune_vector: np.ndarray  # 64-dim rune vector
    style_vector: np.ndarray  # 18-dim style vector
    provenance_hash: str  # SHA-256 of all inputs

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "intent_embedding": self.intent_embedding.tolist(),
            "mood_vector": self.mood_vector.tolist(),
            "rune_vector": self.rune_vector.tolist(),
            "style_vector": self.style_vector.tolist(),
            "provenance_hash": self.provenance_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolicVector":
        """Deserialize from dictionary."""
        return cls(
            intent_embedding=np.array(data["intent_embedding"], dtype=np.float32),
            mood_vector=np.array(data["mood_vector"], dtype=np.float32),
            style_vector=np.array(data["style_vector"], dtype=np.float32),
            rune_vector=np.array(data["rune_vector"], dtype=np.float32),
            provenance_hash=data["provenance_hash"]
        )


class InputModule:
    """
    BeatOven Input Module

    Processes text intent, mood tags, ABX-Runes seed, and optional audio
    style extraction into a normalized symbolic vector.
    """

    # Predefined mood vocabulary for consistent encoding
    MOOD_VOCABULARY = [
        "aggressive", "ambient", "anxious", "calm", "chaotic",
        "dark", "dreamy", "energetic", "ethereal", "euphoric",
        "haunting", "hopeful", "intense", "melancholic", "mysterious",
        "nostalgic", "peaceful", "playful", "powerful", "romantic",
        "sad", "serene", "sinister", "solemn", "spiritual",
        "suspenseful", "tender", "tense", "tranquil", "triumphant",
        "uplifting", "warm"
    ]

    # Intent keywords for basic embedding
    INTENT_KEYWORDS = [
        "beat", "melody", "bass", "pad", "lead", "arp", "chord",
        "ambient", "rhythm", "groove", "texture", "atmosphere",
        "build", "drop", "break", "intro", "outro", "verse", "chorus",
        "bridge", "fill", "transition", "loop", "one-shot", "evolving"
    ]

    def __init__(self, default_seed: str = "beatoven_default"):
        """Initialize InputModule with optional default seed."""
        self.default_seed = default_seed
        self._rng = np.random.default_rng(42)  # For deterministic fallbacks

    def process(
        self,
        text_intent: str,
        mood_tags: Optional[List[MoodTag]] = None,
        abx_seed: Optional[ABXRunesSeed] = None,
        audio_features: Optional[AudioStyleFeatures] = None
    ) -> SymbolicVector:
        """
        Process all inputs into a normalized symbolic vector.

        Args:
            text_intent: Natural language description of desired output
            mood_tags: List of mood tags with intensities
            abx_seed: ABX-Runes seed for determinism
            audio_features: Optional extracted audio style features

        Returns:
            SymbolicVector containing all normalized embeddings
        """
        # Use default seed if none provided
        if abx_seed is None:
            abx_seed = ABXRunesSeed(self.default_seed)

        # Initialize RNG from seed for determinism
        rng = np.random.default_rng(abx_seed.numeric_seed)

        # Generate intent embedding
        intent_embedding = self._encode_intent(text_intent, rng)

        # Generate mood vector
        mood_vector = self._encode_moods(mood_tags or [], rng)

        # Get rune vector from seed
        rune_vector = abx_seed.rune_vector.copy()

        # Generate style vector
        if audio_features is not None:
            style_vector = audio_features.to_vector()
        else:
            style_vector = self._default_style_vector(rng)

        # Compute provenance hash
        provenance_hash = self._compute_provenance(
            text_intent, mood_tags, abx_seed, audio_features
        )

        return SymbolicVector(
            intent_embedding=intent_embedding,
            mood_vector=mood_vector,
            rune_vector=rune_vector,
            style_vector=style_vector,
            provenance_hash=provenance_hash
        )

    def _encode_intent(self, text: str, rng: np.random.Generator) -> np.ndarray:
        """Encode text intent into 128-dim vector."""
        text_lower = text.lower()

        # Keyword-based encoding
        keyword_activations = np.zeros(len(self.INTENT_KEYWORDS), dtype=np.float32)
        for i, keyword in enumerate(self.INTENT_KEYWORDS):
            if keyword in text_lower:
                keyword_activations[i] = 1.0

        # Expand to 128 dimensions with deterministic projection
        projection = rng.standard_normal((len(self.INTENT_KEYWORDS), 128)).astype(np.float32)
        embedding = np.tanh(keyword_activations @ projection / 5.0)

        # Add text hash influence for uniqueness
        text_hash = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        hash_rng = np.random.default_rng(text_hash)
        hash_noise = hash_rng.uniform(-0.1, 0.1, 128).astype(np.float32)

        return embedding + hash_noise

    def _encode_moods(self, moods: List[MoodTag], rng: np.random.Generator) -> np.ndarray:
        """Encode mood tags into 32-dim vector."""
        mood_activations = np.zeros(len(self.MOOD_VOCABULARY), dtype=np.float32)

        for mood in moods:
            mood_name = mood.name.lower()
            if mood_name in self.MOOD_VOCABULARY:
                idx = self.MOOD_VOCABULARY.index(mood_name)
                mood_activations[idx] = mood.intensity

        # Project to 32 dimensions
        projection = rng.standard_normal((len(self.MOOD_VOCABULARY), 32)).astype(np.float32)
        return np.tanh(mood_activations @ projection / 4.0)

    def _default_style_vector(self, rng: np.random.Generator) -> np.ndarray:
        """Generate default style vector when no audio reference provided."""
        return AudioStyleFeatures().to_vector()

    def _compute_provenance(
        self,
        text_intent: str,
        mood_tags: Optional[List[MoodTag]],
        abx_seed: ABXRunesSeed,
        audio_features: Optional[AudioStyleFeatures]
    ) -> str:
        """Compute SHA-256 provenance hash of all inputs."""
        data = {
            "text_intent": text_intent,
            "mood_tags": [(m.name, m.intensity) for m in (mood_tags or [])],
            "abx_seed": abx_seed.seed_string,
            "has_audio_features": audio_features is not None
        }
        if audio_features:
            data["audio_features"] = {
                "spectral_centroid": audio_features.spectral_centroid,
                "spectral_rolloff": audio_features.spectral_rolloff,
                "tempo_estimate": audio_features.tempo_estimate,
                "rms_energy": audio_features.rms_energy,
                "zero_crossing_rate": audio_features.zero_crossing_rate
            }

        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def extract_audio_style(self, audio_path: str) -> AudioStyleFeatures:
        """
        Extract style features from reference audio file.

        Note: Full implementation requires librosa or similar library.
        This provides a deterministic fallback based on filename hash.
        """
        # Deterministic feature extraction based on filename
        file_hash = int(hashlib.md5(audio_path.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(file_hash)

        return AudioStyleFeatures(
            spectral_centroid=rng.uniform(0.3, 0.7),
            spectral_rolloff=rng.uniform(0.4, 0.8),
            tempo_estimate=rng.uniform(80.0, 160.0),
            rms_energy=rng.uniform(0.3, 0.7),
            zero_crossing_rate=rng.uniform(0.05, 0.2),
            mfcc_mean=rng.uniform(-1.0, 1.0, 13).astype(np.float32)
        )


__all__ = [
    "InputModule",
    "MoodTag",
    "ABXRunesSeed",
    "AudioStyleFeatures",
    "SymbolicVector"
]
