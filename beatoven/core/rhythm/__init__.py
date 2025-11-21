"""
BeatOven Rhythm Engine

Deterministic polymeter/polyrhythm generator with Euclidean patterns,
swing, and velocity curves. Outputs MIDI-like events and symbolic descriptors.
"""

import hashlib
import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class NoteValue(Enum):
    """Standard note values."""
    WHOLE = 4.0
    HALF = 2.0
    QUARTER = 1.0
    EIGHTH = 0.5
    SIXTEENTH = 0.25
    THIRTYSECOND = 0.125


@dataclass
class RhythmEvent:
    """A single rhythmic event."""
    time: float  # Time in beats from start
    duration: float  # Duration in beats
    velocity: float  # 0.0 to 1.0
    channel: int = 0  # MIDI-like channel
    note: int = 60  # MIDI note (for pitched drums)
    accent: bool = False
    ghost: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "duration": self.duration,
            "velocity": self.velocity,
            "channel": self.channel,
            "note": self.note,
            "accent": self.accent,
            "ghost": self.ghost
        }


@dataclass
class RhythmPattern:
    """A complete rhythm pattern with multiple layers."""
    name: str
    time_signature: Tuple[int, int]  # (numerator, denominator)
    length_beats: float
    tempo: float
    events: List[RhythmEvent] = field(default_factory=list)
    layers: Dict[str, List[RhythmEvent]] = field(default_factory=dict)
    swing_amount: float = 0.0
    groove_template: Optional[np.ndarray] = None
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "time_signature": list(self.time_signature),
            "length_beats": self.length_beats,
            "tempo": self.tempo,
            "events": [e.to_dict() for e in self.events],
            "layers": {k: [e.to_dict() for e in v] for k, v in self.layers.items()},
            "swing_amount": self.swing_amount,
            "provenance_hash": self.provenance_hash
        }


@dataclass
class RhythmDescriptor:
    """Symbolic descriptor for rhythm characteristics."""
    density: float  # Events per beat
    syncopation: float  # Off-beat emphasis
    polymetric_complexity: float  # Cross-rhythm complexity
    groove_depth: float  # Swing/shuffle intensity
    accent_pattern: np.ndarray  # Accent distribution
    velocity_curve: np.ndarray  # Velocity envelope

    def to_dict(self) -> Dict[str, Any]:
        return {
            "density": self.density,
            "syncopation": self.syncopation,
            "polymetric_complexity": self.polymetric_complexity,
            "groove_depth": self.groove_depth,
            "accent_pattern": self.accent_pattern.tolist(),
            "velocity_curve": self.velocity_curve.tolist()
        }


