"""
BeatOven Drums API Models

Pydantic request/response models for drums endpoints.

These models provide HTTP API interface to the core drums module.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple


# ==================== RIG PROFILE MODELS ====================

class IOCapabilitiesModel(BaseModel):
    """I/O capabilities model."""
    trigger: bool = True
    gate: bool = True
    accent: bool = False
    velocity: bool = False
    cv_range: str = "0_5"  # "0_5", "neg5_5", "0_10"


class ClockingConfigModel(BaseModel):
    """Clocking configuration model."""
    external_clock: bool = False
    external_reset: bool = False
    swing_source: str = "internal"  # "internal", "external", "hybrid"


class OutputMappingModel(BaseModel):
    """Output mapping model."""
    lane_index: int
    role: str  # "kick", "snare", "hat", "perc", "fx"
    out_id: str


class RigProfileCreateRequest(BaseModel):
    """Request to create/update RigProfile."""
    id: str = Field(..., description="Unique profile ID")
    name: str = Field(..., description="Human-readable name")
    emit_target: str = Field(..., description="Output target: dsp_coffee, midi, cv_gate, audio_stems")
    drum_lanes_max: int = Field(..., ge=1, le=16, description="Maximum drum lanes (1-16)")
    lane_roles_allowed: List[str] = Field(
        default=["kick", "snare", "hat", "perc", "fx"],
        description="Allowed drum roles"
    )
    io_caps: Optional[IOCapabilitiesModel] = None
    clocking: Optional[ClockingConfigModel] = None
    output_map: Optional[List[OutputMappingModel]] = None


class RigProfileResponse(BaseModel):
    """Response with RigProfile data."""
    id: str
    name: str
    emit_target: str
    drum_lanes_max: int
    lane_roles_allowed: List[str]
    io_caps: IOCapabilitiesModel
    clocking: ClockingConfigModel
    output_map: Optional[List[OutputMappingModel]]
    created_at_ts_ms: Optional[int]
    config_hash: str


class RigProfileListResponse(BaseModel):
    """Response with list of profiles."""
    profiles: List[RigProfileResponse]
    total: int
    current_profile_id: Optional[str] = None


class SetCurrentProfileRequest(BaseModel):
    """Request to set current profile."""
    profile_id: str


# ==================== TOPOLOGY MODELS ====================

class DrumLaneModel(BaseModel):
    """Drum lane model."""
    lane_id: str
    role: str
    density_budget: float
    syncopation_budget: float
    accent_support: bool
    out_map: Optional[OutputMappingModel] = None
    allocation_reason: Optional[str] = None


class PercussionTopologyModel(BaseModel):
    """Percussion topology model."""
    rig_profile_id: str
    bpm: Optional[float] = None
    meter: Tuple[int, int] = (4, 4)
    lanes: List[DrumLaneModel]
    global_density_cap: float
    syncopation_budget: float
    fill_policy: str  # "none", "sparse", "moderate", "dense"
    provenance_hash: Optional[str] = None


class TopologyPreviewRequest(BaseModel):
    """Request to preview topology allocation."""
    # ResonanceFrame as dict (simplified for API)
    resonance_metrics: Dict[str, float] = Field(
        ...,
        description="Resonance metrics: complexity, emotional_intensity, groove, energy, density, swing, brightness, tension"
    )
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    bpm: Optional[float] = None
    meter: Optional[Tuple[int, int]] = (4, 4)

    # RigProfile reference
    rig_profile_id: str

    # Generation params
    seed: int = Field(default=42, description="RNG seed for determinism")


class AllocationExplanationModel(BaseModel):
    """Explanation of topology allocation."""
    total_lanes_allocated: int
    max_lanes_available: int
    roles_chosen: List[str]
    density_distribution: Dict[str, float]
    syncopation_distribution: Dict[str, float]
    reasoning: str


class TopologyPreviewResponse(BaseModel):
    """Response with allocated topology."""
    topology: PercussionTopologyModel
    explanation: AllocationExplanationModel
    provenance: Dict[str, Any]


# ==================== PATTERN MODELS ====================

class LanePatternModel(BaseModel):
    """Lane pattern model."""
    lane_id: str
    role: str
    steps: List[float]  # Step grid (0-1 velocities)
    accents: List[bool]  # Accent flags
    resolution: float = 0.25  # Step resolution in beats


class PatternTokensModel(BaseModel):
    """Pattern tokens model."""
    bpm: float
    meter: Tuple[int, int]
    length_bars: int
    lane_patterns: List[LanePatternModel]
    swing_amount: float
    humanize_amount: float
    provenance_hash: Optional[str] = None


class PatternPreviewRequest(BaseModel):
    """Request to preview pattern composition."""
    # Topology (simplified)
    topology: PercussionTopologyModel

    # Generation params
    seed: int = Field(default=42, description="RNG seed for determinism")
    length_bars: int = Field(default=4, ge=1, le=32, description="Pattern length in bars")
    swing_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Swing amount")
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Humanization amount")


class PatternPreviewResponse(BaseModel):
    """Response with composed pattern."""
    pattern: PatternTokensModel
    provenance: Dict[str, Any]


# ==================== ERROR MODELS ====================

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


__all__ = [
    # RigProfile
    "IOCapabilitiesModel",
    "ClockingConfigModel",
    "OutputMappingModel",
    "RigProfileCreateRequest",
    "RigProfileResponse",
    "RigProfileListResponse",
    "SetCurrentProfileRequest",
    # Topology
    "DrumLaneModel",
    "PercussionTopologyModel",
    "TopologyPreviewRequest",
    "AllocationExplanationModel",
    "TopologyPreviewResponse",
    # Pattern
    "LanePatternModel",
    "PatternTokensModel",
    "PatternPreviewRequest",
    "PatternPreviewResponse",
    # Error
    "ErrorResponse",
]
