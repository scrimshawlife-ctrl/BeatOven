"""
BeatOven Model-Agnostic Inference Layer

Unified inference interface supporting Torch, JAX, and ONNX backends
with load-balancing, model registry, and compute-cost tracking.
"""

import hashlib
import time
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from enum import Enum
import numpy as np


class InferenceBackend(Enum):
    """Supported inference backends."""
    TORCH = "torch"
    JAX = "jax"
    ONNX = "onnx"
    NUMPY = "numpy"  # CPU-only fallback


class DeviceType(Enum):
    """Compute device types."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"
    TPU = "tpu"


@dataclass
class ComputeMetrics:
    """Compute cost metrics for a single operation."""
    module_name: str
    operation: str
    runtime_ms: float
    memory_bytes: int
    device: DeviceType
    backend: InferenceBackend
    seed_lineage: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "operation": self.operation,
            "runtime_ms": self.runtime_ms,
            "memory_bytes": self.memory_bytes,
            "device": self.device.value,
            "backend": self.backend.value,
            "seed_lineage": self.seed_lineage,
            "timestamp": self.timestamp
        }


@dataclass
class SeedLineage:
    """
    SEED-chain determinism tracker.

    Every module receives a seed derived from:
    base_seed → module_hash → output_seed → next_module
    """
    base_seed: int
    chain: List[Tuple[str, int, str]] = field(default_factory=list)

    def derive_seed(self, module_name: str, state_hash: str) -> int:
        """Derive next seed in the chain."""
        combined = f"{self.current_seed}:{module_name}:{state_hash}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        derived = int.from_bytes(hash_bytes[:8], 'big')
        self.chain.append((module_name, derived, state_hash))
        return derived

    @property
    def current_seed(self) -> int:
        """Get current seed (last in chain or base)."""
        if self.chain:
            return self.chain[-1][1]
        return self.base_seed

    def get_lineage_hash(self) -> str:
        """Get hash of entire lineage for provenance."""
        lineage_str = f"{self.base_seed}:" + ":".join(
            f"{name}_{seed}" for name, seed, _ in self.chain
        )
        return hashlib.sha256(lineage_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_seed": self.base_seed,
            "chain": [
                {"module": name, "seed": seed, "state_hash": state}
                for name, seed, state in self.chain
            ],
            "lineage_hash": self.get_lineage_hash()
        }


class ComputeLedger:
    """
    Compute-cost ledger for tracking all operations.

    Logs runtime, memory, device, backend, and seed lineage
    for every generative operation.
    """

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self._entries: List[ComputeMetrics] = []
        self._total_runtime_ms: float = 0.0
        self._total_memory_bytes: int = 0

    def log(self, metrics: ComputeMetrics):
        """Log compute metrics."""
        self._entries.append(metrics)
        self._total_runtime_ms += metrics.runtime_ms
        self._total_memory_bytes = max(self._total_memory_bytes, metrics.memory_bytes)

        # Rotate if needed
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]

    def get_summary(self) -> Dict[str, Any]:
        """Get ledger summary."""
        if not self._entries:
            return {"entries": 0, "total_runtime_ms": 0}

        by_module = {}
        by_backend = {}
        by_device = {}

        for entry in self._entries:
            by_module[entry.module_name] = by_module.get(entry.module_name, 0) + entry.runtime_ms
            by_backend[entry.backend.value] = by_backend.get(entry.backend.value, 0) + entry.runtime_ms
            by_device[entry.device.value] = by_device.get(entry.device.value, 0) + entry.runtime_ms

        return {
            "entries": len(self._entries),
            "total_runtime_ms": self._total_runtime_ms,
            "peak_memory_bytes": self._total_memory_bytes,
            "by_module": by_module,
            "by_backend": by_backend,
            "by_device": by_device
        }

    def get_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent entries."""
        return [e.to_dict() for e in self._entries[-limit:]]

    def clear(self):
        """Clear ledger."""
        self._entries.clear()
        self._total_runtime_ms = 0.0
        self._total_memory_bytes = 0


