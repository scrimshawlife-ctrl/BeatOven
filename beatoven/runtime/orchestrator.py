"""Deterministic rune orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from beatoven.registry.loader import RuneRegistry
from beatoven.runtime.capabilities import CapabilityPolicy, DEFAULT_POLICY
from beatoven.provenance.manifest import build_manifest
from beatoven.core.rhythm import RhythmEngine
from beatoven.core.harmony import HarmonicEngine, Scale
from beatoven.core.motion import MotionEngine
from beatoven.core.timbre import TimbreEngine
from beatoven.core.stems import StemGenerator, StemType


@dataclass
class RuneResult:
    output: Dict[str, Any]
    manifest: Dict[str, Any]


class Orchestrator:
    """Runes orchestrator enforcing determinism and capability policies."""

    def __init__(self) -> None:
        self._registry = RuneRegistry()
        self._rhythm = RhythmEngine()
        self._harmony = HarmonicEngine()
        self._motion = MotionEngine()
        self._timbre = TimbreEngine()
        self._stems = StemGenerator()

    def run_rune(
        self,
        rune_id: str,
        input_payload: Dict[str, Any],
        seed: int,
        capability_policy: CapabilityPolicy | None = None,
    ) -> RuneResult:
        policy = capability_policy or DEFAULT_POLICY
        spec = self._registry.get_rune(rune_id)

        output: Dict[str, Any]
        if rune_id == "engine.rhythm.generate":
            pattern, desc = self._rhythm.generate(**input_payload)
            output = {"pattern": [e.to_dict() for e in pattern.events], "description": desc.to_dict()}
        elif rune_id == "engine.harmony.generate":
            scale_name = input_payload.get("scale", "MINOR")
            try:
                scale = Scale[scale_name]
            except KeyError:
                scale = Scale.MINOR
            payload = {**input_payload, "scale": scale}
            progression, desc = self._harmony.generate(**payload)
            output = {"progression": [e.to_dict() for e in progression.events], "description": desc.to_dict()}
        elif rune_id == "engine.motion.generate":
            curves, desc = self._motion.generate(**input_payload)
            output = {"curves": {k: v.to_dict() for k, v in curves.items()}, "description": desc.to_dict()}
        elif rune_id == "engine.timbre.generate":
            output = {
                "parameters": input_payload,
                "description": {
                    "texture": input_payload.get("texture"),
                    "brightness": input_payload.get("brightness"),
                    "warmth": input_payload.get("warmth"),
                },
            }
        elif rune_id == "service.stems.generate":
            stem_types = input_payload.get("stem_types")
            stem_enum = [StemType[s] for s in stem_types] if stem_types else None
            stems = self._stems.generate_stems(
                rhythm_events=input_payload["rhythm_events"],
                harmonic_events=input_payload["harmonic_events"],
                duration=input_payload["duration"],
                stem_types=stem_enum,
            )
            output = {"stems": [s.value for s in stems.keys()]}
        else:
            raise ValueError(f"Unsupported rune id: {rune_id}")

        manifest = build_manifest(
            rune_id=rune_id,
            input_payload=input_payload,
            output_payload=output,
            seed=seed,
            capabilities={
                "filesystem": policy.filesystem_paths,
                "network": policy.network_domains,
                "clock": policy.clock_policy,
                "randomness": policy.randomness_policy,
            },
        )

        return RuneResult(output=output, manifest=manifest)
