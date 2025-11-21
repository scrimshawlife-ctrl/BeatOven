"""
BeatOven PsyFi Integration Layer

Accepts emotional vectors from PsyFi and adapts parameters
across rhythm, harmony, and timbre engines.
"""

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class EmotionalDimension(Enum):
    """PsyFi emotional dimensions (Hσ model)."""
    VALENCE = "valence"  # Positive/negative
    AROUSAL = "arousal"  # Energy level
    DOMINANCE = "dominance"  # Control/power
    TENSION = "tension"  # Anxiety/calm
    DEPTH = "depth"  # Superficial/profound
    WARMTH = "warmth"  # Cold/warm
    BRIGHTNESS = "brightness"  # Dark/bright
    MOVEMENT = "movement"  # Static/dynamic


@dataclass
class EmotionalVector:
    """PsyFi Hσ emotional state vector."""
    valence: float = 0.0  # -1 to 1
    arousal: float = 0.0  # -1 to 1
    dominance: float = 0.0  # -1 to 1
    tension: float = 0.0  # -1 to 1
    depth: float = 0.0  # -1 to 1
    warmth: float = 0.0  # -1 to 1
    brightness: float = 0.0  # -1 to 1
    movement: float = 0.0  # -1 to 1

    def __post_init__(self):
        # Clamp all values
        for dim in EmotionalDimension:
            value = getattr(self, dim.value)
            setattr(self, dim.value, max(-1.0, min(1.0, value)))

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([
            self.valence, self.arousal, self.dominance, self.tension,
            self.depth, self.warmth, self.brightness, self.movement
        ], dtype=np.float32)

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "EmotionalVector":
        """Create from numpy array."""
        return cls(
            valence=float(arr[0]) if len(arr) > 0 else 0.0,
            arousal=float(arr[1]) if len(arr) > 1 else 0.0,
            dominance=float(arr[2]) if len(arr) > 2 else 0.0,
            tension=float(arr[3]) if len(arr) > 3 else 0.0,
            depth=float(arr[4]) if len(arr) > 4 else 0.0,
            warmth=float(arr[5]) if len(arr) > 5 else 0.0,
            brightness=float(arr[6]) if len(arr) > 6 else 0.0,
            movement=float(arr[7]) if len(arr) > 7 else 0.0
        )

    def to_dict(self) -> Dict[str, float]:
        return {dim.value: getattr(self, dim.value) for dim in EmotionalDimension}


@dataclass
class ParameterModulation:
    """Modulation to apply to engine parameters."""
    target_engine: str  # "rhythm", "harmony", "timbre", "motion"
    target_param: str
    modulation_amount: float
    modulation_curve: str = "linear"  # "linear", "exponential", "logarithmic"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_engine": self.target_engine,
            "target_param": self.target_param,
            "modulation_amount": self.modulation_amount,
            "modulation_curve": self.modulation_curve
        }


@dataclass
class PsyFiState:
    """Complete PsyFi integration state."""
    emotional_vector: EmotionalVector
    modulations: List[ParameterModulation] = field(default_factory=list)
    intensity: float = 1.0
    blend_mode: str = "multiply"  # "multiply", "add", "replace"
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotional_vector": self.emotional_vector.to_dict(),
            "modulations": [m.to_dict() for m in self.modulations],
            "intensity": self.intensity,
            "blend_mode": self.blend_mode,
            "provenance_hash": self.provenance_hash
        }


