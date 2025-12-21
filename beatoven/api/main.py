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
from beatoven.core.ringtone import RingtoneGenerator, RingtoneType
from beatoven.signals import SignalDocument, SourceCategory, SignalNormalizer, SourceType
from beatoven.signals.feeds import FeedIngester, get_predefined_groups
from beatoven.audio import StemExtractor, AudioIO, StemType as AudioStemType
from beatoven.runtime.orchestrator import Orchestrator


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
    app.state.ringtone_generator = RingtoneGenerator()
    app.state.feed_ingester = FeedIngester()
    app.state.stem_extractor = StemExtractor()
    app.state.orchestrator = Orchestrator()

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
        seed_source = request.seed or hashlib.sha256(request.text_intent.encode()).hexdigest()
        seed = ABXRunesSeed(f"beatoven_{seed_source}")

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
        rhythm_payload = {
            "density": density,
            "tension": tension,
            "drift": drift,
            "tempo": request.tempo,
            "length_bars": int(request.duration / 4),
        }
        rhythm_result = app.state.orchestrator.run_rune(
            "engine.rhythm.generate",
            rhythm_payload,
            seed.numeric_seed,
        )
        rhythm_pattern, rhythm_desc = app.state.rhythm_engine.generate(**rhythm_payload)

        # Generate harmony
        harmony_payload = {
            "resonance": resonance,
            "tension": tension,
            "contrast": contrast,
            "key_root": request.key_root,
            "scale": scale.name,
            "length_bars": int(request.duration / 4),
        }
        harmony_result = app.state.orchestrator.run_rune(
            "engine.harmony.generate",
            harmony_payload,
            seed.numeric_seed,
        )
        harmonic_prog, harmonic_desc = app.state.harmonic_engine.generate(
            resonance=resonance,
            tension=tension,
            contrast=contrast,
            key_root=request.key_root,
            scale=scale,
            length_bars=int(request.duration / 4),
        )

        # Generate motion
        motion_payload = {
            "drift": drift,
            "tension": tension,
            "resonance": resonance,
            "duration": request.duration,
            "rune_vector": symbolic_vector.rune_vector,
        }
        motion_result = app.state.orchestrator.run_rune(
            "engine.motion.generate",
            motion_payload,
            seed.numeric_seed,
        )
        motion_curves, motion_desc = app.state.motion_engine.generate(**motion_payload)

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
            stems_generated=[s.value for s in stems.keys()],
            rarity_metadata={
                "rune_manifests": {
                    "rhythm": rhythm_result.manifest["manifest_hash"],
                    "harmony": harmony_result.manifest["manifest_hash"],
                    "motion": motion_result.manifest["manifest_hash"],
                }
            },
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


@app.get("/api/capabilities")
async def get_capabilities():
    """Expose backend capability availability for UI rendering."""
    return {
        "features": [
            {"id": "gpu", "available": app.state.stem_extractor.device != "cpu", "reason": "CPU fallback" if app.state.stem_extractor.device == "cpu" else None},
            {"id": "rhythm.pattern.polymetric", "available": True, "reason": None},
            {"id": "rhythm.pattern.random", "available": True, "reason": None},
            {"id": "harmony.scale.locrian", "available": True, "reason": None},
            {"id": "timbre.texture.metallic", "available": True, "reason": None},
        ]
    }


@app.get("/api/config/schema")
async def get_config_schema():
    """Expose configuration schema for dynamic UI controls."""
    return {
        "version": "1.0.0",
        "modules": {
            "rhythm": {
                "tempo": {"min": 60, "max": 200, "default": 120},
                "swing": {"min": 0, "max": 1, "default": 0.0},
                "density": {"min": 0, "max": 1, "default": 0.5},
                "pattern": {
                    "options": [
                        {"value": "euclidean", "label": "euclidean"},
                        {"value": "polymetric", "label": "polymetric"},
                        {"value": "linear", "label": "linear"},
                        {"value": "random", "label": "random"},
                    ]
                },
            },
            "harmony": {
                "scale": {
                    "options": [
                        {"value": "major", "label": "major"},
                        {"value": "minor", "label": "minor"},
                        {"value": "dorian", "label": "dorian"},
                        {"value": "phrygian", "label": "phrygian"},
                        {"value": "lydian", "label": "lydian"},
                        {"value": "mixolydian", "label": "mixolydian"},
                        {"value": "locrian", "label": "locrian"},
                    ]
                },
                "tension": {"min": 0, "max": 1, "default": 0.5},
                "complexity": {"min": 0, "max": 1, "default": 0.5},
            },
            "timbre": {
                "texture": {
                    "options": [
                        {"value": "smooth", "label": "smooth"},
                        {"value": "gritty", "label": "gritty"},
                        {"value": "metallic", "label": "metallic"},
                        {"value": "organic", "label": "organic"},
                        {"value": "digital", "label": "digital"},
                    ]
                },
                "brightness": {"min": 0, "max": 1, "default": 0.5},
                "warmth": {"min": 0, "max": 1, "default": 0.5},
                "reverb": {"min": 0, "max": 1, "default": 0.3},
            },
            "motion": {
                "lfoRate": {"min": 0, "max": 1, "default": 0.5},
                "lfoDepth": {"min": 0, "max": 1, "default": 0.3},
                "attack": {"min": 0, "max": 1, "default": 0.1},
                "decay": {"min": 0, "max": 1, "default": 0.5},
            },
        },
    }


