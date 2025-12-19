# Semantic Providers Architecture

## Overview

BeatOven's Media Intelligence system uses hot-swappable semantic providers that gracefully degrade when dependencies are missing. This enables a **progressive enhancement** model:

- **Basic mode**: Physical CV features only (opencv-python)
- **Semantic mode**: + CLIP scene tags, action recognition, audio mood
- **Full mode**: All providers + custom models

The UI **always shows all options** but clearly indicates availability.

## Provider Protocol

All providers implement:

```python
class SemanticProvider(Protocol):
    name: str

    def status(self) -> ProviderStatus:
        """Check if provider is available (dependencies installed)"""
        ...

    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict]) -> Dict:
        """Analyze media and return structured semantic data"""
        ...
```

## Built-in Providers

### 1. CLIP Provider (`clip`)

**Purpose**: Scene/object tags + aesthetic vibes + era inference

**Dependencies**: `torch`, `transformers`, `pillow`

**Model**: `openai/clip-vit-base-patch32` (auto-downloads ~600MB on first run)

**Output**:
```python
{
    "top_tags": [
        ("a dark nightclub scene", 0.82),
        ("a tense dramatic scene", 0.65),
        ...
    ],
    "era_dist": {
        "1990s": 0.15,
        "2000s": 0.45,
        "2010s": 0.30,
        "2020s": 0.10,
    },
    "raw": {...}  # All prompt scores
}
```

**Tuning**: Edit prompts in `clip_provider.py` to match your music-control semantics.

**Performance**:
- Image: ~200-400ms (CPU), ~50-100ms (GPU)
- Video: 3 frames sampled @ 20%, 50%, 80% → ~600ms-1.2s

### 2. Action Provider (`action`)

**Purpose**: Video action recognition for motion-based music control

**Dependencies**: `torch`, `torchvision`, `opencv-python`

**Model**: R3D-18 (torchvision built-in, ~200MB)

**Output**:
```python
{
    "top_actions": [
        ("dancing", 0.72),
        ("running", 0.18),
        ("walking", 0.08),
        ...
    ]
}
```

**Sampling**: 16 frames evenly distributed

**Performance**: ~500-800ms (CPU), ~150-300ms (GPU)

### 3. Audio Mood Provider (`audio_mood`)

**Purpose**: Extract tempo, energy, brightness from audio tracks

**Dependencies**: `librosa`, `soundfile`, `numpy`

**Input**: WAV/MP3 audio file (for video, extract audio track first)

**Output**:
```python
{
    "tempo_bpm": 128.5,
    "rms": 0.23,
    "centroid": 2450.3,
    "rolloff": 5200.1,
    "zcr": 0.082,
    "energy_proxy": 0.67,      # Normalized [0,1]
    "brightness_proxy": 0.61,   # Normalized [0,1]
    "percussive_proxy": 0.41,   # Normalized [0,1]
}
```

**Performance**: ~1-3s for 30s audio (CPU)

## Semantic Engine

`SemanticEngine` orchestrates all providers:

```python
from beatoven.media_intel.semantic_engine import SemanticEngine
from beatoven.media_intel.providers.clip_provider import ClipProvider
from beatoven.media_intel.providers.action_provider import ActionProvider
from beatoven.media_intel.providers.audio_provider import AudioMoodProvider

# Initialize with all providers
engine = SemanticEngine(providers=[
    ClipProvider(),
    ActionProvider(),
    AudioMoodProvider(),
])

# Check capabilities (for UI)
caps = engine.capabilities()
print(caps["available"])    # ["clip", "action", "audio_mood"] or subset
print(caps["unavailable"])  # [{"name": "clip", "reason": "No module named 'torch'"}]

# Analyze media (only runs available providers)
result = engine.analyze(kind="image", path="photo.jpg")
# result = {"clip": {...}, "action": {...}}  (only available)
```

## Availability Reporting

Each provider reports:

```python
ProviderStatus(
    name="clip",
    available=True,
    reason=None,
    version="clip-vit-b32"
)
```

If dependencies missing:

```python
ProviderStatus(
    name="clip",
    available=False,
    reason="No module named 'transformers'",
    version=None
)
```

The UI uses this to:
- Show provider toggle (always visible)
- Gray out if unavailable
- Display reason tooltip: "Install: pip install beatoven[media-full]"

## Adding Custom Providers

### Example: Speech Provider

```python
from beatoven.media_intel.providers.base import ProviderStatus, SemanticProvider
import dataclasses

@dataclasses.dataclass
class SpeechProvider(SemanticProvider):
    name: str = "speech"

    def status(self) -> ProviderStatus:
        try:
            import whisper  # noqa
            return ProviderStatus(name=self.name, available=True, version="whisper-small")
        except Exception as e:
            return ProviderStatus(name=self.name, available=False, reason=str(e))

    def analyze(self, *, kind, path, context=None):
        if kind != "video":
            return {}

        import whisper
        model = whisper.load_model("small")

        # Extract audio, transcribe
        result = model.transcribe(path)
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"],
        }
```

Add to engine:

```python
engine = SemanticEngine(providers=[
    ClipProvider(),
    ActionProvider(),
    AudioMoodProvider(),
    SpeechProvider(),  # Custom
])
```

## Integration with Analyzer

The `analyze_image()` and `analyze_video()` functions accept optional `semantic_engine`:

```python
from beatoven.media_intel import analyze_image
from beatoven.media_intel.semantic_engine import SemanticEngine

# Without semantics (fast, basic)
media_frame = analyze_image("photo.jpg", media_id="img_001")

# With semantics (slower, richer)
engine = SemanticEngine(providers=[ClipProvider()])
media_frame = analyze_image("photo.jpg", media_id="img_001", semantic_engine=engine)

# CLIP era overrides heuristic era if available
print(media_frame.perceived_era)  # From CLIP
```

## Capabilities API

```python
from beatoven.media_intel.capabilities import compute_capabilities

caps = compute_capabilities(engine)

# For UI
{
    "semantic": {
        "providers": [
            {"name": "clip", "available": True, "version": "clip-vit-b32"},
            {"name": "action", "available": False, "reason": "No module named 'torchvision'"},
        ],
        "available": ["clip"],
        "unavailable": [{"name": "action", "reason": "..."}]
    },
    "binaural": {
        "available": True,
        "modes": ["render_fx", "stream_fx"],
        "params": ["carrier_hz", "beat_hz", "mix", ...],
        "safety": {"min_carrier_hz": 80.0, ...}
    }
}
```

## Performance Tuning

### CPU Mode (Orin Nano, basic desktop)
- Install: `pip install beatoven[media]` (opencv only)
- Providers: None (all unavailable)
- Latency: ~50-100ms per image

### GPU Mode (Desktop, CUDA)
- Install: `pip install beatoven[media-full]`
- Providers: CLIP, Action, Audio (all available)
- Latency: ~150-400ms per image (CLIP + Action)

### Hybrid Mode
- Install base + selective providers:
  ```bash
  pip install beatoven[media]
  pip install transformers torch  # CLIP only
  ```
- Providers: CLIP available, Action/Audio unavailable
- Latency: ~200-400ms

## Future Providers

Planned:
- **Object detection**: YOLO for specific object counts
- **Face analysis**: Expression, gaze, emotion
- **Audio speech**: Whisper transcription + sentiment
- **Style transfer**: Aesthetic embeddings
- **Custom models**: User-trained classifiers

All follow same protocol → zero breaking changes.
