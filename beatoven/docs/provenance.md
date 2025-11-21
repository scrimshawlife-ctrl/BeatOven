# BeatOven Provenance System

## Overview

The provenance system ensures complete traceability and reproducibility of all generated content through the SEED Protocol (Secure, Entropy-controlled, Evidential Determinism).

## Provenance Chain

Every BeatOven output includes a provenance hash chain:

```
Input Provenance
      │
      ▼
Translation Provenance
      │
      ▼
Generation Provenance (per module)
      │
      ▼
Stem Provenance (per stem)
      │
      ▼
Output Provenance (final)
```

## Hash Computation

### Input Provenance

```python
# Computed from all input parameters
data = {
    "text_intent": "create ambient beat",
    "mood_tags": [("calm", 0.8)],
    "abx_seed": "my_seed",
    "has_audio_features": False
}
provenance = sha256(json.dumps(data, sort_keys=True))
```

### Translation Provenance

```python
# Includes ABX-Runes fields + input provenance
data = f"{resonance}:{density}:{drift}:{tension}:{contrast}:{input_provenance}"
provenance = sha256(data)
```

### Module Provenance

Each engine computes its own provenance:

```python
# Rhythm Engine example
data = f"{seed}:{density}:{tension}:{drift}:{tempo}:{time_signature}:{length}:{swing}:{layers}"
provenance = sha256(data)
```

### Stem Provenance

```python
# Direct hash of audio samples
provenance = sha256(stem.samples.tobytes())
```

## Determinism Requirements

### Floating-Point Precision

All floating-point values are truncated to 6 decimal places for consistent hashing:

```python
# In provenance computation
value = f"{param:.6f}"
```

### RNG Protocol

All random number generation uses NumPy's default_rng with explicit seeds:

```python
# Always initialize from seed
rng = np.random.default_rng(seed)

# Never use global random state
# Never use time-based seeds
```

### Execution Order

The PatchBay guarantees deterministic execution order through topological sorting:

```python
# Sorted by node ID for determinism
queue.sort()
```

## Verification

### Reproducing Output

```python
# Save provenance
job_data = {
    "text_intent": "ambient pad",
    "seed": "my_seed",
    "parameters": {...},
    "provenance": output_provenance
}

# Later reproduction
new_output = beatoven.generate(**job_data["parameters"])
assert new_output.provenance == job_data["provenance"]
```

### Stem Verification

```python
# Verify stem integrity
computed_hash = sha256(stem.samples.tobytes())
assert computed_hash == stem.metadata.provenance_hash
```

### Echotome Verification

```python
# Verify salted audio
is_valid = echotome.verify_stem(audio, metadata)
```

## Provenance Ledger

The system maintains a provenance ledger (optional):

```yaml
# configs/seed.yaml
ledger:
  enabled: true
  format: "json"
  path: "./provenance_ledger.json"
  max_entries: 10000
```

Ledger format:

```json
{
  "entries": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "job_id": "abc123",
      "input_provenance": "sha256:...",
      "output_provenance": "sha256:...",
      "parameters": {...}
    }
  ]
}
```

## Cross-Module Provenance

### Phonomicon Export

```python
phonomicon_data = {
    "provenance": master_hash,
    "stem_hashes": {
        "drums": "sha256:...",
        "bass": "sha256:...",
        ...
    },
    "rarity_provenance": rarity_metadata.provenance_hash
}
```

### Echotome Package

```python
package = {
    "master_hash": "sha256:...",
    "provenance_chain": [
        "input_hash",
        "translation_hash",
        "generation_hash",
        "salt_hash"
    ]
}
```

## Best Practices

### For Reproducibility

1. Always specify explicit seeds
2. Store complete parameter sets
3. Record provenance hashes
4. Use consistent floating-point precision

### For Verification

1. Verify stem hashes on load
2. Check provenance chain integrity
3. Validate against stored hashes
4. Test determinism in CI

### For Debugging

1. Log provenance at each stage
2. Compare hashes between runs
3. Identify divergence points
4. Check RNG state consistency

## API Provenance

All API responses include provenance:

```python
response = {
    "job_id": "abc123",
    "provenance_hash": "sha256:...",
    "stems_generated": ["drums", "bass"],
    ...
}
```

Query provenance:

```
GET /config
{
    "provenance_tracking": true,
    "hash_algorithm": "sha256"
}
```
