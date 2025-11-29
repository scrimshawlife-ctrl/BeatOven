# BeatOven Stem Extraction & Management

## Overview

BeatOven provides comprehensive stem extraction and management capabilities:

1. **ML-Based Stem Separation**: Extract stems (drums, bass, vocals, etc.) from uploaded audio
2. **Emotional Tagging**: Analyze each stem for symbolic/emotional features
3. **Multi-Format Support**: WAV, FLAC, AIFF, ALAC, MP3, AAC, M4A, OGG, Opus
4. **High-Resolution Audio**: Support for 44.1kHz–192kHz, 16–32 bit
5. **Provenance Tracking**: Deterministic hash for each stem

## Supported Formats

### Input Formats
- **Lossless**: WAV, FLAC, AIFF, ALAC
- **Lossy**: MP3, AAC, M4A, OGG, Opus

### Sample Rates
- 44.1 kHz (CD quality)
- 48 kHz (Professional)
- 88.2 kHz
- 96 kHz
- 176.4 kHz
- 192 kHz (High-resolution)

### Bit Depths
- 16-bit (Standard)
- 24-bit (Professional)
- 32-bit (Studio)

## Stem Types

Available stem categories:

- **DRUMS**: Kick, snare, hi-hats, percussion
- **BASS**: Bass guitar, synth bass
- **VOCALS**: Lead vocals, backing vocals
- **OTHER**: Remaining instruments
- **PIANO**: Piano tracks
- **GUITAR**: Guitar tracks
- **STRINGS**: String instruments
- **SYNTH**: Synthesizers
- **LEADS**: Lead melodies
- **PADS**: Pad sounds, atmospheres
- **ATMOS**: Atmospheric elements
- **FULL_MIX**: Complete mix (no separation)

## Architecture

```
┌──────────────────────────────────────┐
│   Upload Audio File                  │
│   (WAV/FLAC/MP3/etc.)                │
└───────────────┬──────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   Audio I/O Layer                    │
│   Load + Validate + Normalize        │
└───────────────┬──────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   ML-Based Stem Extractor            │
│   (via Model-Agnostic Inference)     │
└───────────────┬──────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   Per-Stem Analysis                  │
│   Resonance • Density • Tension •    │
│   Emotional Index                    │
└───────────────┬──────────────────────┘
                ↓
┌──────────────────────────────────────┐
│   Export Stems                       │
│   WAV/FLAC/MP3/M4A                   │
│   + Metadata + Provenance            │
└──────────────────────────────────────┘
```

## API Endpoints

### Extract Stems
```http
POST /stems/extract
Content-Type: application/json

{
  "file_path": "/path/to/audio.wav",
  "stem_types": ["drums", "bass", "vocals", "other"]
}
```

Response:
```json
{
  "stems": [
    {
      "name": "track_drums",
      "stem_type": "drums",
      "sample_rate": 44100,
      "duration": 180.5,
      "shape": [2, 7942050],
      "symbolic_fields": {
        "resonance": 0.45,
        "density": 0.78,
        "tension": 0.62,
        "emotional_index": 0.55
      },
      "provenance_hash": "a3b7f2c9d4e1"
    },
    ...
  ],
  "count": 4
}
```

### Get Supported Formats
```http
GET /stems/formats
```

Returns:
```json
{
  "input_formats": ["wav", "flac", "aiff", "mp3", "aac", ...],
  "output_formats": ["wav", "flac", "mp3", "m4a"],
  "sample_rates": [44100, 48000, 96000, 192000],
  "bit_depths": [16, 24, 32]
}
```

## Usage Examples

### Python: Extract Stems

```python
from beatoven.audio import StemExtractor, StemType

extractor = StemExtractor(model_name="demucs", device="cuda")
extractor.load_model()

stems = extractor.extract_stems(
    "my_track.wav",
    stem_types=[
        StemType.DRUMS,
        StemType.BASS,
        StemType.VOCALS,
        StemType.OTHER
    ]
)

for stem in stems:
    print(f"{stem.name}:")
    print(f"  Resonance: {stem.resonance:.2f}")
    print(f"  Density: {stem.density:.2f}")
    print(f"  Tension: {stem.tension:.2f}")
    print(f"  Emotional Index: {stem.emotional_index:.2f}")
    print(f"  Provenance: {stem.provenance_hash}")
```

