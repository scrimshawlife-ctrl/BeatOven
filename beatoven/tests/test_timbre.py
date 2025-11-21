"""Tests for TimbreEngine."""

import numpy as np
import pytest
from beatoven.core.timbre import (
    TimbreEngine, TimbrePatch, AudioBuffer,
    Oscillator, Filter, Reverb, Delay,
    WaveShape, FilterType
)


class TestAudioBuffer:
    """Tests for AudioBuffer."""

    def test_basic_creation(self):
        samples = np.zeros(1024, dtype=np.float32)
        buffer = AudioBuffer(samples, sample_rate=44100)

        assert len(buffer.samples) == 1024
        assert buffer.sample_rate == 44100
        assert buffer.channels == 1

    def test_duration(self):
        samples = np.zeros(44100, dtype=np.float32)
        buffer = AudioBuffer(samples, sample_rate=44100)

        assert buffer.duration == 1.0

    def test_to_stereo(self):
        samples = np.ones(100, dtype=np.float32)
        buffer = AudioBuffer(samples, sample_rate=44100)
        stereo = buffer.to_stereo()

        assert stereo.channels == 2


class TestOscillator:
    """Tests for Oscillator."""

    def test_sine_wave(self):
        osc = Oscillator(shape=WaveShape.SINE, frequency=440.0)
        buffer = AudioBuffer(np.zeros(1024, dtype=np.float32), 44100)
        output = osc.process(buffer)

        assert output.samples.shape == (1024,)
        assert -1 <= output.samples.max() <= 1

    def test_saw_wave(self):
        osc = Oscillator(shape=WaveShape.SAW, frequency=440.0)
        buffer = AudioBuffer(np.zeros(1024, dtype=np.float32), 44100)
        output = osc.process(buffer)

        assert output.samples.shape == (1024,)

    def test_amplitude(self):
        osc = Oscillator(shape=WaveShape.SINE, amplitude=0.5)
        buffer = AudioBuffer(np.zeros(1024, dtype=np.float32), 44100)
        output = osc.process(buffer)

        assert output.samples.max() <= 0.5


class TestFilter:
    """Tests for Filter."""

    def test_lowpass(self):
        filt = Filter(filter_type=FilterType.LOWPASS, cutoff=1000.0)
        samples = np.random.uniform(-1, 1, 1024).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)
        output = filt.process(buffer)

        assert output.samples.shape == (1024,)

    def test_highpass(self):
        filt = Filter(filter_type=FilterType.HIGHPASS, cutoff=500.0)
        samples = np.random.uniform(-1, 1, 1024).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)
        output = filt.process(buffer)

        assert output.samples.shape == (1024,)

    def test_resonance(self):
        filt = Filter(filter_type=FilterType.LOWPASS, resonance=2.0)
        samples = np.random.uniform(-1, 1, 1024).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)
        output = filt.process(buffer)

        assert output.samples.shape == (1024,)


class TestReverb:
    """Tests for Reverb effect."""

    def test_basic_reverb(self):
        rev = Reverb(room_size=0.5, wet=0.3)
        samples = np.random.uniform(-1, 1, 4096).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)
        output = rev.process(buffer)

        assert output.samples.shape == (4096,)

    def test_dry_wet_mix(self):
        samples = np.random.uniform(-1, 1, 4096).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)

        rev_dry = Reverb(wet=0.0, dry=1.0)
        output_dry = rev_dry.process(buffer)

        np.testing.assert_array_almost_equal(
            output_dry.samples, samples, decimal=5
        )


class TestDelay:
    """Tests for Delay effect."""

    def test_basic_delay(self):
        dly = Delay(time_ms=250.0, feedback=0.3)
        samples = np.random.uniform(-1, 1, 44100).astype(np.float32)
        buffer = AudioBuffer(samples, 44100)
        output = dly.process(buffer)

        assert output.samples.shape == (44100,)


class TestTimbreEngine:
    """Tests for TimbreEngine."""

    def test_basic_generation(self):
        engine = TimbreEngine(seed=42)
        buffer, patch = engine.generate(
            frequency=440.0,
            duration=1.0
        )

        assert isinstance(buffer, AudioBuffer)
        assert isinstance(patch, TimbrePatch)
        assert len(buffer.samples) == 44100

    def test_density_affects_waveform(self):
        engine = TimbreEngine(seed=42)

        _, patch_low = engine.generate(density=0.1)
        _, patch_high = engine.generate(density=0.9)

        # Different densities should use different oscillators
        assert len(patch_low.oscillators) > 0
        assert len(patch_high.oscillators) > 0

    def test_resonance_adds_reverb(self):
        engine = TimbreEngine(seed=42)

        _, patch_dry = engine.generate(resonance=0.3)
        _, patch_wet = engine.generate(resonance=0.9)

        # High resonance should have reverb
        assert len(patch_wet.oscillators) > 0

    def test_determinism(self):
        engine1 = TimbreEngine(seed=123)
        engine2 = TimbreEngine(seed=123)

        buffer1, _ = engine1.generate(frequency=440.0)
        buffer2, _ = engine2.generate(frequency=440.0)

        np.testing.assert_array_equal(buffer1.samples, buffer2.samples)

    def test_provenance(self):
        engine = TimbreEngine(seed=42)
        _, patch = engine.generate()

        assert len(patch.provenance_hash) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
