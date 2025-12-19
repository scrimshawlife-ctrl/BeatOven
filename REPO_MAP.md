# BeatOven Repository Structure Map

## Backend (Python)

```
beatoven/
├── api/                          # FastAPI application layer
│   ├── main.py                   # Main API app with all routes
│   ├── routes/                   # (empty, routes currently in main.py)
│   └── media/                    # Media intelligence API routes
│       ├── models.py
│       └── routes.py
│
├── core/                         # PURE ENGINE MODULES (deterministic, no I/O)
│   ├── rhythm/                   # RhythmEngine - Euclidean patterns
│   ├── harmony/                  # HarmonicEngine - chord progressions
│   ├── timbre/                   # TimbreEngine - sound synthesis
│   ├── motion/                   # MotionEngine - temporal curves
│   ├── stems/                    # StemGenerator - stem composition
│   ├── event_horizon/            # EventHorizonDetector
│   ├── psyfi/                    # PsyFiIntegration - emotional vectors
│   ├── echotome/                 # EchotomeHooks
│   ├── input/                    # InputModule - intent processing
│   ├── translator/               # SymbolicTranslator - ABX-Runes
│   ├── patchbay/                 # PatchBay - signal routing
│   ├── runic_export/             # RunicVisualExporter
│   └── ringtone.py               # RingtoneGenerator
│
├── dspcoffee_bridge/             # Hardware bridge subsystem
│   ├── schema.py                 # ResonanceFrame, RhythmTokens, PresetBank
│   ├── registry.py               # PresetRegistry
│   ├── scoring.py                # Preset fit scoring
│   ├── transport_udp.py          # UDP realtime transport
│   ├── transport_serial.py       # Serial reliable transport
│   └── runtime.py                # BridgeRuntime orchestrator
│
├── media_intel/                  # Media intelligence subsystem
│   ├── schema.py                 # MediaFrame
│   ├── analyzer.py               # Image/video analysis
│   ├── physical.py               # CV features
│   ├── affect.py                 # VAD emotion model
│   ├── temporal.py               # Era inference
│   ├── semantic_engine.py        # Provider orchestrator
│   ├── capabilities.py           # Capability reporting
│   ├── to_resonance.py           # MediaFrame → ResonanceFrame
│   └── providers/                # Hot-swappable semantic providers
│       ├── base.py
│       ├── clip_provider.py
│       ├── action_provider.py
│       └── audio_provider.py
│
├── audio_fx/                     # Audio effects
│   └── binaural.py               # Binaural beats
│
├── signals/                      # Signal intake
│   └── feeds.py                  # RSS/feed ingestion
│
├── audio/                        # Audio I/O
│   └── __init__.py               # StemExtractor, AudioIO
│
├── configs/                      # YAML configuration
│   ├── abx_core.yaml             # ABX-Core v1.2 config
│   ├── seed.yaml                 # SEED protocol
│   ├── ers.yaml                  # ERS runtime
│   └── plugins.yaml              # Plugin configuration
│
├── mobile/                       # Mobile platform specifics
│   ├── android/
│   └── ios/
│
├── gpu/                          # GPU utilities
│   ├── device_utils.py
│   └── runpod_launcher.py
│
├── docs/                         # Documentation
│   ├── architecture.md
│   ├── runic_system.md
│   ├── provenance.md
│   └── ...
│
└── tests/                        # Backend tests
    ├── test_rhythm.py
    ├── test_harmony.py
    ├── test_api.py
    └── ...
```

## Frontend (React Native / Expo)

```
beatoven-ui/
├── src/
│   ├── screens/                  # Screen components
│   │   ├── HomeScreen.tsx
│   │   ├── ModuleScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   ├── PatchbayScreen.tsx
│   │   ├── SignalsScreen.tsx
│   │   ├── StemsScreen.tsx
│   │   ├── RingtoneScreen.tsx
│   │   └── SymbolicPanelScreen.tsx
│   │
│   ├── components/               # Reusable components
│   │   ├── ConnectionStatus.tsx
│   │   ├── SliderControl.tsx
│   │   ├── ToggleControl.tsx
│   │   ├── StemCard.tsx
│   │   ├── NodeCard.tsx
│   │   └── ...
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useBackend.ts         # Backend API integration
│   │   └── usePresets.ts         # Preset management
│   │
│   ├── navigation/               # Navigation config
│   │   └── index.tsx
│   │
│   └── theme/                    # Theming
│       ├── index.ts
│       └── ThemeContext.tsx
│
├── __tests__/                    # Frontend tests
│   ├── App.test.tsx
│   ├── components.test.tsx
│   ├── screens.test.tsx
│   └── hooks.test.ts
│
└── App.tsx                       # Root component
```

## Scripts & Deployment

```
scripts/
├── patch_inspect.py              # Patch inspection utility
├── run_gpu.sh                    # GPU launcher
└── run_local.sh                  # Local dev launcher

.github/workflows/
└── deploy-azure.yml              # CI/CD pipeline

setup.py                          # Python package setup
Dockerfile                        # Container build
render.yaml                       # Render deployment config
```

## Key Patterns Observed

1. **Schema Models**: Defined using `@dataclass(frozen=True)` with provenance hashing
2. **Engine Structure**: Pure functions in `core/`, I/O adapters separate
3. **API Pattern**: Pydantic models for requests/responses, FastAPI routes in `main.py`
4. **Provenance**: `_stable_hash()` and `provenance_hash` fields throughout
5. **Configuration**: YAML files in `configs/` directory
6. **No existing `runes/` directory**: Need to create ABX-Runes manifest system
7. **UI Backend Integration**: `useBackend.ts` hook for API calls
8. **Existing rhythm system**: Uses `RhythmEngine` with Euclidean patterns, has layers concept
