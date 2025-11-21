"""
BeatOven Timbre Engine

Modular synthesis graph with oscillators, granular, FM, and subtractive synthesis.
Includes FX chain with filters, reverbs, delays, and spectral warping.
Patchable via PatchBay system.
"""

import hashlib
import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from enum import Enum
from abc import ABC, abstractmethod


class WaveShape(Enum):
    """Basic waveform shapes."""
    SINE = "sine"
    SAW = "saw"
    SQUARE = "square"
    TRIANGLE = "triangle"
    NOISE = "noise"
    PULSE = "pulse"


class FilterType(Enum):
    """Filter types."""
    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    BANDPASS = "bandpass"
    NOTCH = "notch"
    PEAK = "peak"
    LOWSHELF = "lowshelf"
    HIGHSHELF = "highshelf"


@dataclass
class AudioBuffer:
    """Audio buffer container."""
    samples: np.ndarray
    sample_rate: int = 44100
    channels: int = 1

    @property
    def duration(self) -> float:
        return len(self.samples) / self.sample_rate

    def to_stereo(self) -> "AudioBuffer":
        if self.channels == 2:
            return self
        stereo = np.column_stack([self.samples, self.samples])
        return AudioBuffer(stereo, self.sample_rate, 2)


class SynthModule(ABC):
    """Abstract base for synthesis modules."""

    @abstractmethod
    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        pass


class Oscillator(SynthModule):
    """Multi-waveform oscillator."""

    def __init__(
        self,
        shape: WaveShape = WaveShape.SINE,
        frequency: float = 440.0,
        amplitude: float = 1.0,
        phase: float = 0.0,
        pulse_width: float = 0.5
    ):
        self.shape = shape
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.pulse_width = pulse_width
        self._phase_acc = phase

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        freq = params.get("frequency", self.frequency)
        amp = params.get("amplitude", self.amplitude)

        n_samples = len(buffer.samples)
        t = np.arange(n_samples) / buffer.sample_rate
        phase = 2 * np.pi * freq * t + self._phase_acc

        if self.shape == WaveShape.SINE:
            samples = np.sin(phase)
        elif self.shape == WaveShape.SAW:
            samples = 2 * (phase / (2 * np.pi) % 1) - 1
        elif self.shape == WaveShape.SQUARE:
            samples = np.sign(np.sin(phase))
        elif self.shape == WaveShape.TRIANGLE:
            samples = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1
        elif self.shape == WaveShape.NOISE:
            rng = np.random.default_rng(int(self._phase_acc * 1000) % (2**31))
            samples = rng.uniform(-1, 1, n_samples)
        elif self.shape == WaveShape.PULSE:
            samples = np.where((phase / (2 * np.pi) % 1) < self.pulse_width, 1.0, -1.0)
        else:
            samples = np.sin(phase)

        self._phase_acc = phase[-1] if len(phase) > 0 else self._phase_acc

        return AudioBuffer(
            samples=(samples * amp).astype(np.float32),
            sample_rate=buffer.sample_rate
        )

    def get_params(self) -> Dict[str, Any]:
        return {
            "shape": self.shape.value,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "pulse_width": self.pulse_width
        }


