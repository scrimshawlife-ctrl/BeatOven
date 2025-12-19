from beatoven.dspcoffee_bridge.schema import PresetBank, PresetSelector, ResonanceFrame, ResonanceMetrics
from beatoven.dspcoffee_bridge.scoring import score_preset_fit

def test_score_inside_range_high():
    f = ResonanceFrame.new(
        source="abraxas_struct",
        genre="techno",
        metrics=ResonanceMetrics(
            complexity=0.6, emotional_intensity=0.7, groove=0.8, energy=0.9,
            density=0.7, swing=0.4, brightness=0.5, tension=0.8
        )
    )
    p = PresetBank(
        preset_id="p1",
        name="Techno Driver",
        selector=PresetSelector(
            genre="techno",
            targets={"groove": (0.7, 0.95), "energy": (0.8, 1.0)},
            weights={"groove": 2.0, "energy": 1.0},
        ),
        patch_graph_id=1,
        macros=["groove","energy","tension","density"],
    )
    s = score_preset_fit(f, p)
    assert s > 0.9

def test_score_wrong_genre_zero():
    f = ResonanceFrame.new(source="abraxas_struct", genre="house")
    p = PresetBank(
        preset_id="p2",
        name="Techno Only",
        selector=PresetSelector(genre="techno"),
        patch_graph_id=2,
    )
    assert score_preset_fit(f, p) == 0.0
