"""Tests for MotionEngine."""

import numpy as np
import pytest
from beatoven.core.motion import (
    MotionEngine, LFO, Envelope, AutomationCurve,
    ModulationPoint, RunicModulation, MotionDescriptor,
    LFOShape, EnvelopeStage
)


class TestLFO:
    """Tests for LFO."""

    def test_sine_lfo(self):
        lfo = LFO(shape=LFOShape.SINE, frequency=1.0)

        # At t=0, sine should be near 0
        assert abs(lfo.get_value_at(0.0)) < 0.1

        # At t=0.25, sine should be near 1
        assert abs(lfo.get_value_at(0.25) - 1.0) < 0.1

    def test_triangle_lfo(self):
        lfo = LFO(shape=LFOShape.TRIANGLE, frequency=1.0)
        value = lfo.get_value_at(0.5)
        assert -1 <= value <= 1

    def test_square_lfo(self):
        lfo = LFO(shape=LFOShape.SQUARE, frequency=1.0)
        value = lfo.get_value_at(0.25)
        assert value == 1.0 or value == -1.0

    def test_amplitude(self):
        lfo = LFO(shape=LFOShape.SINE, amplitude=0.5)
        value = lfo.get_value_at(0.25)
        assert abs(value) <= 0.5

    def test_offset(self):
        lfo = LFO(shape=LFOShape.SINE, offset=0.5)
        value = lfo.get_value_at(0.0)
        assert abs(value - 0.5) < 0.1

    def test_generate_curve(self):
        lfo = LFO(shape=LFOShape.SINE, frequency=1.0)
        curve = lfo.generate_curve(duration=2.0, resolution=100)

        assert isinstance(curve, AutomationCurve)
        assert len(curve.points) == 100


class TestEnvelope:
    """Tests for ADSR Envelope."""

    def test_attack_phase(self):
        env = Envelope(attack=0.1, decay=0.1, sustain=0.5, release=0.1)

        # At t=0, envelope should be 0
        assert env.get_value_at(0.0) == 0.0

        # At end of attack, should be 1
        assert abs(env.get_value_at(0.1) - 1.0) < 0.1

    def test_sustain_phase(self):
        env = Envelope(attack=0.1, decay=0.1, sustain=0.7, release=0.1)

        # After attack and decay, should be at sustain level
        value = env.get_value_at(0.3)
        assert abs(value - 0.7) < 0.1

    def test_release_phase(self):
        env = Envelope(attack=0.1, decay=0.1, sustain=0.7, release=0.2)

        # After note off + release, should be near 0
        value = env.get_value_at(0.5, note_on_duration=0.3)
        assert value < 0.1

    def test_generate_curve(self):
        env = Envelope(attack=0.1, decay=0.1, sustain=0.7, release=0.3)
        curve = env.generate_curve(note_duration=0.5, resolution=100)

        assert isinstance(curve, AutomationCurve)
        assert len(curve.points) == 100


class TestAutomationCurve:
    """Tests for AutomationCurve."""

    def test_linear_interpolation(self):
        points = [
            ModulationPoint(time=0.0, value=0.0),
            ModulationPoint(time=1.0, value=1.0)
        ]
        curve = AutomationCurve(name="test", points=points)

        assert curve.get_value_at(0.0) == 0.0
        assert curve.get_value_at(0.5) == 0.5
        assert curve.get_value_at(1.0) == 1.0

    def test_loop(self):
        points = [
            ModulationPoint(time=0.0, value=0.0),
            ModulationPoint(time=1.0, value=1.0)
        ]
        curve = AutomationCurve(
            name="test",
            points=points,
            loop=True,
            loop_start=0.0,
            loop_end=1.0
        )

        # At t=1.5, should wrap to t=0.5
        assert abs(curve.get_value_at(1.5) - 0.5) < 0.1


class TestMotionEngine:
    """Tests for MotionEngine."""

    def test_basic_generation(self):
        engine = MotionEngine(seed=42)
        curves, descriptor = engine.generate(duration=4.0)

        assert isinstance(curves, dict)
        assert isinstance(descriptor, MotionDescriptor)
        assert "amplitude" in curves
        assert "filter_cutoff" in curves

    def test_drift_affects_motion(self):
        engine = MotionEngine(seed=42)

        _, desc_low = engine.generate(drift=0.1)
        _, desc_high = engine.generate(drift=0.9)

        # Higher drift should produce more temporal variation
        assert desc_high.temporal_variation >= desc_low.temporal_variation

    def test_runic_modulation(self):
        engine = MotionEngine(seed=42)
        rune_vector = np.random.uniform(-1, 1, 64).astype(np.float32)

        curves, _ = engine.generate(
            drift=0.5,
            rune_vector=rune_vector
        )

        assert "runic" in curves

    def test_determinism(self):
        engine1 = MotionEngine(seed=123)
        engine2 = MotionEngine(seed=123)

        curves1, _ = engine1.generate(drift=0.5)
        curves2, _ = engine2.generate(drift=0.5)

        for name in curves1:
            if name in curves2:
                assert len(curves1[name].points) == len(curves2[name].points)


class TestRunicModulation:
    """Tests for RunicModulation."""

    def test_basic_modulation(self):
        rune_vector = np.array([0.5, -0.3, 0.8, 0.1])
        mod = RunicModulation(
            rune_vector=rune_vector,
            target_param="cutoff",
            influence=0.5
        )

        value = mod.apply(base_value=0.5, time=0.0)
        assert value != 0.5  # Should be modulated


class TestMotionDescriptor:
    """Tests for MotionDescriptor."""

    def test_descriptor_values(self):
        engine = MotionEngine(seed=42)
        _, descriptor = engine.generate()

        assert 0 <= descriptor.lfo_depth <= 1
        assert descriptor.envelope_shape in ["percussive", "sustained"]
        assert 0 <= descriptor.modulation_complexity <= 1

    def test_descriptor_serialization(self):
        engine = MotionEngine(seed=42)
        _, descriptor = engine.generate()

        data = descriptor.to_dict()
        assert "lfo_depth" in data
        assert "envelope_shape" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
