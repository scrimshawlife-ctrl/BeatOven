# BeatOven Symbolic Mapping

## Overview

This document describes the mapping from symbolic ABX-Runes fields to concrete audio generation parameters across all BeatOven modules.

## ABX-Runes Fields

| Field | Range | Description |
|-------|-------|-------------|
| **Resonance** | 0.0-1.0 | Harmonic richness and sustain |
| **Density** | 0.0-1.0 | Event density and complexity |
| **Drift** | 0.0-1.0 | Temporal variation and evolution |
| **Tension** | 0.0-1.0 | Harmonic/rhythmic tension |
| **Contrast** | 0.0-1.0 | Dynamic range and variation |

## Mapping Tables

### Rhythm Engine

| ABX Field | Parameter | Mapping |
|-----------|-----------|---------|
| density | events_per_beat | 0.5 + density * 2.0 |
| density | grid_resolution | 16th (< 0.3), 8th (< 0.6), 32nd (> 0.6) |
| tension | syncopation | tension * 0.5 |
| tension | euclidean_rotation | int(tension * steps * 0.25) |
| drift | velocity_variance | drift * 0.3 |
| drift | timing_humanize | drift * 0.02 beats |
| contrast | accent_strength | 0.7 + contrast * 0.3 |

### Harmonic Engine

| ABX Field | Parameter | Mapping |
|-----------|-----------|---------|
| resonance | chord_extensions | 7ths if resonance > 0.7 |
| resonance | voicing_spread | resonance * 24 semitones |
| tension | dissonance_level | tension * 0.5 |
| tension | modal_interchange | probability = tension * 0.3 |
| contrast | velocity_range | 0.3 + contrast * 0.6 |
| contrast | inversion_variety | inversions if contrast > 0.3 |

### Timbre Engine

| ABX Field | Parameter | Mapping |
|-----------|-----------|---------|
| resonance | filter_resonance | 0.5 + resonance * 1.5 |
| resonance | reverb_amount | resonance * 0.6 |
| density | oscillator_type | sine (< 0.3), saw (< 0.6), square (> 0.6) |
| density | harmonic_count | 1 + int(density * 8) |
| drift | lfo_depth | drift * 0.5 |
| tension | filter_cutoff | 500 + (1 - tension) * 8000 Hz |
| tension | envelope_attack | 0.01 + (1 - tension) * 0.2 s |

### Motion Engine

| ABX Field | Parameter | Mapping |
|-----------|-----------|---------|
| drift | lfo_rate | 0.5 + drift * 2.0 Hz |
| drift | automation_complexity | drift * 0.8 |
| resonance | modulation_depth | resonance * 0.6 |
| tension | envelope_shape | percussive (> 0.6), sustained (< 0.6) |

### Stem Generator

| ABX Field | Parameter | Mapping |
|-----------|-----------|---------|
| density | layer_count | 3 + int(density * 4) |
| resonance | stem_reverb | resonance * 0.4 |
| contrast | stem_compression | contrast * 0.5 |

## Extended Field Vectors

Each primary field has an extended vector for fine-grained control:

### Resonance Spectrum (16 dims)
Maps to frequency-specific resonance:
- dims 0-3: Sub-bass resonance (20-80 Hz)
- dims 4-7: Bass resonance (80-300 Hz)
- dims 8-11: Mid resonance (300-2000 Hz)
- dims 12-15: High resonance (2000-20000 Hz)

### Density Layers (8 dims)
Maps to per-layer event density:
- dim 0: Drums density
- dim 1: Bass density
- dim 2: Leads density
- dim 3: Mids density
- dim 4: Pads density
- dim 5: Atmos density
- dim 6: FX density
- dim 7: Percussion density

### Drift Curves (8 dims)
Maps to temporal evolution:
- dims 0-1: Short-term drift (< 1 bar)
- dims 2-3: Medium-term drift (1-4 bars)
- dims 4-5: Long-term drift (4-16 bars)
- dims 6-7: Global drift envelope

### Tension Harmonics (12 dims)
Maps to per-scale-degree tension:
- dim 0: Tonic (I)
- dim 1: Supertonic (ii)
- dim 2: Mediant (iii)
- dim 3: Subdominant (IV)
- dim 4: Dominant (V)
- dim 5: Submediant (vi)
- dim 6: Leading tone (vii°)
- dims 7-11: Extensions and alterations

### Contrast Dynamics (8 dims)
Maps to dynamic contrast:
- dims 0-1: Velocity contrast
- dims 2-3: Frequency contrast
- dims 4-5: Stereo contrast
- dims 6-7: Temporal contrast

## PsyFi Emotional Modulation

Emotional vectors modulate ABX fields:

| Emotion | Affects | Direction |
|---------|---------|-----------|
| Valence (+) | resonance | + |
| Valence (+) | brightness | + |
| Valence (-) | tension | + |
| Arousal (+) | density | + |
| Arousal (+) | drift | + |
| Arousal (-) | resonance | + |
| Dominance (+) | contrast | + |
| Tension (+) | tension | + |
| Depth (+) | resonance | + |
| Warmth (+) | filter_cutoff | - |
| Brightness (+) | filter_cutoff | + |
| Movement (+) | drift | + |

## Transformation Pipeline

```
Input Intent + Mood Tags + Seed
        │
        ▼
┌───────────────────┐
│  Intent Encoding  │  → 128-dim vector
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Mood Encoding   │  → 32-dim vector
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Rune Generation  │  → 64-dim vector
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Symbolic Concat   │  → 242-dim combined
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Translation     │  → 5 primary + 52 extended
│   (projection)    │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ ABX Compression   │  → entropy minimized
└───────────────────┘
        │
        ▼
   ABX-Runes Fields
```

## Determinism Guarantee

For identical:
- Text intent
- Mood tags (name + intensity)
- Seed string

The symbolic mapping produces **identical** ABX-Runes fields, which in turn produce **identical** audio output.

## Examples

### "Dark Ambient Pad"

Input:
- Intent: "dark ambient pad"
- Moods: [("dark", 0.8), ("ambient", 0.9)]
- Seed: "example_1"

Output ABX Fields:
- Resonance: 0.72
- Density: 0.28
- Drift: 0.65
- Tension: 0.35
- Contrast: 0.41

### "Aggressive Industrial Beat"

Input:
- Intent: "aggressive industrial beat"
- Moods: [("aggressive", 0.9), ("dark", 0.7)]
- Seed: "example_2"

Output ABX Fields:
- Resonance: 0.35
- Density: 0.78
- Drift: 0.42
- Tension: 0.82
- Contrast: 0.71

### "Ethereal Melodic Progression"

Input:
- Intent: "ethereal melodic progression"
- Moods: [("ethereal", 0.85), ("peaceful", 0.7)]
- Seed: "example_3"

Output ABX Fields:
- Resonance: 0.88
- Density: 0.35
- Drift: 0.71
- Tension: 0.22
- Contrast: 0.48