### Python: Load Audio

```python
from beatoven.audio import AudioIO

audio_data, sample_rate, metadata = AudioIO.load_audio("track.flac")

print(f"Sample Rate: {metadata.sample_rate} Hz")
print(f"Channels: {metadata.channels}")
print(f"Bit Depth: {metadata.bit_depth}")
print(f"Duration: {metadata.duration_seconds:.2f}s")
print(f"Format: {metadata.format.value}")
```

### Python: Save Stem

```python
from beatoven.audio import AudioIO, AudioFormat

AudioIO.save_audio(
    "stem_drums.flac",
    stem_audio_data,
    sample_rate=48000,
    format=AudioFormat.FLAC,
    bit_depth=24
)
```

## Emotional/Symbolic Analysis

Each extracted stem is analyzed for:

### Resonance
- Computed from spectral centroid
- Higher frequency content → higher resonance
- Range: 0.0–1.0

### Density
- Based on RMS energy
- Louder, more energetic stems → higher density
- Range: 0.0–1.0

### Tension
- Derived from zero-crossing rate
- More rapid changes → higher tension
- Range: 0.0–1.0

### Emotional Index (Hσ)
- Combined metric from PsyFi integration
- Averaged from resonance, density, tension
- Range: 0.0–1.0

Example analysis:
```python
stem = stems[0]  # Drums stem

print(f"Resonance: {stem.resonance:.3f}")  # 0.450
print(f"Density: {stem.density:.3f}")      # 0.780
print(f"Tension: {stem.tension:.3f}")      # 0.620
print(f"Hσ: {stem.emotional_index:.3f}")   # 0.617
```

## Model-Agnostic Inference

Stem extraction uses the BeatOven inference layer:

```python
from beatoven.core.inference import get_inference, InferenceBackend

# Auto-select best backend
inference = get_inference(InferenceBackend.TORCH)

# Or specify backend explicitly
inference = get_inference(InferenceBackend.ONNX)
```

Supported backends:
- **Torch**: PyTorch models
- **JAX**: JAX/Flax models
- **ONNX**: ONNX Runtime
- **NumPy**: CPU-only fallback

## Provenance

Each stem includes a deterministic provenance hash:

```python
stem.compute_provenance()
# Uses:
# - Stem name
# - Stem type
# - First/last 1000 audio samples
# Returns: "a3b7f2c9d4e1"
```

This ensures:
- Traceable lineage
- Reproducibility
- Anti-tampering verification

## No Reinterpretation Mode

When extracting stems from uploaded tracks:

- **Stems are separated as-is**
- **No generative recomposition**
- **Original audio preserved**
- **Metadata tagged**
- **Emotional analysis added**

This is a pure extraction service, not a generative reinterpretation.

## BeatOven-Generated Stems

All BeatOven generations export stems by default:

```python
from beatoven.core.stems import StemGenerator, StemType

generator = StemGenerator(seed=42)

stems = generator.generate_stems(
    duration=16.0,
    stem_types=[
        StemType.DRUMS,
        StemType.BASS,
        StemType.PADS,
        StemType.LEADS
    ]
)

# Each stem includes:
# - WAV/FLAC audio
# - Symbolic metadata
# - Provenance hash
# - Emotional analysis
```

## Mobile UI

The mobile app provides stem management:

### StemsScreen
- Waveform preview
- Audio playback
- Download stems
- View symbolic metadata

Navigate to stems:
```typescript
navigation.navigate('Stems', { jobId: 'gen_12345' });
```

## Monetization Tiers

### Free Tier
- 44.1kHz / 16-bit
- 4 stem types (drums, bass, vocals, other)
- WAV export

### Premium Tier
- Up to 192kHz / 32-bit
- 12+ stem types
- FLAC/ALAC lossless export
- Advanced stem categories
- Mastering chains
- GPU-accelerated processing

## Future Features

- Real-time stem separation
- Multi-track session export
- MIDI extraction from stems
- Stem layering/recombination (with reinterpretation)
- Advanced spectral editing
- Stem-to-symbolic reverse mapping
