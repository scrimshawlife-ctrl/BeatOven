from beatoven.dspcoffee_bridge.schema import PresetBank, PresetSelector

PRESETS = [
    PresetBank(
        preset_id="techno_dark_driver",
        name="Techno — Dark Driver",
        selector=PresetSelector(
            genre="techno",
            subgenre="dark",
            targets={
                "energy": (0.75, 1.0),
                "tension": (0.65, 1.0),
                "groove": (0.60, 0.92),
                "brightness": (0.00, 0.45),
            },
            weights={"energy": 1.5, "tension": 1.2, "groove": 1.0, "brightness": 0.6},
        ),
        patch_graph_id=3,
        kit_id=11,
        macros=["energy","tension","groove","density","swing","brightness"],
        scene_change_quantize="bar",
        crossfade_ms=180,
    ),
    PresetBank(
        preset_id="house_swing_chop",
        name="House — Swing Chop",
        selector=PresetSelector(
            genre="house",
            targets={
                "swing": (0.55, 0.90),
                "groove": (0.70, 1.0),
                "brightness": (0.35, 0.85),
                "energy": (0.45, 0.85),
            },
            weights={"swing": 1.3, "groove": 1.2, "brightness": 0.8, "energy": 0.7},
        ),
        patch_graph_id=4,
        kit_id=7,
        macros=["groove","swing","brightness","density","energy"],
        scene_change_quantize="bar",
        crossfade_ms=150,
    ),
]
