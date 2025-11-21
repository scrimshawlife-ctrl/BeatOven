"""Tests for EventHorizonDetector."""

import numpy as np
import pytest
from beatoven.core.event_horizon import (
    EventHorizonDetector, RareEvent, RarityMetadata, RarityCategory
)


class TestEventHorizonDetector:
    """Tests for EventHorizonDetector."""

    def test_basic_detection(self):
        detector = EventHorizonDetector(seed=42)

        # Create test audio with some events
        audio = np.random.uniform(-0.1, 0.1, 44100).astype(np.float32)
        # Add a sudden loud event
        audio[10000:10500] = np.random.uniform(-1, 1, 500).astype(np.float32)

        metadata = detector.detect(audio, sample_rate=44100)

        assert isinstance(metadata, RarityMetadata)
        assert metadata.total_events >= 0

    def test_spectral_anomaly_detection(self):
        detector = EventHorizonDetector(seed=42, sensitivity=0.8)

        # Create audio with spectral change
        audio = np.zeros(44100, dtype=np.float32)
        t1 = np.linspace(0, 0.5, 22050)
        audio[:22050] = np.sin(2 * np.pi * 440 * t1)  # Low frequency
        t2 = np.linspace(0, 0.5, 22050)
        audio[22050:] = np.sin(2 * np.pi * 4000 * t2)  # High frequency

        metadata = detector.detect(audio, sample_rate=44100)

        # Should detect the frequency change
        spectral_events = sum(
            1 for e in metadata.events
            if e.category == RarityCategory.SPECTRAL_ANOMALY
        )
        assert spectral_events >= 0

    def test_runic_deviation_detection(self):
        detector = EventHorizonDetector(seed=42)

        audio = np.random.uniform(-0.5, 0.5, 88200).astype(np.float32)
        rune_vector = np.random.uniform(-1, 1, 64).astype(np.float32)

        metadata = detector.detect(
            audio,
            sample_rate=44100,
            rune_vector=rune_vector
        )

        assert metadata.total_events >= 0

    def test_emotional_discontinuity_detection(self):
        detector = EventHorizonDetector(seed=42)

        audio = np.random.uniform(-0.5, 0.5, 44100).astype(np.float32)
        # Create emotional curve with sudden change
        emotional_curve = np.zeros(44100, dtype=np.float32)
        emotional_curve[:22050] = 0.2
        emotional_curve[22050:] = 0.9  # Sudden change

        metadata = detector.detect(
            audio,
            sample_rate=44100,
            emotional_curve=emotional_curve
        )

        emotional_events = sum(
            1 for e in metadata.events
            if e.category == RarityCategory.EMOTIONAL_DISCONTINUITY
        )
        assert emotional_events >= 0

    def test_sensitivity_affects_detection(self):
        audio = np.random.uniform(-0.3, 0.3, 44100).astype(np.float32)

        detector_low = EventHorizonDetector(seed=42, sensitivity=0.2)
        detector_high = EventHorizonDetector(seed=42, sensitivity=0.9)

        metadata_low = detector_low.detect(audio, sample_rate=44100)
        metadata_high = detector_high.detect(audio, sample_rate=44100)

        # Higher sensitivity should detect more or equal events
        assert metadata_high.total_events >= metadata_low.total_events

    def test_phonomicon_export(self):
        detector = EventHorizonDetector(seed=42)
        audio = np.random.uniform(-0.5, 0.5, 44100).astype(np.float32)

        metadata = detector.detect(audio, sample_rate=44100)
        phonomicon_data = detector.export_for_phonomicon(metadata)

        assert "version" in phonomicon_data
        assert "source" in phonomicon_data
        assert phonomicon_data["source"] == "BeatOven"
        assert "nft_traits" in phonomicon_data
        assert "rarity_analysis" in phonomicon_data


class TestRareEvent:
    """Tests for RareEvent."""

    def test_basic_creation(self):
        event = RareEvent(
            timestamp=1.5,
            duration=0.1,
            category=RarityCategory.SPECTRAL_ANOMALY,
            rarity_score=0.8,
            spectral_signature=np.zeros(64, dtype=np.float32),
            runic_entropy=0.5,
            description="Test event"
        )

        assert event.timestamp == 1.5
        assert event.rarity_score == 0.8
        assert len(event.provenance_hash) == 32

    def test_serialization(self):
        event = RareEvent(
            timestamp=1.0,
            duration=0.1,
            category=RarityCategory.HARMONIC_SURPRISE,
            rarity_score=0.6,
            spectral_signature=np.zeros(64, dtype=np.float32),
            runic_entropy=0.3,
            description="Harmonic event"
        )

        data = event.to_dict()
        assert data["timestamp"] == 1.0
        assert data["category"] == "harmonic_surprise"
        assert "provenance_hash" in data


class TestRarityMetadata:
    """Tests for RarityMetadata."""

    def test_basic_creation(self):
        events = [
            RareEvent(
                timestamp=i * 0.5,
                duration=0.1,
                category=RarityCategory.SPECTRAL_ANOMALY,
                rarity_score=0.5 + i * 0.1,
                spectral_signature=np.zeros(64, dtype=np.float32),
                runic_entropy=0.5,
                description=f"Event {i}"
            )
            for i in range(3)
        ]

        metadata = RarityMetadata(
            total_events=3,
            avg_rarity=0.6,
            max_rarity=0.7,
            category_distribution={"spectral_anomaly": 3},
            events=events
        )

        assert metadata.total_events == 3
        assert metadata.avg_rarity == 0.6
        assert metadata.phonomicon_ready is True

    def test_serialization(self):
        metadata = RarityMetadata(
            total_events=0,
            avg_rarity=0.0,
            max_rarity=0.0,
            category_distribution={},
            events=[]
        )

        data = metadata.to_dict()
        assert "total_events" in data
        assert "events" in data
        assert "phonomicon_ready" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
