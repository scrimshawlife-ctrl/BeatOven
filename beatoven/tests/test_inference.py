"""Tests for inference layer and SEED-chain determinism."""

import numpy as np
import pytest
from beatoven.core.inference import (
    UnifiedInference, InferenceBackend, DeviceType,
    SeedLineage, ComputeLedger, ComputeMetrics,
    ModelRegistry, ModelSpec, NumpyEngine,
    get_inference
)


class TestSeedLineage:
    """Tests for SEED-chain determinism."""

    def test_basic_lineage(self):
        lineage = SeedLineage(base_seed=12345)
        assert lineage.base_seed == 12345
        assert lineage.current_seed == 12345

    def test_derive_seed(self):
        lineage = SeedLineage(base_seed=42)

        seed1 = lineage.derive_seed("input", "state_hash_1")
        assert seed1 != 42
        assert lineage.current_seed == seed1

        seed2 = lineage.derive_seed("rhythm", "state_hash_2")
        assert seed2 != seed1
        assert lineage.current_seed == seed2

    def test_determinism(self):
        """Same inputs produce same seed lineage."""
        lineage1 = SeedLineage(base_seed=42)
        lineage1.derive_seed("input", "state1")
        lineage1.derive_seed("rhythm", "state2")

        lineage2 = SeedLineage(base_seed=42)
        lineage2.derive_seed("input", "state1")
        lineage2.derive_seed("rhythm", "state2")

        assert lineage1.get_lineage_hash() == lineage2.get_lineage_hash()

    def test_different_seeds(self):
        """Different base seeds produce different lineages."""
        lineage1 = SeedLineage(base_seed=42)
        lineage1.derive_seed("input", "state")

        lineage2 = SeedLineage(base_seed=43)
        lineage2.derive_seed("input", "state")

        assert lineage1.get_lineage_hash() != lineage2.get_lineage_hash()

    def test_serialization(self):
        lineage = SeedLineage(base_seed=42)
        lineage.derive_seed("module1", "hash1")
        lineage.derive_seed("module2", "hash2")

        data = lineage.to_dict()
        assert data["base_seed"] == 42
        assert len(data["chain"]) == 2
        assert "lineage_hash" in data


class TestComputeLedger:
    """Tests for compute-cost tracking."""

    def test_basic_logging(self):
        ledger = ComputeLedger()

        metrics = ComputeMetrics(
            module_name="test",
            operation="inference",
            runtime_ms=100.5,
            memory_bytes=1024 * 1024,
            device=DeviceType.CPU,
            backend=InferenceBackend.NUMPY,
            seed_lineage="hash123"
        )

        ledger.log(metrics)
        assert len(ledger.get_entries()) == 1

    def test_summary(self):
        ledger = ComputeLedger()

        for i in range(5):
            metrics = ComputeMetrics(
                module_name=f"module_{i % 2}",
                operation="op",
                runtime_ms=10.0,
                memory_bytes=1000,
                device=DeviceType.CPU,
                backend=InferenceBackend.NUMPY,
                seed_lineage=""
            )
            ledger.log(metrics)

        summary = ledger.get_summary()
        assert summary["entries"] == 5
        assert summary["total_runtime_ms"] == 50.0
        assert "by_module" in summary

    def test_max_entries(self):
        ledger = ComputeLedger(max_entries=10)

        for i in range(20):
            metrics = ComputeMetrics(
                module_name="test",
                operation="op",
                runtime_ms=1.0,
                memory_bytes=100,
                device=DeviceType.CPU,
                backend=InferenceBackend.NUMPY,
                seed_lineage=""
            )
            ledger.log(metrics)

        entries = ledger.get_entries()
        assert len(entries) == 10


class TestModelRegistry:
    """Tests for model registry."""

    def test_register_model(self):
        registry = ModelRegistry()

        spec = ModelSpec(
            name="test_model",
            path="/path/to/model.onnx",
            backend=InferenceBackend.ONNX,
            input_shapes={"input": (1, 128)},
            output_shapes={"output": (1, 64)}
        )

        registry.register(spec)
        assert "test_model" in registry.list_models()

    def test_get_spec(self):
        registry = ModelRegistry()

        spec = ModelSpec(
            name="my_model",
            path="/path",
            backend=InferenceBackend.TORCH,
            input_shapes={},
            output_shapes={}
        )
        registry.register(spec)

        retrieved = registry.get_spec("my_model")
        assert retrieved.name == "my_model"
        assert retrieved.backend == InferenceBackend.TORCH


