from __future__ import annotations

import socket
from typing import Dict, Tuple

def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)

class UdpRealtimeLane:
    """
    Very small realtime lane.
    Messages are newline-terminated UTF-8 records to stay dead-simple and inspectable:

        /macro <preset_id> <name> <value>
        /meta bpm <value>
        /meta swing <value>

    dsp.coffee firmware can parse these without an OSC library.
    If you want true OSC later, keep the address strings identical and swap encoder.
    """

    def __init__(self, host: str, port: int) -> None:
        self.addr: Tuple[str, int] = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_macro(self, preset_id: str, name: str, value: float) -> None:
        v = _clamp01(value)
        msg = f"/macro {preset_id} {name} {v:.6f}\n".encode("utf-8")
        self.sock.sendto(msg, self.addr)

    def send_meta(self, key: str, value: float) -> None:
        msg = f"/meta {key} {float(value):.6f}\n".encode("utf-8")
        self.sock.sendto(msg, self.addr)

    def send_macros(self, preset_id: str, values: Dict[str, float]) -> None:
        for k, v in values.items():
            self.send_macro(preset_id, k, v)