# ========== SIGNALS INTAKE ROUTES ==========

class SignalIngestRequest(BaseModel):
    """Request to ingest signals from source"""
    source_url: Optional[str] = None
    source_text: Optional[str] = None
    source_category: str = Field(default="CUSTOM")
    title: Optional[str] = "Untitled"


@app.post("/signals/ingest")
async def ingest_signal(request: SignalIngestRequest):
    """Ingest signal from URL or text and normalize to SignalDocument"""
    try:
        category = SourceCategory[request.source_category]

        if request.source_url:
            # Ingest from feed URL
            docs = app.state.feed_ingester.ingest_rss_feed(request.source_url, category)
            return {"documents": [doc.to_dict() for doc in docs]}

        elif request.source_text:
            # Normalize text directly
            doc = SignalNormalizer.normalize_text(
                request.source_text,
                SourceType.TEXT_FILE,
                category,
                request.title
            )
            return {"documents": [doc.to_dict()]}

        else:
            raise HTTPException(status_code=400, detail="Must provide source_url or source_text")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/groups")
async def get_signal_groups():
    """Get predefined signal source groups"""
    groups = get_predefined_groups()
    return {"groups": [g.to_dict() for g in groups]}


@app.get("/signals/categories")
async def get_signal_categories():
    """List all available signal categories"""
    return {
        "categories": [c.value for c in SourceCategory]
    }


# ========== STEM EXTRACTION ROUTES ==========

class StemExtractionRequest(BaseModel):
    """Request for stem extraction from uploaded audio"""
    file_path: str = Field(..., description="Path to uploaded audio file")
    stem_types: Optional[List[str]] = Field(default=None, description="Specific stems to extract")


@app.post("/stems/extract")
async def extract_stems(request: StemExtractionRequest):
    """
    Extract stems from uploaded audio file.
    Returns stems with emotional/symbolic metadata.
    """
    try:
        # Parse stem types
        if request.stem_types:
            stem_types = [AudioStemType[st.upper()] for st in request.stem_types]
        else:
            stem_types = None

        # Extract stems
        stems = app.state.stem_extractor.extract_stems(
            request.file_path,
            stem_types
        )

        return {
            "stems": [stem.to_dict() for stem in stems],
            "count": len(stems)
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stems/formats")
async def get_supported_formats():
    """List supported audio formats for stem extraction"""
    from beatoven.audio import AudioFormat
    return {
        "input_formats": [f.value for f in AudioFormat],
        "output_formats": ["wav", "flac", "mp3", "m4a"],
        "sample_rates": [44100, 48000, 88200, 96000, 176400, 192000],
        "bit_depths": [16, 24, 32]
    }


# ========== RINGTONE GENERATION ROUTES ==========

class RingtoneRequest(BaseModel):
    """Request for ringtone/notification generation"""
    duration_seconds: float = Field(default=25.0, ge=1, le=30)
    ringtone_type: str = Field(default="standard_ringtone")
    melodic: bool = Field(default=True)
    percussive: bool = Field(default=True)
    intensity: float = Field(default=0.7, ge=0, le=1)
    loop_seamless: bool = Field(default=True)


@app.post("/ringtone/generate")
async def generate_ringtone(request: RingtoneRequest):
    """
    Generate ringtone or notification sound.
    Returns audio data and metadata.
    """
    try:
        ringtone_type = RingtoneType[request.ringtone_type.upper()]

        if ringtone_type == RingtoneType.NOTIFICATION:
            audio = app.state.ringtone_generator.generate_notification(
                duration_seconds=request.duration_seconds,
                melodic=request.melodic,
                intensity=request.intensity
            )
        else:
            audio = app.state.ringtone_generator.generate_ringtone(
                duration_seconds=request.duration_seconds,
                melodic=request.melodic,
                percussive=request.percussive,
                intensity=request.intensity,
                loop_seamless=request.loop_seamless
            )

        # Generate provenance hash
        hash_input = f"ringtone:{request.dict()}"
        provenance = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        return {
            "duration": len(audio) / 44100,
            "sample_rate": 44100,
            "samples": int(len(audio)),
            "ringtone_type": ringtone_type.value,
            "provenance_hash": provenance,
            "download_ready": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ringtone/types")
async def get_ringtone_types():
    """List available ringtone types"""
    return {
        "types": [rt.value for rt in RingtoneType],
        "duration_limits": {
            "notification": {"min": 1, "max": 5},
            "short_ringtone": {"min": 10, "max": 15},
            "standard_ringtone": {"min": 20, "max": 30}
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