class InferenceEngine(ABC):
    """Abstract base for inference backends."""

    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> Any:
        """Load model from path."""
        pass

    @abstractmethod
    def infer(self, model: Any, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Run inference."""
        pass

    @abstractmethod
    def get_device(self) -> DeviceType:
        """Get current device."""
        pass

    @abstractmethod
    def get_backend(self) -> InferenceBackend:
        """Get backend type."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available."""
        pass


class TorchEngine(InferenceEngine):
    """PyTorch inference backend."""

    def __init__(self, device: Optional[str] = None):
        self._device = device
        self._torch = None
        self._available = False
        self._init_torch()

    def _init_torch(self):
        try:
            import torch
            self._torch = torch
            self._available = True

            if self._device is None:
                if torch.cuda.is_available():
                    self._device = "cuda"
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self._device = "mps"
                else:
                    self._device = "cpu"
        except ImportError:
            self._available = False

    def load_model(self, model_path: str, **kwargs) -> Any:
        if not self._available:
            raise RuntimeError("PyTorch not available")
        model = self._torch.load(model_path, map_location=self._device)
        model.eval()
        return model

    def infer(self, model: Any, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self._available:
            raise RuntimeError("PyTorch not available")

        with self._torch.no_grad():
            torch_inputs = {
                k: self._torch.from_numpy(v).to(self._device)
                for k, v in inputs.items()
            }
            outputs = model(**torch_inputs)

            if isinstance(outputs, self._torch.Tensor):
                return {"output": outputs.cpu().numpy()}
            elif isinstance(outputs, dict):
                return {k: v.cpu().numpy() for k, v in outputs.items()}
            else:
                return {"output": outputs}

    def get_device(self) -> DeviceType:
        if self._device == "cuda":
            return DeviceType.CUDA
        elif self._device == "mps":
            return DeviceType.MPS
        return DeviceType.CPU

    def get_backend(self) -> InferenceBackend:
        return InferenceBackend.TORCH

    def is_available(self) -> bool:
        return self._available


class JAXEngine(InferenceEngine):
    """JAX inference backend."""

    def __init__(self):
        self._jax = None
        self._available = False
        self._init_jax()

    def _init_jax(self):
        try:
            import jax
            import jax.numpy as jnp
            self._jax = jax
            self._jnp = jnp
            self._available = True
        except ImportError:
            self._available = False

    def load_model(self, model_path: str, **kwargs) -> Any:
        if not self._available:
            raise RuntimeError("JAX not available")
        import pickle
        with open(model_path, 'rb') as f:
            return pickle.load(f)

    def infer(self, model: Any, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self._available:
            raise RuntimeError("JAX not available")

        jax_inputs = {k: self._jnp.array(v) for k, v in inputs.items()}

        if callable(model):
            outputs = model(**jax_inputs)
        else:
            outputs = model

        if isinstance(outputs, self._jnp.ndarray):
            return {"output": np.array(outputs)}
        elif isinstance(outputs, dict):
            return {k: np.array(v) for k, v in outputs.items()}
        return {"output": outputs}

    def get_device(self) -> DeviceType:
        if self._available:
            devices = self._jax.devices()
            if any('gpu' in str(d).lower() for d in devices):
                return DeviceType.CUDA
            if any('tpu' in str(d).lower() for d in devices):
                return DeviceType.TPU
        return DeviceType.CPU

    def get_backend(self) -> InferenceBackend:
        return InferenceBackend.JAX

    def is_available(self) -> bool:
        return self._available


class ONNXEngine(InferenceEngine):
    """ONNX Runtime inference backend."""

    def __init__(self, providers: Optional[List[str]] = None):
        self._ort = None
        self._available = False
        self._providers = providers
        self._init_onnx()

    def _init_onnx(self):
        try:
            import onnxruntime as ort
            self._ort = ort
            self._available = True

            if self._providers is None:
                available = ort.get_available_providers()
                if 'CUDAExecutionProvider' in available:
                    self._providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                elif 'CoreMLExecutionProvider' in available:
                    self._providers = ['CoreMLExecutionProvider', 'CPUExecutionProvider']
                else:
                    self._providers = ['CPUExecutionProvider']
        except ImportError:
            self._available = False

    def load_model(self, model_path: str, **kwargs) -> Any:
        if not self._available:
            raise RuntimeError("ONNX Runtime not available")
        return self._ort.InferenceSession(model_path, providers=self._providers)

    def infer(self, model: Any, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if not self._available:
            raise RuntimeError("ONNX Runtime not available")

        input_names = [i.name for i in model.get_inputs()]
        output_names = [o.name for o in model.get_outputs()]

        ort_inputs = {name: inputs.get(name) for name in input_names if name in inputs}
        outputs = model.run(output_names, ort_inputs)

        return {name: output for name, output in zip(output_names, outputs)}

    def get_device(self) -> DeviceType:
        if self._providers and 'CUDAExecutionProvider' in self._providers:
            return DeviceType.CUDA
        return DeviceType.CPU

    def get_backend(self) -> InferenceBackend:
        return InferenceBackend.ONNX

    def is_available(self) -> bool:
        return self._available


class NumpyEngine(InferenceEngine):
    """NumPy fallback inference (CPU-only)."""

    def load_model(self, model_path: str, **kwargs) -> Any:
        return np.load(model_path, allow_pickle=True)

    def infer(self, model: Any, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if callable(model):
            return {"output": model(**inputs)}
        return {"output": model}

    def get_device(self) -> DeviceType:
        return DeviceType.CPU

    def get_backend(self) -> InferenceBackend:
        return InferenceBackend.NUMPY

    def is_available(self) -> bool:
        return True


@dataclass
class ModelSpec:
    """Model specification for registry."""
    name: str
    path: str
    backend: InferenceBackend
    input_shapes: Dict[str, Tuple[int, ...]]
    output_shapes: Dict[str, Tuple[int, ...]]
    description: str = ""


class ModelRegistry:
    """Registry for managing models across backends."""

    def __init__(self):
        self._models: Dict[str, ModelSpec] = {}
        self._loaded: Dict[str, Any] = {}

    def register(self, spec: ModelSpec):
        """Register a model."""
        self._models[spec.name] = spec

    def unregister(self, name: str):
        """Unregister a model."""
        if name in self._models:
            del self._models[name]
        if name in self._loaded:
            del self._loaded[name]

    def get_spec(self, name: str) -> Optional[ModelSpec]:
        """Get model specification."""
        return self._models.get(name)

    def list_models(self) -> List[str]:
        """List registered models."""
        return list(self._models.keys())

    def is_loaded(self, name: str) -> bool:
        """Check if model is loaded."""
        return name in self._loaded

    def set_loaded(self, name: str, model: Any):
        """Mark model as loaded."""
        self._loaded[name] = model

    def get_loaded(self, name: str) -> Optional[Any]:
        """Get loaded model."""
        return self._loaded.get(name)


class UnifiedInference:
    """
    Unified inference interface for BeatOven.

    Provides model-agnostic inference with automatic backend selection,
    load balancing, seed-chain tracking, and compute-cost logging.
    """

    def __init__(
        self,
        preferred_backend: Optional[InferenceBackend] = None,
        enable_ledger: bool = True
    ):
        self.preferred_backend = preferred_backend
        self.registry = ModelRegistry()
        self.ledger = ComputeLedger() if enable_ledger else None
        self._seed_lineage: Optional[SeedLineage] = None

        # Initialize engines
        self._engines: Dict[InferenceBackend, InferenceEngine] = {}
        self._init_engines()

    def _init_engines(self):
        """Initialize available engines."""
        self._engines[InferenceBackend.TORCH] = TorchEngine()
        self._engines[InferenceBackend.JAX] = JAXEngine()
        self._engines[InferenceBackend.ONNX] = ONNXEngine()
        self._engines[InferenceBackend.NUMPY] = NumpyEngine()

    def get_available_backends(self) -> List[InferenceBackend]:
        """Get list of available backends."""
        return [
            backend for backend, engine in self._engines.items()
            if engine.is_available()
        ]

    def select_backend(self, preferred: Optional[InferenceBackend] = None) -> InferenceBackend:
        """Select best available backend."""
        if preferred and self._engines[preferred].is_available():
            return preferred

        if self.preferred_backend and self._engines[self.preferred_backend].is_available():
            return self.preferred_backend

        # Priority: TORCH > JAX > ONNX > NUMPY
        for backend in [InferenceBackend.TORCH, InferenceBackend.JAX,
                       InferenceBackend.ONNX, InferenceBackend.NUMPY]:
            if self._engines[backend].is_available():
                return backend

        return InferenceBackend.NUMPY

    def init_seed_lineage(self, base_seed: int) -> SeedLineage:
        """Initialize seed lineage chain."""
        self._seed_lineage = SeedLineage(base_seed=base_seed)
        return self._seed_lineage

    def get_seed_lineage(self) -> Optional[SeedLineage]:
        """Get current seed lineage."""
        return self._seed_lineage

    def derive_module_seed(self, module_name: str, state: Any) -> int:
        """Derive seed for a module."""
        if self._seed_lineage is None:
            raise RuntimeError("Seed lineage not initialized")

        # Hash state
        if isinstance(state, np.ndarray):
            state_hash = hashlib.sha256(state.tobytes()).hexdigest()[:16]
        elif isinstance(state, dict):
            import json
            state_hash = hashlib.sha256(
                json.dumps(state, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
        else:
            state_hash = hashlib.sha256(str(state).encode()).hexdigest()[:16]

        return self._seed_lineage.derive_seed(module_name, state_hash)

    def load_model(
        self,
        name: str,
        path: str,
        backend: Optional[InferenceBackend] = None,
        **kwargs
    ) -> Any:
        """Load a model."""
        backend = backend or self.select_backend()
        engine = self._engines[backend]

        model = engine.load_model(path, **kwargs)
        self.registry.set_loaded(name, model)

        return model

    def infer(
        self,
        model_or_name: Union[str, Any],
        inputs: Dict[str, np.ndarray],
        backend: Optional[InferenceBackend] = None,
        module_name: str = "inference"
    ) -> Dict[str, np.ndarray]:
        """
        Run inference with compute tracking.

        Args:
            model_or_name: Model object or registered name
            inputs: Input tensors
            backend: Preferred backend
            module_name: Module name for logging

        Returns:
            Output tensors
        """
        backend = backend or self.select_backend()
        engine = self._engines[backend]

        # Get model
        if isinstance(model_or_name, str):
            model = self.registry.get_loaded(model_or_name)
            if model is None:
                raise ValueError(f"Model {model_or_name} not loaded")
        else:
            model = model_or_name

        # Track compute
        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Run inference
        outputs = engine.infer(model, inputs)

        # Log metrics
        if self.ledger:
            runtime_ms = (time.time() - start_time) * 1000
            memory_bytes = self._get_memory_usage() - start_memory

            metrics = ComputeMetrics(
                module_name=module_name,
                operation="inference",
                runtime_ms=runtime_ms,
                memory_bytes=max(0, memory_bytes),
                device=engine.get_device(),
                backend=engine.get_backend(),
                seed_lineage=self._seed_lineage.get_lineage_hash() if self._seed_lineage else ""
            )
            self.ledger.log(metrics)

        return outputs

    def _get_memory_usage(self) -> int:
        """Get current memory usage."""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except ImportError:
            return 0

    def get_compute_summary(self) -> Dict[str, Any]:
        """Get compute ledger summary."""
        if self.ledger:
            return self.ledger.get_summary()
        return {}


# Global instance
_inference: Optional[UnifiedInference] = None


def get_inference() -> UnifiedInference:
    """Get global inference instance."""
    global _inference
    if _inference is None:
        _inference = UnifiedInference()
    return _inference


__all__ = [
    "UnifiedInference", "InferenceBackend", "DeviceType",
    "InferenceEngine", "TorchEngine", "JAXEngine", "ONNXEngine", "NumpyEngine",
    "ModelRegistry", "ModelSpec", "SeedLineage", "ComputeLedger", "ComputeMetrics",
    "get_inference"
]
