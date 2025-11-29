# BeatOven

**Modular Generative Music Engine**

A Eurorack-inspired generative music system built on ABX-Core v1.2 and enforced by SEED Protocol for deterministic, reproducible output. Part of the Applied Alchemy Labs (AAL) ecosystem.

## Features

### Core Engine
- **Modular Architecture**: Eurorack-inspired module system with PatchBay routing
- **Deterministic Generation**: Same inputs always produce identical outputs
- **ABX-Core v1.2**: Structured, entropy-minimizing framework
- **SEED Protocol**: Complete provenance tracking and reproducibility
- **GPU Acceleration**: CUDA and Apple Silicon (MPS) support
- **API-First**: FastAPI backend with comprehensive endpoints
- **AAL Interoperability**: Clean hooks for PsyFi, Phonomicon, Echotome, and more

### Signal Intake System (NEW)
- **Multi-Source Ingestion**: RSS/Atom feeds, JSON APIs, HTML scraping, text files, PDFs, epub, calendar (ICS), tasks
- **Universal Normalization**: All inputs converted to unified SignalDocument format
- **30+ Source Categories**: World news, technology, AI/ML, sports (NBA, NFL, MLB, NHL), markets, culture, science, personal data
- **Symbolic Interpretation**: Automatic mapping to ABX-Runes fields (resonance, density, tension, etc.)
- **Background Polling**: Configurable ingestion intervals with caching
- **Provenance Tracking**: SHA-256 hashing for all ingested signals

### Stem Extraction Service (NEW)
- **ML-Based Separation**: Extract drums, bass, vocals, and 9+ other stem types from uploaded audio
- **Multi-Format Support**: WAV, FLAC, AIFF, ALAC, MP3, AAC, M4A, OGG, Opus
- **High-Resolution Audio**: 44.1kHz–192kHz sample rates, 16–32 bit depth
- **Emotional Analysis**: Automatic computation of resonance, density, tension, emotional index for each stem
- **No Reinterpretation**: Pure extraction service preserving original audio
- **Model-Agnostic Inference**: Supports PyTorch, JAX, ONNX backends

### Ringtone & Notification Generation (NEW)
- **Short-Form Audio**: Generate 1-30 second ringtones and notifications
- **Three Modes**: Notification (1-5s), Short Ringtone (10-15s), Standard Ringtone (20-30s)
- **Configurable Output**: Melodic/percussive toggles, intensity control, seamless looping
- **Mobile-Optimized**: Export to M4R, MP3, WAV for iOS and Android
- **Deterministic**: Same parameters always produce identical output

### Mobile UI
- **React Native (Expo, TypeScript)** app for iOS and Android
- **Dark/Light Themes**: Full theme switching with persistent preferences
- **Connection Monitoring**: Auto-polling backend health indicator
- **Preset Management**: Save and load module configurations
- **Animated Waveforms**: Visual playback with animated playheads

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/appliedalchemy/beatoven.git
cd beatoven

# Install with pip
pip install -e .

# Or with all dependencies
pip install -e ".[all]"
```

### Run the API Server

```bash
# Local development
./scripts/run_local.sh

# With GPU acceleration
./scripts/run_gpu.sh
```

The API will be available at `http://localhost:8000`. Documentation at `/docs`.

### Run the Mobile App

```bash
cd beatoven-ui

# Install dependencies
npm install

# Start Expo development server
npx expo start

# Run on iOS simulator
npx expo start --ios

# Run on Android emulator
npx expo start --android
```

### Basic Usage

```python
from beatoven.core.input import InputModule, MoodTag, ABXRunesSeed
from beatoven.core.translator import SymbolicTranslator
from beatoven.core.rhythm import RhythmEngine
from beatoven.core.harmony import HarmonicEngine, Scale
from beatoven.core.stems import StemGenerator, StemType

# Initialize modules
input_module = InputModule()
translator = SymbolicTranslator()
rhythm_engine = RhythmEngine(seed=42)
harmony_engine = HarmonicEngine(seed=42)
stem_generator = StemGenerator(seed=42)

# Process input
symbolic = input_module.process(
    text_intent="create a dark ambient pad with subtle rhythm",
    mood_tags=[MoodTag("dark", 0.8), MoodTag("ambient", 0.9)],
    abx_seed=ABXRunesSeed("my_creative_seed")
)

# Translate to ABX-Runes fields
fields = translator.translate(
    intent_embedding=symbolic.intent_embedding,
    mood_vector=symbolic.mood_vector,
    rune_vector=symbolic.rune_vector,
    style_vector=symbolic.style_vector
)

print(f"Resonance: {fields.resonance:.2f}")
print(f"Density: {fields.density:.2f}")
print(f"Tension: {fields.tension:.2f}")

# Generate rhythm
pattern, rhythm_desc = rhythm_engine.generate(
    density=fields.density,
    tension=fields.tension,
    tempo=90.0
)

# Generate harmony
progression, harmony_desc = harmony_engine.generate(
    resonance=fields.resonance,
    tension=fields.tension,
    scale=Scale.MINOR
)

# Generate stems
stems = stem_generator.generate_stems(
    duration=16.0,
    stem_types=[StemType.DRUMS, StemType.BASS, StemType.PADS]
)

print(f"Generated {len(stems)} stems")
print(f"Provenance: {fields.provenance_hash}")
```

