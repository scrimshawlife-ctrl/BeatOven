# PLACEMENT PLAN: RigProfile + Percussion Topology + Equipment-Aware Onboarding

**Status**: PLANNING PHASE (NO CODE CHANGES YET)
**Target**: End-to-end implementation with ABX-Core/SEED/ABX-Runes compliance
**Date**: 2025-12-19

---

## PHASE 0: FILE PLACEMENT DECISIONS

### 1. SCHEMA & DATA MODELS

**Location**: `beatoven/core/drums/` (NEW MODULE)

Following the existing pattern where `dspcoffee_bridge/schema.py` defines hardware-related schemas, we'll create a dedicated drums module in `core/` since percussion is a core engine concern.

**Files to CREATE**:
- `beatoven/core/drums/__init__.py` - Public API exports
- `beatoven/core/drums/schema.py` - RigProfile, PercussionTopology, DrumLane, PatternTokens models
- `beatoven/core/drums/allocator.py` - **PURE ENGINE**: LaneAllocator (topology from ResonanceFrame)
- `beatoven/core/drums/composer.py` - **PURE ENGINE**: PatternComposer (PatternTokens from topology)
- `beatoven/core/drums/profiles.py` - RigProfile storage adapter (filesystem I/O allowed)

**Rationale**:
- `core/drums/` keeps percussion logic separate from `rhythm/` (which generates patterns)
- `allocator.py` and `composer.py` are PURE (no I/O, only injected dependencies)
- `profiles.py` handles persistence (adapter layer, not engine)

---

### 2. API ENDPOINTS

**Location**: `beatoven/api/drums/` (NEW MODULE)

**Files to CREATE**:
- `beatoven/api/drums/__init__.py`
- `beatoven/api/drums/models.py` - Pydantic request/response models
- `beatoven/api/drums/routes.py` - FastAPI routes for rig profiles, topology, patterns
- `beatoven/api/capabilities.py` - **NEW**: Global capabilities endpoint
- `beatoven/api/config_schema.py` - **NEW**: Config schema generation

**Files to MODIFY**:
- `beatoven/api/main.py` - Import and mount drums routes, add capabilities/config_schema routes

**Endpoints to implement**:
```
POST   /api/rig/profiles           # Create/update RigProfile
GET    /api/rig/profiles           # List all profiles
GET    /api/rig/profiles/{id}      # Get specific profile
DELETE /api/rig/profiles/{id}      # Delete profile
POST   /api/rig/profiles/current   # Set current default
GET    /api/rig/profiles/current   # Get current default

POST   /api/drums/topology/preview # Generate topology from ResonanceFrame + rig
POST   /api/drums/pattern/preview  # Generate pattern from topology

GET    /api/capabilities           # System-wide capabilities report
GET    /api/config/schema          # Full config schema with all options
```

**Rationale**:
- Follows existing pattern (`api/media/routes.py`)
- Separates concerns: profiles, topology, patterns
- Capabilities/schema are global, live at API root

---

### 3. ABX-RUNES SYSTEM

**Location**: `beatoven/runes/` (NEW DIRECTORY)

**Files to CREATE**:
- `beatoven/runes/__init__.py` - Rune registry loader
- `beatoven/runes/manifests/` - Directory for YAML manifests
  - `beatoven/runes/manifests/rig.profile.resolve.yaml`
  - `beatoven/runes/manifests/drums.topology.allocate.yaml`
  - `beatoven/runes/manifests/drums.pattern.compose.yaml`
  - `beatoven/runes/manifests/ui.capabilities.yaml`
  - `beatoven/runes/manifests/ui.config.schema.yaml`
- `beatoven/runes/registry.py` - Registry loader and validator
- `beatoven/runes/schema.py` - RuneManifest dataclass

**Manifest Structure** (YAML):
```yaml
rune_id: "drums.topology.allocate"
version: "1.0.0"
category: "engine"  # engine | adapter | api
purity: "pure"      # pure | adapter | impure
seed_required: true
deterministic: true
inputs:
  - name: "resonance_frame"
    type: "ResonanceFrame"
  - name: "rig_profile"
    type: "RigProfile"
  - name: "seed"
    type: "int"
outputs:
  - name: "topology"
    type: "PercussionTopology"
provenance_tracking: true
code_hash: "auto"
dependencies: []
```

