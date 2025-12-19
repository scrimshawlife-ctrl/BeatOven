"""
Pydantic models for media analysis API
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional


class BinauralSpecModel(BaseModel):
    """Binaural beat specification"""
    carrier_hz: float = Field(200.0, ge=80.0, le=1000.0, description="Carrier frequency in Hz")
    beat_hz: float = Field(6.0, ge=0.5, le=40.0, description="Beat frequency in Hz")
    mix: float = Field(0.15, ge=0.0, le=1.0, description="Mix level (0=dry, 1=wet)")
    ramp_s: float = Field(2.0, ge=0.0, le=10.0, description="Fade in/out duration in seconds")
    phase_deg: float = Field(0.0, ge=0.0, le=360.0, description="Phase offset in degrees")
    pan: float = Field(0.0, ge=-1.0, le=1.0, description="Pan bias (-1=left, 0=center, 1=right)")


class MediaAnalysisRequest(BaseModel):
    """Request to analyze uploaded media"""
    media_id: str
    kind: Literal["image", "video"]
    enable_semantic: bool = Field(False, description="Enable semantic providers (CLIP, action, audio)")


class MediaAnalysisResponse(BaseModel):
    """Response from media analysis"""
    media_id: str
    kind: str
    physical: Dict[str, Any]
    semantic: Dict[str, Any]
    affect: Dict[str, float]
    confidence: Dict[str, float]
    perceived_era: Optional[Dict[str, float]]
    era_confidence: float
    resonance_metrics: Dict[str, float]
    provider_status: List[Dict[str, Any]] = Field(default_factory=list)


class CapabilitiesResponse(BaseModel):
    """System capabilities report"""
    semantic: Dict[str, Any]
    binaural: Dict[str, Any]


class BinauralPreviewRequest(BaseModel):
    """Request to preview binaural FX on audio"""
    spec: BinauralSpecModel
    duration_s: float = Field(5.0, ge=1.0, le=30.0, description="Preview duration in seconds")
    sample_rate: int = Field(44100, ge=8000, le=96000, description="Sample rate in Hz")