class Filter(SynthModule):
    """Biquad filter implementation."""

    def __init__(
        self,
        filter_type: FilterType = FilterType.LOWPASS,
        cutoff: float = 1000.0,
        resonance: float = 0.707,
        gain_db: float = 0.0
    ):
        self.filter_type = filter_type
        self.cutoff = cutoff
        self.resonance = resonance
        self.gain_db = gain_db
        self._z1 = 0.0
        self._z2 = 0.0

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        cutoff = params.get("cutoff", self.cutoff)
        q = params.get("resonance", self.resonance)

        # Calculate coefficients
        omega = 2 * np.pi * cutoff / buffer.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * q)

        if self.filter_type == FilterType.LOWPASS:
            b0 = (1 - cos_omega) / 2
            b1 = 1 - cos_omega
            b2 = (1 - cos_omega) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
        elif self.filter_type == FilterType.HIGHPASS:
            b0 = (1 + cos_omega) / 2
            b1 = -(1 + cos_omega)
            b2 = (1 + cos_omega) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
        elif self.filter_type == FilterType.BANDPASS:
            b0 = alpha
            b1 = 0
            b2 = -alpha
            a0 = 1 + alpha
            a1 = -2 * cos_omega
            a2 = 1 - alpha
        else:
            b0, b1, b2 = 1, 0, 0
            a0, a1, a2 = 1, 0, 0

        # Normalize
        b0, b1, b2 = b0/a0, b1/a0, b2/a0
        a1, a2 = a1/a0, a2/a0

        # Process samples
        output = np.zeros_like(buffer.samples)
        z1, z2 = self._z1, self._z2

        for i, x in enumerate(buffer.samples):
            y = b0 * x + z1
            z1 = b1 * x - a1 * y + z2
            z2 = b2 * x - a2 * y
            output[i] = y

        self._z1, self._z2 = z1, z2

        return AudioBuffer(output.astype(np.float32), buffer.sample_rate)

    def get_params(self) -> Dict[str, Any]:
        return {
            "filter_type": self.filter_type.value,
            "cutoff": self.cutoff,
            "resonance": self.resonance,
            "gain_db": self.gain_db
        }


class GranularSynth(SynthModule):
    """Granular synthesis module."""

    def __init__(
        self,
        grain_size_ms: float = 50.0,
        grain_density: float = 10.0,
        position: float = 0.0,
        pitch_shift: float = 1.0,
        randomness: float = 0.1
    ):
        self.grain_size_ms = grain_size_ms
        self.grain_density = grain_density
        self.position = position
        self.pitch_shift = pitch_shift
        self.randomness = randomness
        self._source_buffer: Optional[np.ndarray] = None

    def set_source(self, source: np.ndarray):
        """Set source audio for granular processing."""
        self._source_buffer = source

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        if self._source_buffer is None:
            # Generate sine grain as default
            t = np.linspace(0, 0.05, int(0.05 * buffer.sample_rate))
            self._source_buffer = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        grain_samples = int(self.grain_size_ms * buffer.sample_rate / 1000)
        output = np.zeros(len(buffer.samples), dtype=np.float32)

        rng = np.random.default_rng(42)
        n_grains = int(self.grain_density * buffer.duration)

        for _ in range(n_grains):
            # Random start position in output
            start = rng.integers(0, max(1, len(output) - grain_samples))

            # Random position in source with jitter
            src_pos = self.position + rng.uniform(-self.randomness, self.randomness)
            src_pos = max(0, min(1, src_pos))
            src_start = int(src_pos * (len(self._source_buffer) - grain_samples))
            src_start = max(0, src_start)

            # Extract grain
            grain_end = min(src_start + grain_samples, len(self._source_buffer))
            grain = self._source_buffer[src_start:grain_end].copy()

            # Apply window
            window = np.hanning(len(grain))
            grain = grain * window

            # Add to output
            end = min(start + len(grain), len(output))
            output[start:end] += grain[:end-start]

        # Normalize
        if output.max() > 0:
            output = output / output.max() * 0.8

        return AudioBuffer(output.astype(np.float32), buffer.sample_rate)

    def get_params(self) -> Dict[str, Any]:
        return {
            "grain_size_ms": self.grain_size_ms,
            "grain_density": self.grain_density,
            "position": self.position,
            "pitch_shift": self.pitch_shift,
            "randomness": self.randomness
        }


