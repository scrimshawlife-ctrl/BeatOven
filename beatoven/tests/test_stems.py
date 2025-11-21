"""Tests for StemGenerator."""

import numpy as np
import pytest
from pathlib import Path
import tempfile
from beatoven.core.stems import (
    StemGenerator, Stem, StemMetadata, StemType,
    ExportFormat, MelSpectrogram
)


class TestStem:
    """Tests for Stem class."""

    def test_basic_creation(self):
        samples = np.random.uniform(-1, 1, 88200).astype(np.float32)
        stem = Stem(
            stem_type=StemType.DRUMS,
            samples=samples,
            sample_rate=44100,
            channels=2
        )

        assert stem.stem_type == StemType.DRUMS
        assert len(stem.samples) == 88200
        assert stem.metadata is not None

    def test_metadata_computation(self):
        samples = np.random.uniform(-1, 1, 44100).astype(np.float32)
        stem = Stem(stem_type=StemType.BASS, samples=samples)

        assert stem.metadata.stem_type == StemType.BASS
        assert stem.metadata.peak_amplitude > 0
        assert stem.metadata.rms_level > 0
        assert len(stem.metadata.provenance_hash) == 64

    def test_to_stereo(self):
        samples = np.random.uniform(-1, 1, 1000).astype(np.float32)
        stem = Stem(stem_type=StemType.LEADS, samples=samples, channels=1)
        stereo = stem.to_stereo()

        assert stereo.channels == 2


class TestStemGenerator:
    """Tests for StemGenerator."""

    def test_basic_generation(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(duration=4.0)

        assert len(stems) > 0
        assert StemType.DRUMS in stems or StemType.FULL_MIX in stems

    def test_specific_stem_types(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=4.0,
            stem_types=[StemType.DRUMS, StemType.BASS]
        )

        assert StemType.DRUMS in stems
        assert StemType.BASS in stems
        assert StemType.LEADS not in stems

    def test_full_mix_generation(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=4.0,
            stem_types=[StemType.DRUMS, StemType.BASS, StemType.FULL_MIX]
        )

        assert StemType.FULL_MIX in stems
        full_mix = stems[StemType.FULL_MIX]
        assert len(full_mix.samples) > 0

    def test_determinism(self):
        gen1 = StemGenerator(seed=123)
        gen2 = StemGenerator(seed=123)

        stems1 = gen1.generate_stems(duration=2.0)
        stems2 = gen2.generate_stems(duration=2.0)

        for stem_type in stems1:
            if stem_type in stems2:
                np.testing.assert_array_equal(
                    stems1[stem_type].samples,
                    stems2[stem_type].samples
                )

    def test_wav_export(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=1.0,
            stem_types=[StemType.DRUMS]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_stem.wav"
            provenance = generator.export_wav(stems[StemType.DRUMS], path)

            assert path.exists()
            assert len(provenance) == 64

    def test_export_all(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=1.0,
            stem_types=[StemType.DRUMS, StemType.BASS]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            hashes = generator.export_all(stems, Path(tmpdir), prefix="test")

            assert len(hashes) == len(stems)
            for stem_type in stems:
                expected_file = Path(tmpdir) / f"test_{stem_type.value}.wav"
                assert expected_file.exists()


class TestMelSpectrogram:
    """Tests for MelSpectrogram computation."""

    def test_basic_computation(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=1.0,
            stem_types=[StemType.DRUMS]
        )

        mel = generator.compute_mel_spectrogram(stems[StemType.DRUMS])

        assert isinstance(mel, MelSpectrogram)
        assert mel.n_mels == 128
        assert mel.data.shape[0] == 128

    def test_custom_parameters(self):
        generator = StemGenerator(seed=42)
        stems = generator.generate_stems(
            duration=1.0,
            stem_types=[StemType.BASS]
        )

        mel = generator.compute_mel_spectrogram(
            stems[StemType.BASS],
            n_mels=64,
            n_fft=1024
        )

        assert mel.n_mels == 64
        assert mel.n_fft == 1024
        assert mel.data.shape[0] == 64


class TestStemType:
    """Tests for StemType enum."""

    def test_all_types(self):
        types = list(StemType)
        assert StemType.DRUMS in types
        assert StemType.BASS in types
        assert StemType.LEADS in types
        assert StemType.MIDS in types
        assert StemType.PADS in types
        assert StemType.ATMOS in types
        assert StemType.FULL_MIX in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