class TestNumpyEngine:
    """Tests for NumPy fallback engine."""

    def test_availability(self):
        engine = NumpyEngine()
        assert engine.is_available()

    def test_device(self):
        engine = NumpyEngine()
        assert engine.get_device() == DeviceType.CPU

    def test_backend(self):
        engine = NumpyEngine()
        assert engine.get_backend() == InferenceBackend.NUMPY


class TestUnifiedInference:
    """Tests for unified inference interface."""

    def test_initialization(self):
        inference = UnifiedInference()
        assert inference.registry is not None
        assert inference.ledger is not None

    def test_available_backends(self):
        inference = UnifiedInference()
        backends = inference.get_available_backends()

        # NumPy should always be available
        assert InferenceBackend.NUMPY in backends

    def test_select_backend(self):
        inference = UnifiedInference()
        backend = inference.select_backend()

        # Should return some backend
        assert backend in InferenceBackend

    def test_seed_lineage_init(self):
        inference = UnifiedInference()
        lineage = inference.init_seed_lineage(base_seed=42)

        assert lineage is not None
        assert lineage.base_seed == 42
        assert inference.get_seed_lineage() is lineage

    def test_derive_module_seed(self):
        inference = UnifiedInference()
        inference.init_seed_lineage(base_seed=42)

        state = np.array([1.0, 2.0, 3.0])
        seed1 = inference.derive_module_seed("input", state)

        assert seed1 != 42
        assert isinstance(seed1, int)

    def test_derive_module_seed_dict(self):
        inference = UnifiedInference()
        inference.init_seed_lineage(base_seed=42)

        state = {"resonance": 0.5, "tension": 0.3}
        seed = inference.derive_module_seed("translator", state)

        assert isinstance(seed, int)

    def test_global_instance(self):
        inference = get_inference()
        assert inference is not None
        assert inference is get_inference()


class TestInferenceIntegration:
    """Integration tests for inference system."""

    def test_full_pipeline(self):
        inference = UnifiedInference(enable_ledger=True)

        # Initialize seed lineage
        lineage = inference.init_seed_lineage(base_seed=12345)

        # Simulate module progression
        input_state = np.random.randn(128).astype(np.float32)
        input_seed = inference.derive_module_seed("input", input_state)

        rhythm_state = {"density": 0.5, "tension": 0.4}
        rhythm_seed = inference.derive_module_seed("rhythm", rhythm_state)

        harmony_state = np.random.randn(64).astype(np.float32)
        harmony_seed = inference.derive_module_seed("harmony", harmony_state)

        # Verify lineage
        assert len(lineage.chain) == 3
        assert lineage.chain[0][0] == "input"
        assert lineage.chain[1][0] == "rhythm"
        assert lineage.chain[2][0] == "harmony"

    def test_deterministic_pipeline(self):
        """Same inputs produce same seed chain."""
        def run_pipeline(base_seed):
            inference = UnifiedInference()
            inference.init_seed_lineage(base_seed)

            inference.derive_module_seed("input", {"intent": "test"})
            inference.derive_module_seed("rhythm", {"density": 0.5})
            inference.derive_module_seed("harmony", {"tension": 0.3})

            return inference.get_seed_lineage().get_lineage_hash()

        hash1 = run_pipeline(42)
        hash2 = run_pipeline(42)
        hash3 = run_pipeline(43)

        assert hash1 == hash2
        assert hash1 != hash3


class TestComputeMetrics:
    """Tests for compute metrics."""

    def test_serialization(self):
        metrics = ComputeMetrics(
            module_name="test",
            operation="inference",
            runtime_ms=50.5,
            memory_bytes=1024,
            device=DeviceType.CUDA,
            backend=InferenceBackend.TORCH,
            seed_lineage="abc123"
        )

        data = metrics.to_dict()
        assert data["module_name"] == "test"
        assert data["runtime_ms"] == 50.5
        assert data["device"] == "cuda"
        assert data["backend"] == "torch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
