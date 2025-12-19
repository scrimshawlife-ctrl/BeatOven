from __future__ import annotations

import struct
import time
from typing import Any, Dict, Optional

import cbor2
import serial

class SerialOpsLane:
    """
    Reliable lane over serial with ACK.
    Frame format:
      [u32_be length][cbor payload bytes]
    Payload is a dict with:
      - kind: str
      - nonce: int
      - payload: dict

    Firmware must reply:
      {"ack": nonce, "ok": true}   (CBOR framed the same way)
    """

    def __init__(self, port: str, baud: int = 115200, timeout_s: float = 0.25) -> None:
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=timeout_s)
        self._nonce = 1

    def _next_nonce(self) -> int:
        n = self._nonce
        self._nonce += 1
        if self._nonce > 2_000_000_000:
            self._nonce = 1
        return n

    def _write_frame(self, obj: Dict[str, Any]) -> None:
        raw = cbor2.dumps(obj)
        hdr = struct.pack(">I", len(raw))
        self.ser.write(hdr + raw)

    def _read_frame(self) -> Optional[Dict[str, Any]]:
        hdr = self.ser.read(4)
        if len(hdr) != 4:
            return None
        (n,) = struct.unpack(">I", hdr)
        if n <= 0 or n > 1_000_000:
            return None
        raw = self.ser.read(n)
        if len(raw) != n:
            return None
        obj = cbor2.loads(raw)
        if not isinstance(obj, dict):
            return None
        return obj

    def send(self, kind: str, payload: Dict[str, Any], retries: int = 3) -> bool:
        nonce = self._next_nonce()
        msg = {"kind": kind, "nonce": nonce, "payload": payload}

        for _ in range(max(1, retries)):
            self._write_frame(msg)
            t0 = time.time()
            while (time.time() - t0) < 0.6:
                resp = self._read_frame()
                if not resp:
                    continue
                if resp.get("ack") == nonce:
                    return bool(resp.get("ok", False))
        return False
