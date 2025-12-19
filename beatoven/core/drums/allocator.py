"""
BeatOven Drums Lane Allocator (PURE ENGINE)

Deterministic allocation of drum lanes from ResonanceFrame + RigProfile.

PURITY CONTRACT:
- NO file I/O (os, pathlib)
- NO network (requests, httpx)
- NO system clock (time.time(), datetime.now())
- NO randomness except via explicit seed argument (numpy.random.default_rng(seed))
- NO subprocess, uuid, or other nondeterministic operations

All inputs must be explicitly passed as arguments.
All outputs must be deterministic and reproducible.

Code version: 1.0.0
"""

from __future__ import annotations

from typing import Optional, List, Tuple
from dataclasses import dataclass
import hashlib
import json

import numpy as np

# Import from local schema and external ResonanceFrame
from .schema import (
    RigProfile,
    PercussionTopology,
    DrumLane,
    DrumRole,
    OutputMapping,
    _stable_hash,
    _clamp
)


# Version for provenance tracking
ALLOCATOR_VERSION = "1.0.0"


@dataclass
class AllocationExplanation:
    """Explanation of why lanes were allocated (for UI display)."""
    total_lanes_allocated: int
    max_lanes_available: int
    roles_chosen: List[DrumRole]
    density_distribution: dict  # role -> density budget
    syncopation_distribution: dict  # role -> syncopation budget
    reasoning: str


