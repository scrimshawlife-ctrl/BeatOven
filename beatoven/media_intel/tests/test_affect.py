import pytest
from beatoven.media_intel.affect import affect_from_features


def test_affect_basic():
    """Test basic affect computation with neutral inputs."""
    physical = {
        "luma_mean": 0.5,
        "luma_var": 0.1,
        "sat_mean": 0.4,
        "edge_density": 0.1,
        "motion_energy": 0.0,
    }
    semantic = {}

    affect, conf = affect_from_features(physical, semantic)

    # Check all expected keys present
    assert "valence" in affect
    assert "arousal" in affect
    assert "dominance" in affect
    assert "awe" in affect
    assert "dread" in affect
    assert "nostalgia" in affect
    assert "tenderness" in affect

    # All values in [0,1]
    for k, v in affect.items():
        assert 0.0 <= v <= 1.0, f"{k} = {v} out of range"

    # Confidence present and in range
    assert "affect_confidence" in conf
    assert 0.0 <= conf["affect_confidence"] <= 1.0


def test_affect_bright_high_arousal():
    """Bright, high-contrast, high-edge should yield high arousal."""
    physical = {
        "luma_mean": 0.9,
        "luma_var": 0.4,
        "sat_mean": 0.7,
        "edge_density": 0.6,
        "motion_energy": 0.5,
    }
    semantic = {}

    affect, conf = affect_from_features(physical, semantic)

    # Expect high arousal
    assert affect["arousal"] > 0.6
    # Expect high valence (bright + saturated)
    assert affect["valence"] > 0.5


def test_affect_dark_low_valence():
    """Dark, low saturation should yield lower valence."""
    physical = {
        "luma_mean": 0.2,
        "luma_var": 0.05,
        "sat_mean": 0.2,
        "edge_density": 0.1,
        "motion_energy": 0.0,
    }
    semantic = {}

    affect, conf = affect_from_features(physical, semantic)

    # Expect lower valence
    assert affect["valence"] < 0.55
