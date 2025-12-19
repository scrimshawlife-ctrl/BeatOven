# BeatOven Media Intelligence

Multi-modal intent extraction: convert images and videos into `ResonanceFrame` objects that drive dsp.coffee presets.

## Architecture

```
Media (image/video)
    ↓
MediaFrame (physical + semantic + affect + temporal)
    ↓
ResonanceFrame (metrics + rhythm + extras)
    ↓
dsp.coffee bridge (preset selection + transport)
```

## Design Principles

1. **Deterministic and Explainable**: Physical features are computed using standard CV algorithms with clear semantics
2. **Confidence Tracking**: Every inference includes confidence scores to enable calibration
3. **Stable Contracts**: Model internals can be upgraded without changing calling code
4. **Conservative Estimates**: Start with physics-based features, add ML progressively

## Features

### Physical Analysis (Deterministic)

- **Color**: Brightness (luma), saturation, contrast
- **Texture**: Sharpness (Laplacian variance), edge density
- **Composition**: Symmetry, clutter (edge-based)
- **Motion** (video): Optical flow energy, jitter/shake

### Affect Model (Hybrid)

Core dimensions (continuous):
- **Valence**: pleasant ↔ unpleasant [0,1]
- **Arousal**: calm ↔ intense [0,1]
- **Dominance**: submissive ↔ in-control [0,1]

Emotion blends:
- Awe, dread, nostalgia, tenderness

### Temporal Analysis (Video)

- **Trajectory**: Drift, volatility, peakiness of arousal/valence over time
- **Era Inference**: Perceived time period (1990s, 2000s, 2010s, 2020s) as distribution

### Semantic Analysis (Optional)

Future: CLIP embeddings, scene classification, object detection, action recognition, audio features

## Installation

```bash
# Basic media analysis (opencv only)
pip install beatoven[media]

# Full semantic analysis (includes transformers, torch, timm)
pip install beatoven[media-full]
```

## Usage

### Analyze Image

```python
from beatoven.media_intel import analyze_image, media_to_resonance

# Analyze
media_frame = analyze_image("photo.jpg", media_id="img_001")

# Inspect
print(f"Brightness: {media_frame.physical['luma_mean']:.2f}")
print(f"Valence: {media_frame.affect['valence']:.2f}")
print(f"Arousal: {media_frame.affect['arousal']:.2f}")
print(f"Era: {media_frame.perceived_era}")
print(f"Confidence: {media_frame.confidence}")

# Convert to ResonanceFrame
resonance_frame = media_to_resonance(media_frame)
```

### Analyze Video

```python
from beatoven.media_intel import analyze_video, media_to_resonance

# Analyze (samples at 2 fps, max 60 seconds)
media_frame = analyze_video("clip.mp4", media_id="vid_001", sample_fps=2.0, max_seconds=60.0)

# Inspect temporal features
print(f"Duration: {media_frame.duration_s:.1f}s")
print(f"Motion energy: {media_frame.physical['motion_energy']:.2f}")
print(f"Arousal drift: {media_frame.physical['arousal_drift']:.2f}")
print(f"Valence volatility: {media_frame.physical['valence_vol']:.2f}")

# Convert
resonance_frame = media_to_resonance(media_frame)
```

### Integration with dsp.coffee Bridge

```python
from beatoven.dspcoffee_bridge import BridgeRuntime, PresetRegistry, UdpRealtimeLane, SerialOpsLane
from beatoven.dspcoffee_bridge.example_preset_pack import PRESETS
from beatoven.media_intel import analyze_image, media_to_resonance

# Setup bridge
registry = PresetRegistry(PRESETS)
rt_lane = UdpRealtimeLane(host="192.168.1.50", port=9000)
op_lane = SerialOpsLane(port="/dev/ttyACM0", baud=115200)
bridge = BridgeRuntime(presets=registry, realtime_lane=rt_lane, ops_lane=op_lane)

# Process media
def handle_media_upload(path: str, kind: str, media_id: str):
    # Analyze
    if kind == "image":
        mf = analyze_image(path, media_id=media_id)
    elif kind == "video":
        mf = analyze_video(path, media_id=media_id)
    else:
        raise ValueError("kind must be 'image' or 'video'")

    # Convert to ResonanceFrame
    rf = media_to_resonance(mf)

    # Feed to bridge (preset selection + hardware control)
    bridge.on_frame(rf)

# Use
handle_media_upload("user_photo.jpg", kind="image", media_id="upload_123")
```

## Metric Mapping: MediaFrame → ResonanceFrame

The `media_to_resonance()` function maps affect/physical features to resonance metrics:

| ResonanceMetric | Derived From |
|-----------------|--------------|
| `complexity` | edge_density + luma_var |
| `emotional_intensity` | arousal |
| `groove` | dominance + (1 - jitter) |
| `energy` | arousal |
| `density` | edge_density + motion_energy |
| `swing` | jitter (shaky cam bias) |
| `brightness` | luma_mean |
| `tension` | dread + luma_var |

All mappings are deterministic and tunable.

## Confidence Interpretation

| Confidence Range | Meaning |
|------------------|---------|
| 0.0 - 0.3 | Low confidence (use with caution, or fallback to defaults) |
| 0.3 - 0.6 | Moderate (reasonable estimate) |
| 0.6 - 1.0 | High (strong signal) |

Confidence is intentionally conservative. As you add semantic models, confidence increases.

## Model Versioning

All `MediaFrame` objects include `model_versions` dict:

```python
{
    "physical": "v1",
    "affect": "v1",
    "temporal": "v1",  # video only
    "era": "v1",
}
```

When you upgrade models, increment versions. This enables A/B testing and rollback.

## Extending with Semantic Models

Future enhancement (plug-in pattern):

```python
# beatoven/media_intel/semantic.py (future)
from transformers import CLIPProcessor, CLIPModel

class CLIPAnalyzer:
    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def analyze(self, image):
        # Return scene tags, object tags, aesthetic scores
        pass

# In analyzer.py:
if SEMANTIC_ENABLED:
    semantic = clip_analyzer.analyze(bgr)
else:
    semantic = {}
```

Calling code doesn't change—just `MediaFrame.semantic` gets populated.

## Performance

- **Image**: ~50-100ms on CPU (opencv only)
- **Video**: ~1-2s for 60s clip at 2fps sampling (opencv only)
- **With semantics**: +200-500ms per image (CLIP/transformers)

For real-time use, run analysis async or use GPU.

## Files

```
beatoven/media_intel/
├── __init__.py           - Public API
├── schema.py             - MediaFrame data model
├── physical.py           - Physical feature extraction
├── temporal.py           - Temporal trajectory + era inference
├── affect.py             - Affect/emotion estimation
├── analyzer.py           - Image/video analysis orchestration
├── to_resonance.py       - MediaFrame → ResonanceFrame conversion
├── README.md             - This file
└── tests/
    ├── __init__.py
    ├── test_affect.py
    ├── test_temporal.py
    └── test_to_resonance.py
```

## Next Steps

1. **Calibration**: Collect MediaFrame outputs, compare to manual labels, tune coefficients
2. **Semantic Models**: Add CLIP for scene/object tags, action recognition for video
3. **Audio Features**: Extract loudness, spectral features, tempo from video audio tracks
4. **Preset Expansion**: Create genre-specific presets that respond to media affect
5. **Live Mode**: Real-time webcam analysis → BeatOven → dsp.coffee

## Credits

Architecture: ABX-Core hardened, deterministic feature extraction with confidence tracking.

"Accuracy comes from measurable features + calibrated models + uncertainty tracking, not vibes wearing a trench coat."