class FMSynth(SynthModule):
    """FM synthesis module."""

    def __init__(
        self,
        carrier_freq: float = 440.0,
        mod_freq: float = 440.0,
        mod_index: float = 1.0,
        amplitude: float = 1.0
    ):
        self.carrier_freq = carrier_freq
        self.mod_freq = mod_freq
        self.mod_index = mod_index
        self.amplitude = amplitude

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        carrier = params.get("carrier_freq", self.carrier_freq)
        mod = params.get("mod_freq", self.mod_freq)
        index = params.get("mod_index", self.mod_index)
        amp = params.get("amplitude", self.amplitude)

        t = np.arange(len(buffer.samples)) / buffer.sample_rate
        modulator = np.sin(2 * np.pi * mod * t)
        samples = np.sin(2 * np.pi * carrier * t + index * modulator) * amp

        return AudioBuffer(samples.astype(np.float32), buffer.sample_rate)

    def get_params(self) -> Dict[str, Any]:
        return {
            "carrier_freq": self.carrier_freq,
            "mod_freq": self.mod_freq,
            "mod_index": self.mod_index,
            "amplitude": self.amplitude
        }


class Reverb(SynthModule):
    """Simple reverb effect."""

    def __init__(
        self,
        room_size: float = 0.5,
        damping: float = 0.5,
        wet: float = 0.3,
        dry: float = 0.7
    ):
        self.room_size = room_size
        self.damping = damping
        self.wet = wet
        self.dry = dry

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        wet = params.get("wet", self.wet)
        dry = params.get("dry", self.dry)
        room = params.get("room_size", self.room_size)

        # Simple delay-based reverb
        delays = [int(room * d * buffer.sample_rate) for d in [0.029, 0.037, 0.041, 0.043]]
        decay = 0.5 + 0.4 * room

        output = buffer.samples.copy().astype(np.float64)
        reverb = np.zeros_like(output)

        for delay in delays:
            delayed = np.zeros_like(output)
            if delay < len(output):
                delayed[delay:] = output[:-delay] * decay
            reverb += delayed

        reverb = reverb / len(delays)
        output = dry * buffer.samples + wet * reverb

        return AudioBuffer(output.astype(np.float32), buffer.sample_rate)

    def get_params(self) -> Dict[str, Any]:
        return {
            "room_size": self.room_size,
            "damping": self.damping,
            "wet": self.wet,
            "dry": self.dry
        }


class Delay(SynthModule):
    """Delay effect."""

    def __init__(
        self,
        time_ms: float = 250.0,
        feedback: float = 0.3,
        wet: float = 0.3
    ):
        self.time_ms = time_ms
        self.feedback = feedback
        self.wet = wet
        self._buffer: Optional[np.ndarray] = None

    def process(self, buffer: AudioBuffer, **params) -> AudioBuffer:
        time = params.get("time_ms", self.time_ms)
        feedback = params.get("feedback", self.feedback)
        wet = params.get("wet", self.wet)

        delay_samples = int(time * buffer.sample_rate / 1000)
        output = buffer.samples.copy().astype(np.float64)

        if self._buffer is None or len(self._buffer) != delay_samples:
            self._buffer = np.zeros(delay_samples, dtype=np.float64)

        for i in range(len(output)):
            delayed = self._buffer[i % delay_samples]
            self._buffer[i % delay_samples] = output[i] + delayed * feedback
            output[i] = output[i] * (1 - wet) + delayed * wet

        return AudioBuffer(output.astype(np.float32), buffer.sample_rate)

    def get_params(self) -> Dict[str, Any]:
        return {
            "time_ms": self.time_ms,
            "feedback": self.feedback,
            "wet": self.wet
        }


@dataclass
class TimbrePatch:
    """A complete timbre patch configuration."""
    name: str
    oscillators: List[Dict[str, Any]] = field(default_factory=list)
    filters: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    routing: List[Tuple[int, int]] = field(default_factory=list)
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "oscillators": self.oscillators,
            "filters": self.filters,
            "effects": self.effects,
            "routing": self.routing,
            "provenance_hash": self.provenance_hash
        }


