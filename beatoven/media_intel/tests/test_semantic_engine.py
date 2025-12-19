import pytest
from beatoven.media_intel.semantic_engine import SemanticEngine
from beatoven.media_intel.providers.base import ProviderStatus, SemanticProvider
from typing import Any, Dict, Optional


class MockProvider(SemanticProvider):
    """Mock provider for testing"""
    name = "mock"

    def __init__(self, available: bool = True):
        self._available = available

    def status(self) -> ProviderStatus:
        return ProviderStatus(
            name=self.name,
            available=self._available,
            reason=None if self._available else "mock unavailable",
            version="mock-v1" if self._available else None,
        )

    def analyze(self, *, kind: str, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"mock_result": "test_value"}


def test_semantic_engine_empty():
    """Test empty semantic engine"""
    engine = SemanticEngine(providers=[])
    caps = engine.capabilities()

    assert caps["providers"] == []
    assert caps["available"] == []
    assert caps["unavailable"] == []


def test_semantic_engine_available_provider():
    """Test engine with available provider"""
    provider = MockProvider(available=True)
    engine = SemanticEngine(providers=[provider])

    caps = engine.capabilities()
    assert len(caps["providers"]) == 1
    assert "mock" in caps["available"]
    assert len(caps["unavailable"]) == 0


def test_semantic_engine_unavailable_provider():
    """Test engine with unavailable provider"""
    provider = MockProvider(available=False)
    engine = SemanticEngine(providers=[provider])

    caps = engine.capabilities()
    assert len(caps["providers"]) == 1
    assert "mock" not in caps["available"]
    assert len(caps["unavailable"]) == 1
    assert caps["unavailable"][0]["name"] == "mock"
    assert caps["unavailable"][0]["reason"] == "mock unavailable"


def test_semantic_engine_analyze():
    """Test analysis with available provider"""
    provider = MockProvider(available=True)
    engine = SemanticEngine(providers=[provider])

    result = engine.analyze(kind="image", path="/fake/path.jpg")

    assert "mock" in result
    assert result["mock"]["mock_result"] == "test_value"


def test_semantic_engine_skip_unavailable():
    """Test that unavailable providers are skipped"""
    available = MockProvider(available=True)
    available.name = "available"
    unavailable = MockProvider(available=False)
    unavailable.name = "unavailable"

    engine = SemanticEngine(providers=[available, unavailable])

    result = engine.analyze(kind="image", path="/fake/path.jpg")

    assert "available" in result
    assert "unavailable" not in result
