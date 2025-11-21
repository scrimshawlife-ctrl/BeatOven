# BeatOven Architecture

## Overview

BeatOven is a modular generative music engine inspired by Eurorack modular synthesis systems. It provides a complete pipeline from text intent to audio stems, with deterministic behavior and comprehensive provenance tracking.

## Core Principles

### ABX-Core v1.2
- **Structured**: Clear module boundaries and interfaces
- **Modular**: Independent, replaceable components
- **Entropy-minimizing**: Noise compression throughout the pipeline

### SEED Protocol
- **Provenance**: Every output has a traceable hash chain
- **Determinism**: Same inputs always produce same outputs
- **Reproducibility**: Any generation can be recreated from its seed

### ERS Runtime
- **Energy-Resonance Scheduling**: Optimized hot paths
- **RAM-resident mode**: Low-latency generation
- **GPU/CPU adaptive**: Automatic device selection

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BeatOven Engine                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌─────────────┐    ┌──────────────────┐   │
│  │  Input   │───▶│  Symbolic   │───▶│   ABX-Runes      │   │
│  │  Module  │    │  Translator │    │   Fields         │   │
│  └──────────┘    └─────────────┘    └────────┬─────────┘   │
│                                               │              │
│                         ┌─────────────────────┼──────┐      │
│                         │                     │      │      │
│                         ▼                     ▼      ▼      │
│                  ┌──────────┐          ┌──────────┐ ┌────┐  │
│                  │ Rhythm   │          │ Harmonic │ │Motion│  │
│                  │ Engine   │          │ Engine   │ │Engine│  │
│                  └────┬─────┘          └────┬─────┘ └──┬──┘  │
│                       │                     │          │     │
│                       └──────────┬──────────┘          │     │
│                                  │                     │     │
│                                  ▼                     │     │
│                           ┌──────────┐                 │     │
│                           │ Timbre   │◀────────────────┘     │
│                           │ Engine   │                       │
│                           └────┬─────┘                       │
│                                │                             │
│                                ▼                             │
│                         ┌────────────┐                       │
│                         │   Stem     │                       │
│                         │ Generator  │                       │
│                         └────┬───────┘                       │
│                              │                               │
│              ┌───────────────┼───────────────┐              │
│              │               │               │              │
│              ▼               ▼               ▼              │
│       ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│       │  Event   │    │ Echotome │    │  Runic   │        │
│       │ Horizon  │    │  Hooks   │    │ Export   │        │
│       └──────────┘    └──────────┘    └──────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### Input Module
Accepts:
- Text intent (natural language)
- Mood tags with intensity
- ABX-Runes seed string
- Optional audio style reference

Outputs:
- 128-dim intent embedding
- 32-dim mood vector
- 64-dim rune vector
- 18-dim style vector
- Provenance hash

### Symbolic Translator
Converts symbolic vectors into ABX-Runes semantic fields:
- **Resonance**: Harmonic richness (0-1)
- **Density**: Event complexity (0-1)
- **Drift**: Temporal evolution (0-1)
- **Tension**: Harmonic tension (0-1)
- **Contrast**: Dynamic range (0-1)

### Rhythm Engine
- Euclidean pattern generation
- Polymeter/polyrhythm support
- Swing and groove templates
- Velocity curves and accents
- MIDI-like event output

### Harmonic Engine
- Scale and mode selection
- Chord progression generation
- Modal interchange
- PsyFi emotional modulation
- ABX-Core noise compression

### Timbre Engine
- Multi-waveform oscillators
- FM, granular, subtractive synthesis
- Filter chain (biquad filters)
- Effects: reverb, delay, spectral
- PatchBay integration

### Motion Engine
- LFOs (multiple shapes)
- ADSR envelopes
- Automation curves
- Runic modulation support

### Stem Generator
- Drum, bass, lead, mid, pad, atmos stems
- WAV/FLAC export
- Mel-spectrogram for ONNX
- Per-stem provenance hash

### Event Horizon Detector
- Spectral anomaly detection
- Runic entropy deviation
- Emotional discontinuity
- Rarity metadata for Phonomicon

### PsyFi Integration
- Emotional vector input (Hσ model)
- Parameter modulation mapping
- Cross-engine emotional influence

### Echotome Hooks
- Steganographic salt preparation
- Multiple salt patterns (LSB, phase, spectral)
- Verification hash computation

### Runic Visual Exporter
- Deterministic glyph generation
- SVG and raster output
- Spectral ring visualization
- Color palette from emotion

## PatchBay System

The PatchBay provides a node-graph routing abstraction:

```yaml
nodes:
  - id: input
    type: INPUT
    outputs: [symbolic]
  - id: rhythm
    type: PROCESSOR
    inputs: [symbolic]
    outputs: [events, audio]
  - id: mixer
    type: MIXER
    inputs: [drums, harmony, timbre]
    outputs: [master]
  - id: output
    type: OUTPUT
    inputs: [audio]

connections:
  - source: input:symbolic
    dest: rhythm:symbolic
  - source: rhythm:audio
    dest: mixer:drums
```

Features:
- JSON/YAML patch descriptors
- Hot-reload routing
- Deterministic execution order (topological sort)
- Signal flow inspection

## Data Flow

1. **Input Processing**
   - Text → keyword extraction → intent embedding
   - Moods → vocabulary lookup → mood vector
   - Seed → SHA-256 → numeric seed → rune vector

2. **Translation**
   - Combined vector → projection matrices → ABX-Runes fields
   - Entropy compression applied

3. **Generation**
   - Fields → engine parameters
   - Deterministic generation with seed-based RNG
   - Cross-module parameter sharing via PatchBay

4. **Output**
   - Audio stems with provenance
   - Rarity metadata
   - Runic visual signature

## API Architecture

```
FastAPI Application
├── /health          - System health check
├── /generate        - Full generation pipeline
├── /translate       - Input to ABX-Runes translation
├── /rhythm          - Rhythm-only generation
├── /harmony         - Harmony-only generation
├── /psyfi/modulate  - Emotional modulation
├── /patchbay/flow   - Signal flow inspection
├── /patchbay/load   - Load patch configuration
├── /runic/generate  - Runic signature generation
└── /config          - System configuration
```

## GPU Support

- PyTorch CUDA for NVIDIA GPUs
- MPS for Apple Silicon
- Automatic CPU fallback
- Runpod cloud execution support
