"""
BeatOven Echotome Hooks

Prepares audio for steganographic salting and per-stem salt injection.
Provides hooks for future Echotome cryptographic integration.
"""

import hashlib
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class SaltPattern(Enum):
    """Steganographic salt patterns."""
    LSB = "lsb"  # Least significant bit
    PHASE = "phase"  # Phase modulation
    SPECTRAL = "spectral"  # Spectral embedding
    TEMPORAL = "temporal"  # Temporal micro-shifts
    AMPLITUDE = "amplitude"  # Amplitude modulation


@dataclass
class SaltConfig:
    """Configuration for salt injection."""
    pattern: SaltPattern
    strength: float = 0.001  # Salt strength (very subtle)
    density: float = 0.1  # Salt density (10% of samples)
    seed: int = 0
    checksum_interval: int = 1024  # Samples between checksums

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern.value,
            "strength": self.strength,
            "density": self.density,
            "seed": self.seed,
            "checksum_interval": self.checksum_interval
        }


@dataclass
class SaltMetadata:
    """Metadata for salted audio."""
    stem_name: str
    salt_config: SaltConfig
    injection_points: int
    verification_hash: str
    echotome_ready: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stem_name": self.stem_name,
            "salt_config": self.salt_config.to_dict(),
            "injection_points": self.injection_points,
            "verification_hash": self.verification_hash,
            "echotome_ready": self.echotome_ready
        }


@dataclass
class EchotomePackage:
    """Complete Echotome-ready package."""
    stems: Dict[str, np.ndarray]
    metadata: Dict[str, SaltMetadata]
    master_hash: str
    provenance_chain: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stem_names": list(self.stems.keys()),
            "metadata": {k: v.to_dict() for k, v in self.metadata.items()},
            "master_hash": self.master_hash,
            "provenance_chain": self.provenance_chain
        }


