"""
BeatOven Stem Generator

Bounces stems: drums, bass, leads, mids, pads, atmos.
Exports WAV/FLAC with ONNX mel-spectrogram and provenance hash.
"""

import hashlib
import struct
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from pathlib import Path
import io


class StemType(Enum):
    """Stem categories."""
    DRUMS = "drums"
    BASS = "bass"
    LEADS = "leads"
    MIDS = "mids"
    PADS = "pads"
    ATMOS = "atmos"
    FULL_MIX = "full_mix"


class ExportFormat(Enum):
    """Audio export formats."""
    WAV = "wav"
    FLAC = "flac"


@dataclass
class StemMetadata:
    """Metadata for a single stem."""
    stem_type: StemType
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    peak_amplitude: float
    rms_level: float
    provenance_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stem_type": self.stem_type.value,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "peak_amplitude": self.peak_amplitude,
            "rms_level": self.rms_level,
            "provenance_hash": self.provenance_hash
        }


@dataclass
class Stem:
    """A single audio stem."""
    stem_type: StemType
    samples: np.ndarray
    sample_rate: int = 44100
    channels: int = 2
    metadata: Optional[StemMetadata] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = self._compute_metadata()

    def _compute_metadata(self) -> StemMetadata:
        """Compute metadata from samples."""
        samples = self.samples.astype(np.float64)
        peak = float(np.max(np.abs(samples))) if len(samples) > 0 else 0.0
        rms = float(np.sqrt(np.mean(samples ** 2))) if len(samples) > 0 else 0.0

        return StemMetadata(
            stem_type=self.stem_type,
            duration=len(self.samples) / self.sample_rate / max(1, self.channels),
            sample_rate=self.sample_rate,
            channels=self.channels,
            bit_depth=16,
            peak_amplitude=peak,
            rms_level=rms,
            provenance_hash=self._compute_provenance()
        )

    def _compute_provenance(self) -> str:
        """Compute provenance hash from audio data."""
        audio_bytes = self.samples.tobytes()
        return hashlib.sha256(audio_bytes).hexdigest()

    def to_stereo(self) -> "Stem":
        """Convert to stereo if mono."""
        if self.channels == 2:
            return self
        stereo = np.column_stack([self.samples, self.samples])
        return Stem(
            stem_type=self.stem_type,
            samples=stereo.flatten(),
            sample_rate=self.sample_rate,
            channels=2
        )


@dataclass
class MelSpectrogram:
    """Mel spectrogram representation."""
    data: np.ndarray
    sample_rate: int
    n_mels: int
    hop_length: int
    n_fft: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape": list(self.data.shape),
            "sample_rate": self.sample_rate,
            "n_mels": self.n_mels,
            "hop_length": self.hop_length,
            "n_fft": self.n_fft
        }


