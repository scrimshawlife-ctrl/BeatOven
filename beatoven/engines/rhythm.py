"""Pure rhythm engine wrapper."""

from __future__ import annotations

from typing import Tuple
from beatoven.core.rhythm import RhythmEngine, RhythmPattern, RhythmDescription


class RhythmEnginePure:
    """Stateless wrapper to enforce explicit seeds."""

    def __init__(self, seed: int) -> None:
        self._engine = RhythmEngine(seed=seed)

    def generate(
        self,
        density: float,
        tension: float,
        drift: float,
        tempo: float,
        length_bars: int,
    ) -> Tuple[RhythmPattern, RhythmDescription]:
        return self._engine.generate(
            density=density,
            tension=tension,
            drift=drift,
            tempo=tempo,
            length_bars=length_bars,
        )