**Rationale**:
- Central registry for all runes
- Enforces contracts and purity boundaries
- Enables golden test generation

---

### 4. TESTS & GOLDEN VECTORS

**Location**: `beatoven/tests/` and `beatoven/core/drums/tests/`

**Files to CREATE**:
- `beatoven/core/drums/tests/__init__.py`
- `beatoven/core/drums/tests/test_schema.py` - Schema validation tests
- `beatoven/core/drums/tests/test_allocator.py` - LaneAllocator pure function tests
- `beatoven/core/drums/tests/test_composer.py` - PatternComposer pure function tests
- `beatoven/core/drums/tests/test_golden_topology.py` - **GOLDEN TEST**: stable topology output
- `beatoven/core/drums/tests/test_golden_pattern.py` - **GOLDEN TEST**: stable pattern output
- `beatoven/tests/test_drums_api.py` - API endpoint integration tests
- `beatoven/tests/test_pure_engine_gate.py` - **GATE TEST**: Forbidden imports scanner

**Golden Test Data**:
- `beatoven/tests/goldens/drums/` - Directory for golden files
  - `topology_input_v1.json` - Fixed ResonanceFrame + RigProfile + seed
  - `topology_output_v1.json` - Expected PercussionTopology
  - `pattern_input_v1.json` - Fixed PercussionTopology + seed
  - `pattern_output_v1.json` - Expected PatternTokens

**Rationale**:
- Golden tests ensure determinism across versions
- Gate test enforces PURE-ENGINE rule
- Co-located tests for module internals

---

### 5. UI COMPONENTS

**Location**: `beatoven-ui/src/`

**Files to CREATE**:
- `beatoven-ui/src/screens/OnboardingScreen.tsx` - **NEW**: Multi-step rig onboarding
- `beatoven-ui/src/screens/PercussionPanelScreen.tsx` - **NEW**: Dedicated percussion panel
- `beatoven-ui/src/components/RigProfileCard.tsx` - **NEW**: Display rig profile info
- `beatoven-ui/src/components/PercussionControl.tsx` - **NEW**: Lane controls (always visible)
- `beatoven-ui/src/components/TopologyPreview.tsx` - **NEW**: Visualize topology
- `beatoven-ui/src/hooks/useRigProfile.ts` - **NEW**: Rig profile state management
- `beatoven-ui/src/hooks/useCapabilities.ts` - **NEW**: Capabilities fetching
- `beatoven-ui/src/types/drums.ts` - **NEW**: TypeScript types for drums API

**Files to MODIFY**:
- `beatoven-ui/src/hooks/useBackend.ts` - Add drums API methods
- `beatoven-ui/src/navigation/index.tsx` - Add Onboarding and PercussionPanel to navigation
- `beatoven-ui/src/screens/HomeScreen.tsx` - Add link to percussion panel
- `beatoven-ui/App.tsx` - Check if onboarding needed on app launch

**Onboarding Flow** (5 steps):
1. Select emit_target: `DSP_COFFEE | MIDI | CV_GATE | AUDIO_STEMS`
2. Select drum_lanes_max: `1-16` (slider)
3. Configure lane_roles_allowed: Checkboxes for kick, snare, hat, perc, fx
4. Configure I/O capabilities: trigger, gate, accent, velocity, cv_range
5. Preview topology + save profile

**Percussion Panel** (persistent, all screens):
- Header: Current rig name, lanes: 4/8, emit: DSP_COFFEE
- Lane controls: Density, Accent, Mute (per-lane)
- Global controls: BPM, Swing, Fill intensity
- Disabled controls show reason tooltip from capabilities API

**Rationale**:
- Onboarding captures hardware constraints once
- Percussion panel always visible, honest availability reporting
- Types ensure type-safety with backend

---

### 6. CONFIGURATION & PERSISTENCE

**Location**: `beatoven/configs/` and runtime storage

**Files to CREATE**:
- `beatoven/configs/drums.yaml` - Drums subsystem config (allocator tuning, defaults)
- `~/.beatoven/rig_profiles/` - User profile storage directory (runtime, not in repo)
- `beatoven/core/drums/defaults.py` - Default RigProfile presets (eurorack, MIDI, etc.)