class PsyFiIntegration:
    """
    PsyFi integration layer for emotional modulation.

    Maps emotional vectors to musical parameters across
    all BeatOven engines.
    """

    # Emotion to parameter mappings
    EMOTION_MAPPINGS = {
        "valence": {
            "harmony": {"resonance": 0.3, "tension": -0.2},
            "timbre": {"brightness": 0.4, "warmth": 0.2},
            "rhythm": {"swing": 0.1}
        },
        "arousal": {
            "rhythm": {"density": 0.4, "tempo_mod": 0.2},
            "timbre": {"density": 0.3},
            "motion": {"lfo_rate": 0.3}
        },
        "dominance": {
            "rhythm": {"accent_strength": 0.3},
            "harmony": {"contrast": 0.2},
            "timbre": {"amplitude": 0.2}
        },
        "tension": {
            "harmony": {"tension": 0.5, "dissonance": 0.3},
            "rhythm": {"syncopation": 0.2},
            "motion": {"envelope_attack": -0.2}
        },
        "depth": {
            "timbre": {"reverb_amount": 0.4},
            "harmony": {"voicing_spread": 0.2}
        },
        "warmth": {
            "timbre": {"filter_cutoff": -0.3, "saturation": 0.2}
        },
        "brightness": {
            "timbre": {"filter_cutoff": 0.4, "harmonics": 0.3},
            "harmony": {"modal_brightness": 0.3}
        },
        "movement": {
            "motion": {"lfo_depth": 0.4, "drift": 0.3},
            "rhythm": {"variation": 0.2}
        }
    }

    def __init__(self, sensitivity: float = 1.0):
        """
        Initialize PsyFi integration.

        Args:
            sensitivity: Global sensitivity multiplier
        """
        self.sensitivity = sensitivity
        self._current_state: Optional[PsyFiState] = None

    def process_emotional_vector(
        self,
        vector: EmotionalVector,
        intensity: float = 1.0
    ) -> PsyFiState:
        """
        Process emotional vector and generate parameter modulations.

        Args:
            vector: PsyFi Hσ emotional vector
            intensity: Modulation intensity 0.0-1.0

        Returns:
            PsyFiState with computed modulations
        """
        modulations = []

        for dim in EmotionalDimension:
            dim_value = getattr(vector, dim.value)
            dim_mappings = self.EMOTION_MAPPINGS.get(dim.value, {})

            for engine, params in dim_mappings.items():
                for param, weight in params.items():
                    mod_amount = dim_value * weight * intensity * self.sensitivity
                    modulations.append(ParameterModulation(
                        target_engine=engine,
                        target_param=param,
                        modulation_amount=mod_amount
                    ))

        # Compute provenance
        provenance = self._compute_provenance(vector, intensity)

        state = PsyFiState(
            emotional_vector=vector,
            modulations=modulations,
            intensity=intensity,
            provenance_hash=provenance
        )

        self._current_state = state
        return state

    def get_rhythm_params(
        self,
        base_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Get rhythm parameters with emotional modulation."""
        return self._apply_modulations("rhythm", base_params)

    def get_harmony_params(
        self,
        base_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Get harmony parameters with emotional modulation."""
        return self._apply_modulations("harmony", base_params)

    def get_timbre_params(
        self,
        base_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Get timbre parameters with emotional modulation."""
        return self._apply_modulations("timbre", base_params)

    def get_motion_params(
        self,
        base_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Get motion parameters with emotional modulation."""
        return self._apply_modulations("motion", base_params)

    def _apply_modulations(
        self,
        engine: str,
        base_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Apply emotional modulations to base parameters."""
        if self._current_state is None:
            return base_params

        result = dict(base_params)

        for mod in self._current_state.modulations:
            if mod.target_engine != engine:
                continue

            if mod.target_param in result:
                if self._current_state.blend_mode == "multiply":
                    result[mod.target_param] *= (1 + mod.modulation_amount)
                elif self._current_state.blend_mode == "add":
                    result[mod.target_param] += mod.modulation_amount
                elif self._current_state.blend_mode == "replace":
                    result[mod.target_param] = mod.modulation_amount

                # Clamp to valid range
                result[mod.target_param] = max(0.0, min(1.0, result[mod.target_param]))

        return result

    def interpolate_vectors(
        self,
        v1: EmotionalVector,
        v2: EmotionalVector,
        t: float
    ) -> EmotionalVector:
        """Interpolate between two emotional vectors."""
        t = max(0.0, min(1.0, t))
        arr1 = v1.to_array()
        arr2 = v2.to_array()
        interpolated = arr1 * (1 - t) + arr2 * t
        return EmotionalVector.from_array(interpolated)

    def generate_emotional_curve(
        self,
        keyframes: List[Tuple[float, EmotionalVector]],
        duration: float,
        resolution: int = 100
    ) -> List[Tuple[float, EmotionalVector]]:
        """Generate emotional curve from keyframes."""
        if not keyframes:
            neutral = EmotionalVector()
            return [(t * duration / resolution, neutral) for t in range(resolution)]

        keyframes = sorted(keyframes, key=lambda x: x[0])
        curve = []

        for i in range(resolution):
            t = i * duration / resolution

            # Find surrounding keyframes
            prev_kf = keyframes[0]
            next_kf = keyframes[-1]

            for j, kf in enumerate(keyframes):
                if kf[0] <= t:
                    prev_kf = kf
                if kf[0] >= t and j > 0:
                    next_kf = kf
                    break

            # Interpolate
            if prev_kf[0] == next_kf[0]:
                vector = prev_kf[1]
            else:
                local_t = (t - prev_kf[0]) / (next_kf[0] - prev_kf[0])
                vector = self.interpolate_vectors(prev_kf[1], next_kf[1], local_t)

            curve.append((t, vector))

        return curve

    def _compute_provenance(
        self,
        vector: EmotionalVector,
        intensity: float
    ) -> str:
        """Compute provenance hash."""
        data = f"{vector.to_array().tobytes().hex()}:{intensity}:{self.sensitivity}"
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def from_mood_tags(tags: List[str]) -> EmotionalVector:
        """Convert mood tags to emotional vector."""
        # Mood to emotion mappings
        mappings = {
            "happy": {"valence": 0.8, "arousal": 0.4, "brightness": 0.6},
            "sad": {"valence": -0.7, "arousal": -0.3, "warmth": 0.2},
            "angry": {"valence": -0.5, "arousal": 0.8, "dominance": 0.7},
            "calm": {"valence": 0.3, "arousal": -0.6, "tension": -0.7},
            "energetic": {"arousal": 0.9, "movement": 0.8, "brightness": 0.5},
            "dark": {"valence": -0.3, "brightness": -0.8, "depth": 0.5},
            "ethereal": {"depth": 0.8, "brightness": 0.4, "movement": 0.3},
            "aggressive": {"arousal": 0.9, "dominance": 0.8, "tension": 0.7},
            "peaceful": {"tension": -0.8, "warmth": 0.5, "movement": -0.4},
            "mysterious": {"depth": 0.6, "tension": 0.3, "brightness": -0.3}
        }

        result = {dim.value: 0.0 for dim in EmotionalDimension}

        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in mappings:
                for dim, value in mappings[tag_lower].items():
                    result[dim] += value

        # Normalize
        for dim in result:
            result[dim] = max(-1.0, min(1.0, result[dim]))

        return EmotionalVector(**result)


__all__ = [
    "PsyFiIntegration", "EmotionalVector", "EmotionalDimension",
    "PsyFiState", "ParameterModulation"
]
