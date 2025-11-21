"""
BeatOven FastAPI Application

Main API backend with endpoints for generation, configuration, and export.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import numpy as np
import hashlib
import json
from pathlib import Path

from beatoven.core.input import InputModule, MoodTag, ABXRunesSeed
from beatoven.core.translator import SymbolicTranslator
from beatoven.core.rhythm import RhythmEngine
from beatoven.core.harmony import HarmonicEngine, Scale
from beatoven.core.timbre import TimbreEngine
from beatoven.core.motion import MotionEngine
from beatoven.core.stems import StemGenerator, StemType
from beatoven.core.event_horizon import EventHorizonDetector
from beatoven.core.psyfi import PsyFiIntegration, EmotionalVector
from beatoven.core.echotome import EchotomeHooks
from beatoven.core.patchbay import PatchBay, create_default_patch
from beatoven.core.runic_export import RunicVisualExporter


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="BeatOven API",
        description="Modular generative music engine API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize engines
    app.state.input_module = InputModule()
    app.state.translator = SymbolicTranslator()
    app.state.rhythm_engine = RhythmEngine()
    app.state.harmonic_engine = HarmonicEngine()
    app.state.timbre_engine = TimbreEngine()
    app.state.motion_engine = MotionEngine()
    app.state.stem_generator = StemGenerator()
    app.state.event_detector = EventHorizonDetector()
    app.state.psyfi = PsyFiIntegration()
    app.state.echotome = EchotomeHooks()
    app.state.patchbay = PatchBay()
    app.state.runic_exporter = RunicVisualExporter()

    # Load default patch
    app.state.patchbay.load_patch(create_default_patch())

    return app


app = create_app()


# Request/Response Models

class GenerateRequest(BaseModel):
    """Request model for generation."""
    text_intent: str = Field(..., description="Natural language description")
    mood_tags: Optional[List[str]] = Field(default=None, description="Mood tags")
    seed: Optional[str] = Field(default=None, description="ABX-Runes seed string")
    tempo: float = Field(default=120.0, ge=40, le=300)
    duration: float = Field(default=16.0, ge=1, le=300)
    key_root: int = Field(default=60, ge=0, le=127)
    scale: str = Field(default="MINOR")
    resonance: float = Field(default=0.5, ge=0, le=1)
    density: float = Field(default=0.5, ge=0, le=1)
    tension: float = Field(default=0.5, ge=0, le=1)
    drift: float = Field(default=0.3, ge=0, le=1)
    contrast: float = Field(default=0.5, ge=0, le=1)


class GenerateResponse(BaseModel):
    """Response model for generation."""
    job_id: str
    provenance_hash: str
    rhythm_descriptor: Dict[str, Any]
    harmonic_descriptor: Dict[str, Any]
    motion_descriptor: Dict[str, Any]
    stems_generated: List[str]
    rarity_metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    engines_loaded: List[str]


class PatchRequest(BaseModel):
    """Request for patch operations."""
    patch_json: Optional[str] = None
    patch_yaml: Optional[str] = None


class EmotionalRequest(BaseModel):
    """Request for PsyFi emotional modulation."""
    valence: float = Field(default=0.0, ge=-1, le=1)
    arousal: float = Field(default=0.0, ge=-1, le=1)
    dominance: float = Field(default=0.0, ge=-1, le=1)
    tension: float = Field(default=0.0, ge=-1, le=1)
    depth: float = Field(default=0.0, ge=-1, le=1)
    warmth: float = Field(default=0.0, ge=-1, le=1)
    brightness: float = Field(default=0.0, ge=-1, le=1)
    movement: float = Field(default=0.0, ge=-1, le=1)


# Routes

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        engines_loaded=[
            "input", "translator", "rhythm", "harmony",
            "timbre", "motion", "stems", "event_horizon",
            "psyfi", "echotome", "patchbay", "runic_export"
        ]
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate music from parameters.

    This endpoint processes the input, translates to ABX-Runes fields,
    and generates rhythm, harmony, timbre, and motion.
    """
    try:
        # Process input
        mood_tags = [MoodTag(name=t) for t in (request.mood_tags or [])]
        seed = ABXRunesSeed(request.seed or f"beatoven_{hash(request.text_intent)}")

        symbolic_vector = app.state.input_module.process(
            text_intent=request.text_intent,
            mood_tags=mood_tags,
            abx_seed=seed
        )

        # Translate to ABX-Runes fields
        abx_fields = app.state.translator.translate(
            intent_embedding=symbolic_vector.intent_embedding,
            mood_vector=symbolic_vector.mood_vector,
            rune_vector=symbolic_vector.rune_vector,
            style_vector=symbolic_vector.style_vector,
            input_provenance=symbolic_vector.provenance_hash
        )

        # Apply request parameters to fields
        resonance = request.resonance * abx_fields.resonance
        density = request.density * abx_fields.density
        tension = request.tension * abx_fields.tension
        drift = request.drift * abx_fields.drift
        contrast = request.contrast * abx_fields.contrast

        # Generate rhythm
        try:
            scale = Scale[request.scale.upper()]
        except KeyError:
            scale = Scale.MINOR

        rhythm_pattern, rhythm_desc = app.state.rhythm_engine.generate(
            density=density,
            tension=tension,
            drift=drift,
            tempo=request.tempo,
            length_bars=int(request.duration / 4)
        )

        # Generate harmony
        harmonic_prog, harmonic_desc = app.state.harmonic_engine.generate(
            resonance=resonance,
            tension=tension,
            contrast=contrast,
            key_root=request.key_root,
            scale=scale,
            length_bars=int(request.duration / 4)
        )

        # Generate motion
        motion_curves, motion_desc = app.state.motion_engine.generate(
            drift=drift,
            tension=tension,
            resonance=resonance,
            duration=request.duration,
            rune_vector=symbolic_vector.rune_vector
        )

        # Generate stems
        stems = app.state.stem_generator.generate_stems(
            rhythm_events=[e.to_dict() for e in rhythm_pattern.events],
            harmonic_events=[e.to_dict() for e in harmonic_prog.events],
            duration=request.duration,
            stem_types=[StemType.DRUMS, StemType.BASS, StemType.PADS, StemType.FULL_MIX]
        )

        # Compute job ID
        job_id = hashlib.sha256(
            f"{request.text_intent}:{request.seed}:{symbolic_vector.provenance_hash}".encode()
        ).hexdigest()[:16]

        return GenerateResponse(
            job_id=job_id,
            provenance_hash=abx_fields.provenance_hash,
            rhythm_descriptor=rhythm_desc.to_dict(),
            harmonic_descriptor=harmonic_desc.to_dict(),
            motion_descriptor=motion_desc.to_dict(),
            stems_generated=[s.value for s in stems.keys()]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
async def translate_input(
    text_intent: str,
    mood_tags: Optional[List[str]] = None,
    seed: Optional[str] = None
):
    """Translate input to ABX-Runes fields."""
    try:
        mood_tag_objects = [MoodTag(name=t) for t in (mood_tags or [])]
        abx_seed = ABXRunesSeed(seed or "default")

        symbolic_vector = app.state.input_module.process(
            text_intent=text_intent,
            mood_tags=mood_tag_objects,
            abx_seed=abx_seed
        )

        abx_fields = app.state.translator.translate(
            intent_embedding=symbolic_vector.intent_embedding,
            mood_vector=symbolic_vector.mood_vector,
            rune_vector=symbolic_vector.rune_vector,
            style_vector=symbolic_vector.style_vector
        )

        return {
            "symbolic_vector": symbolic_vector.to_dict(),
            "abx_fields": abx_fields.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rhythm")
async def generate_rhythm(
    density: float = 0.5,
    tension: float = 0.5,
    drift: float = 0.3,
    tempo: float = 120.0,
    length_bars: int = 4,
    swing: float = 0.0
):
    """Generate rhythm pattern."""
    try:
        pattern, descriptor = app.state.rhythm_engine.generate(
            density=density,
            tension=tension,
            drift=drift,
            tempo=tempo,
            length_bars=length_bars,
            swing=swing
        )

        return {
            "pattern": pattern.to_dict(),
            "descriptor": descriptor.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/harmony")
async def generate_harmony(
    resonance: float = 0.5,
    tension: float = 0.5,
    contrast: float = 0.5,
    key_root: int = 60,
    scale: str = "MINOR",
    length_bars: int = 4,
    progression_type: Optional[str] = None
):
    """Generate harmonic progression."""
    try:
        try:
            scale_enum = Scale[scale.upper()]
        except KeyError:
            scale_enum = Scale.MINOR

        progression, descriptor = app.state.harmonic_engine.generate(
            resonance=resonance,
            tension=tension,
            contrast=contrast,
            key_root=key_root,
            scale=scale_enum,
            length_bars=length_bars,
            progression_type=progression_type
        )

        return {
            "progression": progression.to_dict(),
            "descriptor": descriptor.to_dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/psyfi/modulate")
async def psyfi_modulate(request: EmotionalRequest):
    """Apply PsyFi emotional modulation."""
    try:
        vector = EmotionalVector(
            valence=request.valence,
            arousal=request.arousal,
            dominance=request.dominance,
            tension=request.tension,
            depth=request.depth,
            warmth=request.warmth,
            brightness=request.brightness,
            movement=request.movement
        )

        state = app.state.psyfi.process_emotional_vector(vector)

        return {
            "state": state.to_dict(),
            "rhythm_params": app.state.psyfi.get_rhythm_params({"density": 0.5, "tension": 0.5}),
            "harmony_params": app.state.psyfi.get_harmony_params({"resonance": 0.5, "tension": 0.5}),
            "timbre_params": app.state.psyfi.get_timbre_params({"brightness": 0.5, "warmth": 0.5})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patchbay/flow")
async def get_patch_flow():
    """Get current patch signal flow."""
    return app.state.patchbay.inspect_flow()


@app.post("/patchbay/load")
async def load_patch(request: PatchRequest):
    """Load a new patch configuration."""
    try:
        if request.patch_json:
            success = app.state.patchbay.load_from_json(request.patch_json)
        elif request.patch_yaml:
            success = app.state.patchbay.load_from_yaml(request.patch_yaml)
        else:
            raise HTTPException(status_code=400, detail="No patch provided")

        return {"success": success, "flow": app.state.patchbay.inspect_flow()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/runic/generate")
async def generate_runic_signature(
    spectral_data: Optional[List[float]] = None,
    symbolic_data: Optional[List[float]] = None,
    emotional_data: Optional[List[float]] = None
):
    """Generate runic visual signature."""
    try:
        spectral = np.array(spectral_data, dtype=np.float32) if spectral_data else None
        symbolic = np.array(symbolic_data, dtype=np.float32) if symbolic_data else None
        emotional = np.array(emotional_data, dtype=np.float32) if emotional_data else None

        signature = app.state.runic_exporter.generate(
            spectral_vector=spectral,
            symbolic_vector=symbolic,
            emotional_vector=emotional
        )

        return {
            "signature": signature.to_dict(),
            "svg": app.state.runic_exporter.export_svg(signature)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current engine configuration."""
    return {
        "version": "1.0.0",
        "abx_core_version": "1.2",
        "seed_protocol": "1.0",
        "ers_runtime": "1.0",
        "engines": {
            "rhythm": {"seed": app.state.rhythm_engine.seed},
            "harmony": {
                "seed": app.state.harmonic_engine.seed,
                "compression": app.state.harmonic_engine.compression_factor
            },
            "timbre": {"seed": app.state.timbre_engine.seed},
            "motion": {"seed": app.state.motion_engine.seed}
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
