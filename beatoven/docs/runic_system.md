# BeatOven Runic System

## Overview

The Runic System provides symbolic mapping between abstract concepts and generative parameters through ABX-Runes vectors. This system ensures deterministic, reproducible generation while maintaining semantic meaning.

## ABX-Runes Vector

The ABX-Runes vector is a 64-dimensional floating-point array derived deterministically from a seed string:

```python
from beatoven.core.input import ABXRunesSeed

seed = ABXRunesSeed("my_creative_seed")
print(seed.rune_vector.shape)  # (64,)
print(seed.numeric_seed)  # Deterministic integer
```

### Generation Process

1. **String → Hash**: SHA-256 hash of seed string
2. **Hash → Numeric Seed**: First 8 bytes as integer
3. **Numeric Seed → RNG**: NumPy default_rng initialization
4. **RNG → Vector**: 64 uniform values in [-1, 1]

## ABX-Runes Semantic Fields

The Symbolic Translator converts input vectors into five core semantic fields:

### Resonance (0.0 - 1.0)
- **Low**: Dry, percussive, short decay
- **High**: Rich harmonics, long sustain, lush

Affects:
- Reverb amount
- Harmonic content
- Sustain envelopes
- Spectral richness

### Density (0.0 - 1.0)
- **Low**: Sparse, minimal, spacious
- **High**: Busy, complex, layered

Affects:
- Event frequency
- Voice count
- Rhythmic complexity
- Textural layers

### Drift (0.0 - 1.0)
- **Low**: Static, stable, unchanging
- **High**: Evolving, morphing, dynamic

Affects:
- LFO rates and depths
- Parameter automation
- Timbral evolution
- Temporal variation

### Tension (0.0 - 1.0)
- **Low**: Relaxed, resolved, consonant
- **High**: Anxious, dissonant, unresolved

Affects:
- Harmonic dissonance
- Rhythmic syncopation
- Filter resonance
- Envelope attack

### Contrast (0.0 - 1.0)
- **Low**: Even, consistent, flat
- **High**: Dynamic, varied, dramatic

Affects:
- Velocity range
- Dynamic range
- Structural variation
- Textural diversity

## Extended Field Vectors

Each primary field has an extended vector for fine-grained control:

```python
fields = translator.translate(...)

# Extended vectors
fields.resonance_spectrum  # (16,) - frequency-specific resonance
fields.density_layers      # (8,) - per-layer density
fields.drift_curves        # (8,) - drift behavior over time
fields.tension_harmonics   # (12,) - per-harmonic tension
fields.contrast_dynamics   # (8,) - dynamic contrast curves
```

## Runic Modulation

The Motion Engine supports runic modulation for parameter automation:

```python
from beatoven.core.motion import RunicModulation

mod = RunicModulation(
    rune_vector=seed.rune_vector,
    target_param="filter_cutoff",
    influence=0.5
)

# Apply modulation
modulated_value = mod.apply(base_value=0.5, time=1.5)
```

The rune vector is sampled over time to create evolving modulation.

## Runic Visual Signatures

The RunicVisualExporter generates deterministic visual representations:

### Glyph Types (16 variants)
0. Vertical line
1. Horizontal line
2. Diagonal
3. Anti-diagonal
4. Triangle down
5. Triangle up
6. Left angle
7. Right angle
8. Diamond
9. Square
10. Rotated square
11. Hexagon
12. Y shape
13. Arrow
14. Cross
15. Complex polygon

### Color Palettes
- **Positive** (valence > 0.3): Gold, orange, light tones
- **Negative** (valence < -0.3): Violet, indigo, dark tones
- **Energetic** (arousal > 0.5): Red, orange-red, warm
- **Neutral**: Silver, steel blue, lavender

### Visual Elements
- **Glyphs**: Positioned by vector values, sized by intensity
- **Spectral Ring**: Circular visualization of spectral data
- **Border Pattern**: Derived from rune vector

## Determinism Guarantees

All runic operations are deterministic:

```python
# Same seed always produces same results
seed1 = ABXRunesSeed("test")
seed2 = ABXRunesSeed("test")

assert seed1.numeric_seed == seed2.numeric_seed
assert np.array_equal(seed1.rune_vector, seed2.rune_vector)

# Same inputs always produce same outputs
fields1 = translator.translate(intent, mood, seed1.rune_vector, style)
fields2 = translator.translate(intent, mood, seed2.rune_vector, style)

assert fields1.resonance == fields2.resonance
assert fields1.provenance_hash == fields2.provenance_hash
```

## Entropy Compression

ABX-Core applies entropy compression to reduce noise:

```python
# Compression formula
compressed = mean + compression_factor * (value - mean)

# With compression_factor = 0.8:
# Values are pulled 20% toward the mean
```

This ensures more consistent, less chaotic output while preserving musical variation.

## Integration with Other Systems

### PsyFi Integration
Emotional vectors modulate runic fields:
- Valence affects resonance and brightness
- Arousal affects density and motion
- Tension directly maps to harmonic tension

### Echotome Integration
Rune vectors influence steganographic salting:
- Salt positions derived from rune vector
- Pattern selection based on entropy
- Verification hashes include runic provenance

### Phonomicon Integration
Event Horizon uses runic entropy for rarity:
- Entropy deviations flagged as rare events
- Runic signatures included in NFT metadata
- Provenance chain includes rune hashes
