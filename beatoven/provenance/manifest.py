"""Provenance manifest helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict


def stable_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(obj: Any) -> str:
    return hashlib.sha256(stable_dumps(obj).encode("utf-8")).hexdigest()


def compute_code_hash() -> str:
    """Compute code hash from git commit or tracked files."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        root = Path(__file__).resolve().parents[2]
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        files = [root / line for line in tracked.stdout.splitlines() if line]
        digest = hashlib.sha256()
        for path in sorted(files):
            if path.is_file():
                digest.update(path.read_bytes())
        return digest.hexdigest()


def build_manifest(
    rune_id: str,
    input_payload: Dict[str, Any],
    output_payload: Dict[str, Any],
    seed: int,
    capabilities: Dict[str, Any],
) -> Dict[str, Any]:
    input_hash = stable_hash(input_payload)
    output_hash = stable_hash(output_payload)
    manifest = {
        "rune_id": rune_id,
        "code_hash": compute_code_hash(),
        "config_hash": stable_hash(capabilities),
        "input_hash": input_hash,
        "output_hash": output_hash,
        "seed": seed,
        "timestamp_policy": "none",
    }
    manifest["manifest_hash"] = stable_hash(manifest)
    return manifest


def write_manifest(output_path: Path, manifest: Dict[str, Any]) -> Path:
    manifest_path = output_path.with_suffix(output_path.suffix + ".manifest.json")
    manifest_path.write_text(stable_dumps(manifest), encoding="utf-8")
    return manifest_path
