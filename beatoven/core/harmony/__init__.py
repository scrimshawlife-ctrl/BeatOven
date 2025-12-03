"""
BeatOven Harmonic Engine

Scales, modes, chord progressions with modal interchange.
Accepts PsyFi Hσ emotional modulation and applies ABX-Core noise compression.
"""

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class Scale(Enum):
    """Musical scales as semitone intervals from root."""
    MAJOR = (0, 2, 4, 5, 7, 9, 11)
    MINOR = (0, 2, 3, 5, 7, 8, 10)
    DORIAN = (0, 2, 3, 5, 7, 9, 10)
    PHRYGIAN = (0, 1, 3, 5, 7, 8, 10)
    LYDIAN = (0, 2, 4, 6, 7, 9, 11)
    MIXOLYDIAN = (0, 2, 4, 5, 7, 9, 10)
    AEOLIAN = (0, 2, 3, 5, 7, 8, 10)
    LOCRIAN = (0, 1, 3, 5, 6, 8, 10)
    HARMONIC_MINOR = (0, 2, 3, 5, 7, 8, 11)
    MELODIC_MINOR = (0, 2, 3, 5, 7, 9, 11)
    PENTATONIC_MAJOR = (0, 2, 4, 7, 9)
    PENTATONIC_MINOR = (0, 3, 5, 7, 10)
    BLUES = (0, 3, 5, 6, 7, 10)
    WHOLE_TONE = (0, 2, 4, 6, 8, 10)
    CHROMATIC = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


class ChordQuality(Enum):
    """Chord qualities."""
    MAJOR = "maj"
    MINOR = "min"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    DOMINANT7 = "7"
    MAJOR7 = "maj7"
    MINOR7 = "min7"
    HALF_DIM7 = "m7b5"
    DIM7 = "dim7"
    SUS2 = "sus2"
    SUS4 = "sus4"
    ADD9 = "add9"


@dataclass
class Chord:
    """Represents a chord."""
    root: int  # MIDI note of root
    quality: ChordQuality
    inversion: int = 0
    voicing: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.voicing:
            self.voicing = self._default_voicing()

    def _default_voicing(self) -> List[int]:
        """Generate default voicing based on quality."""
        intervals = {
            ChordQuality.MAJOR: [0, 4, 7],
            ChordQuality.MINOR: [0, 3, 7],
            ChordQuality.DIMINISHED: [0, 3, 6],
            ChordQuality.AUGMENTED: [0, 4, 8],
            ChordQuality.DOMINANT7: [0, 4, 7, 10],
            ChordQuality.MAJOR7: [0, 4, 7, 11],
            ChordQuality.MINOR7: [0, 3, 7, 10],
            ChordQuality.HALF_DIM7: [0, 3, 6, 10],
            ChordQuality.DIM7: [0, 3, 6, 9],
            ChordQuality.SUS2: [0, 2, 7],
            ChordQuality.SUS4: [0, 5, 7],
            ChordQuality.ADD9: [0, 4, 7, 14],
        }
        base = intervals.get(self.quality, [0, 4, 7])
        voicing = [(self.root + i) for i in base]

        # Apply inversion
        for _ in range(self.inversion % len(voicing)):
            voicing[0] += 12
            voicing = voicing[1:] + [voicing[0]]

        return voicing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "quality": self.quality.value,
            "inversion": self.inversion,
            "voicing": self.voicing
        }


@dataclass
class HarmonicEvent:
    """A harmonic event (chord) at a specific time."""
    time: float  # Time in beats
    duration: float  # Duration in beats
    chord: Chord
    velocity: float = 0.7
    tension: float = 0.0  # Harmonic tension level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "duration": self.duration,
            "chord": self.chord.to_dict(),
            "velocity": self.velocity,
            "tension": self.tension
        }


@dataclass
class HarmonicProgression:
    """A complete harmonic progression."""
    name: str
    key_root: int  # MIDI note of key
    scale: Scale
    events: List[HarmonicEvent] = field(default_factory=list)
    length_beats: float = 16.0
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "key_root": self.key_root,
            "scale": self.scale.name,
            "events": [e.to_dict() for e in self.events],
            "length_beats": self.length_beats,
            "provenance_hash": self.provenance_hash
        }


