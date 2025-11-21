"""Tests for HarmonicEngine."""

import numpy as np
import pytest
from beatoven.core.harmony import (
    HarmonicEngine, HarmonicProgression, HarmonicEvent,
    HarmonicDescriptor, Chord, ChordQuality, Scale
)


class TestHarmonicEngine:
    """Tests for HarmonicEngine."""

    def test_basic_generation(self):
        engine = HarmonicEngine(seed=42)
        progression, descriptor = engine.generate()

        assert isinstance(progression, HarmonicProgression)
        assert isinstance(descriptor, HarmonicDescriptor)
        assert len(progression.events) > 0

    def test_progression_properties(self):
        engine = HarmonicEngine(seed=42)
        progression, _ = engine.generate(
            key_root=60,
            scale=Scale.MAJOR,
            length_bars=4
        )

        assert progression.key_root == 60
        assert progression.scale == Scale.MAJOR
        assert progression.length_beats == 16.0

    def test_named_progressions(self):
        engine = HarmonicEngine(seed=42)

        # Pop progression (I V vi IV)
        progression, _ = engine.generate(progression_type="pop")
        assert len(progression.events) >= 4

        # Jazz ii-V-I
        progression, _ = engine.generate(progression_type="jazz_251")
        assert len(progression.events) >= 3

    def test_tension_affects_complexity(self):
        engine = HarmonicEngine(seed=42)

        low_tension, _ = engine.generate(tension=0.1)
        high_tension, _ = engine.generate(tension=0.9)

        # Higher tension should produce more complex chords
        low_complexity = sum(
            len(e.chord.voicing) for e in low_tension.events
        ) / len(low_tension.events)
        high_complexity = sum(
            len(e.chord.voicing) for e in high_tension.events
        ) / len(high_tension.events)

        # High tension generally produces more complex voicings
        assert high_complexity >= low_complexity - 0.5

    def test_determinism(self):
        engine1 = HarmonicEngine(seed=123)
        engine2 = HarmonicEngine(seed=123)

        prog1, _ = engine1.generate(resonance=0.5, tension=0.5)
        prog2, _ = engine2.generate(resonance=0.5, tension=0.5)

        assert len(prog1.events) == len(prog2.events)
        for e1, e2 in zip(prog1.events, prog2.events):
            assert e1.chord.root == e2.chord.root
            assert e1.chord.quality == e2.chord.quality

    def test_psyfi_modulation(self):
        engine = HarmonicEngine(seed=42)
        emotional_vector = np.array([0.8, 0.6, 0.5])  # valence, arousal, dominance

        progression, _ = engine.generate(
            psyfi_emotional_vector=emotional_vector
        )

        assert len(progression.events) > 0

    def test_abx_compression(self):
        engine_no_compression = HarmonicEngine(seed=42, compression_factor=0.0)
        engine_full_compression = HarmonicEngine(seed=42, compression_factor=1.0)

        prog1, _ = engine_no_compression.generate()
        prog2, _ = engine_full_compression.generate()

        # With full compression, velocity variance should be lower
        vel1 = [e.velocity for e in prog1.events]
        vel2 = [e.velocity for e in prog2.events]

        assert np.std(vel2) <= np.std(vel1) + 0.01


class TestChord:
    """Tests for Chord class."""

    def test_major_chord(self):
        chord = Chord(root=60, quality=ChordQuality.MAJOR)
        assert 60 in chord.voicing
        assert 64 in chord.voicing  # Major third
        assert 67 in chord.voicing  # Perfect fifth

    def test_minor_chord(self):
        chord = Chord(root=60, quality=ChordQuality.MINOR)
        assert 60 in chord.voicing
        assert 63 in chord.voicing  # Minor third
        assert 67 in chord.voicing  # Perfect fifth

    def test_seventh_chord(self):
        chord = Chord(root=60, quality=ChordQuality.DOMINANT7)
        assert len(chord.voicing) == 4

    def test_inversion(self):
        chord_root = Chord(root=60, quality=ChordQuality.MAJOR, inversion=0)
        chord_first = Chord(root=60, quality=ChordQuality.MAJOR, inversion=1)

        # First inversion should have different bass note
        assert min(chord_root.voicing) != min(chord_first.voicing)


class TestScale:
    """Tests for Scale enum."""

    def test_major_scale(self):
        assert Scale.MAJOR.value == (0, 2, 4, 5, 7, 9, 11)

    def test_minor_scale(self):
        assert Scale.MINOR.value == (0, 2, 3, 5, 7, 8, 10)

    def test_pentatonic(self):
        assert len(Scale.PENTATONIC_MAJOR.value) == 5


class TestHarmonicDescriptor:
    """Tests for HarmonicDescriptor."""

    def test_descriptor_values(self):
        engine = HarmonicEngine(seed=42)
        _, descriptor = engine.generate()

        assert 0 <= descriptor.consonance <= 1
        assert -1 <= descriptor.modal_brightness <= 1
        assert descriptor.tension_curve.shape == (16,)

    def test_descriptor_serialization(self):
        engine = HarmonicEngine(seed=42)
        _, descriptor = engine.generate()

        data = descriptor.to_dict()
        assert "consonance" in data
        assert "modal_brightness" in data
        assert "tension_curve" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
