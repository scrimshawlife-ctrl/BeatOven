"""Tests for doctrine spine and intent compiler."""

from fastapi.testclient import TestClient

from beatoven.api.main import app
from beatoven.core.doctrine import IntentCompiler, IntentToken, RitualPhase


def test_intent_compiler_determinism():
    intent = IntentToken(
        text_intent="echoes of neon rain",
        mood_tags=["ambient", "ethereal"],
        seed="deterministic_seed",
    )
    compiler = IntentCompiler()

    bundle_a = compiler.compile(intent=intent, phase=RitualPhase.PREP, seed=1234)
    bundle_b = compiler.compile(intent=intent, phase=RitualPhase.PREP, seed=1234)

    assert bundle_a == bundle_b


def test_generate_smoke():
    client = TestClient(app)
    response = client.post(
        "/generate",
        json={
            "text_intent": "smoke test beat",
            "tempo": 110.0,
            "duration": 4.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