def allocate_lanes(
    resonance_frame: "ResonanceFrame",  # type: ignore
    rig_profile: RigProfile,
    seed: int,
    genre_hint: Optional[str] = None,
    subgenre_hint: Optional[str] = None
) -> Tuple[PercussionTopology, AllocationExplanation]:
    """
    Allocate drum lanes based on ResonanceFrame metrics and RigProfile constraints.

    This is a PURE function: same inputs + seed → same outputs.

    Algorithm:
    1. Extract metrics from ResonanceFrame (complexity, groove, energy, density, etc.)
    2. Determine how many lanes to allocate (1 to rig.drum_lanes_max)
    3. Select which roles to use from rig.lane_roles_allowed
    4. Assign density and syncopation budgets per lane
    5. Allocate output mappings (if rig has explicit mappings)
    6. Compute provenance hash

    Args:
        resonance_frame: Input metrics and context
        rig_profile: Hardware constraints
        seed: RNG seed for deterministic tie-breaking
        genre_hint: Optional genre override
        subgenre_hint: Optional subgenre override

    Returns:
        Tuple of (PercussionTopology, AllocationExplanation)
    """
    rng = np.random.default_rng(seed)

    # Extract metrics (with safe defaults if None)
    metrics = resonance_frame.metrics
    if metrics is None:
        # Default neutral metrics
        complexity = 0.5
        emotional_intensity = 0.5
        groove = 0.5
        energy = 0.5
        density = 0.5
        swing = 0.0
        brightness = 0.5
        tension = 0.5
    else:
        complexity = _clamp(metrics.complexity, 0.0, 1.0)
        emotional_intensity = _clamp(metrics.emotional_intensity, 0.0, 1.0)
        groove = _clamp(metrics.groove, 0.0, 1.0)
        energy = _clamp(metrics.energy, 0.0, 1.0)
        density = _clamp(metrics.density, 0.0, 1.0)
        swing = _clamp(metrics.swing, 0.0, 1.0)
        brightness = _clamp(metrics.brightness, 0.0, 1.0)
        tension = _clamp(metrics.tension, 0.0, 1.0)

    # Genre/subgenre (use from frame if not overridden)
    genre = genre_hint or resonance_frame.genre or "unknown"
    subgenre = subgenre_hint or resonance_frame.subgenre or "unknown"

    # Step 1: Determine number of lanes
    # Formula: base lanes + complexity/energy bonus, clamped to rig max
    base_lanes = _determine_base_lane_count(genre, subgenre)
    complexity_bonus = int(complexity * 2)  # 0-2 extra lanes
    energy_bonus = int(energy * 1.5)  # 0-1 extra lanes

    desired_lanes = base_lanes + complexity_bonus + energy_bonus
    num_lanes = min(desired_lanes, rig_profile.drum_lanes_max)
    num_lanes = max(1, num_lanes)  # At least 1 lane

    # Step 2: Select which roles to use
    # Priority order: kick > snare > hat > perc > fx
    # Always include kick if available, then add others based on complexity/groove
    allowed_roles = list(rig_profile.lane_roles_allowed)
    allowed_roles_sorted = _sort_roles_by_priority(allowed_roles)

    selected_roles = _select_roles(
        allowed_roles_sorted,
        num_lanes,
        groove,
        complexity,
        energy,
        rng
    )

    # Step 3: Assign density budgets per lane
    # Kick gets baseline density, snare gets less, hats get more if groove is high
    lane_densities = _assign_density_budgets(
        selected_roles,
        density,
        groove,
        energy,
        rng
    )

    # Step 4: Assign syncopation budgets
    lane_syncopations = _assign_syncopation_budgets(
        selected_roles,
        complexity,
        tension,
        groove,
        rng
    )

    # Step 5: Create DrumLane objects
    lanes = []
    for i, role in enumerate(selected_roles):
        lane_id = f"lane_{i}_{role.value}"
        density_budget = lane_densities[role]
        syncopation_budget = lane_syncopations[role]
        accent_support = rig_profile.io_caps.accent or rig_profile.io_caps.velocity

        # Assign output mapping if rig has explicit mappings
        out_map = None
        if rig_profile.output_map is not None:
            # Find first unused output with matching role
            for om in rig_profile.output_map:
                if om.role == role and om.lane_index == i:
                    out_map = om
                    break

        allocation_reason = _generate_allocation_reason(role, density_budget, syncopation_budget, metrics)

        lane = DrumLane(
            lane_id=lane_id,
            role=role,
            density_budget=density_budget,
            syncopation_budget=syncopation_budget,
            accent_support=accent_support,
            out_map=out_map,
            allocation_reason=allocation_reason
        )
        lanes.append(lane)

    # Step 6: Determine global constraints
    global_density_cap = _clamp(density * 1.2, 0.0, 1.0)  # Allow slight overage
    syncopation_budget = _clamp((complexity + tension) / 2.0, 0.0, 1.0)

    # Fill policy based on energy/complexity
    if energy < 0.3 and complexity < 0.3:
        fill_policy = "none"
    elif energy < 0.6 and complexity < 0.6:
        fill_policy = "sparse"
    elif energy > 0.8 or complexity > 0.8:
        fill_policy = "dense"
    else:
        fill_policy = "moderate"

    # Step 7: Extract BPM and meter
    bpm = None
    meter = (4, 4)
    if resonance_frame.rhythm is not None:
        bpm = resonance_frame.rhythm.bpm
        meter = resonance_frame.rhythm.meter

    # Step 8: Create topology
    topology = PercussionTopology(
        rig_profile_id=rig_profile.id,
        bpm=bpm,
        meter=meter,
        lanes=tuple(lanes),
        global_density_cap=global_density_cap,
        syncopation_budget=syncopation_budget,
        fill_policy=fill_policy
    )

    # Step 9: Compute provenance
    input_data = {
        "resonance_frame_hash": resonance_frame.provenance_hash or "unknown",
        "rig_profile_hash": rig_profile.config_hash(),
        "genre": genre,
        "subgenre": subgenre,
        "metrics": {
            "complexity": complexity,
            "emotional_intensity": emotional_intensity,
            "groove": groove,
            "energy": energy,
            "density": density,
            "swing": swing,
            "brightness": brightness,
            "tension": tension
        }
    }
    input_hash = _stable_hash(input_data)
    topology = topology.with_provenance_hash(seed, input_hash, ALLOCATOR_VERSION)

    # Step 10: Create explanation
    explanation = AllocationExplanation(
        total_lanes_allocated=len(lanes),
        max_lanes_available=rig_profile.drum_lanes_max,
        roles_chosen=selected_roles,
        density_distribution={role: lane_densities[role] for role in selected_roles},
        syncopation_distribution={role: lane_syncopations[role] for role in selected_roles},
        reasoning=f"Allocated {len(lanes)}/{rig_profile.drum_lanes_max} lanes for {genre} "
                  f"(complexity={complexity:.2f}, energy={energy:.2f}, groove={groove:.2f})"
    )

    return topology, explanation


# ==================== HELPER FUNCTIONS ====================

