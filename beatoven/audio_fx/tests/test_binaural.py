import pytest
import numpy as np
from beatoven.audio_fx import BinauralSpec, apply_binaural


def test_binaural_spec_defaults():
    """Test BinauralSpec defaults"""
    spec = BinauralSpec(carrier_hz=200.0, beat_hz=6.0)
    assert spec.carrier_hz == 200.0
    assert spec.beat_hz == 6.0
    assert spec.mix == 0.15
    assert spec.ramp_s == 2.0
    assert spec.phase_deg == 0.0
    assert spec.pan == 0.0


def test_apply_binaural_basic():
    """Test basic binaural application"""
    sr = 44100
    duration = 1.0
    n = int(sr * duration)

    # Create test signal
    stereo = np.zeros((n, 2), dtype=np.float32)

    spec = BinauralSpec(carrier_hz=200.0, beat_hz=6.0, mix=0.5)
    result = apply_binaural(stereo, sr, spec)

    # Check shape preserved
    assert result.shape == stereo.shape

    # Check output is not all zeros
    assert np.any(result != 0.0)

    # Check range (should be clipped to reasonable values)
    assert np.all(np.abs(result) <= 1.0)


def test_apply_binaural_zero_mix():
    """Zero mix should return input unchanged"""
    sr = 44100
    n = 1000
    stereo = np.random.randn(n, 2).astype(np.float32) * 0.5

    spec = BinauralSpec(carrier_hz=200.0, beat_hz=6.0, mix=0.0)
    result = apply_binaural(stereo, sr, spec)

    # Should be identical
    assert np.allclose(result, stereo)


def test_apply_binaural_clamping():
    """Test parameter clamping"""
    sr = 44100
    n = 1000
    stereo = np.zeros((n, 2), dtype=np.float32)

    # Out of range values should be clamped
    spec = BinauralSpec(
        carrier_hz=5000.0,  # > max
        beat_hz=100.0,      # > max
        mix=2.0,            # > 1.0
        pan=5.0,            # > 1.0
    )
    result = apply_binaural(stereo, sr, spec)

    # Should not crash and output should be valid
    assert result.shape == stereo.shape
    assert not np.any(np.isnan(result))
    assert not np.any(np.isinf(result))


def test_apply_binaural_stereo_difference():
    """Left and right channels should differ due to beat frequency"""
    sr = 44100
    duration = 1.0
    n = int(sr * duration)

    stereo = np.zeros((n, 2), dtype=np.float32)

    spec = BinauralSpec(carrier_hz=200.0, beat_hz=10.0, mix=1.0, ramp_s=0.0)
    result = apply_binaural(stereo, sr, spec)

    # Left and right should be different (due to frequency offset)
    assert not np.allclose(result[:, 0], result[:, 1])


def test_apply_binaural_invalid_shape():
    """Test error on invalid input shape"""
    sr = 44100
    mono = np.zeros((1000,), dtype=np.float32)

    spec = BinauralSpec(carrier_hz=200.0, beat_hz=6.0)

    with pytest.raises(ValueError, match="stereo must be"):
        apply_binaural(mono, sr, spec)
