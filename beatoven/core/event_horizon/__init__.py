"""
BeatOven Event Horizon Detector

Identifies "rare" sonic events through spectral novelty,
runic entropy deviations, and emotional discontinuities.
Outputs rarity metadata for Phonomicon integration.
"""

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class RarityCategory(Enum):
    """Categories of rare events."""
    SPECTRAL_ANOMALY = "spectral_anomaly"
    RUNIC_DEVIATION = "runic_deviation"
    EMOTIONAL_DISCONTINUITY = "emotional_discontinuity"
    HARMONIC_SURPRISE = "harmonic_surprise"
    TEMPORAL_SINGULARITY = "temporal_singularity"
    TEXTURAL_EMERGENCE = "textural_emergence"


@dataclass
class RareEvent:
    """A detected rare sonic event."""
    timestamp: float  # Time in seconds
    duration: float
    category: RarityCategory
    rarity_score: float  # 0.0 to 1.0
    spectral_signature: np.ndarray
    runic_entropy: float
    description: str
    provenance_hash: str = ""

    def __post_init__(self):
        if not self.provenance_hash:
            self.provenance_hash = self._compute_provenance()

    def _compute_provenance(self) -> str:
        data = f"{self.timestamp}:{self.duration}:{self.category.value}:{self.rarity_score}:{self.runic_entropy}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "duration": self.duration,
            "category": self.category.value,
            "rarity_score": self.rarity_score,
            "spectral_signature": self.spectral_signature.tolist(),
            "runic_entropy": self.runic_entropy,
            "description": self.description,
            "provenance_hash": self.provenance_hash
        }


@dataclass
class RarityMetadata:
    """Complete rarity analysis for a piece."""
    total_events: int
    avg_rarity: float
    max_rarity: float
    category_distribution: Dict[str, int]
    events: List[RareEvent]
    phonomicon_ready: bool = True
    provenance_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_events": self.total_events,
            "avg_rarity": self.avg_rarity,
            "max_rarity": self.max_rarity,
            "category_distribution": self.category_distribution,
            "events": [e.to_dict() for e in self.events],
            "phonomicon_ready": self.phonomicon_ready,
            "provenance_hash": self.provenance_hash
        }