**Files to MODIFY**:
- `beatoven/configs/abx_core.yaml` - Add drums field ranges if needed

**Rationale**:
- Follows existing pattern (configs/ for static YAML)
- User profiles stored in home directory (not tracked in git)
- Defaults ship with package for quick start

---

### 7. DOCUMENTATION

**Files to CREATE**:
- `beatoven/docs/drums.md` - **NEW**: Drums subsystem documentation
- `beatoven/docs/rig_profiles.md` - **NEW**: RigProfile guide
- `beatoven/docs/topology_allocation.md` - **NEW**: How LaneAllocator works
- `beatoven/runes/README.md` - **NEW**: ABX-Runes system overview

**Files to MODIFY**:
- `README.md` - Add section on RigProfile + Percussion Topology
- `beatoven/docs/architecture.md` - Update with drums subsystem diagram
- `beatoven/docs/modules.md` - Add drums module to list

**Rationale**:
- Complete documentation for new subsystem
- Inline with existing docs/ structure

---

## IMPORT RULES & BOUNDARIES

### **PURE ENGINE MODULES** (STRICT)

**Allowed**:
- `beatoven/core/drums/allocator.py`
- `beatoven/core/drums/composer.py`

**Rules**:
- ✅ `from dataclasses import dataclass`
- ✅ `import hashlib, json` (for provenance)
- ✅ `import numpy as np` (deterministic operations only)
- ✅ `from typing import ...`
- ✅ Imports from other `beatoven.core.*` pure modules
- ✅ Imports from `beatoven.dspcoffee_bridge.schema` (ResonanceFrame)
- ❌ **FORBIDDEN**: `os, pathlib, requests, httpx, time.time(), datetime.now(), random, uuid, subprocess`
- ❌ **FORBIDDEN**: Any file I/O, network, system clock (except for provenance timestamps passed as args)

**Enforcement**: Gate test scans these files and fails CI if forbidden imports found.

### **ADAPTER MODULES** (I/O ALLOWED)

**Files**:
- `beatoven/core/drums/profiles.py`
- `beatoven/api/drums/routes.py`

**Rules**:
- ✅ Can use `os, pathlib` for file operations
- ✅ Can use `time.time()` for timestamps (passed to engines as args)
- ✅ Can call PURE engines with injected dependencies
- ❌ Must NOT contain core logic (delegate to engines)

### **API LAYER** (ALL I/O ALLOWED)

**Files**:
- `beatoven/api/drums/routes.py`
- `beatoven/api/capabilities.py`
- `beatoven/api/config_schema.py`

**Rules**:
- ✅ FastAPI dependencies, HTTP, filesystem, database
- ✅ Call adapters and engines
- ✅ Serialize/deserialize responses

---

## DEPENDENCY FLOW

```
┌─────────────────────────────────────────────────────────────┐
│  UI (React Native)                                           │
│  - OnboardingScreen                                          │
│  - PercussionPanelScreen                                     │
│  - useRigProfile, useCapabilities hooks                      │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI)                                         │
│  - /api/rig/profiles (CRUD)                                  │
│  - /api/drums/topology/preview                               │
│  - /api/drums/pattern/preview                                │
│  - /api/capabilities                                         │
│  - /api/config/schema                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Adapter Layer                                               │
│  - RigProfileStorage (filesystem read/write)                 │
│  - CurrentProfileManager (state management)                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  PURE ENGINE LAYER (deterministic, no I/O)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LaneAllocator                                         │   │
│  │  Input: ResonanceFrame + RigProfile + seed           │   │
│  │  Output: PercussionTopology                           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PatternComposer                                       │   │
│  │  Input: PercussionTopology + seed                     │   │
│  │  Output: PatternTokens                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Integration with Existing Systems                           │
│  - RhythmEngine (existing) - adapts to use PercussionTopology│
│  - dsp.coffee bridge - consumes PatternTokens                │
│  - ResonanceFrame schema (existing) - input to allocator     │
└─────────────────────────────────────────────────────────────┘
```

---

## INTEGRATION POINTS WITH EXISTING CODE

