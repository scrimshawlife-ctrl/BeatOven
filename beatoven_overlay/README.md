# BeatOven Overlay Service

**Abraxas/AAL-core compatible HTTP overlay for BeatOven**

A clean, production-ready overlay service that exposes BeatOven's generative music engine through a standardized HTTP interface compatible with the Abraxas/AAL-core ecosystem.

## Features

- ✅ **Stable HTTP Interface**: `/health` and `/run` endpoints
- ✅ **Deterministic Provenance**: SHA-256 hashing with SEED Protocol compliance
- ✅ **Explicit Capability Routing**: No silent guessing, clear error messages
- ✅ **Thread-Safe Server**: Concurrent request handling with ThreadedHTTPServer
- ✅ **Environment Fingerprinting**: Git HEAD, Python version, platform tracking
- ✅ **Zero Hallucination**: Explicit binding points for real BeatOven engine

## Quick Start

### Start the Overlay Service

```bash
# From the BeatOven repository root
python -m beatoven_overlay.server --host 127.0.0.1 --port 8790
```

### Test Health Endpoint

```bash
curl http://127.0.0.1:8790/health
```

**Response:**
```json
{
  "ok": true,
  "service": "beatoven_overlay",
  "version": "0.1"
}
```

### Test Capability Execution

```bash
curl -X POST http://127.0.0.1:8790/run \
  -H "Content-Type: application/json" \
  -d '{"capability": "beatoven.ping"}'
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "pong": true,
    "engine_bound": false
  },
  "error": null,
  "provenance": {
    "run_id": "fbb1c41fa26dcd4b72f821a78e6e1ea885665d285036422db060858779d723a8",
    "ts_utc": "2025-12-14T03:21:06+00:00",
    "payload_hash": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
    "env": {
      "python": "3.11.14",
      "platform": "Linux-4.4.0-x86_64-with-glibc2.39",
      "git_head": "9e39580f2cab943c0b5aecedda239f3d4ad674f7",
      "cwd": "/home/user/BeatOven"
    }
  }
}
```

## API Specification

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (returns service status) |
| `/run` | POST | Execute capability with provenance tracking |

### Request Format (`/run`)

```json
{
  "capability": "beatoven.generate",
  "seed": "optional_deterministic_seed",
  "input": {
    "style": "dark ambient",
    "bpm": 90,
    "key": "Am",
    "length_s": 30,
    "instruments": ["drums", "bass", "pads"],
    "emotion_vector": {
      "resonance": 0.7,
      "density": 0.4,
      "tension": 0.6
    }
  }
}
```

### Response Format

```json
{
  "ok": true,
  "result": { ... },
  "error": null,
  "provenance": {
    "run_id": "deterministic_sha256_hash",
    "ts_utc": "2025-12-14T03:21:06+00:00",
    "payload_hash": "sha256_of_input_payload",
    "env": {
      "python": "3.11.14",
      "platform": "Linux-4.4.0-x86_64-with-glibc2.39",
      "git_head": "commit_hash",
      "cwd": "/path/to/repo"
    }
  }
}
```

## Capabilities

### Always Available

| Capability | Description | Input | Output |
|------------|-------------|-------|--------|
| `beatoven.ping` | Diagnostic ping | `{}` | `{"pong": true, "engine_bound": bool}` |
| `beatoven.echo` | Echo payload back | Any dict | `{"echo": <input>}` |

### Core Capability (Binding Point)

| Capability | Status | Description |
|------------|--------|-------------|
| `beatoven.generate` | 🔴 Not wired | Music generation (see "Binding the Real Engine" below) |

## Provenance System

Every request generates deterministic provenance metadata:

- **run_id**: SHA-256 hash of (overlay, capability, payload_hash, seed)
- **ts_utc**: UTC timestamp in ISO format
- **payload_hash**: SHA-256 hash of canonical JSON input
- **env**: Environment fingerprint (Python version, platform, Git HEAD, cwd)

### Deterministic Provenance Example

Same seed → Same run_id:

```bash
# First request
curl -X POST http://127.0.0.1:8790/run \
  -d '{"capability": "beatoven.ping", "seed": "test_seed_123", "input": {}}'
# run_id: c3f64292cdde677d383998700e457194939a628c8e0711a3a1c4a4a5a6f6282a

# Second request (same seed)
curl -X POST http://127.0.0.1:8790/run \
  -d '{"capability": "beatoven.ping", "seed": "test_seed_123", "input": {}}'
# run_id: c3f64292cdde677d383998700e457194939a628c8e0711a3a1c4a4a5a6f6282a (identical!)
```

