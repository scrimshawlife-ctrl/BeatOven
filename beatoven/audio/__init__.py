"""
BeatOven Audio I/O and Stem Extraction
Handles audio file formats and ML-based stem separation
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
from pathlib import Path
import numpy as np
import hashlib


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    FLAC = "flac"
    AIFF = "aiff"
    ALAC = "alac"
    MP3 = "mp3"
    AAC = "aac"
    M4A = "m4a"
    OGG = "ogg"
    OPUS = "opus"


class StemType(Enum):
    """Stem categories"""
    DRUMS = "drums"
    BASS = "bass"
    VOCALS = "vocals"
    OTHER = "other"
    PIANO = "piano"
    GUITAR = "guitar"
    STRINGS = "strings"
    SYNTH = "synth"
    LEADS = "leads"
    PADS = "pads"
    ATMOS = "atmos"
    FULL_MIX = "full_mix"


@dataclass
class AudioMetadata:
    """Audio file metadata"""
    sample_rate: int
    channels: int
    bit_depth: int
    duration_seconds: float
    format: AudioFormat
    file_size_bytes: int


@dataclass
class AudioStem:
    """Single audio stem with metadata"""
    name: str
    stem_type: StemType
    audio_data: np.ndarray
    sample_rate: int
    duration: float

    # Emotional/symbolic analysis
    resonance: float = 0.0
    density: float = 0.0
    tension: float = 0.0
    emotional_index: float = 0.0

    # Provenance
    provenance_hash: str = ""

    def compute_provenance(self) -> str:
        """Generate deterministic hash for stem"""
        # Use first and last 1000 samples for hash
        sample_subset = np.concatenate([
            self.audio_data[:1000].flatten(),
            self.audio_data[-1000:].flatten()
        ])
        hash_input = f"{self.name}:{self.stem_type.value}:{sample_subset.tobytes()[:100]}"
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()
        self.provenance_hash = hash_bytes.hex()[:16]
        return self.provenance_hash

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "stem_type": self.stem_type.value,
            "sample_rate": self.sample_rate,
            "duration": self.duration,
            "shape": list(self.audio_data.shape),
            "symbolic_fields": {
                "resonance": self.resonance,
                "density": self.density,
                "tension": self.tension,
                "emotional_index": self.emotional_index,
            },
            "provenance_hash": self.provenance_hash,
        }


class AudioIO:
    """
    Audio file I/O for multiple formats.
    Supports: WAV, FLAC, AIFF, ALAC, MP3, AAC, M4A, OGG, Opus
    Sample rates: 44.1kHz - 192kHz, 16-32 bit
    """

    SUPPORTED_SAMPLE_RATES = [44100, 48000, 88200, 96000, 176400, 192000]
    SUPPORTED_BIT_DEPTHS = [16, 24, 32]

    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int, AudioMetadata]:
        """
        Load audio file and return (audio_data, sample_rate, metadata).
        Uses scipy for WAV/FLAC, soundfile for other formats.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        format_str = path.suffix[1:].lower()
        if format_str not in [f.value for f in AudioFormat]:
            raise ValueError(f"Unsupported format: {format_str}")

        try:
            import soundfile as sf

            audio_data, sample_rate = sf.read(file_path, dtype='float32')

            # Get metadata
            info = sf.info(file_path)
            metadata = AudioMetadata(
                sample_rate=info.samplerate,
                channels=info.channels,
                bit_depth=info.subtype_info.bits if hasattr(info.subtype_info, 'bits') else 16,
                duration_seconds=info.duration,
                format=AudioFormat(format_str),
                file_size_bytes=path.stat().st_size,
            )

            return audio_data, sample_rate, metadata

        except ImportError:
            # Fallback to scipy for WAV
            if format_str == 'wav':
                from scipy.io import wavfile
                sample_rate, audio_data = wavfile.read(file_path)
                audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize to [-1, 1]

                metadata = AudioMetadata(
                    sample_rate=sample_rate,
                    channels=1 if audio_data.ndim == 1 else audio_data.shape[1],
                    bit_depth=16,
                    duration_seconds=len(audio_data) / sample_rate,
                    format=AudioFormat.WAV,
                    file_size_bytes=path.stat().st_size,
                )

                return audio_data, sample_rate, metadata
            else:
                raise ImportError("soundfile required for non-WAV formats")

    @staticmethod
    def save_audio(
        file_path: str,
        audio_data: np.ndarray,
        sample_rate: int,
        format: AudioFormat = AudioFormat.WAV,
        bit_depth: int = 24
    ):
        """Save audio to file"""
        try:
            import soundfile as sf

            subtype_map = {
                16: 'PCM_16',
                24: 'PCM_24',
                32: 'PCM_32',
            }

            sf.write(
                file_path,
                audio_data,
                sample_rate,
                subtype=subtype_map.get(bit_depth, 'PCM_24')
            )

        except ImportError:
            # Fallback to scipy for WAV
            if format == AudioFormat.WAV:
                from scipy.io import wavfile
                audio_int = (audio_data * 32767).astype(np.int16)
                wavfile.write(file_path, sample_rate, audio_int)
            else:
                raise ImportError("soundfile required for non-WAV formats")


