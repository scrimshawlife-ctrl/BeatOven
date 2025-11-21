"""
BeatOven Motion Engine

LFOs, envelopes, and automation curves with runic/symbolic modulation support.
"""

import hashlib
import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from enum import Enum


class LFOShape(Enum):
    """LFO waveform shapes."""
    SINE = "sine"
    TRIANGLE = "triangle"
    SAW_UP = "saw_up"
    SAW_DOWN = "saw_down"
    SQUARE = "square"
    RANDOM = "random"
    SAMPLE_HOLD = "sample_hold"


class EnvelopeStage(Enum):
    """ADSR envelope stages."""
    ATTACK = "attack"
    DECAY = "decay"
    SUSTAIN = "sustain"
    RELEASE = "release"
    IDLE = "idle"


@dataclass
class ModulationPoint:
    """A single automation point."""
    time: float  # Time in beats
    value: float  # 0.0 to 1.0
    curve: float = 0.0  # -1 to 1, 0 = linear

    def to_dict(self) -> Dict[str, Any]:
        return {"time": self.time, "value": self.value, "curve": self.curve}


@dataclass
class AutomationCurve:
    """An automation curve with multiple points."""
    name: str
    points: List[ModulationPoint] = field(default_factory=list)
    loop: bool = False
    loop_start: float = 0.0
    loop_end: float = 4.0

    def get_value_at(self, time: float) -> float:
        """Get interpolated value at time."""
        if not self.points:
            return 0.5

        if self.loop and self.loop_end > self.loop_start:
            loop_len = self.loop_end - self.loop_start
            if time >= self.loop_start:
                time = self.loop_start + (time - self.loop_start) % loop_len

        # Find surrounding points
        prev_point = self.points[0]
        next_point = self.points[-1]

        for i, point in enumerate(self.points):
            if point.time <= time:
                prev_point = point
            if point.time >= time:
                next_point = point
                break

        if prev_point.time == next_point.time:
            return prev_point.value

        # Interpolate
        t = (time - prev_point.time) / (next_point.time - prev_point.time)

        # Apply curve
        if prev_point.curve != 0:
            if prev_point.curve > 0:
                t = t ** (1 + prev_point.curve * 2)
            else:
                t = 1 - (1 - t) ** (1 - prev_point.curve * 2)

        return prev_point.value + t * (next_point.value - prev_point.value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "points": [p.to_dict() for p in self.points],
            "loop": self.loop,
            "loop_start": self.loop_start,
            "loop_end": self.loop_end
        }


class LFO:
    """Low-Frequency Oscillator for modulation."""

    def __init__(
        self,
        shape: LFOShape = LFOShape.SINE,
        frequency: float = 1.0,  # Hz
        amplitude: float = 1.0,
        phase: float = 0.0,
        offset: float = 0.0
    ):
        self.shape = shape
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.offset = offset
        self._rng = np.random.default_rng(42)
        self._sample_hold_value = 0.0
        self._last_phase = 0.0

    def get_value_at(self, time: float) -> float:
        """Get LFO value at time in seconds."""
        phase = (time * self.frequency + self.phase) % 1.0

        if self.shape == LFOShape.SINE:
            value = math.sin(2 * math.pi * phase)
        elif self.shape == LFOShape.TRIANGLE:
            value = 4 * abs(phase - 0.5) - 1
        elif self.shape == LFOShape.SAW_UP:
            value = 2 * phase - 1
        elif self.shape == LFOShape.SAW_DOWN:
            value = 1 - 2 * phase
        elif self.shape == LFOShape.SQUARE:
            value = 1.0 if phase < 0.5 else -1.0
        elif self.shape == LFOShape.RANDOM:
            value = self._rng.uniform(-1, 1)
        elif self.shape == LFOShape.SAMPLE_HOLD:
            if phase < self._last_phase:  # New cycle
                self._sample_hold_value = self._rng.uniform(-1, 1)
            self._last_phase = phase
            value = self._sample_hold_value
        else:
            value = 0.0

        return value * self.amplitude + self.offset

    def generate_curve(
        self,
        duration: float,
        resolution: int = 100
    ) -> AutomationCurve:
        """Generate automation curve from LFO."""
        points = []
        for i in range(resolution):
            time = i * duration / resolution
            value = (self.get_value_at(time) + 1) / 2  # Normalize to 0-1
            points.append(ModulationPoint(time=time, value=value))

        return AutomationCurve(
            name=f"lfo_{self.shape.value}",
            points=points,
            loop=True,
            loop_start=0.0,
            loop_end=duration
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape": self.shape.value,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "offset": self.offset
        }


