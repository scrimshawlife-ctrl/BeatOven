# BeatOven Modules

## Core Modules

### InputModule

**Purpose**: Process user inputs into symbolic vectors.

**Usage**:
```python
from beatoven.core.input import InputModule, MoodTag, ABXRunesSeed

module = InputModule()
result = module.process(
    text_intent="create an ambient pad",
    mood_tags=[MoodTag("calm", 0.8), MoodTag("ethereal", 0.6)],
    abx_seed=ABXRunesSeed("my_seed")
)

print(result.intent_embedding.shape)  # (128,)
print(result.provenance_hash)  # SHA-256 hash
```

**Outputs**:
- `intent_embedding`: 128-dimensional intent vector
- `mood_vector`: 32-dimensional mood vector
- `rune_vector`: 64-dimensional ABX-Runes vector
- `style_vector`: 18-dimensional style features
- `provenance_hash`: SHA-256 of all inputs

---

### SymbolicTranslator

**Purpose**: Convert symbolic vectors to ABX-Runes semantic fields.

**Usage**:
```python
from beatoven.core.translator import SymbolicTranslator

translator = SymbolicTranslator(compression_factor=0.8)
fields = translator.translate(
    intent_embedding=symbolic_vector.intent_embedding,
    mood_vector=symbolic_vector.mood_vector,
    rune_vector=symbolic_vector.rune_vector,
    style_vector=symbolic_vector.style_vector
)

print(f"Resonance: {fields.resonance}")
print(f"Density: {fields.density}")
print(f"Tension: {fields.tension}")
```

**ABX-Runes Fields**:
- `resonance`: Harmonic richness and sustain (0.0-1.0)
- `density`: Event density and complexity (0.0-1.0)
- `drift`: Temporal variation and evolution (0.0-1.0)
- `tension`: Harmonic/rhythmic tension level (0.0-1.0)
- `contrast`: Dynamic range and variation (0.0-1.0)

---

### RhythmEngine

**Purpose**: Generate deterministic rhythm patterns.

**Usage**:
```python
from beatoven.core.rhythm import RhythmEngine

engine = RhythmEngine(seed=42)
pattern, descriptor = engine.generate(
    density=0.6,
    tension=0.4,
    drift=0.2,
    tempo=120.0,
    time_signature=(4, 4),
    length_bars=4,
    swing=0.15,
    layers=["kick", "snare", "hihat_closed"]
)

for event in pattern.events[:5]:
    print(f"Time: {event.time}, Velocity: {event.velocity}")
```

**Features**:
- Euclidean rhythm patterns
- Multi-layer generation (drums, percussion)
- Swing and groove templates
- Velocity curves and accents

---

### HarmonicEngine

**Purpose**: Generate chord progressions with modal interchange.

**Usage**:
```python
from beatoven.core.harmony import HarmonicEngine, Scale

engine = HarmonicEngine(seed=42)
progression, descriptor = engine.generate(
    resonance=0.6,
    tension=0.5,
    contrast=0.4,
    key_root=60,  # Middle C
    scale=Scale.MINOR,
    length_bars=4,
    progression_type="emotional"  # or None for generated
)

for event in progression.events:
    print(f"Chord: {event.chord.quality.value} at {event.time}")
```

**Named Progressions**:
- `pop`: I-V-vi-IV
- `jazz_251`: ii-V-I
- `blues`: 12-bar blues
- `emotional`: vi-IV-I-V
- `pachelbel`: Canon progression

---

### TimbreEngine

**Purpose**: Modular synthesis and audio generation.

**Usage**:
```python
from beatoven.core.timbre import TimbreEngine, WaveShape

engine = TimbreEngine(seed=42)
buffer, patch = engine.generate(
    resonance=0.7,
    density=0.5,
    tension=0.3,
    frequency=440.0,
    duration=2.0
)

print(f"Duration: {buffer.duration}s")
print(f"Patch oscillators: {len(patch.oscillators)}")
```

**Synthesis Types**:
- Oscillators: sine, saw, square, triangle, pulse, noise
- Filters: lowpass, highpass, bandpass, notch
- Effects: reverb, delay, spectral warping

