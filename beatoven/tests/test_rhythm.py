"""Tests for RhythmEngine."""

import numpy as np
import pytest
from beatoven.core.rhythm import (
    RhythmEngine, RhythmPattern, RhythmEvent,
    RhythmDescriptor, NoteValue
)


class TestRhythmEngine:
    """Tests for RhythmEngine."""

    def test_basic_generation(self):
        engine = RhythmEngine(seed=42)
        pattern, descriptor = engine.generate()

        assert isinstance(pattern, RhythmPattern)
        assert isinstance(descriptor, RhythmDescriptor)
        assert len(pattern.events) > 0

    def test_pattern_properties(self):
        engine = RhythmEngine(seed=42)
        pattern, _ = engine.generate(
            tempo=120.0,
            time_signature=(4, 4),
            length_bars=4
        )

        assert pattern.tempo == 120.0
        assert pattern.time_signature == (4, 4)
        assert pattern.length_beats == 16.0  # 4 bars * 4 beats

    def test_density_affects_events(self):
        engine = RhythmEngine(seed=42)

        sparse, _ = engine.generate(density=0.2)
        dense, _ = engine.generate(density=0.9)

        # Higher density should produce more events
        assert len(dense.events) >= len(sparse.events)

    def test_determinism(self):
        engine1 = RhythmEngine(seed=123)
        engine2 = RhythmEngine(seed=123)

        pattern1, _ = engine1.generate(density=0.5, tension=0.5)
        pattern2, _ = engine2.generate(density=0.5, tension=0.5)

        assert len(pattern1.events) == len(pattern2.events)
        for e1, e2 in zip(pattern1.events, pattern2.events):
            assert e1.time == e2.time
            assert e1.velocity == e2.velocity

    def test_swing(self):
        engine = RhythmEngine(seed=42)
        pattern, _ = engine.generate(swing=0.5)

        assert pattern.swing_amount == 0.5

    def test_layers(self):
        engine = RhythmEngine(seed=42)
        pattern, _ = engine.generate(
            layers=["kick", "snare", "hihat_closed"]
        )

        assert "kick" in pattern.layers
        assert "snare" in pattern.layers
        assert "hihat_closed" in pattern.layers

    def test_provenance_hash(self):
        engine = RhythmEngine(seed=42)
        pattern, _ = engine.generate()

        assert len(pattern.provenance_hash) == 64


class TestEuclideanRhythm:
    """Tests for Euclidean rhythm generation."""

    def test_basic_euclidean(self):
        engine = RhythmEngine()

        # Classic 4-on-the-floor
        pattern = engine.euclidean_rhythm(4, 16)
        assert sum(pattern) == 4
        assert len(pattern) == 16

    def test_euclidean_edge_cases(self):
        engine = RhythmEngine()

        # All hits
        pattern = engine.euclidean_rhythm(8, 8)
        assert all(pattern)

        # No hits
        pattern = engine.euclidean_rhythm(0, 8)
        assert not any(pattern)

    def test_euclidean_rotation(self):
        engine = RhythmEngine()

        pattern1 = engine.euclidean_rhythm(3, 8, rotation=0)
        pattern2 = engine.euclidean_rhythm(3, 8, rotation=1)

        # Same number of hits
        assert sum(pattern1) == sum(pattern2)
        # But different positions
        assert pattern1 != pattern2


class TestRhythmDescriptor:
    """Tests for RhythmDescriptor."""

    def test_descriptor_values(self):
        engine = RhythmEngine(seed=42)
        _, descriptor = engine.generate()

        assert 0 <= descriptor.density
        assert 0 <= descriptor.syncopation <= 1
        assert 0 <= descriptor.polymetric_complexity
        assert descriptor.accent_pattern.shape == (16,)
        assert descriptor.velocity_curve.shape == (16,)

    def test_descriptor_serialization(self):
        engine = RhythmEngine(seed=42)
        _, descriptor = engine.generate()

        data = descriptor.to_dict()
        assert "density" in data
        assert "syncopation" in data
        assert "accent_pattern" in data


class TestRhythmEvent:
    """Tests for RhythmEvent."""

    def test_event_properties(self):
        event = RhythmEvent(
            time=1.5,
            duration=0.25,
            velocity=0.8,
            note=36,
            accent=True
        )

        assert event.time == 1.5
        assert event.duration == 0.25
        assert event.velocity == 0.8
        assert event.accent is True

    def test_event_serialization(self):
        event = RhythmEvent(time=0.0, duration=0.5, velocity=0.7)
        data = event.to_dict()

        assert data["time"] == 0.0
        assert data["duration"] == 0.5
        assert data["velocity"] == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