class Envelope:
    """ADSR envelope generator."""

    def __init__(
        self,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.3,
        curve: float = 0.0
    ):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.curve = curve
        self._stage = EnvelopeStage.IDLE
        self._stage_time = 0.0
        self._value = 0.0

    def trigger(self):
        """Trigger envelope attack."""
        self._stage = EnvelopeStage.ATTACK
        self._stage_time = 0.0

    def release_note(self):
        """Start release stage."""
        self._stage = EnvelopeStage.RELEASE
        self._stage_time = 0.0

    def get_value_at(self, time: float, note_on_duration: Optional[float] = None) -> float:
        """
        Get envelope value at time.

        Args:
            time: Time since note on
            note_on_duration: If set, release starts at this time
        """
        if note_on_duration is not None and time >= note_on_duration:
            release_time = time - note_on_duration
            if release_time < self.release:
                # Calculate value at note off
                if note_on_duration < self.attack:
                    note_off_value = note_on_duration / self.attack
                elif note_on_duration < self.attack + self.decay:
                    decay_progress = (note_on_duration - self.attack) / self.decay
                    note_off_value = 1.0 - (1.0 - self.sustain) * decay_progress
                else:
                    note_off_value = self.sustain

                t = release_time / self.release
                return note_off_value * (1 - self._apply_curve(t))
            return 0.0

        if time < self.attack:
            t = time / self.attack
            return self._apply_curve(t)
        elif time < self.attack + self.decay:
            t = (time - self.attack) / self.decay
            return 1.0 - (1.0 - self.sustain) * self._apply_curve(t)
        else:
            return self.sustain

    def _apply_curve(self, t: float) -> float:
        """Apply curve shaping to linear value."""
        if self.curve == 0:
            return t
        elif self.curve > 0:
            return t ** (1 + self.curve * 2)
        else:
            return 1 - (1 - t) ** (1 - self.curve * 2)

    def generate_curve(
        self,
        note_duration: float,
        resolution: int = 100
    ) -> AutomationCurve:
        """Generate automation curve from envelope."""
        total_duration = note_duration + self.release
        points = []

        for i in range(resolution):
            time = i * total_duration / resolution
            value = self.get_value_at(time, note_duration)
            points.append(ModulationPoint(time=time, value=value))

        return AutomationCurve(
            name="envelope",
            points=points,
            loop=False
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack": self.attack,
            "decay": self.decay,
            "sustain": self.sustain,
            "release": self.release,
            "curve": self.curve
        }


@dataclass
class RunicModulation:
    """Runic/symbolic modulation configuration."""
    rune_vector: np.ndarray
    target_param: str
    influence: float = 1.0
    mapping_curve: Optional[AutomationCurve] = None

    def apply(self, base_value: float, time: float) -> float:
        """Apply runic modulation to base value."""
        # Use rune vector to derive modulation
        rune_index = int(time * 10) % len(self.rune_vector)
        rune_mod = self.rune_vector[rune_index]

        if self.mapping_curve:
            curve_value = self.mapping_curve.get_value_at(time)
            rune_mod *= curve_value

        return base_value + rune_mod * self.influence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rune_vector": self.rune_vector.tolist(),
            "target_param": self.target_param,
            "influence": self.influence
        }


@dataclass
class MotionDescriptor:
    """Symbolic descriptor for motion characteristics."""
    lfo_depth: float
    envelope_shape: str
    modulation_complexity: float
    temporal_variation: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lfo_depth": self.lfo_depth,
            "envelope_shape": self.envelope_shape,
            "modulation_complexity": self.modulation_complexity,
            "temporal_variation": self.temporal_variation
        }


