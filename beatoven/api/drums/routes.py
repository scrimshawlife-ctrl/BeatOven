"""
BeatOven Drums API Routes

FastAPI routes for rig profiles, topology preview, and pattern preview.

Endpoints:
- POST /api/rig/profiles - Create/update profile
- GET /api/rig/profiles - List all profiles
- GET /api/rig/profiles/{id} - Get specific profile
- DELETE /api/rig/profiles/{id} - Delete profile
- POST /api/rig/profiles/current - Set current profile
- GET /api/rig/profiles/current - Get current profile
- POST /api/drums/topology/preview - Preview topology allocation
- POST /api/drums/pattern/preview - Preview pattern composition
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time

from beatoven.core.drums import (
    RigProfile,
    EmitTarget,
    DrumRole,
    IOCapabilities,
    ClockingConfig,
    OutputMapping,
    CVRange,
    SwingSource,
    allocate_lanes,
    compose_pattern,
    get_default_storage,
    RigProfileStorage,
    PercussionTopology,
    DrumLane,
    ALLOCATOR_VERSION,
    COMPOSER_VERSION,
)

from beatoven.dspcoffee_bridge.schema import ResonanceFrame, ResonanceMetrics

from .models import (
    RigProfileCreateRequest,
    RigProfileResponse,
    RigProfileListResponse,
    SetCurrentProfileRequest,
    TopologyPreviewRequest,
    TopologyPreviewResponse,
    PatternPreviewRequest,
    PatternPreviewResponse,
    DrumLaneModel,
    PercussionTopologyModel,
    AllocationExplanationModel,
    LanePatternModel,
    PatternTokensModel,
    IOCapabilitiesModel,
    ClockingConfigModel,
    OutputMappingModel,
)


router = APIRouter()


# ==================== DEPENDENCY INJECTION ====================

def get_storage() -> RigProfileStorage:
    """Get RigProfileStorage instance."""
    return get_default_storage()


# ==================== CONVERSION HELPERS ====================

def _rig_profile_to_response(profile: RigProfile) -> RigProfileResponse:
    """Convert RigProfile to response model."""
    return RigProfileResponse(
        id=profile.id,
        name=profile.name,
        emit_target=profile.emit_target.value,
        drum_lanes_max=profile.drum_lanes_max,
        lane_roles_allowed=[r.value for r in profile.lane_roles_allowed],
        io_caps=IOCapabilitiesModel(
            trigger=profile.io_caps.trigger,
            gate=profile.io_caps.gate,
            accent=profile.io_caps.accent,
            velocity=profile.io_caps.velocity,
            cv_range=profile.io_caps.cv_range.value
        ),
        clocking=ClockingConfigModel(
            external_clock=profile.clocking.external_clock,
            external_reset=profile.clocking.external_reset,
            swing_source=profile.clocking.swing_source.value
        ),
        output_map=[
            OutputMappingModel(
                lane_index=om.lane_index,
                role=om.role.value,
                out_id=om.out_id
            )
            for om in profile.output_map
        ] if profile.output_map else None,
        created_at_ts_ms=profile.created_at_ts_ms,
        config_hash=profile.config_hash()
    )


def _request_to_rig_profile(req: RigProfileCreateRequest) -> RigProfile:
    """Convert request to RigProfile."""
    io_caps = IOCapabilities(
        trigger=req.io_caps.trigger if req.io_caps else True,
        gate=req.io_caps.gate if req.io_caps else True,
        accent=req.io_caps.accent if req.io_caps else False,
        velocity=req.io_caps.velocity if req.io_caps else False,
        cv_range=CVRange(req.io_caps.cv_range) if req.io_caps else CVRange.ZERO_5V
    )

    clocking = ClockingConfig(
        external_clock=req.clocking.external_clock if req.clocking else False,
        external_reset=req.clocking.external_reset if req.clocking else False,
        swing_source=SwingSource(req.clocking.swing_source) if req.clocking else SwingSource.INTERNAL
    )

    output_map = tuple(
        OutputMapping(
            lane_index=om.lane_index,
            role=DrumRole(om.role),
            out_id=om.out_id
        )
        for om in req.output_map
    ) if req.output_map else None

    return RigProfile(
        id=req.id,
        name=req.name,
        emit_target=EmitTarget(req.emit_target),
        drum_lanes_max=req.drum_lanes_max,
        lane_roles_allowed=tuple(DrumRole(r) for r in req.lane_roles_allowed),
        io_caps=io_caps,
        clocking=clocking,
        output_map=output_map,
        created_at_ts_ms=int(time.time() * 1000)
    )


def _topology_to_model(topology: PercussionTopology) -> PercussionTopologyModel:
    """Convert PercussionTopology to model."""
    return PercussionTopologyModel(
        rig_profile_id=topology.rig_profile_id,
        bpm=topology.bpm,
        meter=topology.meter,
        lanes=[
            DrumLaneModel(
                lane_id=lane.lane_id,
                role=lane.role.value,
                density_budget=lane.density_budget,
                syncopation_budget=lane.syncopation_budget,
                accent_support=lane.accent_support,
                out_map=OutputMappingModel(
                    lane_index=lane.out_map.lane_index,
                    role=lane.out_map.role.value,
                    out_id=lane.out_map.out_id
                ) if lane.out_map else None,
                allocation_reason=lane.allocation_reason
            )
            for lane in topology.lanes
        ],
        global_density_cap=topology.global_density_cap,
        syncopation_budget=topology.syncopation_budget,
        fill_policy=topology.fill_policy,
        provenance_hash=topology.provenance_hash
    )


def _model_to_topology(model: PercussionTopologyModel) -> PercussionTopology:
    """Convert model to PercussionTopology."""
    return PercussionTopology(
        rig_profile_id=model.rig_profile_id,
        bpm=model.bpm,
        meter=model.meter,
        lanes=tuple(
            DrumLane(
                lane_id=lane.lane_id,
                role=DrumRole(lane.role),
                density_budget=lane.density_budget,
                syncopation_budget=lane.syncopation_budget,
                accent_support=lane.accent_support,
                out_map=OutputMapping(
                    lane_index=lane.out_map.lane_index,
                    role=DrumRole(lane.out_map.role),
                    out_id=lane.out_map.out_id
                ) if lane.out_map else None,
                allocation_reason=lane.allocation_reason
            )
            for lane in model.lanes
        ),
        global_density_cap=model.global_density_cap,
        syncopation_budget=model.syncopation_budget,
        fill_policy=model.fill_policy,
        provenance_hash=model.provenance_hash
    )


# ==================== RIG PROFILE ROUTES ====================

@router.post("/rig/profiles", response_model=RigProfileResponse)
async def create_profile(request: RigProfileCreateRequest, storage: RigProfileStorage = Depends(get_storage)):
    """Create or update a rig profile."""
    try:
        profile = _request_to_rig_profile(request)
        storage.save(profile)
        return _rig_profile_to_response(profile)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rig/profiles", response_model=RigProfileListResponse)
async def list_profiles(storage: RigProfileStorage = Depends(get_storage)):
    """List all rig profiles."""
    try:
        profiles = storage.list()
        current_id = storage.get_current_id()

        return RigProfileListResponse(
            profiles=[_rig_profile_to_response(p) for p in profiles],
            total=len(profiles),
            current_profile_id=current_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rig/profiles/{profile_id}", response_model=RigProfileResponse)
async def get_profile(profile_id: str, storage: RigProfileStorage = Depends(get_storage)):
    """Get a specific rig profile."""
    try:
        profile = storage.load(profile_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")

        return _rig_profile_to_response(profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rig/profiles/{profile_id}")
async def delete_profile(profile_id: str, storage: RigProfileStorage = Depends(get_storage)):
    """Delete a rig profile."""
    try:
        success = storage.delete(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found")

        return {"success": True, "deleted_id": profile_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rig/profiles/current")
async def set_current_profile(request: SetCurrentProfileRequest, storage: RigProfileStorage = Depends(get_storage)):
    """Set the current active rig profile."""
    try:
        success = storage.set_current(request.profile_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Profile '{request.profile_id}' not found")

        return {"success": True, "current_profile_id": request.profile_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rig/profiles/current", response_model=RigProfileResponse)
async def get_current_profile(storage: RigProfileStorage = Depends(get_storage)):
    """Get the current active rig profile."""
    try:
        profile = storage.get_current()
        if profile is None:
            raise HTTPException(status_code=404, detail="No current profile set")

        return _rig_profile_to_response(profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TOPOLOGY PREVIEW ROUTES ====================

@router.post("/drums/topology/preview", response_model=TopologyPreviewResponse)
async def preview_topology(request: TopologyPreviewRequest, storage: RigProfileStorage = Depends(get_storage)):
    """
    Preview percussion topology allocation.

    Generates topology from resonance metrics and rig profile constraints.
    Deterministic: same inputs + seed → same topology.
    """
    try:
        # Load rig profile
        rig_profile = storage.load(request.rig_profile_id)
        if rig_profile is None:
            raise HTTPException(status_code=404, detail=f"Rig profile '{request.rig_profile_id}' not found")

        # Build ResonanceMetrics from request
        metrics = ResonanceMetrics(
            complexity=request.resonance_metrics.get("complexity", 0.5),
            emotional_intensity=request.resonance_metrics.get("emotional_intensity", 0.5),
            groove=request.resonance_metrics.get("groove", 0.5),
            energy=request.resonance_metrics.get("energy", 0.5),
            density=request.resonance_metrics.get("density", 0.5),
            swing=request.resonance_metrics.get("swing", 0.0),
            brightness=request.resonance_metrics.get("brightness", 0.5),
            tension=request.resonance_metrics.get("tension", 0.5),
        )

        # Build minimal ResonanceFrame
        resonance_frame = ResonanceFrame.new(
            source="beatoven_render",
            genre=request.genre or "unknown",
            subgenre=request.subgenre,
            metrics=metrics
        ).with_provenance_hash()

        # Allocate topology
        topology, explanation = allocate_lanes(
            resonance_frame,
            rig_profile,
            request.seed,
            genre_hint=request.genre,
            subgenre_hint=request.subgenre
        )

        # Build response
        return TopologyPreviewResponse(
            topology=_topology_to_model(topology),
            explanation=AllocationExplanationModel(
                total_lanes_allocated=explanation.total_lanes_allocated,
                max_lanes_available=explanation.max_lanes_available,
                roles_chosen=[r.value for r in explanation.roles_chosen],
                density_distribution={r.value: v for r, v in explanation.density_distribution.items()},
                syncopation_distribution={r.value: v for r, v in explanation.syncopation_distribution.items()},
                reasoning=explanation.reasoning
            ),
            provenance={
                "allocator_version": ALLOCATOR_VERSION,
                "seed": request.seed,
                "rig_profile_hash": rig_profile.config_hash(),
                "resonance_frame_hash": resonance_frame.provenance_hash,
                "topology_hash": topology.provenance_hash
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PATTERN PREVIEW ROUTES ====================

@router.post("/drums/pattern/preview", response_model=PatternPreviewResponse)
async def preview_pattern(request: PatternPreviewRequest):
    """
    Preview pattern composition from topology.

    Generates concrete step grids from percussion topology.
    Deterministic: same topology + seed → same pattern.
    """
    try:
        # Convert model to topology
        topology = _model_to_topology(request.topology)

        # Compose pattern
        pattern = compose_pattern(
            topology,
            request.seed,
            length_bars=request.length_bars,
            swing_amount=request.swing_amount,
            humanize_amount=request.humanize_amount
        )

        # Convert to model
        pattern_model = PatternTokensModel(
            bpm=pattern.bpm,
            meter=pattern.meter,
            length_bars=pattern.length_bars,
            lane_patterns=[
                LanePatternModel(
                    lane_id=lp.lane_id,
                    role=lp.role.value,
                    steps=list(lp.steps),
                    accents=list(lp.accents),
                    resolution=lp.resolution
                )
                for lp in pattern.lane_patterns
            ],
            swing_amount=pattern.swing_amount,
            humanize_amount=pattern.humanize_amount,
            provenance_hash=pattern.provenance_hash
        )

        return PatternPreviewResponse(
            pattern=pattern_model,
            provenance={
                "composer_version": COMPOSER_VERSION,
                "seed": request.seed,
                "topology_hash": topology.provenance_hash,
                "pattern_hash": pattern.provenance_hash
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
