"""
BeatOven Drums Default RigProfiles

Predefined equipment profiles for common setups.

These ship with the package and are auto-installed on first run.
"""

from typing import List
import time

from .schema import (
    RigProfile,
    EmitTarget,
    DrumRole,
    IOCapabilities,
    ClockingConfig,
    CVRange,
    SwingSource,
    OutputMapping
)


def get_default_profiles() -> List[RigProfile]:
    """
    Get list of default RigProfile presets.

    Returns:
        List of default profiles
    """
    timestamp = int(time.time() * 1000)

    return [
        # 1. Eurorack 4-voice (dsp.coffee)
        RigProfile(
            id="eurorack_dspcoffee_4voice",
            name="Eurorack 4-Voice (dsp.coffee)",
            emit_target=EmitTarget.DSP_COFFEE,
            drum_lanes_max=4,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.HAT,
                DrumRole.PERC
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=True,
                accent=True,
                velocity=False,
                cv_range=CVRange.ZERO_5V
            ),
            clocking=ClockingConfig(
                external_clock=True,
                external_reset=True,
                swing_source=SwingSource.INTERNAL
            ),
            output_map=(
                OutputMapping(lane_index=0, role=DrumRole.KICK, out_id="trigger_1"),
                OutputMapping(lane_index=1, role=DrumRole.SNARE, out_id="trigger_2"),
                OutputMapping(lane_index=2, role=DrumRole.HAT, out_id="trigger_3"),
                OutputMapping(lane_index=3, role=DrumRole.PERC, out_id="trigger_4"),
            ),
            created_at_ts_ms=timestamp
        ),

        # 2. MIDI Drum Machine (8 channels)
        RigProfile(
            id="midi_drum_machine_8ch",
            name="MIDI Drum Machine (8 Channels)",
            emit_target=EmitTarget.MIDI,
            drum_lanes_max=8,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.HAT,
                DrumRole.PERC,
                DrumRole.FX
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=True,
                accent=True,
                velocity=True,  # MIDI has velocity
                cv_range=CVRange.ZERO_5V  # Not used for MIDI
            ),
            clocking=ClockingConfig(
                external_clock=False,
                external_reset=False,
                swing_source=SwingSource.INTERNAL
            ),
            output_map=(
                OutputMapping(lane_index=0, role=DrumRole.KICK, out_id="midi_ch10_note36"),
                OutputMapping(lane_index=1, role=DrumRole.SNARE, out_id="midi_ch10_note38"),
                OutputMapping(lane_index=2, role=DrumRole.HAT, out_id="midi_ch10_note42"),
                OutputMapping(lane_index=3, role=DrumRole.PERC, out_id="midi_ch10_note47"),
                OutputMapping(lane_index=4, role=DrumRole.PERC, out_id="midi_ch10_note50"),
                OutputMapping(lane_index=5, role=DrumRole.FX, out_id="midi_ch10_note49"),
                OutputMapping(lane_index=6, role=DrumRole.FX, out_id="midi_ch10_note51"),
                OutputMapping(lane_index=7, role=DrumRole.PERC, out_id="midi_ch10_note45"),
            ),
            created_at_ts_ms=timestamp
        ),

        # 3. Minimal CV/Gate (2-voice)
        RigProfile(
            id="minimal_cvgate_2voice",
            name="Minimal CV/Gate (2-Voice)",
            emit_target=EmitTarget.CV_GATE,
            drum_lanes_max=2,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.HAT
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=False,  # Trigger only
                accent=False,
                velocity=False,
                cv_range=CVRange.ZERO_5V
            ),
            clocking=ClockingConfig(
                external_clock=True,
                external_reset=True,
                swing_source=SwingSource.EXTERNAL
            ),
            output_map=(
                OutputMapping(lane_index=0, role=DrumRole.KICK, out_id="cv_a"),
                OutputMapping(lane_index=1, role=DrumRole.SNARE, out_id="cv_b"),
            ),
            created_at_ts_ms=timestamp
        ),

        # 4. Audio Stems (unlimited virtual lanes)
        RigProfile(
            id="audio_stems_16lane",
            name="Audio Stems (16-Lane Virtual)",
            emit_target=EmitTarget.AUDIO_STEMS,
            drum_lanes_max=16,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.HAT,
                DrumRole.PERC,
                DrumRole.FX
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=True,
                accent=True,
                velocity=True,
                cv_range=CVRange.ZERO_5V  # Not used for audio stems
            ),
            clocking=ClockingConfig(
                external_clock=False,
                external_reset=False,
                swing_source=SwingSource.INTERNAL
            ),
            output_map=None,  # Auto-assigned to audio stems
            created_at_ts_ms=timestamp
        ),

        # 5. Eurorack 8-voice (expanded)
        RigProfile(
            id="eurorack_dspcoffee_8voice",
            name="Eurorack 8-Voice (Expanded dsp.coffee)",
            emit_target=EmitTarget.DSP_COFFEE,
            drum_lanes_max=8,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.HAT,
                DrumRole.PERC,
                DrumRole.FX
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=True,
                accent=True,
                velocity=False,
                cv_range=CVRange.ZERO_5V
            ),
            clocking=ClockingConfig(
                external_clock=True,
                external_reset=True,
                swing_source=SwingSource.HYBRID
            ),
            output_map=(
                OutputMapping(lane_index=0, role=DrumRole.KICK, out_id="trigger_1"),
                OutputMapping(lane_index=1, role=DrumRole.SNARE, out_id="trigger_2"),
                OutputMapping(lane_index=2, role=DrumRole.HAT, out_id="trigger_3"),
                OutputMapping(lane_index=3, role=DrumRole.PERC, out_id="trigger_4"),
                OutputMapping(lane_index=4, role=DrumRole.PERC, out_id="trigger_5"),
                OutputMapping(lane_index=5, role=DrumRole.PERC, out_id="trigger_6"),
                OutputMapping(lane_index=6, role=DrumRole.FX, out_id="trigger_7"),
                OutputMapping(lane_index=7, role=DrumRole.FX, out_id="trigger_8"),
            ),
            created_at_ts_ms=timestamp
        ),

        # 6. Buchla-style (0-10V bipolar)
        RigProfile(
            id="buchla_cvgate_4voice",
            name="Buchla-style CV/Gate (4-Voice)",
            emit_target=EmitTarget.CV_GATE,
            drum_lanes_max=4,
            lane_roles_allowed=(
                DrumRole.KICK,
                DrumRole.SNARE,
                DrumRole.PERC,
                DrumRole.FX
            ),
            io_caps=IOCapabilities(
                trigger=True,
                gate=True,
                accent=True,
                velocity=False,
                cv_range=CVRange.ZERO_10V
            ),
            clocking=ClockingConfig(
                external_clock=True,
                external_reset=False,
                swing_source=SwingSource.EXTERNAL
            ),
            output_map=(
                OutputMapping(lane_index=0, role=DrumRole.KICK, out_id="pulse_1"),
                OutputMapping(lane_index=1, role=DrumRole.SNARE, out_id="pulse_2"),
                OutputMapping(lane_index=2, role=DrumRole.PERC, out_id="pulse_3"),
                OutputMapping(lane_index=3, role=DrumRole.FX, out_id="pulse_4"),
            ),
            created_at_ts_ms=timestamp
        ),
    ]


__all__ = [
    "get_default_profiles",
]