class StemExtractor:
    """
    ML-based stem extraction using model-agnostic inference.
    Separates audio into stems (drums, bass, vocals, other).
    Tags each stem with emotional/symbolic metadata.
    """

    def __init__(self, model_name: str = "demucs", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None

    def load_model(self):
        """Load separation model via inference layer"""
        # In production, this would use the inference layer
        # For now, provide interface
        from beatoven.core.inference import get_inference, InferenceBackend

        try:
            self.inference = get_inference(InferenceBackend.TORCH)
            # Model would be loaded here
            self.model = "placeholder"  # Actual model loading
        except Exception as e:
            print(f"Model loading failed: {e}")
            self.model = None

    def extract_stems(
        self,
        audio_path: str,
        stem_types: Optional[List[StemType]] = None
    ) -> List[AudioStem]:
        """
        Extract stems from audio file.
        Returns list of AudioStem objects with emotional metadata.
        """
        # Load audio
        audio_data, sample_rate, metadata = AudioIO.load_audio(audio_path)

        if stem_types is None:
            stem_types = [
                StemType.DRUMS,
                StemType.BASS,
                StemType.VOCALS,
                StemType.OTHER
            ]

        # Mock stem extraction for now
        # In production, this would use actual separation model
        stems = []
        duration = len(audio_data) / sample_rate

        for stem_type in stem_types:
            # Create stem (in production, actual separated audio)
            stem_audio = self._mock_separate_stem(audio_data, stem_type)

            stem = AudioStem(
                name=f"{Path(audio_path).stem}_{stem_type.value}",
                stem_type=stem_type,
                audio_data=stem_audio,
                sample_rate=sample_rate,
                duration=duration,
            )

            # Analyze stem emotionally/symbolically
            stem.resonance, stem.density, stem.tension, stem.emotional_index = (
                self._analyze_stem(stem_audio, sample_rate)
            )

            stem.compute_provenance()
            stems.append(stem)

        return stems

    def _mock_separate_stem(self, audio: np.ndarray, stem_type: StemType) -> np.ndarray:
        """Mock stem separation - returns filtered audio"""
        # In production, this uses actual ML model
        # For now, apply simple filtering as placeholder
        return audio * 0.5  # Placeholder

    def _analyze_stem(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> Tuple[float, float, float, float]:
        """
        Analyze stem for symbolic/emotional features.
        Returns (resonance, density, tension, emotional_index).
        """
        # Compute basic audio features
        rms = np.sqrt(np.mean(audio ** 2))
        spectral_centroid = self._compute_spectral_centroid(audio, sample_rate)
        zero_crossings = np.sum(np.diff(np.sign(audio)) != 0) / len(audio)

        # Map to symbolic fields
        resonance = min(1.0, spectral_centroid / 10000.0)
        density = min(1.0, rms * 2.0)
        tension = min(1.0, zero_crossings * 100.0)
        emotional_index = (resonance + density + tension) / 3.0

        return resonance, density, tension, emotional_index

    def _compute_spectral_centroid(self, audio: np.ndarray, sample_rate: int) -> float:
        """Compute spectral centroid"""
        # Simple spectral centroid via FFT
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)
        centroid = np.sum(freqs * spectrum) / (np.sum(spectrum) + 1e-10)
        return centroid


__all__ = [
    "AudioFormat",
    "StemType",
    "AudioMetadata",
    "AudioStem",
    "AudioIO",
    "StemExtractor",
]
