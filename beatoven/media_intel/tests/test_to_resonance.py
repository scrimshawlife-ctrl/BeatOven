import pytest
from beatoven.media_intel.schema import MediaFrame
from beatoven.media_intel.to_resonance import media_to_resonance


def test_media_to_resonance_basic():
    """Test basic MediaFrame to ResonanceFrame conversion."""
    mf = MediaFrame(
        media_id="test_001",
        kind="image",
        path="/fake/path.jpg",
        physical={
            "luma_mean": 0.6,
            "luma_var": 0.15,
            "edge_density": 0.3,
            "motion_energy": 0.0,
            "jitter": 0.0,
        },
        affect={
            "valence": 0.7,
            "arousal": 0.5,
            "dominance": 0.6,
            "awe": 0.4,
            "dread": 0.2,
            "nostalgia": 0.3,
            "tenderness": 0.5,
        },
        confidence={"affect_confidence": 0.65},
        perceived_era={"2010s": 0.6, "2020s": 0.4},
        era_confidence=0.55,
    )

    rf = media_to_resonance(mf)

    # Check structure
    assert rf.source == "beatoven_render"
    assert rf.metrics is not None
    assert rf.beatoven_version == "beatoven-media-intel-v1"

    # Check metrics are in range
    m = rf.metrics
    assert 0.0 <= m.complexity <= 1.0
    assert 0.0 <= m.emotional_intensity <= 1.0
    assert 0.0 <= m.groove <= 1.0
    assert 0.0 <= m.energy <= 1.0
    assert 0.0 <= m.density <= 1.0
    assert 0.0 <= m.swing <= 1.0
    assert 0.0 <= m.brightness <= 1.0
    assert 0.0 <= m.tension <= 1.0

    # Check extras contain media info
    assert "media_kind" in rf.extras
    assert "media_path" in rf.extras
    assert "affect" in rf.extras
    assert "perceived_era" in rf.extras
    assert rf.extras["media_kind"] == "image"


def test_media_to_resonance_high_arousal():
    """High arousal should map to high energy and intensity."""
    mf = MediaFrame(
        media_id="test_002",
        kind="video",
        path="/fake/video.mp4",
        physical={
            "luma_mean": 0.5,
            "edge_density": 0.5,
            "motion_energy": 0.7,
            "jitter": 0.3,
        },
        affect={
            "valence": 0.5,
            "arousal": 0.9,
            "dominance": 0.6,
            "dread": 0.1,
        },
        confidence={"affect_confidence": 0.5},
    )

    rf = media_to_resonance(mf)
    m = rf.metrics

    # High arousal → high energy and emotional_intensity
    assert m.energy > 0.6
    assert m.emotional_intensity > 0.8
