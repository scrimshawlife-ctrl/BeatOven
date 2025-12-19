from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Optional

from .schema import PresetBank

class PresetRegistry:
    def __init__(self, presets: Optional[Iterable[PresetBank]] = None) -> None:
        self._by_id: Dict[str, PresetBank] = {}
        if presets:
            for p in presets:
                self.add(p)

    def add(self, preset: PresetBank) -> None:
        if preset.preset_id in self._by_id:
            raise ValueError(f"Duplicate preset_id: {preset.preset_id}")
        self._by_id[preset.preset_id] = preset

    def get(self, preset_id: str) -> PresetBank:
        return self._by_id[preset_id]

    def all(self) -> List[PresetBank]:
        return list(self._by_id.values())

    def to_jsonable(self) -> List[dict]:
        return [asdict(p) for p in self.all()]