### Signal Intake Usage

```python
from beatoven.signals import FeedIngester, SourceCategory, SignalNormalizer
from beatoven.signals.feeds import get_predefined_groups

# Initialize ingester
ingester = FeedIngester()

# Ingest from predefined groups
groups = get_predefined_groups()
tech_group = next(g for g in groups if g.name == "Technology News")

for source in tech_group.sources:
    signals = ingester.ingest_rss_feed(source.url, tech_group.category)
    for signal in signals:
        print(f"{signal.title}")
        print(f"  Resonance: {signal.resonance:.2f}")
        print(f"  Density: {signal.density:.2f}")
        print(f"  Tension: {signal.tension:.2f}")
        print(f"  Provenance: {signal.provenance_hash}")

# Ingest from custom text
text_signal = SignalNormalizer.normalize_text(
    text="Breaking: AI model achieves breakthrough in music generation",
    category=SourceCategory.AI_ML
)
print(f"Text signal emotional index: {text_signal.emotional_index:.2f}")
```

### Stem Extraction Usage

```python
from beatoven.audio import StemExtractor, StemType, AudioIO

# Initialize extractor
extractor = StemExtractor(model_name="demucs", device="cuda")
extractor.load_model()

# Extract stems from uploaded track
stems = extractor.extract_stems(
    "uploaded_track.mp3",
    stem_types=[
        StemType.DRUMS,
        StemType.BASS,
        StemType.VOCALS,
        StemType.OTHER
    ]
)

for stem in stems:
    print(f"\n{stem.name}:")
    print(f"  Duration: {stem.duration:.2f}s")
    print(f"  Sample Rate: {stem.sample_rate}Hz")
    print(f"  Resonance: {stem.resonance:.3f}")
    print(f"  Density: {stem.density:.3f}")
    print(f"  Tension: {stem.tension:.3f}")
    print(f"  Emotional Index: {stem.emotional_index:.3f}")

    # Save stem to FLAC
    AudioIO.save_audio(
        f"{stem.name}.flac",
        stem.audio_data,
        sample_rate=stem.sample_rate,
        bit_depth=24
    )
```

### Ringtone Generation Usage

```python
from beatoven.core.ringtone import RingtoneGenerator, RingtoneType
from beatoven.audio import AudioIO, AudioFormat

# Initialize generator
generator = RingtoneGenerator(seed=42)

# Generate notification sound
notification = generator.generate_notification(
    duration_seconds=2.0,
    melodic=True,
    intensity=0.7
)

# Save as M4R for iOS
AudioIO.save_audio(
    "notification.m4r",
    notification,
    sample_rate=44100,
    format=AudioFormat.M4A
)

# Generate standard ringtone
ringtone = generator.generate_ringtone(
    duration_seconds=25.0,
    melodic=True,
    percussive=True,
    intensity=0.8,
    loop=True
)

# Save as MP3 for Android
AudioIO.save_audio(
    "ringtone.mp3",
    ringtone,
    sample_rate=48000,
    format=AudioFormat.MP3
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BeatOven Engine                         │
├─────────────────────────────────────────────────────────────┤
│  Input Module → Symbolic Translator → ABX-Runes Fields      │
│                         ↓                                    │
│         ┌───────────────┼───────────────┐                   │
│         ↓               ↓               ↓                   │
│   Rhythm Engine   Harmonic Engine   Motion Engine           │
│         └───────────────┼───────────────┘                   │
│                         ↓                                    │
│                   Timbre Engine                              │
│                         ↓                                    │
│                  Stem Generator                              │
│         ┌───────────────┼───────────────┐                   │
│         ↓               ↓               ↓                   │
│   Event Horizon   Echotome Hooks   Runic Export             │
└─────────────────────────────────────────────────────────────┘
```

## Mobile App (beatoven-ui)

The React Native app provides the primary user interface:

| Screen | Description |
|--------|-------------|
| **Home** | Quick generate, recent renders, presets |
| **PatchBay** | Visual node graph of module signal flow |
| **Module** | Configure rhythm, harmony, timbre, motion parameters |
| **Stems** | Waveform previews, playback, download |
| **Symbolic** | Live ABX-Runes field visualization |
| **Signals** | Multi-source signal intake, feed management, recent signals |
| **Ringtone** | Generate notifications and ringtones (1-30s), export to mobile |
| **Settings** | Backend URL, device mode, theme switching |

### Design Language