class EchotomeHooks:
    """
    Echotome integration hooks for steganographic preparation.

    Provides infrastructure for future cryptographic audio watermarking
    and ownership verification via the Echotome system.
    """

    def __init__(
        self,
        master_seed: int = 0,
        default_pattern: SaltPattern = SaltPattern.LSB
    ):
        """
        Initialize Echotome hooks.

        Args:
            master_seed: Master seed for deterministic salt generation
            default_pattern: Default salt pattern
        """
        self.master_seed = master_seed
        self.default_pattern = default_pattern
        self._rng = np.random.default_rng(master_seed)
        self._provenance_chain: List[str] = []

    def prepare_stem(
        self,
        stem_name: str,
        audio: np.ndarray,
        config: Optional[SaltConfig] = None
    ) -> Tuple[np.ndarray, SaltMetadata]:
        """
        Prepare a stem for Echotome integration.

        Args:
            stem_name: Name of the stem
            audio: Audio samples
            config: Salt configuration (uses defaults if None)

        Returns:
            Tuple of (salted audio, metadata)
        """
        if config is None:
            config = SaltConfig(
                pattern=self.default_pattern,
                seed=self._derive_stem_seed(stem_name)
            )

        # Apply salt based on pattern
        if config.pattern == SaltPattern.LSB:
            salted, points = self._apply_lsb_salt(audio, config)
        elif config.pattern == SaltPattern.PHASE:
            salted, points = self._apply_phase_salt(audio, config)
        elif config.pattern == SaltPattern.SPECTRAL:
            salted, points = self._apply_spectral_salt(audio, config)
        elif config.pattern == SaltPattern.TEMPORAL:
            salted, points = self._apply_temporal_salt(audio, config)
        elif config.pattern == SaltPattern.AMPLITUDE:
            salted, points = self._apply_amplitude_salt(audio, config)
        else:
            salted, points = audio.copy(), 0

        # Generate verification hash
        verification_hash = self._compute_verification_hash(salted, config)

        # Update provenance chain
        self._provenance_chain.append(verification_hash)

        metadata = SaltMetadata(
            stem_name=stem_name,
            salt_config=config,
            injection_points=points,
            verification_hash=verification_hash
        )

        return salted, metadata

    def prepare_package(
        self,
        stems: Dict[str, np.ndarray],
        configs: Optional[Dict[str, SaltConfig]] = None
    ) -> EchotomePackage:
        """
        Prepare complete package of stems for Echotome.

        Args:
            stems: Dictionary of stem_name -> audio
            configs: Optional per-stem configurations

        Returns:
            EchotomePackage ready for integration
        """
        if configs is None:
            configs = {}

        salted_stems = {}
        metadata = {}

        for stem_name, audio in stems.items():
            config = configs.get(stem_name)
            salted, meta = self.prepare_stem(stem_name, audio, config)
            salted_stems[stem_name] = salted
            metadata[stem_name] = meta

        # Compute master hash
        master_hash = self._compute_master_hash(metadata)

        return EchotomePackage(
            stems=salted_stems,
            metadata=metadata,
            master_hash=master_hash,
            provenance_chain=list(self._provenance_chain)
        )

    def verify_stem(
        self,
        audio: np.ndarray,
        metadata: SaltMetadata
    ) -> bool:
        """
        Verify stem integrity against metadata.

        Args:
            audio: Audio samples to verify
            metadata: Expected metadata

        Returns:
            True if verification passes
        """
        computed_hash = self._compute_verification_hash(
            audio, metadata.salt_config
        )
        return computed_hash == metadata.verification_hash

    def extract_provenance(
        self,
        package: EchotomePackage
    ) -> Dict[str, Any]:
        """
        Extract provenance information from package.

        Returns:
            Provenance dictionary for external systems
        """
        return {
            "master_hash": package.master_hash,
            "stem_count": len(package.stems),
            "provenance_chain": package.provenance_chain,
            "stem_hashes": {
                name: meta.verification_hash
                for name, meta in package.metadata.items()
            }
        }

    def _derive_stem_seed(self, stem_name: str) -> int:
        """Derive deterministic seed for stem."""
        combined = f"{self.master_seed}:{stem_name}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        return int.from_bytes(hash_bytes[:4], 'big')

    def _apply_lsb_salt(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> Tuple[np.ndarray, int]:
        """Apply LSB salt pattern."""
        salted = audio.copy()
        rng = np.random.default_rng(config.seed)

        # Select injection points
        n_points = int(len(audio) * config.density)
        points = rng.choice(len(audio), n_points, replace=False)

        # Generate salt values
        salt_bits = rng.integers(0, 2, n_points)

        # Apply to float samples (simulated LSB)
        for i, point in enumerate(points):
            tiny_mod = config.strength * (2 * salt_bits[i] - 1)
            salted[point] += tiny_mod

        return salted.astype(np.float32), n_points

    def _apply_phase_salt(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> Tuple[np.ndarray, int]:
        """Apply phase modulation salt."""
        # FFT-based phase modification
        spectrum = np.fft.rfft(audio)
        rng = np.random.default_rng(config.seed)

        n_points = int(len(spectrum) * config.density)
        points = rng.choice(len(spectrum), n_points, replace=False)

        for point in points:
            phase_mod = rng.uniform(-np.pi * config.strength, np.pi * config.strength)
            spectrum[point] *= np.exp(1j * phase_mod)

        salted = np.fft.irfft(spectrum, len(audio))
        return salted.astype(np.float32), n_points

    def _apply_spectral_salt(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> Tuple[np.ndarray, int]:
        """Apply spectral embedding salt."""
        spectrum = np.fft.rfft(audio)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)

        rng = np.random.default_rng(config.seed)
        n_points = int(len(magnitude) * config.density)
        points = rng.choice(len(magnitude), n_points, replace=False)

        for point in points:
            magnitude[point] *= (1 + config.strength * rng.uniform(-1, 1))

        spectrum = magnitude * np.exp(1j * phase)
        salted = np.fft.irfft(spectrum, len(audio))
        return salted.astype(np.float32), n_points

    def _apply_temporal_salt(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> Tuple[np.ndarray, int]:
        """Apply temporal micro-shift salt."""
        salted = audio.copy()
        rng = np.random.default_rng(config.seed)

        n_points = int(len(audio) * config.density)
        points = sorted(rng.choice(len(audio) - 1, n_points, replace=False))

        for point in points:
            # Micro-swap adjacent samples
            if rng.random() < 0.5:
                blend = config.strength
                temp = salted[point]
                salted[point] = salted[point] * (1 - blend) + salted[point + 1] * blend
                salted[point + 1] = salted[point + 1] * (1 - blend) + temp * blend

        return salted.astype(np.float32), n_points

    def _apply_amplitude_salt(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> Tuple[np.ndarray, int]:
        """Apply amplitude modulation salt."""
        salted = audio.copy()
        rng = np.random.default_rng(config.seed)

        n_points = int(len(audio) * config.density)
        points = rng.choice(len(audio), n_points, replace=False)

        for point in points:
            mod = 1 + config.strength * rng.uniform(-1, 1)
            salted[point] *= mod

        return salted.astype(np.float32), n_points

    def _compute_verification_hash(
        self,
        audio: np.ndarray,
        config: SaltConfig
    ) -> str:
        """Compute verification hash for salted audio."""
        # Sample at checksum intervals
        checksums = []
        for i in range(0, len(audio), config.checksum_interval):
            chunk = audio[i:i + config.checksum_interval]
            chunk_hash = hashlib.md5(chunk.tobytes()).hexdigest()[:8]
            checksums.append(chunk_hash)

        combined = ":".join(checksums)
        return hashlib.sha256(combined.encode()).hexdigest()

    def _compute_master_hash(
        self,
        metadata: Dict[str, SaltMetadata]
    ) -> str:
        """Compute master hash from all stem metadata."""
        hashes = sorted([m.verification_hash for m in metadata.values()])
        combined = ":".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()


__all__ = [
    "EchotomeHooks", "SaltConfig", "SaltMetadata",
    "EchotomePackage", "SaltPattern"
]
