"""Tests for BeatOven API."""

import pytest
from fastapi.testclient import TestClient
from beatoven.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert len(data["engines_loaded"]) > 0


class TestGenerateEndpoint:
    """Tests for generate endpoint."""

    def test_basic_generation(self, client):
        response = client.post("/generate", json={
            "text_intent": "create a chill ambient beat",
            "tempo": 90.0,
            "duration": 8.0
        })

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "provenance_hash" in data
        assert "rhythm_descriptor" in data
        assert "harmonic_descriptor" in data

    def test_generation_with_mood_tags(self, client):
        response = client.post("/generate", json={
            "text_intent": "dark industrial beat",
            "mood_tags": ["dark", "aggressive"],
            "tempo": 130.0
        })

        assert response.status_code == 200
        data = response.json()
        assert len(data["stems_generated"]) > 0

    def test_generation_with_seed(self, client):
        response = client.post("/generate", json={
            "text_intent": "test beat",
            "seed": "my_deterministic_seed"
        })

        assert response.status_code == 200


class TestTranslateEndpoint:
    """Tests for translate endpoint."""

    def test_basic_translation(self, client):
        response = client.post("/translate", params={
            "text_intent": "melodic techno"
        })

        assert response.status_code == 200
        data = response.json()
        assert "symbolic_vector" in data
        assert "abx_fields" in data

    def test_translation_with_moods(self, client):
        response = client.post("/translate", params={
            "text_intent": "ambient pad",
            "mood_tags": ["calm", "ethereal"]
        })

        assert response.status_code == 200


class TestRhythmEndpoint:
    """Tests for rhythm endpoint."""

    def test_rhythm_generation(self, client):
        response = client.post("/rhythm", params={
            "density": 0.6,
            "tension": 0.4,
            "tempo": 120.0
        })

        assert response.status_code == 200
        data = response.json()
        assert "pattern" in data
        assert "descriptor" in data


class TestHarmonyEndpoint:
    """Tests for harmony endpoint."""

    def test_harmony_generation(self, client):
        response = client.post("/harmony", params={
            "resonance": 0.5,
            "tension": 0.5,
            "key_root": 60,
            "scale": "MINOR"
        })

        assert response.status_code == 200
        data = response.json()
        assert "progression" in data
        assert "descriptor" in data

    def test_named_progression(self, client):
        response = client.post("/harmony", params={
            "progression_type": "pop"
        })

        assert response.status_code == 200


class TestPsyFiEndpoint:
    """Tests for PsyFi modulation endpoint."""

    def test_emotional_modulation(self, client):
        response = client.post("/psyfi/modulate", json={
            "valence": 0.8,
            "arousal": 0.6,
            "dominance": 0.5
        })

        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        assert "rhythm_params" in data
        assert "harmony_params" in data


class TestPatchBayEndpoint:
    """Tests for PatchBay endpoints."""

    def test_get_flow(self, client):
        response = client.get("/patchbay/flow")
        assert response.status_code == 200

        data = response.json()
        assert "nodes" in data
        assert "connections" in data
        assert "execution_order" in data


class TestRunicEndpoint:
    """Tests for runic signature endpoint."""

    def test_runic_generation(self, client):
        response = client.post("/runic/generate", params={})
        assert response.status_code == 200

        data = response.json()
        assert "signature" in data
        assert "svg" in data

    def test_runic_with_data(self, client):
        response = client.post("/runic/generate", params={
            "spectral_data": [0.5, 0.3, 0.8],
            "emotional_data": [0.7, 0.4]
        })

        assert response.status_code == 200


class TestConfigEndpoint:
    """Tests for config endpoint."""

    def test_get_config(self, client):
        response = client.get("/config")
        assert response.status_code == 200

        data = response.json()
        assert data["version"] == "1.0.0"
        assert data["abx_core_version"] == "1.2"
        assert "engines" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