def _determine_base_lane_count(genre: str, subgenre: str) -> int:
    """
    Determine base number of lanes based on genre.

    Args:
        genre: Music genre
        subgenre: Music subgenre

    Returns:
        Base lane count (1-4)
    """
    genre_lower = genre.lower()
    subgenre_lower = subgenre.lower()

    # Minimal genres: 1-2 lanes
    if any(g in genre_lower for g in ["minimal", "dub", "ambient"]):
        return 2

    # Simple genres: 2-3 lanes
    if any(g in genre_lower for g in ["house", "disco", "funk"]):
        return 3

    # Complex genres: 3-4 lanes
    if any(g in genre_lower for g in ["techno", "dnb", "jungle", "breakbeat", "idm"]):
        return 4

    # Very complex: 4+ lanes
    if any(g in genre_lower for g in ["experimental", "glitch", "footwork"]):
        return 4

    # Default: 3 lanes (kick, snare, hat)
    return 3


def _sort_roles_by_priority(roles: List[DrumRole]) -> List[DrumRole]:
    """
    Sort roles by priority for allocation.

    Priority: kick > snare > hat > perc > fx

    Args:
        roles: List of allowed roles

    Returns:
        Sorted list
    """
    priority_order = {
        DrumRole.KICK: 0,
        DrumRole.SNARE: 1,
        DrumRole.HAT: 2,
        DrumRole.PERC: 3,
        DrumRole.FX: 4
    }
    return sorted(roles, key=lambda r: priority_order.get(r, 99))


def _select_roles(
    allowed_roles: List[DrumRole],
    num_lanes: int,
    groove: float,
    complexity: float,
    energy: float,
    rng: np.random.Generator
) -> List[DrumRole]:
    """
    Select which roles to use for lanes.

    Args:
        allowed_roles: Sorted list of allowed roles
        num_lanes: Number of lanes to allocate
        groove: Groove metric (0-1)
        complexity: Complexity metric (0-1)
        energy: Energy metric (0-1)
        rng: RNG for deterministic tie-breaking

    Returns:
        List of selected roles (length = num_lanes)
    """
    selected = []

    # Always include kick if available
    if DrumRole.KICK in allowed_roles:
        selected.append(DrumRole.KICK)

    # Add snare if available and num_lanes > 1
    if len(selected) < num_lanes and DrumRole.SNARE in allowed_roles:
        selected.append(DrumRole.SNARE)

    # Add hat if available and groove > 0.3
    if len(selected) < num_lanes and DrumRole.HAT in allowed_roles and groove > 0.3:
        selected.append(DrumRole.HAT)

    # Fill remaining with perc/fx based on complexity
    remaining_roles = [r for r in allowed_roles if r not in selected]
    while len(selected) < num_lanes and remaining_roles:
        # Prefer perc if complexity > 0.5, else fx
        if DrumRole.PERC in remaining_roles and complexity > 0.5:
            selected.append(DrumRole.PERC)
            remaining_roles.remove(DrumRole.PERC)
        elif DrumRole.FX in remaining_roles and energy > 0.6:
            selected.append(DrumRole.FX)
            remaining_roles.remove(DrumRole.FX)
        elif remaining_roles:
            # Deterministic fallback: pick first remaining (already sorted by priority)
            selected.append(remaining_roles[0])
            remaining_roles.pop(0)
        else:
            break

    # If still not enough lanes, duplicate roles deterministically
    while len(selected) < num_lanes:
        # Duplicate in priority order: kick, snare, hat, perc, fx
        for role in [DrumRole.KICK, DrumRole.SNARE, DrumRole.HAT, DrumRole.PERC, DrumRole.FX]:
            if role in allowed_roles:
                selected.append(role)
                if len(selected) >= num_lanes:
                    break

    return selected[:num_lanes]


