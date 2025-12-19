from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .providers.base import MediaKind, ProviderStatus, SemanticProvider

@dataclass
class SemanticEngine:
    """
    Runs every installed provider that reports available=True.
    Returns:
      semantic: merged dict keyed by provider name
      provider_status: list with availability reasons (for UI)
    """
    providers: List[SemanticProvider] = field(default_factory=list)

    def capabilities(self) -> Dict[str, Any]:
        sts = [p.status().__dict__ for p in self.providers]
        return {
            "providers": sts,
            "available": [s["name"] for s in sts if s["available"]],
            "unavailable": [s for s in sts if not s["available"]],
        }

    def analyze(self, *, kind: MediaKind, path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for p in self.providers:
            st = p.status()
            if not st.available:
                continue
            try:
                result = p.analyze(kind=kind, path=path, context=context)
                if result:
                    out[p.name] = result
            except Exception as e:
                # Log but don't crash entire analysis
                out[p.name] = {"error": str(e)}
        return out
