# BeatOven

**Modular Generative Music Engine**

A Eurorack-inspired generative music system built on ABX-Core v1.2 and enforced by SEED Protocol for deterministic, reproducible output. Part of the Applied Alchemy Labs (AAL) ecosystem.

## Features

- **Modular Architecture**: Eurorack-inspired module system with PatchBay routing
- **Deterministic Generation**: Same inputs always produce identical outputs
- **ABX-Core v1.2**: Structured, entropy-minimizing framework
- **SEED Protocol**: Complete provenance tracking and reproducibility
- **GPU Acceleration**: CUDA and Apple Silicon (MPS) support
- **API-First**: FastAPI backend with comprehensive endpoints
- **Mobile UI**: React Native (Expo, TypeScript) app for iOS and Android
- **AAL Interoperability**: Clean hooks for PsyFi, Phonomicon, Echotome, and more

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
| **Settings** | Backend URL, device mode, theme |

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