---

### MotionEngine

**Purpose**: Generate LFOs, envelopes, and automation.

**Usage**:
```python
from beatoven.core.motion import MotionEngine

engine = MotionEngine(seed=42)
curves, descriptor = engine.generate(
    drift=0.5,
    tension=0.4,
    resonance=0.6,
    duration=4.0,
    rune_vector=rune_vector  # Optional
)

print(f"Curves: {list(curves.keys())}")
# ['amplitude', 'filter_cutoff', 'pan', ...]
```

**LFO Shapes**:
- Sine, triangle, saw (up/down)
- Square, random, sample & hold

---

### StemGenerator

**Purpose**: Bounce and export audio stems.

**Usage**:
```python
from beatoven.core.stems import StemGenerator, StemType
from pathlib import Path

generator = StemGenerator(seed=42)
stems = generator.generate_stems(
    duration=16.0,
    stem_types=[StemType.DRUMS, StemType.BASS, StemType.PADS, StemType.FULL_MIX]
)

# Export
hashes = generator.export_all(stems, Path("./output"), prefix="track")
```

**Stem Types**:
- DRUMS, BASS, LEADS, MIDS, PADS, ATMOS, FULL_MIX

---

### EventHorizonDetector

**Purpose**: Detect rare sonic events for NFT metadata.

**Usage**:
```python
from beatoven.core.event_horizon import EventHorizonDetector

detector = EventHorizonDetector(seed=42, sensitivity=0.7)
metadata = detector.detect(
    audio=stem.samples,
    sample_rate=44100,
    rune_vector=rune_vector,
    emotional_curve=emotional_curve
)

print(f"Rare events: {metadata.total_events}")
print(f"Average rarity: {metadata.avg_rarity}")

# Export for Phonomicon
phonomicon_data = detector.export_for_phonomicon(metadata)
```

---

### PsyFiIntegration

**Purpose**: Emotional modulation from PsyFi vectors.

**Usage**:
```python
from beatoven.core.psyfi import PsyFiIntegration, EmotionalVector

psyfi = PsyFiIntegration(sensitivity=1.0)
vector = EmotionalVector(
    valence=0.8,
    arousal=0.6,
    dominance=0.5,
    tension=0.3
)

state = psyfi.process_emotional_vector(vector, intensity=0.8)

# Get modulated parameters
rhythm_params = psyfi.get_rhythm_params({"density": 0.5, "tension": 0.5})
harmony_params = psyfi.get_harmony_params({"resonance": 0.5})
```

---

### EchotomeHooks

**Purpose**: Prepare audio for steganographic integration.

**Usage**:
```python
from beatoven.core.echotome import EchotomeHooks, SaltPattern

echotome = EchotomeHooks(master_seed=42)
salted_audio, metadata = echotome.prepare_stem(
    stem_name="drums",
    audio=drum_samples,
    config=SaltConfig(pattern=SaltPattern.LSB, strength=0.001)
)

# Verify integrity
is_valid = echotome.verify_stem(salted_audio, metadata)
```

---

### RunicVisualExporter

**Purpose**: Generate visual runic signatures.

**Usage**:
```python
from beatoven.core.runic_export import RunicVisualExporter

exporter = RunicVisualExporter(seed=42, width=512, height=512)
signature = exporter.generate(
    spectral_vector=spectral_data,
    emotional_vector=emotional_data,
    rune_vector=rune_vector
)

# Export SVG
svg_content = exporter.export_svg(signature)

# Render to array
image = exporter.render_to_array(signature)  # (512, 512, 3)
```

---

### PatchBay

**Purpose**: Node-graph signal routing.

**Usage**:
```python
from beatoven.core.patchbay import PatchBay, create_default_patch

patchbay = PatchBay()
patchbay.load_patch(create_default_patch())

# Inspect flow
flow = patchbay.inspect_flow()
print(f"Execution order: {flow['execution_order']}")

# Load from file
patchbay.load_from_file("my_patch.yaml")

# Hot reload
patchbay.hot_reload(new_patch_descriptor)
```
