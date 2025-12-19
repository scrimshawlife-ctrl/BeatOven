from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional, Protocol, runtime_checkable

MediaKind = Literal["image", "video"]

@dataclass(frozen=True)
class ProviderStatus:
    name: str
    available: bool
    reason: Optional[str] = None
    version: Optional[str] = None

@runtime_checkable
class SemanticProvider(Protocol):
    name: str

    def status(self) -> ProviderStatus: ...
    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: ...