### 1. **ResonanceFrame** (already exists)
**File**: `beatoven/dspcoffee_bridge/schema.py`
**Action**: NO CHANGES NEEDED
**Usage**: `LaneAllocator` takes `ResonanceFrame` as input

### 2. **RhythmEngine** (already exists)
**File**: `beatoven/core/rhythm/__init__.py`
**Action**: MODIFY to accept optional `PercussionTopology`
**Changes**:
- Add parameter `topology: Optional[PercussionTopology] = None` to `generate()`
- If topology provided, constrain layers to topology.lanes
- If not provided, use existing default behavior (backward compat)

### 3. **API main.py** (already exists)
**File**: `beatoven/api/main.py`
**Action**: MODIFY to mount drums routes and add capabilities
**Changes**:
- Import `from beatoven.api.drums.routes import router as drums_router`
- `app.include_router(drums_router, prefix="/api")`
- Import `from beatoven.api import capabilities, config_schema`
- Add routes: `@app.get("/api/capabilities")`, `@app.get("/api/config/schema")`

### 4. **UI Navigation** (already exists)
**File**: `beatoven-ui/src/navigation/index.tsx`
**Action**: MODIFY to add new screens
**Changes**:
- Add `Onboarding` stack screen
- Add `PercussionPanel` tab/drawer item
- Check on app load if rig profile exists, if not, show onboarding

---

## PROVENANCE & DETERMINISM GUARANTEES

### **Provenance Manifest Structure**

Every output from engines includes:
```json
{
  "provenance": {
    "code_hash": "sha256(<source code>)",
    "config_hash": "sha256(<config params>)",
    "input_hash": "sha256(<stable sorted input>)",
    "seed": 42,
    "timestamp_policy": "monotonic_injected",
    "rune_version": "1.0.0",
    "beatoven_version": "1.0.0"
  }
}
```

### **Determinism Enforcement**

1. **Stable Sorting**: All lists sorted by deterministic key before hashing
2. **Stable Serialization**: JSON with `sort_keys=True, separators=(",", ":")`
3. **Seed Injection**: All RNG uses `np.random.default_rng(seed)`
4. **No System Clock**: Timestamps passed as arguments, not queried inside engines
5. **Gate Test**: CI fails if forbidden imports detected in engine modules

---

## TESTING STRATEGY

### **Unit Tests** (fast, pure logic)
- Test `LaneAllocator` with fixed inputs
- Test `PatternComposer` with fixed topology
- Test schema validation
- Test provenance hash stability

### **Golden Tests** (regression)
- Load `goldens/drums/topology_input_v1.json`
- Call `LaneAllocator.allocate(...)`
- Assert output matches `goldens/drums/topology_output_v1.json` exactly

### **Gate Test** (purity enforcement)
- Scan all `beatoven/core/drums/allocator.py`, `composer.py` AST
- Fail if imports contain: `os, pathlib, requests, time, datetime, random, uuid`
- Allow imports: `hashlib, json, dataclasses, typing, numpy`

### **Integration Tests** (API)
- POST `/api/rig/profiles` → 201 Created
- GET `/api/rig/profiles/current` → returns profile
- POST `/api/drums/topology/preview` → returns stable topology + provenance
- POST `/api/drums/pattern/preview` → returns stable pattern + provenance

### **UI Tests** (E2E)
- Onboarding flow completes successfully
- Percussion panel shows correct controls
- Disabled controls show reason tooltips
- Topology preview renders correctly

---

## SUMMARY: FILES TO CREATE vs MODIFY

### **CREATE** (30 new files)

