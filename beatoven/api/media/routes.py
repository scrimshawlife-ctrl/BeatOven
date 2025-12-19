"""
Media analysis and FX routes for BeatOven API

Endpoints:
- GET /api/capabilities - System capabilities (providers, FX)
- POST /api/media/analyze - Analyze uploaded media
- POST /api/fx/binaural/preview - Preview binaural FX
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pathlib import Path
import tempfile
import numpy as np
from typing import Any, Dict, Optional

from .models import (
    MediaAnalysisRequest,
    MediaAnalysisResponse,
    CapabilitiesResponse,
    BinauralPreviewRequest,
    BinauralSpecModel,
)

# Create router
router = APIRouter(prefix="/api", tags=["media"])

# Global semantic engine (initialized on startup)
_semantic_engine: Optional[Any] = None


def get_semantic_engine():
    """Dependency to get semantic engine"""
    global _semantic_engine
    if _semantic_engine is None:
        from beatoven.media_intel.semantic_engine import SemanticEngine
        from beatoven.media_intel.providers.clip_provider import ClipProvider
        from beatoven.media_intel.providers.action_provider import ActionProvider
        from beatoven.media_intel.providers.audio_provider import AudioMoodProvider

        _semantic_engine = SemanticEngine(providers=[
            ClipProvider(),
            ActionProvider(),
            AudioMoodProvider(),
        ])
    return _semantic_engine


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities(sem_engine = Depends(get_semantic_engine)):
    """
    Get system capabilities.

    Returns available providers and FX with installation status.
    UI can show all options and gray out unavailable ones.
    """
    from beatoven.media_intel.capabilities import compute_capabilities

    caps = compute_capabilities(sem_engine)
    return CapabilitiesResponse(
        semantic=caps.semantic,
        binaural=caps.binaural,
    )


@router.post("/media/analyze", response_model=MediaAnalysisResponse)
async def analyze_media(
    file: UploadFile = File(...),
    media_id: str = "upload",
    kind: str = "image",
    enable_semantic: bool = False,
    sem_engine = Depends(get_semantic_engine)
):
    """
    Analyze uploaded image or video.

    Returns:
    - Physical features (color, texture, motion)
    - Semantic tags (if enabled and providers available)
    - Affect scores (valence, arousal, dominance, blends)
    - Resonance metrics for dsp.coffee bridge
    - Provider status (what ran, what failed)
    """
    from beatoven.media_intel.analyzer import analyze_image, analyze_video
    from beatoven.media_intel.to_resonance import media_to_resonance

    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or "upload").suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Analyze
        sem = sem_engine if enable_semantic else None
        if kind == "image":
            media_frame = analyze_image(tmp_path, media_id=media_id, semantic_engine=sem)
        elif kind == "video":
            media_frame = analyze_video(tmp_path, media_id=media_id, semantic_engine=sem)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid kind: {kind}")

        # Convert to resonance
        resonance_frame = media_to_resonance(media_frame)

        # Build response
        return MediaAnalysisResponse(
            media_id=media_frame.media_id,
            kind=media_frame.kind,
            physical=media_frame.physical,
            semantic=media_frame.semantic,
            affect=media_frame.affect,
            confidence=media_frame.confidence,
            perceived_era=media_frame.perceived_era,
            era_confidence=media_frame.era_confidence,
            resonance_metrics={
                "complexity": resonance_frame.metrics.complexity,
                "emotional_intensity": resonance_frame.metrics.emotional_intensity,
                "groove": resonance_frame.metrics.groove,
                "energy": resonance_frame.metrics.energy,
                "density": resonance_frame.metrics.density,
                "swing": resonance_frame.metrics.swing,
                "brightness": resonance_frame.metrics.brightness,
                "tension": resonance_frame.metrics.tension,
            } if resonance_frame.metrics else {},
            provider_status=sem_engine.capabilities()["providers"] if enable_semantic else [],
        )
    finally:
        # Cleanup temp file
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/fx/binaural/preview")
async def preview_binaural(request: BinauralPreviewRequest):
    """
    Generate preview of binaural FX.

    Returns base64-encoded WAV audio for playback.
    Useful for testing binaural settings before applying to full render.
    """
    from beatoven.audio_fx import BinauralSpec, apply_binaural
    import io
    import wave
    import base64

    # Generate test tone (stereo)
    sr = request.sample_rate
    duration = request.duration_s
    n = int(sr * duration)

    # Simple test signal: pink noise + gentle tone
    t = np.arange(n, dtype=np.float32) / float(sr)
    tone = 0.3 * np.sin(2.0 * np.pi * 440.0 * t)
    noise = np.random.randn(n).astype(np.float32) * 0.1
    test = tone + noise

    # Make stereo
    stereo = np.stack([test, test], axis=1)

    # Apply binaural
    spec = BinauralSpec(
        carrier_hz=request.spec.carrier_hz,
        beat_hz=request.spec.beat_hz,
        mix=request.spec.mix,
        ramp_s=request.spec.ramp_s,
        phase_deg=request.spec.phase_deg,
        pan=request.spec.pan,
    )
    result = apply_binaural(stereo, sr, spec)

    # Convert to int16 PCM
    pcm = (result * 32767.0).astype(np.int16)

    # Encode as WAV
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

    # Return base64
    wav_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return {
        "audio_base64": wav_b64,
        "format": "wav",
        "sample_rate": sr,
        "duration_s": duration,
        "spec": request.spec.dict(),
    }
