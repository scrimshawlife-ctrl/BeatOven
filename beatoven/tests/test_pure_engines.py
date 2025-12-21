"""Ensure engine modules avoid side-effect imports."""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_IMPORTS = {
    "os",
    "pathlib",
    "requests",
    "httpx",
    "time",
    "datetime",
    "random",
    "uuid",
}


def _iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if path.name.startswith("__"):
            continue
        yield path


def _find_forbidden_imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    violations.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                violations.append(node.module)
    return violations


def test_engines_are_pure():
    engine_root = Path(__file__).resolve().parents[1] / "engines"
    violations = {}
    for path in _iter_python_files(engine_root):
        found = _find_forbidden_imports(path)
        if found:
            violations[str(path)] = found

    assert not violations, f"Forbidden imports in engines: {violations}"
