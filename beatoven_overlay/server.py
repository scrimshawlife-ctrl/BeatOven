"""
BeatOven Overlay Server

Abraxas/AAL-core compatible HTTP overlay service.

Endpoints:
  GET  /health  - Health check
  POST /run     - Execute capability

Capabilities:
  beatoven.ping     - Diagnostic ping
  beatoven.echo     - Echo payload back
  beatoven.generate - Generate music (binding point for real engine)

Start locally:
  python -m beatoven_overlay.server --host 127.0.0.1 --port 8790

Test:
  curl http://127.0.0.1:8790/health
  curl -X POST http://127.0.0.1:8790/run \
    -H "Content-Type: application/json" \
    -d '{"capability": "beatoven.ping"}'
"""
from __future__ import annotations

import argparse
import json
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Tuple

from .provenance import make_provenance

JSON_CT = "application/json; charset=utf-8"


# ============================================================
# INTERNAL BEATOVEN BINDING
# ============================================================
def _try_import_beatoven_core():
    """
    Bind BeatOven's REAL generation function here.
    This overlay refuses to hallucinate internal APIs.

    Example (replace with real path):
        from beatoven.core.generator import generate_track
        return generate_track

    Until wired, advanced capabilities return a structured error.
    """
    try:
        # TODO: Bind real BeatOven entrypoint when ready
        # Example:
        # from beatoven.api.main import app
        # from beatoven.core.generator import BeatOvenGenerator
        # return BeatOvenGenerator()
        return None
    except Exception:
        return None


_BEATOVEN_GENERATE = _try_import_beatoven_core()


# ============================================================
# HTTP HELPERS
# ============================================================
def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    """Read and parse JSON request body."""
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("root must be object")
    return obj


def _write_json(handler: BaseHTTPRequestHandler, status: int, body: Dict[str, Any]) -> None:
    """Write JSON response."""
    raw = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", JSON_CT)
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


# ============================================================
# CAPABILITY ROUTER
# ============================================================
def _capability_router(cap: str, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Route capability requests to appropriate handlers.

    Args:
        cap: Capability name (e.g., "beatoven.ping")
        payload: Input payload dictionary

    Returns:
        Tuple of (success: bool, result: dict)
    """
    # Always-on diagnostics
    if cap == "beatoven.ping":
        return True, {
            "pong": True,
            "engine_bound": _BEATOVEN_GENERATE is not None,
        }

    if cap == "beatoven.echo":
        return True, {"echo": payload}

    # Core capability (to be wired)
    if cap == "beatoven.generate":
        if _BEATOVEN_GENERATE is None:
            return False, {
                "message": "BeatOven generate engine not wired",
                "expected_input": {
                    "style": "string (e.g., 'dark ambient', 'upbeat techno')",
                    "bpm": "int (60-200)",
                    "key": "string (e.g., 'C', 'Am', 'F#m')",
                    "length_s": "int (duration in seconds)",
                    "instruments": "list[str] (e.g., ['drums', 'bass', 'pads'])",
                    "emotion_vector": "dict (ABX-Runes fields: resonance, density, tension, etc.)",
                    "seed": "optional string (for deterministic output)",
                },
                "action": "Bind BeatOven generator in _try_import_beatoven_core() in server.py",
                "example_request": {
                    "capability": "beatoven.generate",
                    "seed": "my_deterministic_seed",
                    "input": {
                        "style": "dark ambient",
                        "bpm": 90,
                        "key": "Am",
                        "length_s": 30,
                        "instruments": ["drums", "bass", "pads"],
                        "emotion_vector": {
                            "resonance": 0.7,
                            "density": 0.4,
                            "tension": 0.6,
                        },
                    },
                },
            }

        # Example call once wired:
        # result = _BEATOVEN_GENERATE(**payload)
        # return True, result

        return False, {"message": "generate wired but not implemented"}

    return False, {"message": f"unknown capability: {cap}"}


# ============================================================
# HTTP SERVER
# ============================================================
class BeatOvenOverlayHandler(BaseHTTPRequestHandler):
    """HTTP request handler for BeatOven overlay service."""
    server_version = "beatoven-overlay/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        """Silence default HTTP logging."""
        return

    def do_GET(self) -> None:
        """Handle GET requests (health check)."""
        if self.path == "/health":
            _write_json(
                self,
                200,
                {"ok": True, "service": "beatoven_overlay", "version": "0.1"},
            )
            return
        _write_json(self, 404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        """Handle POST requests (capability execution)."""
        if self.path != "/run":
            _write_json(self, 404, {"ok": False, "error": "not found"})
            return

        try:
            req = _read_json(self)
        except Exception as e:
            _write_json(self, 400, {"ok": False, "error": f"invalid json: {e}"})
            return

        cap = req.get("capability", "beatoven.echo")
        seed = req.get("seed")
        input_payload = req.get("input", {})

        if not isinstance(input_payload, dict):
            _write_json(self, 400, {"ok": False, "error": "input must be an object"})
            return

        prov = make_provenance(
            overlay="beatoven",
            capability=cap,
            payload=input_payload,
            seed=seed,
        ).to_dict()

        ok, out = _capability_router(cap, input_payload)

        if ok:
            _write_json(
                self,
                200,
                {"ok": True, "result": out, "error": None, "provenance": prov},
            )
        else:
            _write_json(
                self,
                200,
                {"ok": False, "result": None, "error": out, "provenance": prov},
            )


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Threaded HTTP server for concurrent request handling."""
    daemon_threads = True


def main() -> None:
    """Start the BeatOven overlay HTTP server."""
    ap = argparse.ArgumentParser(description="BeatOven Overlay Service")
    ap.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    ap.add_argument("--port", type=int, default=8790, help="Port to bind to")
    args = ap.parse_args()

    print(f"Starting BeatOven Overlay Service on {args.host}:{args.port}")
    print(f"Health check: http://{args.host}:{args.port}/health")
    print(f"Capability endpoint: http://{args.host}:{args.port}/run")

    srv = ThreadedHTTPServer((args.host, args.port), BeatOvenOverlayHandler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