- Dark UI with high contrast
- Geometric blocks
- Single accent color (#00D9FF)
- No skeuomorphic elements

### Running Tests

```bash
cd beatoven-ui
npm test
```

## Core Modules

| Module | Description |
|--------|-------------|
| **InputModule** | Processes text intent, mood tags, and seeds into symbolic vectors |
| **SymbolicTranslator** | Converts vectors to ABX-Runes fields (resonance, density, drift, tension, contrast) |
| **RhythmEngine** | Euclidean patterns, polyrhythms, swing, velocity curves |
| **HarmonicEngine** | Scales, modes, chord progressions, modal interchange |
| **TimbreEngine** | Oscillators, filters, FM/granular synthesis, effects |
| **MotionEngine** | LFOs, envelopes, automation curves, runic modulation |
| **StemGenerator** | Bounces stems (drums, bass, leads, pads, atmos) to WAV/FLAC |
| **EventHorizonDetector** | Identifies rare sonic events for NFT metadata |
| **PsyFiIntegration** | Emotional vector modulation across engines |
| **EchotomeHooks** | Steganographic preparation for audio provenance |
| **RunicVisualExporter** | Generates deterministic runic signature images |
| **PatchBay** | Node-graph signal routing with hot-reload |

## PatchBay System

BeatOven uses a Eurorack-inspired routing system:

```yaml
# patches/my_patch.yaml
name: custom_patch
version: "1.0"
nodes:
  - id: input
    type: INPUT
    outputs: [symbolic]
  - id: rhythm
    type: PROCESSOR
    inputs: [symbolic]
    outputs: [events, audio]
connections:
  - source: input:symbolic
    dest: rhythm:symbolic
```

```python
from beatoven.core.patchbay import PatchBay

patchbay = PatchBay()
patchbay.load_from_file("patches/my_patch.yaml")

# Inspect signal flow
flow = patchbay.inspect_flow()
print(f"Execution order: {flow['execution_order']}")
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/generate` | POST | Full generation pipeline |
| `/translate` | POST | Input to ABX-Runes translation |
| `/rhythm` | POST | Rhythm-only generation |
| `/harmony` | POST | Harmony-only generation |
| `/psyfi/modulate` | POST | Emotional modulation |
| `/patchbay/flow` | GET | Signal flow inspection |
| `/runic/generate` | POST | Runic signature generation |
| `/signals/ingest` | POST | Ingest signals from URL or text |
| `/signals/groups` | GET | Get predefined source groups |
| `/signals/categories` | GET | List available source categories |
| `/stems/extract` | POST | Extract stems from uploaded audio |
| `/stems/formats` | GET | Get supported audio formats |
| `/ringtone/generate` | POST | Generate ringtone or notification |
| `/ringtone/types` | GET | List ringtone types |
| `/config` | GET | System configuration |

## ABX-Runes Fields

| Field | Range | Description |
|-------|-------|-------------|
| **Resonance** | 0.0-1.0 | Harmonic richness and sustain |
| **Density** | 0.0-1.0 | Event density and complexity |
| **Drift** | 0.0-1.0 | Temporal variation and evolution |
| **Tension** | 0.0-1.0 | Harmonic/rhythmic tension level |
| **Contrast** | 0.0-1.0 | Dynamic range and variation |

## AAL Ecosystem Integration

BeatOven provides clean interoperability hooks for:

- **PsyFi**: Emotional intelligence and Hσ emotional vectors
- **Phonomicon**: NFT metadata and rarity scoring
- **Dream Engine (Somnus-1)**: Dream-state audio generation
- **Neon Genie**: Visual generation coordination
- **Echotome**: Audio steganography and provenance
- **Abraxas Engine**: Advanced synthesis (future)

## GPU Support

```python
from beatoven.gpu import DeviceManager, is_gpu_available

if is_gpu_available():
    manager = DeviceManager()
    print(f"Using: {manager.get_device().name}")
```

Supports:
- NVIDIA CUDA (GTX 10-series+, RTX, Tesla, A-series)
- Apple Silicon MPS (M1/M2/M3)
- CPU fallback (always available)

## Testing

```bash
# Run all tests
pytest beatoven/tests/ -v

# Run specific module tests
pytest beatoven/tests/test_rhythm.py -v

# Run with coverage
pytest --cov=beatoven beatoven/tests/
```

## Documentation

- [Architecture](beatoven/docs/architecture.md)
- [Modules](beatoven/docs/modules.md)
- [Runic System](beatoven/docs/runic_system.md)
- [Symbolic Mapping](beatoven/docs/symbolic_mapping.md)
- [Provenance](beatoven/docs/provenance.md)
- [GPU Support](beatoven/docs/gpu.md)
- [Mobile Integration](beatoven/docs/mobile.md)
- [Signal Intake System](beatoven/docs/signals.md) - Multi-source signal ingestion and normalization
- [Stem Extraction](beatoven/docs/stems.md) - ML-based audio separation with emotional analysis

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file.

### Open-Core Model

This repository contains the open-source core of BeatOven. The following components are proprietary and not included:

- ABX-Core advanced optimizers
- Symbolic Translator trained models
- Runic modulation advanced logic
- PsyFi deep learning components
- NFT rarity detector core
- Echotome cryptographic implementation
- Advanced GPU model architectures
- Commercial expansion packs

See [NOTICE](NOTICE) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to the main branch.

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: See the `/docs` directory
- API Docs: Run the server and visit `/docs`

---

**BeatOven** - Generative music, deterministically forged.

*Part of the Applied Alchemy Labs ecosystem.*