class MotionEngine:
    """
    Motion engine for LFOs, envelopes, and automation.

    Supports runic/symbolic modulation from ABX-Runes vectors.
    """

    def __init__(self, seed: int = 0):
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        self._lfos: Dict[str, LFO] = {}
        self._envelopes: Dict[str, Envelope] = {}
        self._automations: Dict[str, AutomationCurve] = {}
        self._runic_mods: List[RunicModulation] = []

    def create_lfo(self, name: str, **kwargs) -> LFO:
        """Create and register an LFO."""
        lfo = LFO(**kwargs)
        self._lfos[name] = lfo
        return lfo

    def create_envelope(self, name: str, **kwargs) -> Envelope:
        """Create and register an envelope."""
        env = Envelope(**kwargs)
        self._envelopes[name] = env
        return env

    def create_automation(
        self,
        name: str,
        points: List[Tuple[float, float]],
        loop: bool = False
    ) -> AutomationCurve:
        """Create automation curve from points."""
        mod_points = [ModulationPoint(time=t, value=v) for t, v in points]
        curve = AutomationCurve(
            name=name,
            points=mod_points,
            loop=loop,
            loop_end=points[-1][0] if points else 4.0
        )
        self._automations[name] = curve
        return curve

    def add_runic_modulation(
        self,
        rune_vector: np.ndarray,
        target_param: str,
        influence: float = 1.0
    ) -> RunicModulation:
        """Add runic modulation source."""
        mod = RunicModulation(
            rune_vector=rune_vector,
            target_param=target_param,
            influence=influence
        )
        self._runic_mods.append(mod)
        return mod

    def generate(
        self,
        drift: float = 0.5,
        tension: float = 0.5,
        resonance: float = 0.5,
        duration: float = 4.0,
        rune_vector: Optional[np.ndarray] = None
    ) -> Tuple[Dict[str, AutomationCurve], MotionDescriptor]:
        """
        Generate motion curves based on parameters.

        Args:
            drift: Temporal variation 0.0-1.0
            tension: Rhythmic tension 0.0-1.0
            resonance: Modulation depth 0.0-1.0
            duration: Duration in beats
            rune_vector: Optional ABX-Runes vector for modulation

        Returns:
            Tuple of (curves dict, MotionDescriptor)
        """
        curves = {}

        # Main amplitude envelope
        amp_env = Envelope(
            attack=0.01 + (1 - tension) * 0.2,
            decay=0.1 + drift * 0.3,
            sustain=0.5 + resonance * 0.3,
            release=0.2 + drift * 0.5
        )
        curves["amplitude"] = amp_env.generate_curve(duration * 0.8)

        # Filter cutoff LFO
        filter_lfo = LFO(
            shape=LFOShape.SINE if tension < 0.5 else LFOShape.TRIANGLE,
            frequency=0.5 + drift * 2,
            amplitude=0.3 + resonance * 0.4
        )
        curves["filter_cutoff"] = filter_lfo.generate_curve(duration)

        # Pitch modulation
        if drift > 0.3:
            pitch_lfo = LFO(
                shape=LFOShape.SINE,
                frequency=4 + tension * 4,
                amplitude=0.1 * drift
            )
            curves["pitch"] = pitch_lfo.generate_curve(duration)

        # Pan automation
        pan_lfo = LFO(
            shape=LFOShape.TRIANGLE,
            frequency=0.25 + drift * 0.5,
            amplitude=0.5 * drift
        )
        curves["pan"] = pan_lfo.generate_curve(duration)

        # Apply runic modulation if provided
        if rune_vector is not None:
            runic_curve = self._generate_runic_curve(rune_vector, duration)
            curves["runic"] = runic_curve

        # Compute descriptor
        descriptor = MotionDescriptor(
            lfo_depth=resonance,
            envelope_shape="percussive" if tension > 0.6 else "sustained",
            modulation_complexity=drift,
            temporal_variation=drift * tension
        )

        return curves, descriptor

    def _generate_runic_curve(
        self,
        rune_vector: np.ndarray,
        duration: float
    ) -> AutomationCurve:
        """Generate automation curve from rune vector."""
        points = []
        n_points = min(len(rune_vector), 64)

        for i in range(n_points):
            time = i * duration / n_points
            value = (rune_vector[i % len(rune_vector)] + 1) / 2  # Normalize to 0-1
            points.append(ModulationPoint(time=time, value=float(value)))

        return AutomationCurve(
            name="runic_modulation",
            points=points,
            loop=True,
            loop_end=duration
        )

    def get_modulated_value(
        self,
        param_name: str,
        base_value: float,
        time: float
    ) -> float:
        """Get parameter value with all modulations applied."""
        value = base_value

        # Apply automation curves
        if param_name in self._automations:
            curve_value = self._automations[param_name].get_value_at(time)
            value = base_value * curve_value

        # Apply runic modulations
        for mod in self._runic_mods:
            if mod.target_param == param_name:
                value = mod.apply(value, time)

        return max(0.0, min(1.0, value))

    def compute_provenance(self) -> str:
        """Compute provenance hash for current state."""
        data = {
            "seed": self.seed,
            "lfos": [lfo.to_dict() for lfo in self._lfos.values()],
            "envelopes": [env.to_dict() for env in self._envelopes.values()],
            "automations": [a.to_dict() for a in self._automations.values()]
        }
        import json
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


__all__ = [
    "MotionEngine", "LFO", "Envelope", "AutomationCurve",
    "ModulationPoint", "RunicModulation", "MotionDescriptor",
    "LFOShape", "EnvelopeStage"
]
