from __future__ import annotations

from typing import Dict, Literal, Optional, Tuple

from .schema import PresetBank, ResonanceFrame

def _metric(frame: ResonanceFrame, key: str) -> Optional[float]:
    if frame.metrics is None:
        return None
    return getattr(frame.metrics, key, None)

def score_preset_fit(frame: ResonanceFrame, preset: PresetBank) -> float:
    """
    Deterministic fit score in [0,1].
    - Genre/subgenre are hard gates if set in selector.
    - Metrics contribute weighted overlap with target ranges.
    """
    sel = preset.selector

    if sel.genre and frame.genre and sel.genre.lower() != frame.genre.lower():
        return 0.0
    if sel.subgenre and frame.subgenre and sel.subgenre.lower() != frame.subgenre.lower():
        return 0.0

    if not sel.targets:
        return 0.25  # minimal neutral score if only genre gating is used

    total_w = 0.0
    accum = 0.0

    for k, (lo, hi) in sel.targets.items():
        v = _metric(frame, k)
        if v is None:
            continue
        w = float(sel.weights.get(k, 1.0))
        total_w += w

        # score: 1 if inside range; else linearly decays to 0 at distance 0.5
        if lo <= v <= hi:
            s = 1.0
        else:
            dist = min(abs(v - lo), abs(v - hi))
            s = max(0.0, 1.0 - (dist / 0.5))
        accum += w * s

    if total_w <= 0.0:
        return 0.2
    return max(0.0, min(1.0, accum / total_w))

ActionKind = Literal["PARAM_NUDGE", "SCENE_CHANGE", "PATTERN_INJECT", "NOOP"]

def choose_action(
    frame: ResonanceFrame,
    current_preset_id: Optional[str],
    best_preset_id: Optional[str],
    best_score: float,
    thresholds: Tuple[float, float] = (0.72, 0.88),
) -> ActionKind:
    """
    - If no metrics/rhythm: NOOP
    - If best score < low: NOOP
    - If preset changes and score >= high: SCENE_CHANGE
    - If rhythm tokens present: PATTERN_INJECT (unless scene change triggered)
    - Else: PARAM_NUDGE
    """
    low, high = thresholds

    if frame.metrics is None and frame.rhythm is None:
        return "NOOP"
    if best_preset_id is None or best_score < low:
        return "NOOP"

    if current_preset_id != best_preset_id and best_score >= high:
        return "SCENE_CHANGE"

    if frame.rhythm is not None and any([
        frame.rhythm.kick, frame.rhythm.snare, frame.rhythm.hat, frame.rhythm.perc
    ]):
        return "PATTERN_INJECT"

    return "PARAM_NUDGE"
