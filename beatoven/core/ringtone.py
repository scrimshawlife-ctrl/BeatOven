"""
Ringtone & Notification Generator
Short-form audio generation (1-30 seconds)
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import numpy as np
import hashlib

from beatoven.audio import AudioIO, AudioFormat, StemType


class RingtoneType(Enum):
    """Ringtone duration categories"""
    NOTIFICATION = "notification"  # 1-5 seconds
    SHORT_RINGTONE = "short_ringtone"  # 10-15 seconds
    STANDARD_RINGTONE = "standard_ringtone"  # 20-30 seconds


@dataclass
class RingtoneConfig:
    """Configuration for ringtone generation"""
    duration_seconds: float
    ringtone_type: RingtoneType
    tempo: float = 120.0
    intensity: float = 0.5  # 0.0-1.0
    melodic: bool = True
    percussive: bool = True
    fade_in_ms: int = 50
    fade_out_ms: int = 100
    loop_seamless: bool = True


class RingtoneGenerator:
    """
    Generate short-form audio for ringtones and notifications.
    Constrains rhythm/harmony/timbre engines for brief output.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_notification(
        self,
        duration_seconds: float = 2.0,
        melodic: bool = True,
        intensity: float = 0.6
    ) -> np.ndarray:
        """
        Generate notification sound (1-5 seconds).
        Simple, attention-grabbing, non-intrusive.
        """
        config = RingtoneConfig(
            duration_seconds=min(duration_seconds, 5.0),
            ringtone_type=RingtoneType.NOTIFICATION,
            intensity=intensity,
            melodic=melodic,
            percussive=True,
        )
        return self._generate_audio(config)

    def generate_ringtone(
        self,
        duration_seconds: float = 25.0,
        melodic: bool = True,
        percussive: bool = True,
        intensity: float = 0.7,
        loop_seamless: bool = True
    ) -> np.ndarray:
        """
        Generate ringtone (10-30 seconds).
        Musical, loopable, clear melody.
        """
        duration_clamped = np.clip(duration_seconds, 10.0, 30.0)

        ringtone_type = (
            RingtoneType.SHORT_RINGTONE if duration_clamped < 18
            else RingtoneType.STANDARD_RINGTONE
        )

        config = RingtoneConfig(
            duration_seconds=duration_clamped,
            ringtone_type=ringtone_type,
            intensity=intensity,
            melodic=melodic,
            percussive=percussive,
            loop_seamless=loop_seamless,
        )
        return self._generate_audio(config)

    def _generate_audio(self, config: RingtoneConfig) -> np.ndarray:
        """
        Core audio generation constrained for short-form.
        Uses simplified rhythm + harmonic engines.
        """
        sample_rate = 44100
        num_samples = int(config.duration_seconds * sample_rate)

        # Generate time array
        t = np.linspace(0, config.duration_seconds, num_samples)

        # Initialize audio
        audio = np.zeros(num_samples, dtype=np.float32)

        # Add melodic component
        if config.melodic:
            melody = self._generate_melody(t, config)
            audio += melody * 0.6

        # Add percussive component
        if config.percussive:
            percussion = self._generate_percussion(t, config)
            audio += percussion * 0.4

        # Apply envelopes
        audio = self._apply_envelope(audio, config, sample_rate)

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-10) * 0.9

        return audio

    def _generate_melody(self, t: np.ndarray, config: RingtoneConfig) -> np.ndarray:
        """Generate melodic component"""
        # Simple harmonic series
        fundamental = 440.0  # A4

        # Major triad
        if config.ringtone_type == RingtoneType.NOTIFICATION:
            # Simple two-note pattern
            freqs = [fundamental, fundamental * 1.5]  # A4, E5
            pattern = np.sin(2 * np.pi * freqs[0] * t[:len(t)//2])
            pattern = np.concatenate([
                pattern,
                np.sin(2 * np.pi * freqs[1] * t[len(t)//2:])
            ])
        else:
            # Arpeggio pattern for ringtones
            notes = [1.0, 1.25, 1.5, 2.0]  # Major triad + octave
            pattern = np.zeros_like(t)
            segment_len = len(t) // len(notes)

            for i, note_ratio in enumerate(notes):
                start = i * segment_len
                end = start + segment_len if i < len(notes) - 1 else len(t)
                freq = fundamental * note_ratio
                pattern[start:end] = np.sin(2 * np.pi * freq * t[start:end])

        # Add harmonics
        harmonics = pattern + 0.3 * np.sin(4 * np.pi * fundamental * t)

        return harmonics

    def _generate_percussion(self, t: np.ndarray, config: RingtoneType) -> np.ndarray:
        """Generate percussive component"""
        percussion = np.zeros_like(t)

        # Simple kick pattern
        beat_interval = 0.5  # 120 BPM
        num_beats = int(config.duration_seconds / beat_interval)

        sample_rate = len(t) / config.duration_seconds

        for i in range(num_beats):
            beat_time = i * beat_interval
            beat_sample = int(beat_time * sample_rate)
            if beat_sample < len(percussion):
                # Kick drum synthesis (decaying sine)
                kick_duration = 0.2
                kick_samples = int(kick_duration * sample_rate)
                kick_t = np.linspace(0, kick_duration, kick_samples)
                kick = np.sin(2 * np.pi * 60 * kick_t) * np.exp(-kick_t * 10)

                end_idx = min(beat_sample + len(kick), len(percussion))
                percussion[beat_sample:end_idx] += kick[:end_idx - beat_sample]

        return percussion

    def _apply_envelope(
        self,
        audio: np.ndarray,
        config: RingtoneConfig,
        sample_rate: int
    ) -> np.ndarray:
        """Apply fade in/out envelopes"""
        fade_in_samples = int(config.fade_in_ms * sample_rate / 1000)
        fade_out_samples = int(config.fade_out_ms * sample_rate / 1000)

        # Fade in
        if fade_in_samples > 0:
            fade_in = np.linspace(0, 1, fade_in_samples)
            audio[:fade_in_samples] *= fade_in

        # Fade out
        if fade_out_samples > 0:
            fade_out = np.linspace(1, 0, fade_out_samples)
            audio[-fade_out_samples:] *= fade_out

        return audio

    def export_ringtone(
        self,
        audio: np.ndarray,
        output_path: str,
        format: AudioFormat = AudioFormat.M4A,
        sample_rate: int = 44100
    ):
        """Export ringtone to mobile-friendly format"""
        # Convert to format
        AudioIO.save_audio(output_path, audio, sample_rate, format)

        # Compute provenance
        hash_input = f"ringtone:{audio.tobytes()[:100]}"
        provenance = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

        return {
            "output_path": output_path,
            "format": format.value,
            "duration": len(audio) / sample_rate,
            "sample_rate": sample_rate,
            "provenance_hash": provenance,
        }


__all__ = [
    "RingtoneType",
    "RingtoneConfig",
    "RingtoneGenerator",
]