class EventHorizonDetector:
    """
    Detects rare sonic events for NFT rarity metadata.

    Analyzes spectral content, runic entropy, and emotional
    discontinuities to identify unique moments.
    """

    # Rarity thresholds
    SPECTRAL_NOVELTY_THRESHOLD = 0.6
    ENTROPY_DEVIATION_THRESHOLD = 2.0
    EMOTIONAL_DISCONTINUITY_THRESHOLD = 0.5

    def __init__(
        self,
        seed: int = 0,
        sensitivity: float = 0.5,
        min_event_duration: float = 0.1
    ):
        """
        Initialize detector.

        Args:
            seed: Deterministic seed
            sensitivity: Detection sensitivity 0.0-1.0
            min_event_duration: Minimum event duration in seconds
        """
        self.seed = seed
        self.sensitivity = sensitivity
        self.min_event_duration = min_event_duration
        self._rng = np.random.default_rng(seed)

    def detect(
        self,
        audio: np.ndarray,
        sample_rate: int = 44100,
        rune_vector: Optional[np.ndarray] = None,
        emotional_curve: Optional[np.ndarray] = None
    ) -> RarityMetadata:
        """
        Detect rare events in audio.

        Args:
            audio: Audio samples
            sample_rate: Sample rate
            rune_vector: ABX-Runes vector for entropy analysis
            emotional_curve: Emotional intensity over time

        Returns:
            RarityMetadata with detected events
        """
        events = []

        # Detect spectral anomalies
        spectral_events = self._detect_spectral_anomalies(audio, sample_rate)
        events.extend(spectral_events)

        # Detect runic deviations
        if rune_vector is not None:
            runic_events = self._detect_runic_deviations(
                audio, sample_rate, rune_vector
            )
            events.extend(runic_events)

        # Detect emotional discontinuities
        if emotional_curve is not None:
            emotional_events = self._detect_emotional_discontinuities(
                emotional_curve, sample_rate
            )
            events.extend(emotional_events)

        # Detect harmonic surprises
        harmonic_events = self._detect_harmonic_surprises(audio, sample_rate)
        events.extend(harmonic_events)

        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)

        # Compute statistics
        if events:
            avg_rarity = sum(e.rarity_score for e in events) / len(events)
            max_rarity = max(e.rarity_score for e in events)
        else:
            avg_rarity = 0.0
            max_rarity = 0.0

        # Category distribution
        category_dist = {}
        for cat in RarityCategory:
            category_dist[cat.value] = sum(
                1 for e in events if e.category == cat
            )

        # Compute overall provenance
        event_hashes = "".join(e.provenance_hash for e in events)
        provenance = hashlib.sha256(event_hashes.encode()).hexdigest()

        return RarityMetadata(
            total_events=len(events),
            avg_rarity=avg_rarity,
            max_rarity=max_rarity,
            category_distribution=category_dist,
            events=events,
            phonomicon_ready=len(events) > 0,
            provenance_hash=provenance
        )

    def _detect_spectral_anomalies(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> List[RareEvent]:
        """Detect spectral novelty peaks."""
        events = []

        # Compute spectral flux
        frame_size = 2048
        hop_size = 512
        n_frames = (len(audio) - frame_size) // hop_size

        if n_frames <= 1:
            return events

        prev_spectrum = None
        flux_values = []

        for i in range(n_frames):
            start = i * hop_size
            frame = audio[start:start + frame_size]

            # Apply window
            window = np.hanning(frame_size)
            windowed = frame[:len(window)] * window[:len(frame)]

            # Compute spectrum
            spectrum = np.abs(np.fft.rfft(windowed))

            if prev_spectrum is not None:
                # Spectral flux
                diff = spectrum - prev_spectrum
                flux = np.sum(np.maximum(diff, 0))
                flux_values.append(flux)
            else:
                flux_values.append(0)

            prev_spectrum = spectrum

        # Normalize flux
        flux_array = np.array(flux_values)
        if flux_array.std() > 0:
            flux_normalized = (flux_array - flux_array.mean()) / flux_array.std()
        else:
            flux_normalized = flux_array

        # Find peaks above threshold
        threshold = self.SPECTRAL_NOVELTY_THRESHOLD / self.sensitivity
        for i, flux in enumerate(flux_normalized):
            if flux > threshold:
                timestamp = i * hop_size / sample_rate
                rarity = min(1.0, flux / 4.0)

                # Extract spectral signature
                start = i * hop_size
                frame = audio[start:start + frame_size]
                signature = np.abs(np.fft.rfft(frame * np.hanning(len(frame))))
                signature = signature[:64] / (signature.max() + 1e-10)

                events.append(RareEvent(
                    timestamp=timestamp,
                    duration=self.min_event_duration,
                    category=RarityCategory.SPECTRAL_ANOMALY,
                    rarity_score=rarity,
                    spectral_signature=signature.astype(np.float32),
                    runic_entropy=float(flux),
                    description=f"Spectral novelty peak at {timestamp:.2f}s"
                ))

        return events

    def _detect_runic_deviations(
        self,
        audio: np.ndarray,
        sample_rate: int,
        rune_vector: np.ndarray
    ) -> List[RareEvent]:
        """Detect deviations from expected runic entropy."""
        events = []

        # Expected entropy from rune vector
        expected_entropy = np.std(rune_vector)

        # Compute local entropy over time
        frame_size = 4096
        hop_size = 2048
        n_frames = (len(audio) - frame_size) // hop_size

        for i in range(n_frames):
            start = i * hop_size
            frame = audio[start:start + frame_size]

            # Local entropy approximation
            hist, _ = np.histogram(frame, bins=50)
            hist = hist / (hist.sum() + 1e-10)
            local_entropy = -np.sum(hist * np.log2(hist + 1e-10))

            # Compare to expected
            deviation = abs(local_entropy - expected_entropy * 5)

            if deviation > self.ENTROPY_DEVIATION_THRESHOLD / self.sensitivity:
                timestamp = i * hop_size / sample_rate
                rarity = min(1.0, deviation / 5.0)

                events.append(RareEvent(
                    timestamp=timestamp,
                    duration=frame_size / sample_rate,
                    category=RarityCategory.RUNIC_DEVIATION,
                    rarity_score=rarity,
                    spectral_signature=np.zeros(64, dtype=np.float32),
                    runic_entropy=local_entropy,
                    description=f"Runic entropy deviation at {timestamp:.2f}s"
                ))

        return events

    def _detect_emotional_discontinuities(
        self,
        emotional_curve: np.ndarray,
        sample_rate: int
    ) -> List[RareEvent]:
        """Detect sudden changes in emotional intensity."""
        events = []

        if len(emotional_curve) < 2:
            return events

        # Compute derivative
        derivative = np.diff(emotional_curve)
        threshold = self.EMOTIONAL_DISCONTINUITY_THRESHOLD / self.sensitivity

        for i, d in enumerate(derivative):
            if abs(d) > threshold:
                timestamp = i / sample_rate
                rarity = min(1.0, abs(d))

                events.append(RareEvent(
                    timestamp=timestamp,
                    duration=self.min_event_duration,
                    category=RarityCategory.EMOTIONAL_DISCONTINUITY,
                    rarity_score=rarity,
                    spectral_signature=np.zeros(64, dtype=np.float32),
                    runic_entropy=abs(d),
                    description=f"Emotional discontinuity at {timestamp:.2f}s"
                ))

        return events

    def _detect_harmonic_surprises(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> List[RareEvent]:
        """Detect unexpected harmonic content."""
        events = []

        frame_size = 4096
        hop_size = 2048
        n_frames = (len(audio) - frame_size) // hop_size

        prev_peaks = None

        for i in range(n_frames):
            start = i * hop_size
            frame = audio[start:start + frame_size]

            # Compute spectrum
            spectrum = np.abs(np.fft.rfft(frame * np.hanning(frame_size)))

            # Find peaks
            peaks = self._find_spectral_peaks(spectrum)

            if prev_peaks is not None:
                # Check for unexpected new peaks
                new_peaks = set(peaks) - set(prev_peaks)
                if len(new_peaks) > 3:  # Threshold for "surprise"
                    timestamp = i * hop_size / sample_rate
                    rarity = min(1.0, len(new_peaks) / 10.0)

                    events.append(RareEvent(
                        timestamp=timestamp,
                        duration=self.min_event_duration,
                        category=RarityCategory.HARMONIC_SURPRISE,
                        rarity_score=rarity,
                        spectral_signature=spectrum[:64].astype(np.float32),
                        runic_entropy=len(new_peaks),
                        description=f"Harmonic surprise at {timestamp:.2f}s"
                    ))

            prev_peaks = peaks

        return events

    def _find_spectral_peaks(
        self,
        spectrum: np.ndarray,
        threshold: float = 0.1
    ) -> List[int]:
        """Find peaks in spectrum."""
        peaks = []
        normalized = spectrum / (spectrum.max() + 1e-10)

        for i in range(1, len(normalized) - 1):
            if (normalized[i] > normalized[i-1] and
                normalized[i] > normalized[i+1] and
                normalized[i] > threshold):
                peaks.append(i)

        return peaks

    def export_for_phonomicon(
        self,
        metadata: RarityMetadata
    ) -> Dict[str, Any]:
        """Export rarity metadata for Phonomicon NFT integration."""
        return {
            "version": "1.0",
            "source": "BeatOven",
            "rarity_analysis": metadata.to_dict(),
            "nft_traits": {
                "total_rare_events": metadata.total_events,
                "rarity_score": metadata.avg_rarity,
                "peak_rarity": metadata.max_rarity,
                "dominant_category": max(
                    metadata.category_distribution.items(),
                    key=lambda x: x[1],
                    default=("none", 0)
                )[0],
                "provenance": metadata.provenance_hash
            }
        }


__all__ = [
    "EventHorizonDetector", "RareEvent", "RarityMetadata", "RarityCategory"
]
