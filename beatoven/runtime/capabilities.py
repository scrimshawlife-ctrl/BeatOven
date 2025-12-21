"""Capability policy definitions for runtime execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CapabilityPolicy:
    filesystem_paths: List[str] = field(default_factory=list)
    network_domains: List[str] = field(default_factory=list)
    clock_policy: str = "none"
    randomness_policy: str = "seed_required"

    def allows_filesystem(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.filesystem_paths)

    def allows_network(self, domain: str) -> bool:
        return domain in self.network_domains


DEFAULT_POLICY = CapabilityPolicy()
