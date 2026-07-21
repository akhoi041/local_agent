from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonModuleOwnership:
    module: str
    owner: str
    role: str
    migration_target: str
    hot_path: bool = False
    fallback_required: bool = False
    notes: str = ""


PYTHON_MODULE_OWNERSHIP: tuple[PythonModuleOwnership, ...] = (
    PythonModuleOwnership(module="desktop_app", owner="shell", role="launcher", migration_target="shell", notes="Thin desktop entry point."),
    PythonModuleOwnership(module="talos.shell.profile", owner="shell", role="shell_provider", migration_target="webview/native shell"),
    PythonModuleOwnership(module="talos.shell.pywebview_provider", owner="shell", role="shell_provider", migration_target="webview/native shell"),
    PythonModuleOwnership(module="talos.core", owner="core", role="core_implementation", migration_target="native core"),
    PythonModuleOwnership(module="talos.contracts", owner="core", role="local_api_contract", migration_target="native core"),
    PythonModuleOwnership(module="talos.runtime_core", owner="core", role="orchestration_boundary", migration_target="native core", hot_path=True),
    PythonModuleOwnership(module="talos.state_service", owner="core", role="state_projection", migration_target="native core", hot_path=True),
    PythonModuleOwnership(module="talos.targets", owner="targets", role="target_adapter_boundary", migration_target="target host"),
    PythonModuleOwnership(module="talos.arduino_adapter", owner="targets", role="target_adapter", migration_target="target host"),
    PythonModuleOwnership(module="talos.arduino", owner="targets", role="migration_candidate", migration_target="target host", hot_path=True, fallback_required=True, notes="Heavy Arduino discovery, scanning, hashing, verify preparation."),
    PythonModuleOwnership(module="talos.arduino_events", owner="targets", role="migration_candidate", migration_target="target host", hot_path=True, fallback_required=True, notes="Process/window discovery and file-change watching."),
    PythonModuleOwnership(module="talos.runtime_provider", owner="runtime", role="runtime_provider", migration_target="runtime host"),
    PythonModuleOwnership(module="talos.runtime_service", owner="runtime", role="runtime_projection", migration_target="runtime host"),
    PythonModuleOwnership(module="talos.codex_runtime", owner="runtime", role="runtime_discovery", migration_target="runtime host", hot_path=True, fallback_required=True),
    PythonModuleOwnership(module="talos.codex_bridge", owner="runtime", role="runtime_bridge", migration_target="runtime host", hot_path=True, fallback_required=True, notes="Runtime process/message/patch orchestration."),
    PythonModuleOwnership(module="talos.native_bridge", owner="native", role="native_fallback", migration_target="native helper", hot_path=True, fallback_required=True),
    PythonModuleOwnership(module="talos.native_boundary", owner="native", role="native_adapter", migration_target="native helper", hot_path=True, fallback_required=True),
    PythonModuleOwnership(module="talos.checkpoints", owner="storage", role="core_implementation", migration_target="storage"),
    PythonModuleOwnership(module="talos.run_history", owner="storage", role="core_implementation", migration_target="storage", hot_path=True),
    PythonModuleOwnership(module="talos.diagnostics", owner="diagnostics", role="diagnostics", migration_target="diagnostics"),
    PythonModuleOwnership(module="talos.event_bus", owner="diagnostics", role="event_bus", migration_target="event bus", hot_path=True),
    PythonModuleOwnership(module="talos.performance", owner="diagnostics", role="performance", migration_target="diagnostics"),
    PythonModuleOwnership(module="talos.server", owner="api", role="python_bridge", migration_target="api host", notes="Compatibility HTTP layer until native API host exists."),
    PythonModuleOwnership(module="talos.client", owner="api", role="python_bridge", migration_target="api host"),
)

HOT_PATH_MIGRATION_TARGETS: tuple[str, ...] = (
    "process/window discovery",
    "file watching",
    "hashing/cache keys",
    "diff/hunk parsing",
    "task orchestration",
    "heavy workspace scans",
)

FALLBACK_POLICY = (
    "Python remains available as a bridge/fallback while native/core boundaries are introduced. "
    "Missing native helper support must be non-fatal."
)

SERVER_IMPORT_BASELINE: frozenset[str] = frozenset({
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
    "talos.runtime_service",
    "talos.shell.profile",
    "talos.state_service",
    "talos.targets",
})


def ownership_by_module() -> dict[str, PythonModuleOwnership]:
    return {entry.module: entry for entry in PYTHON_MODULE_OWNERSHIP}


def ownership_report() -> dict[str, object]:
    entries = [entry.__dict__ for entry in PYTHON_MODULE_OWNERSHIP]
    return {
        "entries": entries,
        "hot_paths": [entry.__dict__ for entry in PYTHON_MODULE_OWNERSHIP if entry.hot_path],
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
            if node.module == "talos" or node.module.startswith("talos."):
                imports.add(node.module)
    return imports


def boundary_check(root: Path) -> dict[str, object]:
    """Return Stage 6 ownership/boundary status.

    The current compatibility server still has legacy direct imports. The check
    freezes that baseline so new direct server access to internal helpers is
    caught before 0.6.5 migrates the hot paths.
    """

    server_path = root / "talos" / "server.py"
    imports = _talos_imports(server_path) if server_path.exists() else set()
    new_direct_imports = sorted(imports - SERVER_IMPORT_BASELINE)
    stale_declared = sorted(
        entry.module
        for entry in PYTHON_MODULE_OWNERSHIP
        if entry.role == "stale"
    )
    return {
        "ok": not new_direct_imports and not stale_declared,
        "server_imports": sorted(imports),
        "new_direct_imports": new_direct_imports,
        "stale_declared": stale_declared,
        "fallback_policy": FALLBACK_POLICY,
    }
