"""
BeatOven Drums Pattern Composer (PURE ENGINE)

Deterministic composition of drum patterns from PercussionTopology.

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

from typing import List, Tuple
import hashlib
import json

import numpy as np

# Import from local schema
from .schema import (
    PercussionTopology,
    PatternTokens,
    LanePattern,
    DrumRole,
    DrumLane,
    _stable_hash,
    _clamp
)


# Version for provenance tracking
COMPOSER_VERSION = "1.0.0"


def compose_pattern(
    topology: PercussionTopology,
    seed: int,
    length_bars: int = 4,
    swing_amount: float = 0.0,
    humanize_amount: float = 0.0
) -> PatternTokens:
    """
    Compose drum pattern from topology.

    This is a PURE function: same inputs + seed → same outputs.

    Algorithm:
    1. For each lane in topology, generate step grid using Euclidean rhythm
    2. Apply density and syncopation budgets
    3. Generate accent patterns
    4. Apply global swing if specified
    5. Compute provenance hash

    Args:
        topology: Percussion topology with lanes and budgets
        seed: RNG seed for deterministic composition
        length_bars: Pattern length in bars
        swing_amount: Global swing amount (0-1), overrides topology hints
        humanize_amount: Timing/velocity humanization (0-1)

    Returns:
        PatternTokens with step grids and accents
    """
    rng = np.random.default_rng(seed)

    # Extract global parameters
    bpm = topology.bpm or 120.0
    meter = topology.meter
    beats_per_bar = meter[0] * (4 / meter[1])
    total_beats = beats_per_bar * length_bars

    # Determine step resolution (16th notes = 0.25 beats)
    resolution = 0.25
    total_steps = int(total_beats / resolution)

    # Generate patterns for each lane
    lane_patterns = []
    for lane in topology.lanes:
        pattern = _generate_lane_pattern(
            lane,
            total_steps,
            resolution,
            topology.global_density_cap,
            topology.syncopation_budget,
            rng
        )
        lane_patterns.append(pattern)

    # Create pattern tokens
    tokens = PatternTokens(
        bpm=bpm,
        meter=meter,
        length_bars=length_bars,
        lane_patterns=tuple(lane_patterns),
        swing_amount=swing_amount,
        humanize_amount=humanize_amount
    )

    # Compute provenance
    input_data = {
        "topology_hash": topology.provenance_hash or "unknown",
        "length_bars": length_bars,
        "swing_amount": swing_amount,
        "humanize_amount": humanize_amount
    }
    input_hash = _stable_hash(input_data)
    tokens = tokens.with_provenance_hash(seed, input_hash, COMPOSER_VERSION)

    return tokens


def _generate_lane_pattern(
    lane: DrumLane,
    total_steps: int,
    resolution: float,
    global_density_cap: float,
    global_syncopation_budget: float,
    rng: np.random.Generator
) -> LanePattern:
    """
    Generate step grid for a single lane.

    Args:
        lane: DrumLane with role and budgets
        total_steps: Total number of steps in pattern
        resolution: Step resolution in beats
        global_density_cap: Global density limit (0-1)
        global_syncopation_budget: Global syncopation budget (0-1)
        rng: RNG for deterministic composition

    Returns:
        LanePattern with steps and accents
    """
    # Clamp budgets to global caps
    density = min(lane.density_budget, global_density_cap)
    syncopation = min(lane.syncopation_budget, global_syncopation_budget)

    # Calculate number of hits for Euclidean rhythm
    # density determines how many steps have hits
    pulses = int(total_steps * density)
    pulses = max(1, min(pulses, total_steps))  # At least 1 hit, at most all steps

    # Generate base Euclidean pattern
    euclidean_pattern = _euclidean_rhythm(pulses, total_steps)

    # Apply syncopation: shift some hits off-beat
    if syncopation > 0.3:
        euclidean_pattern = _apply_syncopation(euclidean_pattern, syncopation, rng)

    # Convert boolean pattern to velocity/probability grid
    steps = []
    for hit in euclidean_pattern:
        if hit:
            # Base velocity determined by role
            if lane.role == DrumRole.KICK:
                base_vel = 0.85  # Strong
            elif lane.role == DrumRole.SNARE:
                base_vel = 0.8
            elif lane.role == DrumRole.HAT:
                base_vel = 0.6   # Lighter
            elif lane.role == DrumRole.PERC:
                base_vel = 0.7
            elif lane.role == DrumRole.FX:
                base_vel = 0.5   # Variable
            else:
                base_vel = 0.7

            # Add small variation
            variation = (rng.random() - 0.5) * 0.15
            velocity = _clamp(base_vel + variation, 0.0, 1.0)
            steps.append(velocity)
        else:
            steps.append(0.0)

    # Generate accent pattern
    accents = _generate_accents(
        steps,
        lane.role,
        lane.accent_support,
        syncopation,
        rng
    )

    return LanePattern(
        lane_id=lane.lane_id,
        role=lane.role,
        steps=tuple(steps),
        accents=tuple(accents),
        resolution=resolution
    )


def _euclidean_rhythm(pulses: int, steps: int) -> List[bool]:
    """
    Generate Euclidean rhythm pattern (Bjorklund algorithm).

    This distributes 'pulses' hits as evenly as possible across 'steps' positions.

    Args:
        pulses: Number of hits
        steps: Total number of steps

    Returns:
        List of booleans (True = hit, False = rest)
    """
    if pulses > steps:
        pulses = steps
    if pulses == 0:
        return [False] * steps

    pattern = []
    bucket = 0

    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            pattern.append(True)
        else:
            pattern.append(False)

    return pattern


def _apply_syncopation(
    pattern: List[bool],
    syncopation: float,
    rng: np.random.Generator
) -> List[bool]:
    """
    Apply syncopation by shifting some on-beat hits to off-beat positions.

    Args:
        pattern: Original Euclidean pattern
        syncopation: Syncopation budget (0-1)
        rng: RNG for deterministic shifting

    Returns:
        Modified pattern with syncopation
    """
    if syncopation < 0.3:
        return pattern  # No significant syncopation

    pattern_copy = pattern.copy()
    steps = len(pattern)

    # Find on-beat positions (multiples of 4 steps = quarter notes)
    on_beats = []
    off_beats = []
    for i, hit in enumerate(pattern):
        if hit:
            if i % 4 == 0:  # On-beat
                on_beats.append(i)
            else:  # Already off-beat
                off_beats.append(i)

    # Shift some on-beat hits to off-beat
    num_to_shift = int(len(on_beats) * syncopation * 0.5)  # Shift up to 50% based on budget
    num_to_shift = min(num_to_shift, len(on_beats))

    # Deterministic selection of which beats to shift
    indices_to_shift = sorted(rng.choice(len(on_beats), size=num_to_shift, replace=False))

    for idx in indices_to_shift:
        on_beat_pos = on_beats[idx]
        # Find nearest off-beat position (prefer +1 or +2 steps)
        candidates = [(on_beat_pos + offset) % steps for offset in [1, 2, 3]]
        # Pick first available off-beat position that's empty
        for candidate in candidates:
            if not pattern_copy[candidate]:
                pattern_copy[on_beat_pos] = False
                pattern_copy[candidate] = True
                break

    return pattern_copy


def _generate_accents(
    steps: List[float],
    role: DrumRole,
    accent_support: bool,
    syncopation: float,
    rng: np.random.Generator
) -> List[bool]:
    """
    Generate accent pattern for steps.

    Args:
        steps: Velocity grid (0-1 values)
        role: Drum role
        accent_support: Whether hardware supports accents
        syncopation: Syncopation budget (affects accent placement)
        rng: RNG for deterministic selection

    Returns:
        List of booleans (True = accented)
    """
    if not accent_support:
        return [False] * len(steps)

    accents = [False] * len(steps)

    # Accent on-beat hits for kick/snare
    if role in [DrumRole.KICK, DrumRole.SNARE]:
        for i, vel in enumerate(steps):
            if vel > 0.0:
                # Downbeat (step 0) always accented
                if i == 0:
                    accents[i] = True
                # Every 4th step (quarter notes) sometimes accented
                elif i % 4 == 0 and rng.random() < 0.6:
                    accents[i] = True
                # Off-beat accents if high syncopation
                elif syncopation > 0.6 and i % 4 != 0 and rng.random() < syncopation * 0.3:
                    accents[i] = True

    # Sparse accents for hats
    elif role == DrumRole.HAT:
        for i, vel in enumerate(steps):
            if vel > 0.0 and i % 8 == 0 and rng.random() < 0.4:
                accents[i] = True

    # Random accents for perc/fx
    elif role in [DrumRole.PERC, DrumRole.FX]:
        for i, vel in enumerate(steps):
            if vel > 0.0 and rng.random() < 0.25:
                accents[i] = True

    return accents


__all__ = [
    "COMPOSER_VERSION",
    "compose_pattern",
]