def _assign_density_budgets(
    roles: List[DrumRole],
    density: float,
    groove: float,
    energy: float,
    rng: np.random.Generator
) -> dict:
    """
    Assign density budgets per role.

    Args:
        roles: Selected roles
        density: Global density metric (0-1)
        groove: Groove metric (0-1)
        energy: Energy metric (0-1)
        rng: RNG for variation

    Returns:
        Dict mapping role to density budget
    """
    budgets = {}

    for role in roles:
        if role == DrumRole.KICK:
            # Kick: moderate density, boosted by energy
            base = 0.3 + (energy * 0.3)
        elif role == DrumRole.SNARE:
            # Snare: lower density, boosted by groove
            base = 0.2 + (groove * 0.3)
        elif role == DrumRole.HAT:
            # Hat: high density, boosted by groove
            base = 0.5 + (groove * 0.4)
        elif role == DrumRole.PERC:
            # Perc: moderate, boosted by density
            base = 0.25 + (density * 0.35)
        elif role == DrumRole.FX:
            # FX: sparse, boosted by energy
            base = 0.15 + (energy * 0.25)
        else:
            base = 0.3

        # Apply global density scaling
        budget = base * (0.5 + density * 0.5)

        # Add small deterministic variation to avoid exact ties
        variation = (rng.random() - 0.5) * 0.1
        budget = _clamp(budget + variation, 0.0, 1.0)

        budgets[role] = budget

    return budgets


def _assign_syncopation_budgets(
    roles: List[DrumRole],
    complexity: float,
    tension: float,
    groove: float,
    rng: np.random.Generator
) -> dict:
    """
    Assign syncopation budgets per role.

    Args:
        roles: Selected roles
        complexity: Complexity metric (0-1)
        tension: Tension metric (0-1)
        groove: Groove metric (0-1)
        rng: RNG for variation

    Returns:
        Dict mapping role to syncopation budget
    """
    budgets = {}

    for role in roles:
        if role == DrumRole.KICK:
            # Kick: low syncopation, boosted by tension
            base = 0.2 + (tension * 0.3)
        elif role == DrumRole.SNARE:
            # Snare: moderate syncopation, boosted by complexity
            base = 0.3 + (complexity * 0.4)
        elif role == DrumRole.HAT:
            # Hat: high syncopation, boosted by groove
            base = 0.4 + (groove * 0.4)
        elif role == DrumRole.PERC:
            # Perc: high syncopation, boosted by complexity
            base = 0.5 + (complexity * 0.3)
        elif role == DrumRole.FX:
            # FX: very high syncopation
            base = 0.6 + (tension * 0.3)
        else:
            base = 0.3

        # Add small deterministic variation
        variation = (rng.random() - 0.5) * 0.1
        budget = _clamp(base + variation, 0.0, 1.0)

        budgets[role] = budget

    return budgets


def _generate_allocation_reason(
    role: DrumRole,
    density_budget: float,
    syncopation_budget: float,
    metrics: Optional[Any]
) -> str:
    """
    Generate human-readable explanation for why this lane was allocated.

    Args:
        role: Drum role
        density_budget: Allocated density
        syncopation_budget: Allocated syncopation
        metrics: ResonanceMetrics (optional)

    Returns:
        Explanation string
    """
    if metrics is None:
        return f"{role.value} lane allocated with density={density_budget:.2f}, syncopation={syncopation_budget:.2f}"

    # Extract key metrics
    energy = _clamp(metrics.energy, 0.0, 1.0)
    groove = _clamp(metrics.groove, 0.0, 1.0)
    complexity = _clamp(metrics.complexity, 0.0, 1.0)

    # Generate reason based on role and metrics
    if role == DrumRole.KICK:
        if energy > 0.7:
            return f"High-energy kick (energy={energy:.2f})"
        else:
            return f"Foundational kick layer"
    elif role == DrumRole.SNARE:
        if groove > 0.6:
            return f"Groove-driven snare (groove={groove:.2f})"
        else:
            return f"Backbeat snare"
    elif role == DrumRole.HAT:
        if groove > 0.7:
            return f"Dense hat pattern for groove (groove={groove:.2f})"
        else:
            return f"Rhythmic hat layer"
    elif role == DrumRole.PERC:
        if complexity > 0.6:
            return f"Complex percussion (complexity={complexity:.2f})"
        else:
            return f"Accent percussion"
    elif role == DrumRole.FX:
        if energy > 0.7:
            return f"High-energy FX layer (energy={energy:.2f})"
        else:
            return f"Textural FX"
    else:
        return f"{role.value} lane"


__all__ = [
    "ALLOCATOR_VERSION",
    "AllocationExplanation",
    "allocate_lanes",
]
