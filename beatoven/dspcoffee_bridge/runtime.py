from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Optional, Tuple

from .schema import FrameDelta, MacroUpdate, OpsCommand, PresetBank, ResonanceFrame, ResonanceMetrics
from .registry import PresetRegistry
from .scoring import choose_action, score_preset_fit
from .transport_udp import UdpRealtimeLane
from .transport_serial import SerialOpsLane

def _safe01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)

def _metrics_to_macros(m: ResonanceMetrics) -> Dict[str, float]:
    """
    Default mapping. You will tune this once your dsp.coffee macro table exists.
    Kept deterministic and explicit.
    """
    m = m.clamp01()
    return {
        "complexity": m.complexity,
        "intensity": m.emotional_intensity,
        "groove": m.groove,
        "energy": m.energy,
        "density": m.density,
        "swing": m.swing,
        "brightness": m.brightness,
        "tension": m.tension,
    }

class BridgeRuntime:
    """
    Plug-in runtime: you feed it frames/deltas, it selects preset + sends messages.

    This file intentionally does NOT implement the network server layer
    (WS/HTTP). BeatOven likely already has its own bus/service framework.
    You call:
        rt.on_delta(...)
        rt.on_frame(...)
    from your existing ingestion code.
    """

    def __init__(
        self,
        presets: PresetRegistry,
        realtime_lane: UdpRealtimeLane,
        ops_lane: SerialOpsLane,
        score_thresholds: Tuple[float, float] = (0.72, 0.88),
    ) -> None:
        self.presets = presets
        self.rt = realtime_lane
        self.ops = ops_lane
        self.score_thresholds = score_thresholds

        self._cache: Optional[ResonanceFrame] = None
        self._current_preset_id: Optional[str] = None

    def _merge_delta(self, base: ResonanceFrame, d: FrameDelta) -> ResonanceFrame:
        merged = base
        if d.genre is not None:
            merged = replace(merged, genre=d.genre)
        if d.subgenre is not None:
            merged = replace(merged, subgenre=d.subgenre)
        if d.metrics is not None:
            merged = replace(merged, metrics=d.metrics)
        if d.rhythm is not None:
            merged = replace(merged, rhythm=d.rhythm)
        if d.extras is not None:
            merged = replace(merged, extras={**merged.extras, **d.extras})
        merged = replace(merged, ts_ms=d.ts_ms)
        return merged.with_provenance_hash()

    def _best_preset(self, frame: ResonanceFrame) -> Tuple[Optional[PresetBank], float]:
        best: Optional[PresetBank] = None
        best_s = 0.0
        for p in self.presets.all():
            s = score_preset_fit(frame, p)
            if s > best_s:
                best_s = s
                best = p
        return best, best_s

    def on_delta(self, delta: FrameDelta) -> None:
        if self._cache is None:
            # Convert first delta into a minimal frame; BeatOven should ideally send a full frame first.
            self._cache = ResonanceFrame.new(source="abraxas_stream", ts_ms=delta.ts_ms)
        self._cache = self._merge_delta(self._cache, delta)
        self._process(self._cache)

    def on_frame(self, frame: ResonanceFrame) -> None:
        self._cache = frame.with_provenance_hash()
        self._process(self._cache)

    def _process(self, frame: ResonanceFrame) -> None:
        best, best_score = self._best_preset(frame)
        best_id = None if best is None else best.preset_id

        action = choose_action(
            frame=frame,
            current_preset_id=self._current_preset_id,
            best_preset_id=best_id,
            best_score=best_score,
            thresholds=self.score_thresholds,
        )

        if action == "NOOP" or best is None:
            return

        if action == "SCENE_CHANGE":
            ok = self.ops.send("LOAD_PRESET", {
                "preset_id": best.preset_id,
                "patch_graph_id": best.patch_graph_id,
                "kit_id": best.kit_id,
                "quantize": best.scene_change_quantize,
                "crossfade_ms": best.crossfade_ms,
                "provenance_hash": frame.provenance_hash,
            })
            if ok:
                self._current_preset_id = best.preset_id
            return

        # Ensure we have a current preset loaded, otherwise stage it safely first.
        if self._current_preset_id != best.preset_id:
            ok = self.ops.send("STAGE_NEXT", {
                "preset_id": best.preset_id,
                "patch_graph_id": best.patch_graph_id,
                "kit_id": best.kit_id,
                "quantize": "bar",
                "crossfade_ms": best.crossfade_ms,
                "provenance_hash": frame.provenance_hash,
            })
            if ok:
                self._current_preset_id = best.preset_id

        if action == "PATTERN_INJECT" and frame.rhythm is not None:
            payload: Dict[str, Any] = {
                "preset_id": best.preset_id,
                "bpm": float(frame.rhythm.bpm),
                "meter": list(frame.rhythm.meter),
                "kick": frame.rhythm.kick,
                "snare": frame.rhythm.snare,
                "hat": frame.rhythm.hat,
                "perc": frame.rhythm.perc,
                "provenance_hash": frame.provenance_hash,
            }
            self.ops.send("COMMIT_PATTERN", payload)
            # also nudge tempo/swing realtime if present in metrics
            self.rt.send_meta("bpm", float(frame.rhythm.bpm))
            if frame.metrics is not None:
                self.rt.send_meta("swing", float(frame.metrics.swing))
            return

        # PARAM_NUDGE
        if frame.metrics is not None:
            macros = _metrics_to_macros(frame.metrics)
            # Only send macros that exist in this preset's contract (if defined)
            if best.macros:
                macros = {k: _safe01(v) for k, v in macros.items() if k in set(best.macros)}
            self.rt.send_macros(best.preset_id, macros)
