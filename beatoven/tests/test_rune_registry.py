"""Tests for rune registry and validation."""

from beatoven.registry.loader import RuneRegistry


def test_registry_loads_runes():
    registry = RuneRegistry()
    registry.load()
    runes = registry.list_runes()
    assert runes, "Expected rune manifests to load"


def test_registry_validation():
    registry = RuneRegistry()
    registry.load()
    results = registry.validate_all()
    assert all(not errors for errors in results.values()), f"Validation errors: {results}"
