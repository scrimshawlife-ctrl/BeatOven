"""
BeatOven ↔ dsp.coffee Bridge (ABX-Core hardened)

Adds:
- ResonanceFrame schema (stream + structured unified)
- PresetBank registry + deterministic scorer
- Two-lane transport to dsp.coffee:
    Lane A: realtime macros/params via UDP (OSC-compatible simple messages)
    Lane B: reliable ops via serial (length-prefixed CBOR frames w/ ACK)

You can plug this into BeatOven as a subsystem:
    from beatoven.dspcoffee_bridge.runtime import BridgeRuntime
    BridgeRuntime(...).run()

No mock data, no placeholders: this is a working spine you can extend.
"""

from .schema import ResonanceFrame, FrameDelta, PresetBank, MacroUpdate, OpsCommand
from .registry import PresetRegistry
from .scoring import score_preset_fit, choose_action
from .transport_udp import UdpRealtimeLane
from .transport_serial import SerialOpsLane
from .runtime import BridgeRuntime

__all__ = [
    "ResonanceFrame",
    "FrameDelta",
    "PresetBank",
    "MacroUpdate",
    "OpsCommand",
    "PresetRegistry",
    "score_preset_fit",
    "choose_action",
    "UdpRealtimeLane",
    "SerialOpsLane",
    "BridgeRuntime",
]
