from __future__ import annotations

"""Python compatibility view of the Rust-owned Talos module boundary.

The ownership manifest lives in `core/talos_core`. This module is intentionally
thin: it adapts Rust JSONL output for Python tests and diagnostics while the
0.8.x rewrite removes Python product logic from hot paths.
"""

import ast
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from talos.core_bridge import core_python_manifest

@dataclass(frozen=True)
class PythonModuleOwnership:
    module: str
    owner: str
    role: str
    migration_target: str
    hot_path: bool = False
    fallback_required: bool = False
    notes: str = ""

HOT_PATH_MIGRATION_TARGETS: tuple[str, ...] = (
    "process/window discovery",
    "file watching",
    "hashing/cache keys",
    "diff/hunk parsing",
    "task orchestration",
    "heavy workspace scans",
)

FALLBACK_POLICY = (
    "Python remains only as a bridge/debug/fallback surface while Rust owns "
    "core logic, scans, hashes, orchestration boundaries, and hot-path gates."
)

SERVER_IMPORT_BASELINE: frozenset[str] = frozenset(
    {
        "talos.arduino_adapter",
        "talos.checkpoints",
        "talos.codex_bridge",
        "talos.codex_runtime",
        "talos.contracts",
        "talos.core",
        "talos.diagnostics",
        "talos.event_bus",
        "talos.native_bridge",
        "talos.native_boundary",
        "talos.performance",
        "talos.run_history",
        "talos.runtime_core",
        "talos.runtime_provider",
        "talos.runtime_service",
        "talos.shell.profile",
        "talos.state_service",
        "talos.targets",
        "talos.task_orchestrator",
        "talos.workspace_scanner",
    }
)

def _entry_from_row(row: dict[str, Any]) -> PythonModuleOwnership:
    return PythonModuleOwnership(
        module=str(row.get("module", "")),
        owner=str(row.get("owner", "")),
        role=str(row.get("role", "")),
        migration_target=str(row.get("migration_target", "")),
        hot_path=bool(row.get("hot_path")),
        fallback_required=bool(row.get("fallback_required")),
        notes=str(row.get("notes", "")),
    )

@lru_cache(maxsize=1)
def _ownership_entries() -> tuple[PythonModuleOwnership, ...]:
    return tuple(
        entry
        for row in core_python_manifest()
        if (entry := _entry_from_row(row)).module
    )

def ownership_by_module() -> dict[str, PythonModuleOwnership]:
    return {entry.module: entry for entry in _ownership_entries()}

def ownership_report() -> dict[str, object]:
    entries = [asdict(entry) for entry in _ownership_entries()]
    return {
        "entries": entries,
        "hot_paths": [entry for entry in entries if entry["hot_path"]],
        "migration_targets": list(HOT_PATH_MIGRATION_TARGETS),
        "fallback_policy": FALLBACK_POLICY,
    }

def _talos_imports(source_path: Path) -> set[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "talos" or alias.name.startswith("talos."):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "talos":
                for alias in node.names:
                    imports.add(f"talos.{alias.name.split('.')[0]}")
            elif node.module.startswith("talos."):
                imports.add(node.module)
    return imports

def boundary_check(root: Path) -> dict[str, object]:
    """Return native-boundary status for the compatibility Python API host."""

    server_path = root / "talos" / "server.py"
    imports = _talos_imports(server_path) if server_path.exists() else set()
    new_direct_imports = sorted(imports - SERVER_IMPORT_BASELINE)
    declared_modules = ownership_by_module()
    stale_declared = sorted(
        module
        for module, entry in declared_modules.items()
        if entry.role == "stale"
    )
    return {
        "ok": not new_direct_imports and not stale_declared,
        "server_imports": sorted(imports),
        "new_direct_imports": new_direct_imports,
        "stale_declared": stale_declared,
        "fallback_policy": FALLBACK_POLICY,
    }
