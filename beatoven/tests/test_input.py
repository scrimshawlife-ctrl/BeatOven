"""Tests for InputModule."""

import numpy as np
import pytest
from beatoven.core.input import (
    InputModule, MoodTag, ABXRunesSeed,
    AudioStyleFeatures, SymbolicVector
)


class TestMoodTag:
    """Tests for MoodTag dataclass."""

    def test_basic_creation(self):
        tag = MoodTag(name="happy", intensity=0.8)
        assert tag.name == "happy"
        assert tag.intensity == 0.8

    def test_intensity_clamping(self):
        tag = MoodTag(name="sad", intensity=1.5)
        assert tag.intensity == 1.0

        tag = MoodTag(name="calm", intensity=-0.5)
        assert tag.intensity == 0.0


class TestABXRunesSeed:
    """Tests for ABXRunesSeed."""

    def test_seed_generation(self):
        seed = ABXRunesSeed("test_seed")
        assert seed.seed_string == "test_seed"
        assert isinstance(seed.numeric_seed, int)
        assert seed.rune_vector.shape == (64,)

    def test_determinism(self):
        seed1 = ABXRunesSeed("same_seed")
        seed2 = ABXRunesSeed("same_seed")
        assert seed1.numeric_seed == seed2.numeric_seed
        np.testing.assert_array_equal(seed1.rune_vector, seed2.rune_vector)

    def test_different_seeds(self):
        seed1 = ABXRunesSeed("seed_a")
        seed2 = ABXRunesSeed("seed_b")
        assert seed1.numeric_seed != seed2.numeric_seed


class TestAudioStyleFeatures:
    """Tests for AudioStyleFeatures."""

    def test_default_values(self):
        features = AudioStyleFeatures()
        assert features.spectral_centroid == 0.5
        assert features.tempo_estimate == 120.0
        assert features.mfcc_mean.shape == (13,)

    def test_to_vector(self):
        features = AudioStyleFeatures(
            spectral_centroid=0.6,
            tempo_estimate=140.0
        )
        vec = features.to_vector()
        assert vec.shape == (18,)  # 5 base + 13 MFCC


class TestInputModule:
    """Tests for InputModule."""

    def test_basic_process(self):
        module = InputModule()
        result = module.process("create a chill beat")

        assert isinstance(result, SymbolicVector)
        assert result.intent_embedding.shape == (128,)
        assert result.mood_vector.shape == (32,)
        assert result.rune_vector.shape == (64,)
        assert result.style_vector.shape == (18,)
        assert len(result.provenance_hash) == 64

    def test_with_mood_tags(self):
        module = InputModule()
        moods = [MoodTag("dark", 0.9), MoodTag("energetic", 0.7)]
        result = module.process("aggressive bass drop", mood_tags=moods)

        assert result.mood_vector.shape == (32,)
        # Mood vector should be influenced
        assert not np.allclose(result.mood_vector, 0)

    def test_with_seed(self):
        module = InputModule()
        seed = ABXRunesSeed("my_custom_seed")
        result = module.process("melodic phrase", abx_seed=seed)

        np.testing.assert_array_equal(result.rune_vector, seed.rune_vector)

    def test_determinism(self):
        module = InputModule()
        seed = ABXRunesSeed("determinism_test")

        result1 = module.process("test intent", abx_seed=seed)
        result2 = module.process("test intent", abx_seed=seed)

        np.testing.assert_array_equal(
            result1.intent_embedding,
            result2.intent_embedding
        )
        assert result1.provenance_hash == result2.provenance_hash

    def test_provenance_uniqueness(self):
        module = InputModule()

        result1 = module.process("intent one")
        result2 = module.process("intent two")

        assert result1.provenance_hash != result2.provenance_hash

    def test_symbolic_vector_serialization(self):
        module = InputModule()
        result = module.process("test")

        # Serialize
        data = result.to_dict()
        assert "intent_embedding" in data
        assert "provenance_hash" in data

        # Deserialize
        restored = SymbolicVector.from_dict(data)
        np.testing.assert_array_almost_equal(
            result.intent_embedding,
            restored.intent_embedding
        )
        assert result.provenance_hash == restored.provenance_hash


class TestInputDeterminism:
    """Tests for deterministic behavior."""

    def test_same_input_same_output(self):
        """Same inputs should produce identical outputs."""
        module1 = InputModule(default_seed="fixed")
        module2 = InputModule(default_seed="fixed")

        result1 = module1.process(
            "ambient pad",
            mood_tags=[MoodTag("calm", 0.8)],
            abx_seed=ABXRunesSeed("test")
        )
        result2 = module2.process(
            "ambient pad",
            mood_tags=[MoodTag("calm", 0.8)],
            abx_seed=ABXRunesSeed("test")
        )

        np.testing.assert_array_equal(
            result1.intent_embedding,
            result2.intent_embedding
        )
        np.testing.assert_array_equal(
            result1.mood_vector,
            result2.mood_vector
        )
        assert result1.provenance_hash == result2.provenance_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
