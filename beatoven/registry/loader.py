"""ABX-Runes registry loader and validator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import yaml

REQUIRED_FIELDS = {
    "id",
    "version",
    "name",
    "description",
    "inputs_schema",
    "outputs_schema",
    "capabilities",
    "determinism",
    "performance_envelope",
    "tests",
    "provenance",
    "routing",
}


@dataclass(frozen=True)
class RuneSpec:
    data: Dict[str, Any]

    @property
    def rune_id(self) -> str:
        return str(self.data.get("id"))


class RuneRegistry:
    """Registry of loaded rune manifests."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or Path(__file__).resolve().parents[1] / "runes"
        self._runes: Dict[str, RuneSpec] = {}

    def load(self) -> None:
        self._runes.clear()
        for path in sorted(self._root.glob("*.yaml")):
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            spec = RuneSpec(data=data)
            self._runes[spec.rune_id] = spec

    def list_runes(self) -> List[RuneSpec]:
        if not self._runes:
            self.load()
        return list(self._runes.values())

    def get_rune(self, rune_id: str) -> RuneSpec:
        if not self._runes:
            self.load()
        if rune_id not in self._runes:
            raise KeyError(f"Unknown rune id: {rune_id}")
        return self._runes[rune_id]

    def validate_rune(self, rune_id: str) -> List[str]:
        spec = self.get_rune(rune_id)
        errors: List[str] = []
        missing = REQUIRED_FIELDS - set(spec.data.keys())
        if missing:
            errors.append(f"Missing required fields: {sorted(missing)}")

        for key in ("inputs_schema", "outputs_schema"):
            value = spec.data.get(key)
            if not isinstance(value, str):
                errors.append(f"{key} must be a string path")
                continue
            schema_path = Path(value)
            if not schema_path.exists():
                errors.append(f"Schema path does not exist: {value}")

        return errors

    def validate_all(self) -> Dict[str, List[str]]:
        return {spec.rune_id: self.validate_rune(spec.rune_id) for spec in self.list_runes()}


def list_runes() -> List[RuneSpec]:
    registry = RuneRegistry()
    return registry.list_runes()


def get_rune(rune_id: str) -> RuneSpec:
    registry = RuneRegistry()
    return registry.get_rune(rune_id)


def validate_rune(rune_id: str) -> List[str]:
    registry = RuneRegistry()
    return registry.validate_rune(rune_id)


def validate_all() -> Dict[str, List[str]]:
    registry = RuneRegistry()
    return registry.validate_all()