class TimbreEngine:
    """
    Modular timbre synthesis engine.

    Supports multiple synthesis methods and effect chains,
    configurable via the PatchBay system.
    """

    def __init__(self, seed: int = 0, sample_rate: int = 44100):
        self.seed = seed
        self.sample_rate = sample_rate
        self._rng = np.random.default_rng(seed)
        self._modules: Dict[str, SynthModule] = {}

    def create_oscillator(
        self,
        name: str,
        shape: WaveShape = WaveShape.SINE,
        **kwargs
    ) -> Oscillator:
        """Create and register an oscillator."""
        osc = Oscillator(shape=shape, **kwargs)
        self._modules[name] = osc
        return osc

    def create_filter(
        self,
        name: str,
        filter_type: FilterType = FilterType.LOWPASS,
        **kwargs
    ) -> Filter:
        """Create and register a filter."""
        filt = Filter(filter_type=filter_type, **kwargs)
        self._modules[name] = filt
        return filt

    def create_reverb(self, name: str, **kwargs) -> Reverb:
        """Create and register a reverb."""
        rev = Reverb(**kwargs)
        self._modules[name] = rev
        return rev

    def create_delay(self, name: str, **kwargs) -> Delay:
        """Create and register a delay."""
        dly = Delay(**kwargs)
        self._modules[name] = dly
        return dly

    def generate(
        self,
        resonance: float = 0.5,
        density: float = 0.5,
        tension: float = 0.5,
        frequency: float = 440.0,
        duration: float = 1.0
    ) -> Tuple[AudioBuffer, TimbrePatch]:
        """
        Generate audio with a dynamically created timbre.

        Args:
            resonance: Harmonic richness 0.0-1.0
            density: Timbral density 0.0-1.0
            tension: Timbral tension 0.0-1.0
            frequency: Base frequency
            duration: Duration in seconds

        Returns:
            Tuple of (AudioBuffer, TimbrePatch)
        """
        n_samples = int(duration * self.sample_rate)
        buffer = AudioBuffer(
            np.zeros(n_samples, dtype=np.float32),
            self.sample_rate
        )

        # Choose synthesis based on density
        if density < 0.3:
            osc = Oscillator(WaveShape.SINE, frequency)
        elif density < 0.6:
            osc = Oscillator(WaveShape.SAW, frequency)
        else:
            osc = Oscillator(WaveShape.SQUARE, frequency)

        # Generate base
        output = osc.process(buffer)

        # Add filter based on tension
        cutoff = 500 + (1 - tension) * 8000
        filt = Filter(FilterType.LOWPASS, cutoff, 0.5 + resonance)
        output = filt.process(output)

        # Add effects based on resonance
        if resonance > 0.5:
            rev = Reverb(room_size=resonance * 0.8, wet=resonance * 0.4)
            output = rev.process(output)

        # Apply envelope
        envelope = self._create_envelope(n_samples, tension)
        output.samples = output.samples * envelope

        # Build patch descriptor
        patch = TimbrePatch(
            name=f"timbre_{self.seed}",
            oscillators=[osc.get_params()],
            filters=[filt.get_params()],
            effects=[],
            provenance_hash=self._compute_provenance(
                resonance, density, tension, frequency, duration
            )
        )

        return output, patch

    def _create_envelope(self, n_samples: int, tension: float) -> np.ndarray:
        """Create amplitude envelope."""
        attack = int(0.01 * n_samples)
        decay = int(0.1 * n_samples)
        sustain_level = 0.7 - tension * 0.3
        release = int(0.2 * n_samples)

        envelope = np.ones(n_samples, dtype=np.float32)

        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)

        # Decay
        envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)

        # Release
        release_start = n_samples - release
        envelope[release_start:] = np.linspace(sustain_level, 0, release)

        return envelope

    def _compute_provenance(
        self,
        resonance: float,
        density: float,
        tension: float,
        frequency: float,
        duration: float
    ) -> str:
        """Compute provenance hash."""
        data = f"{self.seed}:{resonance}:{density}:{tension}:{frequency}:{duration}"
        return hashlib.sha256(data.encode()).hexdigest()


__all__ = [
    "TimbreEngine", "TimbrePatch", "AudioBuffer",
    "Oscillator", "Filter", "GranularSynth", "FMSynth",
    "Reverb", "Delay", "WaveShape", "FilterType", "SynthModule"
]
