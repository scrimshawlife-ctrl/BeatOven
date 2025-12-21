# Refactor Report

## Repo map summary
- `beatoven/`: core engines, API, signals, audio, runtime utilities
- `beatoven-ui/`: React Native client
- `scripts/`: run_local/run_gpu entrypoints
- `.github/workflows/`: deploy-azure workflow

## Top issues (pre-refactor)
1. Non-deterministic default seed source in API (`hash()` usage).
2. No rune registry or validator despite runic system claims.
3. No capability/schema endpoints for UI-driven configuration.
4. Missing ABI-level manifests for generated artifacts.
5. Pure-engine rule not enforced by tests.

## Target architecture alignment
- Added `beatoven/runes/`, `beatoven/registry/`, `beatoven/runtime/`, `beatoven/provenance/`, `beatoven/schema/`.
- Introduced a deterministic orchestrator stub and capability policy.
- Added a pure-engine test gate for `beatoven/engines/`.

## Changes delivered
- ABX-Runes YAML manifests and JSON schema references.
- Rune registry CLI (`python -m beatoven.registry list|validate`).
- Runtime orchestrator with provenance manifest generation.
- Capability + config schema endpoints for UI.
- UI now renders module options from the backend schema with availability flags.

## Metrics (baseline vs after)

### 1) API startup and cold path
Command:
```bash
python - <<'PY'
import json
import time
from beatoven.api.main import create_app
from beatoven.signals import SignalNormalizer, SourceType, SourceCategory
from beatoven.core.stems import StemGenerator, StemType

results = {}
start = time.perf_counter()
app = create_app()
results['api_startup_ms'] = (time.perf_counter() - start) * 1000

try:
    from beatoven.gpu.device_utils import DeviceManager
    start = time.perf_counter()
    manager = DeviceManager()
    results['gpu_detect'] = {'device': manager.get_device_string(), 'runtime_ms': (time.perf_counter() - start) * 1000}
except Exception as e:
    results['gpu_detect'] = {'error': str(e)}

start = time.perf_counter()
normalized = SignalNormalizer.normalize_text(
    "Test signal payload for normalization.",
    SourceType.TEXT_FILE,
    SourceCategory.CUSTOM,
    "Baseline"
)
results['ingest_normalize_ms'] = (time.perf_counter() - start) * 1000
results['ingest_hash'] = normalized.provenance_hash

stem_gen = StemGenerator()
start = time.perf_counter()
stems = stem_gen.generate_stems(
    rhythm_events=[{'time': 0.0, 'velocity': 0.8}],
    harmonic_events=[{'time': 0.0, 'notes': [60, 64, 67], 'velocity': 0.8}],
    duration=4.0,
    stem_types=[StemType.DRUMS, StemType.BASS]
)
results['stem_generate_ms'] = (time.perf_counter() - start) * 1000
results['stem_count'] = len(stems)

print(json.dumps(results, indent=2))
PY
```

**Baseline**
```json
{
  "api_startup_ms": 1.8969770000012431,
  "gpu_detect": {"device": "cpu", "runtime_ms": 0.31447700007447565},
  "ingest_normalize_ms": 0.08787199999460427,
  "ingest_hash": "f13254ad5cd7a429",
  "stem_generate_ms": 189.29157800005214,
  "stem_count": 2
}
```

**After**
```json
{
  "api_startup_ms": 2.538968999942881,
  "gpu_detect": {"device": "cpu", "runtime_ms": 0.335635000055845},
  "ingest_normalize_ms": 0.13584800012722553,
  "ingest_hash": "4dc2f75f0f3ec731",
  "stem_generate_ms": 202.01727699986805,
  "stem_count": 2
}
```

**Notes**
- GPU path reported `cpu` in this environment.
- The ingestion hash changed because the title changed ("Baseline" vs "After").

