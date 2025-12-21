# ABX-Runes Quickstart

## Validate rune manifests

```bash
python -m beatoven.registry list
python -m beatoven.registry validate
```

## Run a rune via the runtime orchestrator

```python
from beatoven.runtime.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run_rune(
    "engine.rhythm.generate",
    {
        "density": 0.5,
        "tension": 0.4,
        "drift": 0.2,
        "tempo": 120,
        "length_bars": 4,
    },
    seed=4242,
)

print(result.output)
print(result.manifest)
```

## Update rune manifests

- Add new manifests under `beatoven/runes/`.
- Keep inputs/outputs aligned with JSON schema in `beatoven/schema/`.
- Provide golden vector references under `beatoven/runes/test_vectors/`.