@dataclass
class HarmonicDescriptor:
    """Symbolic descriptor for harmonic content."""
    consonance: float  # 0.0 (dissonant) to 1.0 (consonant)
    modal_brightness: float  # -1.0 (dark) to 1.0 (bright)
    tension_curve: np.ndarray  # Tension over time
    chord_complexity: float  # Average chord complexity
    modulation_depth: float  # Key change frequency

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consonance": self.consonance,
            "modal_brightness": self.modal_brightness,
            "tension_curve": self.tension_curve.tolist(),
            "chord_complexity": self.chord_complexity,
            "modulation_depth": self.modulation_depth
        }


class HarmonicEngine:
    """
    Generates chord progressions with modal interchange,
    PsyFi emotional modulation, and ABX-Core noise compression.
    """

    # Roman numeral chord degrees (major scale)
    MAJOR_DEGREES = {
        1: ChordQuality.MAJOR,
        2: ChordQuality.MINOR,
        3: ChordQuality.MINOR,
        4: ChordQuality.MAJOR,
        5: ChordQuality.MAJOR,
        6: ChordQuality.MINOR,
        7: ChordQuality.DIMINISHED
    }

    # Common progressions (as scale degrees)
    PROGRESSIONS = {
        "pop": [1, 5, 6, 4],
        "jazz_251": [2, 5, 1],
        "blues": [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],
        "circle": [1, 4, 7, 3, 6, 2, 5, 1],
        "andalusian": [6, 5, 4, 3],
        "pachelbel": [1, 5, 6, 3, 4, 1, 4, 5],
        "emotional": [6, 4, 1, 5],
        "dark": [6, 4, 1, 7],
        "triumphant": [1, 4, 5, 1],
        "mysterious": [1, 7, 6, 5]
    }

    # Modal brightness (lydian=brightest, locrian=darkest)
    MODE_BRIGHTNESS = {
        Scale.LYDIAN: 1.0,
        Scale.MAJOR: 0.7,
        Scale.MIXOLYDIAN: 0.4,
        Scale.DORIAN: 0.0,
        Scale.AEOLIAN: -0.3,
        Scale.MINOR: -0.3,
        Scale.PHRYGIAN: -0.7,
        Scale.LOCRIAN: -1.0
    }

    def __init__(self, seed: int = 0, compression_factor: float = 0.8):
        """
        Initialize harmonic engine.

        Args:
            seed: Deterministic seed
            compression_factor: ABX-Core noise compression (0.0-1.0)
        """
        self.seed = seed
        self.compression_factor = compression_factor
        self._rng = np.random.default_rng(seed)

    def generate(
        self,
        resonance: float = 0.5,
        tension: float = 0.5,
        contrast: float = 0.5,
        key_root: int = 60,  # Middle C
        scale: Scale = Scale.MINOR,
        length_bars: int = 4,
        beats_per_bar: int = 4,
        progression_type: Optional[str] = None,
        psyfi_emotional_vector: Optional[np.ndarray] = None
    ) -> Tuple[HarmonicProgression, HarmonicDescriptor]:
        """
        Generate a harmonic progression.

        Args:
            resonance: Harmonic richness 0.0-1.0
            tension: Harmonic tension 0.0-1.0
            contrast: Dynamic variation 0.0-1.0
            key_root: Root note (MIDI)
            scale: Musical scale
            length_bars: Length in bars
            beats_per_bar: Beats per bar
            progression_type: Named progression or None for generated
            psyfi_emotional_vector: PsyFi Hσ emotional modulation

        Returns:
            Tuple of (HarmonicProgression, HarmonicDescriptor)
        """
        total_beats = length_bars * beats_per_bar

        # Apply PsyFi emotional modulation if provided
        if psyfi_emotional_vector is not None:
            resonance, tension, contrast = self._apply_psyfi_modulation(
                resonance, tension, contrast, psyfi_emotional_vector
            )

        # Select or generate progression
        if progression_type and progression_type in self.PROGRESSIONS:
            degrees = self.PROGRESSIONS[progression_type]
        else:
            degrees = self._generate_progression(tension, contrast)

        # Generate chords from degrees
        events = self._generate_events(
            degrees, key_root, scale, total_beats,
            resonance, tension, contrast
        )

        # Apply ABX-Core compression
        events = self._apply_compression(events)

        # Compute provenance
        provenance = self._compute_provenance(
            resonance, tension, contrast, key_root, scale, length_bars, progression_type
        )

        progression = HarmonicProgression(
            name=f"progression_{self.seed}",
            key_root=key_root,
            scale=scale,
            events=events,
            length_beats=total_beats,
            provenance_hash=provenance
        )

        descriptor = self._compute_descriptor(progression)

        return progression, descriptor

    def _apply_psyfi_modulation(
        self,
        resonance: float,
        tension: float,
        contrast: float,
        emotional_vector: np.ndarray
    ) -> Tuple[float, float, float]:
        """Apply PsyFi Hσ emotional modulation to parameters."""
        # Emotional vector dimensions: [valence, arousal, dominance, ...]
        if len(emotional_vector) >= 3:
            valence = emotional_vector[0]  # Positive/negative
            arousal = emotional_vector[1]  # Energy level
            dominance = emotional_vector[2]  # Control

            # Modulate parameters
            resonance = resonance * (0.7 + 0.3 * valence)
            tension = tension * (0.5 + 0.5 * arousal)
            contrast = contrast * (0.6 + 0.4 * dominance)

        return (
            max(0.0, min(1.0, resonance)),
            max(0.0, min(1.0, tension)),
            max(0.0, min(1.0, contrast))
        )

    def _generate_progression(self, tension: float, contrast: float) -> List[int]:
        """Generate chord progression based on tension/contrast."""
        length = 4 + int(contrast * 4)  # 4-8 chords

        # Start and end on tonic
        progression = [1]

        for _ in range(length - 2):
            # Higher tension = more distant chords
            if self._rng.random() < tension:
                # Add a more distant chord
                choices = [2, 3, 6, 7] if tension > 0.5 else [4, 5, 6]
            else:
                # Stay closer to tonic
                choices = [4, 5]

            progression.append(int(self._rng.choice(choices)))

        # Resolve to tonic via dominant
        if self._rng.random() < 0.7:
            progression.append(5)  # V
        progression.append(1)  # I

        return progression

    def _generate_events(
        self,
        degrees: List[int],
        key_root: int,
        scale: Scale,
        total_beats: float,
        resonance: float,
        tension: float,
        contrast: float
    ) -> List[HarmonicEvent]:
        """Generate harmonic events from chord degrees."""
        events = []
        scale_intervals = scale.value
        beat_duration = total_beats / len(degrees)

        for i, degree in enumerate(degrees):
            # Get scale degree root
            degree_idx = (degree - 1) % len(scale_intervals)
            root = key_root + scale_intervals[degree_idx]

            # Determine chord quality
            quality = self._get_chord_quality(degree, scale, tension)

            # Add extensions based on resonance
            if resonance > 0.7 and self._rng.random() < resonance:
                if quality == ChordQuality.MAJOR:
                    quality = ChordQuality.MAJOR7
                elif quality == ChordQuality.MINOR:
                    quality = ChordQuality.MINOR7
                elif quality == ChordQuality.DOMINANT7:
                    pass  # Already has 7th

            # Determine inversion based on voice leading
            inversion = 0
            if i > 0 and contrast > 0.3:
                inversion = int(self._rng.integers(0, 3))

            chord = Chord(root=root, quality=quality, inversion=inversion)

            # Calculate tension for this chord
            chord_tension = self._calculate_chord_tension(degree, quality)

            # Velocity variation based on contrast
            velocity = 0.7 + contrast * 0.2 * (self._rng.random() - 0.5)
            velocity = max(0.4, min(1.0, velocity))

            events.append(HarmonicEvent(
                time=i * beat_duration,
                duration=beat_duration,
                chord=chord,
                velocity=velocity,
                tension=chord_tension
            ))

        return events

    def _get_chord_quality(self, degree: int, scale: Scale, tension: float) -> ChordQuality:
        """Get chord quality for scale degree with potential alterations."""
        base_quality = self.MAJOR_DEGREES.get(degree, ChordQuality.MAJOR)

        # Modal interchange based on tension
        if tension > 0.6 and self._rng.random() < tension * 0.3:
            # Borrow from parallel mode
            if base_quality == ChordQuality.MAJOR:
                return ChordQuality.MINOR
            elif base_quality == ChordQuality.MINOR:
                return ChordQuality.MAJOR

        # Dominant substitution
        if degree == 5 and self._rng.random() < tension:
            return ChordQuality.DOMINANT7

        return base_quality

    def _calculate_chord_tension(self, degree: int, quality: ChordQuality) -> float:
        """Calculate harmonic tension for a chord."""
        # Base tension by degree
        degree_tension = {1: 0.0, 2: 0.4, 3: 0.3, 4: 0.2, 5: 0.5, 6: 0.3, 7: 0.8}
        base = degree_tension.get(degree, 0.5)

        # Quality modifiers
        quality_mod = {
            ChordQuality.DIMINISHED: 0.3,
            ChordQuality.AUGMENTED: 0.25,
            ChordQuality.DOMINANT7: 0.2,
            ChordQuality.HALF_DIM7: 0.35
        }
        base += quality_mod.get(quality, 0.0)

        return max(0.0, min(1.0, base))

    def _apply_compression(self, events: List[HarmonicEvent]) -> List[HarmonicEvent]:
        """Apply ABX-Core noise compression to events."""
        if not events:
            return events

        # Compress velocity variance
        velocities = [e.velocity for e in events]
        mean_vel = np.mean(velocities)

        compression_scale = max(0.0, min(1.0, 1.0 - self.compression_factor))

        for event in events:
            event.velocity = mean_vel + compression_scale * (event.velocity - mean_vel)
            event.velocity = max(0.3, min(1.0, event.velocity))

        return events

    def _compute_descriptor(self, progression: HarmonicProgression) -> HarmonicDescriptor:
        """Compute harmonic descriptor."""
        if not progression.events:
            return HarmonicDescriptor(
                consonance=0.5,
                modal_brightness=0.0,
                tension_curve=np.zeros(16, dtype=np.float32),
                chord_complexity=0.0,
                modulation_depth=0.0
            )

        # Consonance: inverse of average tension
        tensions = [e.tension for e in progression.events]
        consonance = 1.0 - np.mean(tensions)

        # Modal brightness
        modal_brightness = self.MODE_BRIGHTNESS.get(progression.scale, 0.0)

        # Tension curve (16 steps)
        tension_curve = np.zeros(16, dtype=np.float32)
        for event in progression.events:
            step = int(event.time / progression.length_beats * 16) % 16
            tension_curve[step] = event.tension

        # Chord complexity: average voicing size
        complexities = [len(e.chord.voicing) / 4.0 for e in progression.events]
        chord_complexity = np.mean(complexities)

        # Modulation depth (placeholder for key changes)
        modulation_depth = 0.0

        return HarmonicDescriptor(
            consonance=consonance,
            modal_brightness=modal_brightness,
            tension_curve=tension_curve,
            chord_complexity=chord_complexity,
            modulation_depth=modulation_depth
        )

    def _compute_provenance(
        self,
        resonance: float,
        tension: float,
        contrast: float,
        key_root: int,
        scale: Scale,
        length_bars: int,
        progression_type: Optional[str]
    ) -> str:
        """Compute provenance hash."""
        data = f"{self.seed}:{resonance}:{tension}:{contrast}:{key_root}:{scale.name}:{length_bars}:{progression_type}"
        return hashlib.sha256(data.encode()).hexdigest()


__all__ = [
    "HarmonicEngine", "HarmonicProgression", "HarmonicEvent",
    "HarmonicDescriptor", "Chord", "ChordQuality", "Scale"
]
