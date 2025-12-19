"""
BeatOven Drums Module

Equipment-aware percussion generation with RigProfile constraints.

Architecture:
- schema.py: Data models (RigProfile, PercussionTopology, PatternTokens)
- allocator.py: PURE ENGINE - topology allocation from ResonanceFrame
- composer.py: PURE ENGINE - pattern composition from topology
- profiles.py: ADAPTER - filesystem storage for profiles
- defaults.py: Default equipment presets

Usage:
    from beatoven.core.drums import (
        RigProfile,
        allocate_lanes,
        compose_pattern,
        get_default_storage
    )

    # Load rig profile
    storage = get_default_storage()
    rig = storage.get_current()

    # Allocate topology
    topology, explanation = allocate_lanes(
        resonance_frame,
        rig,
        seed=42
    )

    # Compose pattern
    pattern = compose_pattern(
        topology,
        seed=42,
        length_bars=4
    )
"""

# Schema exports
from .schema import (
    EmitTarget,
    CVRange,
    SwingSource,
    DrumRole,
    IOCapabilities,
    ClockingConfig,
    OutputMapping,
    RigProfile,
    DrumLane,
    PercussionTopology,
    LanePattern,
    PatternTokens,
)

# Engine exports (PURE)
from .allocator import (
    ALLOCATOR_VERSION,
    AllocationExplanation,
    allocate_lanes,
)

from .composer import (
    COMPOSER_VERSION,
    compose_pattern,
)

# Adapter exports (I/O)
from .profiles import (
    RigProfileStorage,
    get_default_storage,
    DEFAULT_PROFILE_DIR,
)

# Defaults
from .defaults import (
    get_default_profiles,
)


__all__ = [
    # Schema
    "EmitTarget",
    "CVRange",
    "SwingSource",
    "DrumRole",
    "IOCapabilities",
    "ClockingConfig",
    "OutputMapping",
    "RigProfile",
    "DrumLane",
    "PercussionTopology",
    "LanePattern",
    "PatternTokens",
    # Allocator
    "ALLOCATOR_VERSION",
    "AllocationExplanation",
    "allocate_lanes",
    # Composer
    "COMPOSER_VERSION",
    "compose_pattern",
    # Profiles
    "RigProfileStorage",
    "get_default_storage",
    "DEFAULT_PROFILE_DIR",
    # Defaults
    "get_default_profiles",
]