## Binding the Real Engine

The overlay service has an **explicit binding point** for the real BeatOven generator.

### Current State

The `beatoven.generate` capability returns a structured error explaining:
- Expected input format
- Example request
- Where to wire the real engine

```bash
curl -X POST http://127.0.0.1:8790/run \
  -d '{"capability": "beatoven.generate", "input": {"style": "dark ambient"}}'
```

**Response:**
```json
{
  "ok": false,
  "error": {
    "message": "BeatOven generate engine not wired",
    "action": "Bind BeatOven generator in _try_import_beatoven_core() in server.py",
    "expected_input": {
      "style": "string (e.g., 'dark ambient', 'upbeat techno')",
      "bpm": "int (60-200)",
      "key": "string (e.g., 'C', 'Am', 'F#m')",
      "length_s": "int (duration in seconds)",
      "instruments": "list[str] (e.g., ['drums', 'bass', 'pads'])",
      "emotion_vector": "dict (ABX-Runes fields: resonance, density, tension, etc.)",
      "seed": "optional string (for deterministic output)"
    }
  }
}
```

### Wiring Instructions

Edit `beatoven_overlay/server.py`:

```python
def _try_import_beatoven_core():
    """
    Bind BeatOven's REAL generation function here.
    """
    try:
        # Example: Import your existing BeatOven API
        from beatoven.api.main import app
        from beatoven.core.generator import BeatOvenGenerator
        return BeatOvenGenerator()
    except Exception:
        return None
```

Then update the `beatoven.generate` handler in `_capability_router()`:

```python
if cap == "beatoven.generate":
    if _BEATOVEN_GENERATE is None:
        return False, {"message": "BeatOven generate engine not wired", ...}

    # Call the real engine
    result = _BEATOVEN_GENERATE.generate(**payload)
    return True, result
```

## Integration with AAL-Core

This overlay is designed to work seamlessly with the AAL-core overlay dispatcher:

```yaml
# aal_core_config.yaml
overlays:
  - name: beatoven
    url: http://127.0.0.1:8790
    capabilities:
      - beatoven.ping
      - beatoven.echo
      - beatoven.generate
```

## Architecture

```
┌─────────────────────────────────────────────┐
│         BeatOven Overlay Service            │
├─────────────────────────────────────────────┤
│  HTTP Server (ThreadedHTTPServer)           │
│    ├─ GET  /health                          │
│    └─ POST /run                             │
│         ↓                                    │
│  Capability Router                          │
│    ├─ beatoven.ping       (diagnostic)      │
│    ├─ beatoven.echo       (diagnostic)      │
│    └─ beatoven.generate   (binding point)   │
│         ↓                                    │
│  Provenance System                          │
│    ├─ Deterministic run_id (SHA-256)        │
│    ├─ Payload hashing                       │
│    └─ Environment fingerprinting            │
│         ↓                                    │
│  [BINDING POINT]                            │
│  Real BeatOven Engine                       │
│  (to be wired in _try_import_beatoven_core) │
└─────────────────────────────────────────────┘
```

## File Structure

```
beatoven_overlay/
├── __init__.py          # Package marker
├── provenance.py        # Provenance tracking system
├── server.py            # HTTP server + capability router
└── README.md            # This file
```

## Testing

All capabilities are tested and verified:

- ✅ Health endpoint returns service status
- ✅ Ping capability works with engine_bound indicator
- ✅ Echo capability reflects input payload
- ✅ Generate capability returns structured error when unwired
- ✅ Deterministic run_id generation with same seed
- ✅ Provenance tracking includes Git HEAD and environment

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/beatoven-overlay.service`:

```ini
[Unit]
Description=BeatOven Overlay Service
After=network.target

[Service]
Type=simple
User=beatoven
WorkingDirectory=/opt/beatoven
ExecStart=/usr/bin/python3 -m beatoven_overlay.server --host 0.0.0.0 --port 8790
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8790
CMD ["python", "-m", "beatoven_overlay.server", "--host", "0.0.0.0", "--port", "8790"]
```

## License

Apache 2.0 (matches parent BeatOven project)

## Next Steps

1. ✅ Overlay service implemented and tested
2. 🔲 Bind real BeatOven generator in `_try_import_beatoven_core()`
3. 🔲 Add manifest file for AAL-core discovery
4. 🔲 Deploy to production with systemd/Docker
5. 🔲 Integrate with HollerSports overlay (next module)

---

**BeatOven Overlay** - One module, one clean graft.

*Part of the Applied Alchemy Labs ecosystem.*