class StemGenerator:
    """
    Generates and exports audio stems with provenance tracking.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        bit_depth: int = 16,
        seed: int = 0
    ):
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.seed = seed
        self._rng = np.random.default_rng(seed)

    def generate_stems(
        self,
        rhythm_events: Optional[List[Dict]] = None,
        harmonic_events: Optional[List[Dict]] = None,
        timbre_buffer: Optional[np.ndarray] = None,
        duration: float = 16.0,
        stem_types: Optional[List[StemType]] = None
    ) -> Dict[StemType, Stem]:
        """
        Generate stems from engine outputs.

        Args:
            rhythm_events: Events from RhythmEngine
            harmonic_events: Events from HarmonicEngine
            timbre_buffer: Audio from TimbreEngine
            duration: Duration in seconds
            stem_types: Which stems to generate

        Returns:
            Dictionary of StemType -> Stem
        """
        if stem_types is None:
            stem_types = list(StemType)

        n_samples = int(duration * self.sample_rate)
        stems = {}

        for stem_type in stem_types:
            if stem_type == StemType.DRUMS:
                samples = self._generate_drum_stem(rhythm_events, n_samples)
            elif stem_type == StemType.BASS:
                samples = self._generate_bass_stem(harmonic_events, n_samples)
            elif stem_type == StemType.LEADS:
                samples = self._generate_lead_stem(harmonic_events, n_samples)
            elif stem_type == StemType.MIDS:
                samples = self._generate_mid_stem(harmonic_events, n_samples)
            elif stem_type == StemType.PADS:
                samples = self._generate_pad_stem(harmonic_events, n_samples)
            elif stem_type == StemType.ATMOS:
                samples = self._generate_atmos_stem(n_samples)
            elif stem_type == StemType.FULL_MIX:
                continue  # Generate after other stems
            else:
                samples = np.zeros(n_samples * 2, dtype=np.float32)

            stems[stem_type] = Stem(
                stem_type=stem_type,
                samples=samples,
                sample_rate=self.sample_rate,
                channels=2
            )

        # Generate full mix from other stems
        if StemType.FULL_MIX in stem_types:
            stems[StemType.FULL_MIX] = self._mix_stems(stems, n_samples)

        return stems

    def _generate_drum_stem(
        self,
        events: Optional[List[Dict]],
        n_samples: int
    ) -> np.ndarray:
        """Generate drum stem from rhythm events."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)

        if not events:
            # Generate default drum pattern
            kick_times = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]
            for t in kick_times:
                self._add_drum_hit(samples, t, "kick", n_samples)

        return samples

    def _add_drum_hit(
        self,
        samples: np.ndarray,
        time: float,
        drum_type: str,
        n_samples: int
    ):
        """Add a drum hit to the buffer."""
        start = int(time * self.sample_rate) * 2
        if start >= len(samples):
            return

        # Simple drum synthesis
        hit_samples = int(0.1 * self.sample_rate)
        t = np.linspace(0, 0.1, hit_samples)

        if drum_type == "kick":
            freq = 60 * np.exp(-t * 20)
            hit = np.sin(2 * np.pi * freq * t) * np.exp(-t * 15)
        elif drum_type == "snare":
            hit = self._rng.uniform(-1, 1, hit_samples) * np.exp(-t * 20)
        else:
            hit = np.sin(2 * np.pi * 8000 * t) * np.exp(-t * 40)

        # Stereo
        for i, s in enumerate(hit):
            idx = start + i * 2
            if idx + 1 < len(samples):
                samples[idx] += s * 0.5
                samples[idx + 1] += s * 0.5

    def _generate_bass_stem(
        self,
        events: Optional[List[Dict]],
        n_samples: int
    ) -> np.ndarray:
        """Generate bass stem."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)
        t = np.arange(n_samples) / self.sample_rate

        # Simple bass line
        freq = 55  # A1
        bass = np.sin(2 * np.pi * freq * t) * 0.3

        # Apply envelope
        env = np.minimum(t * 10, 1) * np.exp(-t * 0.5)
        bass *= env

        # Stereo
        for i, s in enumerate(bass):
            samples[i * 2] = s
            samples[i * 2 + 1] = s

        return samples

    def _generate_lead_stem(
        self,
        events: Optional[List[Dict]],
        n_samples: int
    ) -> np.ndarray:
        """Generate lead stem."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)
        t = np.arange(n_samples) / self.sample_rate

        # Simple lead
        freq = 440
        lead = np.sin(2 * np.pi * freq * t) * 0.2
        lead += np.sin(2 * np.pi * freq * 2 * t) * 0.1

        env = np.exp(-t * 0.3)
        lead *= env

        for i, s in enumerate(lead):
            samples[i * 2] = s
            samples[i * 2 + 1] = s

        return samples

    def _generate_mid_stem(
        self,
        events: Optional[List[Dict]],
        n_samples: int
    ) -> np.ndarray:
        """Generate mid-frequency stem."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)
        t = np.arange(n_samples) / self.sample_rate

        # Chord stab
        freqs = [261.63, 329.63, 392.0]  # C major
        mid = sum(np.sin(2 * np.pi * f * t) for f in freqs) * 0.15 / len(freqs)

        for i, s in enumerate(mid):
            samples[i * 2] = s
            samples[i * 2 + 1] = s

        return samples

    def _generate_pad_stem(
        self,
        events: Optional[List[Dict]],
        n_samples: int
    ) -> np.ndarray:
        """Generate pad stem."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)
        t = np.arange(n_samples) / self.sample_rate

        # Soft pad
        freqs = [130.81, 164.81, 196.0, 261.63]  # C major 7
        pad = sum(np.sin(2 * np.pi * f * t) for f in freqs) * 0.1 / len(freqs)

        # Slow attack
        env = 1 - np.exp(-t * 0.5)
        pad *= env

        for i, s in enumerate(pad):
            samples[i * 2] = s
            samples[i * 2 + 1] = s

        return samples

    def _generate_atmos_stem(self, n_samples: int) -> np.ndarray:
        """Generate atmospheric stem."""
        samples = np.zeros(n_samples * 2, dtype=np.float32)

        # Filtered noise
        noise = self._rng.uniform(-0.05, 0.05, n_samples).astype(np.float32)

        for i, s in enumerate(noise):
            samples[i * 2] = s
            samples[i * 2 + 1] = s

        return samples

    def _mix_stems(
        self,
        stems: Dict[StemType, Stem],
        n_samples: int
    ) -> Stem:
        """Mix all stems into full mix."""
        mixed = np.zeros(n_samples * 2, dtype=np.float32)

        gains = {
            StemType.DRUMS: 0.8,
            StemType.BASS: 0.7,
            StemType.LEADS: 0.6,
            StemType.MIDS: 0.5,
            StemType.PADS: 0.4,
            StemType.ATMOS: 0.3
        }

        for stem_type, stem in stems.items():
            if stem_type == StemType.FULL_MIX:
                continue
            gain = gains.get(stem_type, 0.5)
            length = min(len(stem.samples), len(mixed))
            mixed[:length] += stem.samples[:length] * gain

        # Normalize
        peak = np.max(np.abs(mixed))
        if peak > 0:
            mixed = mixed / peak * 0.9

        return Stem(
            stem_type=StemType.FULL_MIX,
            samples=mixed,
            sample_rate=self.sample_rate,
            channels=2
        )

    def export_wav(self, stem: Stem, path: Path) -> str:
        """Export stem to WAV file."""
        path = Path(path)
        samples = (stem.samples * 32767).astype(np.int16)

        with open(path, 'wb') as f:
            # RIFF header
            f.write(b'RIFF')
            data_size = len(samples) * 2
            f.write(struct.pack('<I', 36 + data_size))
            f.write(b'WAVE')

            # fmt chunk
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))  # Chunk size
            f.write(struct.pack('<H', 1))   # Audio format (PCM)
            f.write(struct.pack('<H', stem.channels))
            f.write(struct.pack('<I', stem.sample_rate))
            f.write(struct.pack('<I', stem.sample_rate * stem.channels * 2))
            f.write(struct.pack('<H', stem.channels * 2))
            f.write(struct.pack('<H', 16))  # Bits per sample

            # data chunk
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            f.write(samples.tobytes())

        return stem.metadata.provenance_hash if stem.metadata else ""

    def export_all(
        self,
        stems: Dict[StemType, Stem],
        output_dir: Path,
        prefix: str = "stem"
    ) -> Dict[StemType, str]:
        """Export all stems to directory."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        provenance_hashes = {}
        for stem_type, stem in stems.items():
            filename = f"{prefix}_{stem_type.value}.wav"
            path = output_dir / filename
            provenance_hashes[stem_type] = self.export_wav(stem, path)

        return provenance_hashes

    def compute_mel_spectrogram(
        self,
        stem: Stem,
        n_mels: int = 128,
        n_fft: int = 2048,
        hop_length: int = 512
    ) -> MelSpectrogram:
        """Compute mel spectrogram for ONNX export."""
        # Simple mel spectrogram computation
        samples = stem.samples[::2] if stem.channels == 2 else stem.samples

        # Pad to frame boundary
        pad_length = n_fft - (len(samples) % hop_length)
        samples = np.pad(samples, (0, pad_length))

        # Compute STFT
        n_frames = (len(samples) - n_fft) // hop_length + 1
        stft = np.zeros((n_fft // 2 + 1, n_frames), dtype=np.complex128)

        window = np.hanning(n_fft)
        for i in range(n_frames):
            start = i * hop_length
            frame = samples[start:start + n_fft] * window
            stft[:, i] = np.fft.rfft(frame)

        # Convert to power spectrum
        power = np.abs(stft) ** 2

        # Create mel filterbank
        mel_filters = self._create_mel_filterbank(
            stem.sample_rate, n_fft, n_mels
        )

        # Apply mel filterbank
        mel_spec = np.dot(mel_filters, power)

        # Convert to dB
        mel_spec = 10 * np.log10(mel_spec + 1e-10)

        return MelSpectrogram(
            data=mel_spec.astype(np.float32),
            sample_rate=stem.sample_rate,
            n_mels=n_mels,
            hop_length=hop_length,
            n_fft=n_fft
        )

    def _create_mel_filterbank(
        self,
        sample_rate: int,
        n_fft: int,
        n_mels: int
    ) -> np.ndarray:
        """Create mel filterbank matrix."""
        def hz_to_mel(hz):
            return 2595 * np.log10(1 + hz / 700)

        def mel_to_hz(mel):
            return 700 * (10 ** (mel / 2595) - 1)

        n_freqs = n_fft // 2 + 1
        mel_min = hz_to_mel(0)
        mel_max = hz_to_mel(sample_rate / 2)

        mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
        hz_points = mel_to_hz(mel_points)
        bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

        filters = np.zeros((n_mels, n_freqs))
        for i in range(n_mels):
            start = bin_points[i]
            mid = bin_points[i + 1]
            end = bin_points[i + 2]

            for j in range(start, mid):
                if mid > start:
                    filters[i, j] = (j - start) / (mid - start)
            for j in range(mid, end):
                if end > mid:
                    filters[i, j] = (end - j) / (end - mid)

        return filters


__all__ = [
    "StemGenerator", "Stem", "StemMetadata", "StemType",
    "ExportFormat", "MelSpectrogram"
]
