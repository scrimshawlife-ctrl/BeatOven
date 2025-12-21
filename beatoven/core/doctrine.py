"""
Doctrine spine for BeatOven (PR1).

This module introduces IntentToken -> ParamBundle compilation while keeping
existing generation behavior intact. Ritual phases are represented as types
only; phase enforcement is out of scope for PR1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
import hashlib


class RitualPhase(str, Enum):
    """Ritual phases for future enforcement (PR2)."""

    PREP = "prep"
    THRESHOLD = "threshold"
    PEAK = "peak"
    RELEASE = "release"
    SEAL = "seal"


@dataclass(frozen=True)
class IntentToken:
    """
    Compressed intent symbol.

    Intent enters the system as a minimal, typed, serializable token.
    """

    text_intent: str
    mood_tags: List[str] = field(default_factory=list)
    seed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize intent to a dictionary."""
        return {
            "text_intent": self.text_intent,
            "mood_tags": list(self.mood_tags),
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentToken":
        """Deserialize intent from a dictionary."""
        return cls(
            text_intent=data["text_intent"],
            mood_tags=list(data.get("mood_tags", [])),
            seed=data.get("seed"),
        )


@dataclass(frozen=True)
class RitualPlan:
    """
    Ritual plan stub (PR1).

    Phase enforcement is added in PR2. This provides a default plan shell.
    """

    phases: List[RitualPhase] = field(
        default_factory=lambda: [
            RitualPhase.PREP,
            RitualPhase.THRESHOLD,
            RitualPhase.PEAK,
            RitualPhase.RELEASE,
            RitualPhase.SEAL,
        ]
    )


@dataclass(frozen=True)
class ParamBundle:
    """Canonical parameters passed downstream after intent compilation."""

    intent: IntentToken
    phase: RitualPhase
    seed: int
    seed_string: str
    tempo: float
    duration: float
    key_root: int
    scale: str
    resonance: float
    density: float
    tension: float
    drift: float
    contrast: float

    def to_dict(self) -> Dict[str, Any]:
        """Serialize bundle to a dictionary."""
        return {
            "intent": self.intent.to_dict(),
            "phase": self.phase.value,
            "seed": self.seed,
            "seed_string": self.seed_string,
            "tempo": self.tempo,
            "duration": self.duration,
            "key_root": self.key_root,
            "scale": self.scale,
            "resonance": self.resonance,
            "density": self.density,
            "tension": self.tension,
            "drift": self.drift,
            "contrast": self.contrast,
        }


class Compiler(Protocol):
    """Protocol for intent compilers."""

    def compile(
        self,
        intent: IntentToken,
        phase: RitualPhase,
        seed: int,
        memory: Optional[Any] = None,
    ) -> ParamBundle:
        """Compile intent into a ParamBundle."""


def derive_seed_string(text_intent: str) -> str:
    """Deterministically derive a seed string from intent text."""
    digest = hashlib.sha256(text_intent.encode()).hexdigest()[:16]
    return f"beatoven_{digest}"


def derive_seed_int(seed_string: str) -> int:
    """Deterministically derive a numeric seed from seed string."""
    digest = hashlib.sha256(seed_string.encode()).digest()
    return int.from_bytes(digest[:8], "big")


def to_legacy_params(bundle: ParamBundle) -> Dict[str, Any]:
    """Adapter for legacy generation call signatures."""
    return {
        "text_intent": bundle.intent.text_intent,
        "mood_tags": bundle.intent.mood_tags,
        "seed": bundle.seed_string,
        "tempo": bundle.tempo,
        "duration": bundle.duration,
        "key_root": bundle.key_root,
        "scale": bundle.scale,
        "resonance": bundle.resonance,
        "density": bundle.density,
        "tension": bundle.tension,
        "drift": bundle.drift,
        "contrast": bundle.contrast,
    }


class IntentCompiler:
    """Deterministic compiler from IntentToken to ParamBundle (PR1)."""

    DEFAULTS = {
        "tempo": 120.0,
        "duration": 16.0,
        "key_root": 60,
        "scale": "MINOR",
        "resonance": 0.5,
        "density": 0.5,
        "tension": 0.5,
        "drift": 0.3,
        "contrast": 0.5,
    }

    def __init__(self, compat_mode: bool = True):
        self.compat_mode = compat_mode

    def compile(
        self,
        intent: IntentToken,
        phase: RitualPhase,
        seed: int,
        memory: Optional[Any] = None,
    ) -> ParamBundle:
        """
        Compile intent into a ParamBundle.

        Deterministic given (intent, phase, seed). If memory is provided as a
        dict, its values are used as legacy overrides in compat mode.
        """
        overrides: Dict[str, Any] = memory if isinstance(memory, dict) else {}
        seed_string = intent.seed or derive_seed_string(intent.text_intent)

        def pick(name: str) -> Any:
            if self.compat_mode and name in overrides:
                return overrides[name]
            return self.DEFAULTS[name]

        return ParamBundle(
            intent=intent,
            phase=phase,
            seed=seed,
            seed_string=seed_string,
            tempo=float(pick("tempo")),
            duration=float(pick("duration")),
            key_root=int(pick("key_root")),
            scale=str(pick("scale")),
            resonance=float(pick("resonance")),
            density=float(pick("density")),
            tension=float(pick("tension")),
            drift=float(pick("drift")),
            contrast=float(pick("contrast")),
        )