**Backend**:
1. `beatoven/core/drums/__init__.py`
2. `beatoven/core/drums/schema.py`
3. `beatoven/core/drums/allocator.py` ⚡ PURE ENGINE
4. `beatoven/core/drums/composer.py` ⚡ PURE ENGINE
5. `beatoven/core/drums/profiles.py`
6. `beatoven/core/drums/defaults.py`
7. `beatoven/core/drums/tests/__init__.py`
8. `beatoven/core/drums/tests/test_schema.py`
9. `beatoven/core/drums/tests/test_allocator.py`
10. `beatoven/core/drums/tests/test_composer.py`
11. `beatoven/core/drums/tests/test_golden_topology.py`
12. `beatoven/core/drums/tests/test_golden_pattern.py`
13. `beatoven/api/drums/__init__.py`
14. `beatoven/api/drums/models.py`
15. `beatoven/api/drums/routes.py`
16. `beatoven/api/capabilities.py`
17. `beatoven/api/config_schema.py`
18. `beatoven/runes/__init__.py`
19. `beatoven/runes/schema.py`
20. `beatoven/runes/registry.py`
21. `beatoven/runes/manifests/rig.profile.resolve.yaml`
22. `beatoven/runes/manifests/drums.topology.allocate.yaml`
23. `beatoven/runes/manifests/drums.pattern.compose.yaml`
24. `beatoven/runes/manifests/ui.capabilities.yaml`
25. `beatoven/runes/manifests/ui.config.schema.yaml`
26. `beatoven/tests/test_drums_api.py`
27. `beatoven/tests/test_pure_engine_gate.py`
28. `beatoven/tests/goldens/drums/topology_input_v1.json`
29. `beatoven/tests/goldens/drums/topology_output_v1.json`
30. `beatoven/tests/goldens/drums/pattern_input_v1.json`
31. `beatoven/tests/goldens/drums/pattern_output_v1.json`
32. `beatoven/configs/drums.yaml`
33. `beatoven/docs/drums.md`
34. `beatoven/docs/rig_profiles.md`
35. `beatoven/docs/topology_allocation.md`
36. `beatoven/runes/README.md`

**Frontend**:
37. `beatoven-ui/src/screens/OnboardingScreen.tsx`
38. `beatoven-ui/src/screens/PercussionPanelScreen.tsx`
39. `beatoven-ui/src/components/RigProfileCard.tsx`
40. `beatoven-ui/src/components/PercussionControl.tsx`
41. `beatoven-ui/src/components/TopologyPreview.tsx`
42. `beatoven-ui/src/hooks/useRigProfile.ts`
43. `beatoven-ui/src/hooks/useCapabilities.ts`
44. `beatoven-ui/src/types/drums.ts`

### **MODIFY** (6 existing files)

**Backend**:
1. `beatoven/core/rhythm/__init__.py` - Accept optional PercussionTopology
2. `beatoven/api/main.py` - Mount drums routes, add capabilities/config_schema
3. `README.md` - Add RigProfile + Percussion Topology section
4. `beatoven/docs/architecture.md` - Add drums subsystem diagram

**Frontend**:
5. `beatoven-ui/src/hooks/useBackend.ts` - Add drums API methods
6. `beatoven-ui/src/navigation/index.tsx` - Add Onboarding + PercussionPanel
7. `beatoven-ui/src/screens/HomeScreen.tsx` - Link to percussion panel
8. `beatoven-ui/App.tsx` - Onboarding check on launch

---

## NEXT STEPS (IN ORDER)

1. ✅ **PHASE 0 COMPLETE**: Placement plan created
2. **PHASE 1**: Implement backend schema + engines (pure functions)
3. **PHASE 2**: Implement API routes + adapters
4. **PHASE 3**: Implement ABX-Runes system + registry
5. **PHASE 4**: Implement tests (unit, golden, gate)
6. **PHASE 5**: Implement UI (onboarding + percussion panel)
7. **PHASE 6**: Integration testing + documentation
8. **PHASE 7**: Final report: determinism verification, compute economy metrics

---

## CRITICAL CONSTRAINTS CHECKLIST

- [x] PURE-ENGINE RULE: Allocator and Composer have NO I/O imports
- [x] Determinism: All outputs reproducible with same seed
- [x] Provenance: All outputs include full provenance manifest
- [x] ABX-Runes: All engines have YAML manifests + registry entries
- [x] Golden Tests: Stable outputs verified with golden files
- [x] Gate Test: CI fails on forbidden imports in engines
- [x] UI Honesty: All options visible, disabled with reasons
- [x] Backward Compat: Existing RhythmEngine still works without topology
- [x] Schema-Driven UI: UI derives controls from /api/config/schema
- [x] Stable Sorting: All serialization uses deterministic order

---

**READY TO PROCEED TO IMPLEMENTATION**
