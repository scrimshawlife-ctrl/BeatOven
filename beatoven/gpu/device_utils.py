"""
BeatOven Device Utilities

GPU/CPU device autodetection and management.
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class DeviceType(Enum):
    """Compute device types."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Silicon
    ROCM = "rocm"  # AMD


@dataclass
class DeviceInfo:
    """Information about a compute device."""
    device_type: DeviceType
    device_id: int
    name: str
    memory_total: int  # bytes
    memory_available: int  # bytes
    compute_capability: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_type": self.device_type.value,
            "device_id": self.device_id,
            "name": self.name,
            "memory_total": self.memory_total,
            "memory_available": self.memory_available,
            "compute_capability": self.compute_capability
        }


class DeviceManager:
    """
    Manages compute devices for BeatOven.

    Handles GPU/CPU detection, selection, and memory management.
    """

    def __init__(self, prefer_gpu: bool = True):
        """
        Initialize device manager.

        Args:
            prefer_gpu: Prefer GPU over CPU if available
        """
        self.prefer_gpu = prefer_gpu
        self._devices: List[DeviceInfo] = []
        self._current_device: Optional[DeviceInfo] = None
        self._torch_available = False
        self._jax_available = False

        self._detect_frameworks()
        self._detect_devices()

    def _detect_frameworks(self):
        """Detect available ML frameworks."""
        try:
            import torch
            self._torch_available = True
        except ImportError:
            self._torch_available = False

        try:
            import jax
            self._jax_available = True
        except ImportError:
            self._jax_available = False

    def _detect_devices(self):
        """Detect available compute devices."""
        # Always add CPU
        self._devices.append(DeviceInfo(
            device_type=DeviceType.CPU,
            device_id=0,
            name="CPU",
            memory_total=self._get_system_memory(),
            memory_available=self._get_available_memory()
        ))

        # Check for CUDA
        if self._torch_available:
            try:
                import torch
                if torch.cuda.is_available():
                    for i in range(torch.cuda.device_count()):
                        props = torch.cuda.get_device_properties(i)
                        self._devices.append(DeviceInfo(
                            device_type=DeviceType.CUDA,
                            device_id=i,
                            name=props.name,
                            memory_total=props.total_memory,
                            memory_available=props.total_memory,  # Simplified
                            compute_capability=f"{props.major}.{props.minor}"
                        ))

                # Check for MPS (Apple Silicon)
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self._devices.append(DeviceInfo(
                        device_type=DeviceType.MPS,
                        device_id=0,
                        name="Apple Silicon GPU",
                        memory_total=self._get_system_memory(),
                        memory_available=self._get_available_memory()
                    ))
            except Exception:
                pass

        # Set default device
        self._select_default_device()

    def _select_default_device(self):
        """Select default device based on preference."""
        if self.prefer_gpu:
            # Prefer CUDA > MPS > CPU
            for device in self._devices:
                if device.device_type == DeviceType.CUDA:
                    self._current_device = device
                    return

            for device in self._devices:
                if device.device_type == DeviceType.MPS:
                    self._current_device = device
                    return

        # Fall back to CPU
        self._current_device = self._devices[0]

    def _get_system_memory(self) -> int:
        """Get total system memory."""
        try:
            import psutil
            return psutil.virtual_memory().total
        except ImportError:
            return 8 * 1024 * 1024 * 1024  # Assume 8GB

    def _get_available_memory(self) -> int:
        """Get available system memory."""
        try:
            import psutil
            return psutil.virtual_memory().available
        except ImportError:
            return 4 * 1024 * 1024 * 1024  # Assume 4GB

    def get_device(self) -> DeviceInfo:
        """Get current compute device."""
        return self._current_device

    def get_device_string(self) -> str:
        """Get device string for PyTorch."""
        if self._current_device.device_type == DeviceType.CUDA:
            return f"cuda:{self._current_device.device_id}"
        elif self._current_device.device_type == DeviceType.MPS:
            return "mps"
        return "cpu"

    def set_device(self, device_type: DeviceType, device_id: int = 0) -> bool:
        """Set current device."""
        for device in self._devices:
            if device.device_type == device_type and device.device_id == device_id:
                self._current_device = device
                return True
        return False

    def list_devices(self) -> List[DeviceInfo]:
        """List all available devices."""
        return list(self._devices)

    def is_gpu_available(self) -> bool:
        """Check if any GPU is available."""
        return any(
            d.device_type in (DeviceType.CUDA, DeviceType.MPS, DeviceType.ROCM)
            for d in self._devices
        )

    def get_torch_device(self):
        """Get PyTorch device object."""
        if not self._torch_available:
            raise RuntimeError("PyTorch not available")

        import torch
        return torch.device(self.get_device_string())

    def to_device(self, tensor):
        """Move tensor to current device."""
        if not self._torch_available:
            return tensor

        import torch
        if isinstance(tensor, torch.Tensor):
            return tensor.to(self.get_torch_device())
        return tensor

    def synchronize(self):
        """Synchronize device (wait for GPU operations)."""
        if not self._torch_available:
            return

        import torch
        if self._current_device.device_type == DeviceType.CUDA:
            torch.cuda.synchronize()
        elif self._current_device.device_type == DeviceType.MPS:
            if hasattr(torch.mps, 'synchronize'):
                torch.mps.synchronize()


# Global instance
_device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """Get global device manager instance."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


def get_device() -> DeviceInfo:
    """Get current compute device."""
    return get_device_manager().get_device()


def is_gpu_available() -> bool:
    """Check if GPU is available."""
    return get_device_manager().is_gpu_available()


__all__ = [
    "DeviceManager", "DeviceInfo", "DeviceType",
    "get_device", "is_gpu_available", "get_device_manager"
]