class RhythmEngine:
    """
    Deterministic rhythm generator using Euclidean patterns,
    polymeters, and configurable groove templates.
    """

    # Standard drum mapping
    DRUM_MAP = {
        "kick": 36,
        "snare": 38,
        "clap": 39,
        "hihat_closed": 42,
        "hihat_open": 46,
        "tom_low": 45,
        "tom_mid": 47,
        "tom_high": 50,
        "crash": 49,
        "ride": 51,
        "rim": 37,
        "cowbell": 56,
        "conga_high": 62,
        "conga_low": 63,
        "shaker": 70
    }

    def __init__(self, seed: int = 0):
        """Initialize rhythm engine with deterministic seed."""
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    def generate(
        self,
        density: float = 0.5,
        tension: float = 0.5,
        drift: float = 0.0,
        tempo: float = 120.0,
        time_signature: Tuple[int, int] = (4, 4),
        length_bars: int = 4,
        swing: float = 0.0,
        layers: Optional[List[str]] = None
    ) -> Tuple[RhythmPattern, RhythmDescriptor]:
        """
        Generate a complete rhythm pattern.

        Args:
            density: Event density 0.0-1.0
            tension: Rhythmic tension/complexity 0.0-1.0
            drift: Temporal drift/variation 0.0-1.0
            tempo: BPM
            time_signature: (numerator, denominator)
            length_bars: Pattern length in bars
            swing: Swing amount 0.0-1.0
            layers: Drum layers to generate (default: kick, snare, hihat)

        Returns:
            Tuple of (RhythmPattern, RhythmDescriptor)
        """
        if layers is None:
            layers = ["kick", "snare", "hihat_closed"]

        beats_per_bar = time_signature[0] * (4 / time_signature[1])
        total_beats = beats_per_bar * length_bars

        all_events = []
        layer_events = {}

        for layer_name in layers:
            events = self._generate_layer(
                layer_name, density, tension, drift,
                total_beats, time_signature, swing
            )
            layer_events[layer_name] = events
            all_events.extend(events)

        # Sort all events by time
        all_events.sort(key=lambda e: e.time)

        # Apply global swing
        if swing > 0:
            all_events = self._apply_swing(all_events, swing, time_signature)
            for layer_name in layer_events:
                layer_events[layer_name] = self._apply_swing(
                    layer_events[layer_name], swing, time_signature
                )

        # Compute provenance
        provenance = self._compute_provenance(
            density, tension, drift, tempo, time_signature, length_bars, swing, layers
        )

        pattern = RhythmPattern(
            name=f"pattern_{self.seed}",
            time_signature=time_signature,
            length_beats=total_beats,
            tempo=tempo,
            events=all_events,
            layers=layer_events,
            swing_amount=swing,
            provenance_hash=provenance
        )

        descriptor = self._compute_descriptor(pattern)

        return pattern, descriptor

    def euclidean_rhythm(self, pulses: int, steps: int, rotation: int = 0) -> List[bool]:
        """
        Generate Euclidean rhythm pattern.

        Args:
            pulses: Number of hits
            steps: Total steps in pattern
            rotation: Rotation offset

        Returns:
            List of booleans representing hits
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

        # Apply rotation
        if rotation != 0:
            rotation = rotation % steps
            pattern = pattern[-rotation:] + pattern[:-rotation]

        return pattern

    def _generate_layer(
        self,
        layer_name: str,
        density: float,
        tension: float,
        drift: float,
        total_beats: float,
        time_signature: Tuple[int, int],
        swing: float
    ) -> List[RhythmEvent]:
        """Generate events for a single drum layer."""
        events = []
        note = self.DRUM_MAP.get(layer_name, 60)

        # Determine grid resolution based on density
        if density < 0.3:
            resolution = NoteValue.QUARTER.value
        elif density < 0.6:
            resolution = NoteValue.EIGHTH.value
        else:
            resolution = NoteValue.SIXTEENTH.value

        steps = int(total_beats / resolution)

        # Calculate Euclidean parameters
        if "kick" in layer_name:
            base_pulses = max(1, int(steps * 0.15 * (0.5 + density)))
        elif "snare" in layer_name or "clap" in layer_name:
            base_pulses = max(1, int(steps * 0.12 * (0.5 + density)))
        elif "hihat" in layer_name:
            base_pulses = max(1, int(steps * 0.5 * (0.5 + density)))
        else:
            base_pulses = max(1, int(steps * 0.2 * (0.5 + density)))

        # Add tension variation
        pulses = int(base_pulses * (1 + tension * 0.3))
        pulses = min(pulses, steps)

        # Generate base pattern
        rotation = int(tension * steps * 0.25) % steps
        pattern = self.euclidean_rhythm(pulses, steps, rotation)

        # Generate events from pattern
        for i, hit in enumerate(pattern):
            if hit:
                time = i * resolution

                # Calculate velocity with accent pattern
                base_velocity = 0.7
                beat_position = time % time_signature[0]

                # Accent on downbeats
                if abs(beat_position - round(beat_position)) < 0.01:
                    if int(beat_position) == 0:
                        velocity = min(1.0, base_velocity + 0.25)
                        accent = True
                    elif int(beat_position) % 2 == 0:
                        velocity = min(1.0, base_velocity + 0.1)
                        accent = False
                    else:
                        velocity = base_velocity
                        accent = False
                else:
                    velocity = base_velocity * 0.85
                    accent = False

                # Add drift variation
                if drift > 0:
                    velocity *= (1 + self._rng.uniform(-drift * 0.2, drift * 0.2))
                    velocity = max(0.1, min(1.0, velocity))

                # Ghost notes for hi-hats
                ghost = False
                if "hihat" in layer_name and velocity < 0.6:
                    ghost = self._rng.random() < tension * 0.3

                events.append(RhythmEvent(
                    time=time,
                    duration=resolution * 0.8,
                    velocity=velocity,
                    note=note,
                    accent=accent,
                    ghost=ghost
                ))

        return events

    def _apply_swing(
        self,
        events: List[RhythmEvent],
        swing: float,
        time_signature: Tuple[int, int]
    ) -> List[RhythmEvent]:
        """Apply swing to events."""
        swing_amount = swing * 0.33  # Max 33% swing

        swung_events = []
        for event in events:
            new_event = RhythmEvent(
                time=event.time,
                duration=event.duration,
                velocity=event.velocity,
                channel=event.channel,
                note=event.note,
                accent=event.accent,
                ghost=event.ghost
            )

            # Swing off-beats (eighth note positions)
            eighth_pos = event.time / 0.5
            if abs(eighth_pos - round(eighth_pos)) < 0.01:
                if int(round(eighth_pos)) % 2 == 1:  # Off-beat
                    new_event.time += swing_amount * 0.5

            swung_events.append(new_event)

        return swung_events

    def _compute_descriptor(self, pattern: RhythmPattern) -> RhythmDescriptor:
        """Compute symbolic descriptor for pattern."""
        if not pattern.events:
            return RhythmDescriptor(
                density=0.0,
                syncopation=0.0,
                polymetric_complexity=0.0,
                groove_depth=pattern.swing_amount,
                accent_pattern=np.zeros(16, dtype=np.float32),
                velocity_curve=np.zeros(16, dtype=np.float32)
            )

        # Density: events per beat
        density = len(pattern.events) / max(1, pattern.length_beats)

        # Syncopation: ratio of off-beat to on-beat events
        on_beat = sum(1 for e in pattern.events if abs(e.time - round(e.time)) < 0.1)
        off_beat = len(pattern.events) - on_beat
        syncopation = off_beat / max(1, len(pattern.events))

        # Polymetric complexity: variance in layer densities
        layer_densities = []
        for events in pattern.layers.values():
            if pattern.length_beats > 0:
                layer_densities.append(len(events) / pattern.length_beats)
        polymetric_complexity = float(np.std(layer_densities)) if layer_densities else 0.0

        # Accent pattern (16 steps)
        accent_pattern = np.zeros(16, dtype=np.float32)
        for event in pattern.events:
            step = int(event.time / pattern.length_beats * 16) % 16
            if event.accent:
                accent_pattern[step] += 1.0
        if accent_pattern.max() > 0:
            accent_pattern /= accent_pattern.max()

        # Velocity curve (16 steps)
        velocity_curve = np.zeros(16, dtype=np.float32)
        velocity_counts = np.zeros(16, dtype=np.float32)
        for event in pattern.events:
            step = int(event.time / pattern.length_beats * 16) % 16
            velocity_curve[step] += event.velocity
            velocity_counts[step] += 1
        velocity_curve = np.divide(
            velocity_curve, velocity_counts,
            out=np.zeros_like(velocity_curve),
            where=velocity_counts > 0
        )

        return RhythmDescriptor(
            density=density,
            syncopation=syncopation,
            polymetric_complexity=polymetric_complexity,
            groove_depth=pattern.swing_amount,
            accent_pattern=accent_pattern,
            velocity_curve=velocity_curve
        )

    def _compute_provenance(
        self,
        density: float,
        tension: float,
        drift: float,
        tempo: float,
        time_signature: Tuple[int, int],
        length_bars: int,
        swing: float,
        layers: List[str]
    ) -> str:
        """Compute provenance hash."""
        data = f"{self.seed}:{density}:{tension}:{drift}:{tempo}:{time_signature}:{length_bars}:{swing}:{sorted(layers)}"
        return hashlib.sha256(data.encode()).hexdigest()


__all__ = ["RhythmEngine", "RhythmPattern", "RhythmEvent", "RhythmDescriptor", "NoteValue"]
