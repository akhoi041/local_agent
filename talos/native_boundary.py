from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from talos import native_bridge

T = TypeVar("T")


@dataclass(frozen=True)
class NativeOperation:
    key: str
    label: str
    category: str
    native_capability: str | None
    fallback_backed: bool


OPERATIONS: tuple[NativeOperation, ...] = (
    NativeOperation("detection.window_titles", "Window title detection", "detection", "window_titles", True),
    NativeOperation("detection.window_rows", "Window row detection", "detection", "window_rows", True),
    NativeOperation("detection.arduino_processes", "Arduino process detection", "detection", "process_rows", True),
    NativeOperation("scan.open_workspaces", "Arduino open workspace scan", "scan", None, True),
    NativeOperation("scan.workspace_boards", "Arduino board profile scan", "scan", None, True),
    NativeOperation("hash.cache_keys", "Cache key hashing", "hash", None, True),
    NativeOperation("diff.hunks", "Diff and hunk parsing", "diff", None, True),
    NativeOperation("verify.preparation", "Verify preparation", "verify", None, True),
)

MIGRATION_GATES: tuple[dict[str, str], ...] = (
    {
        "primitive": "hashing/cache keys",
        "status": "fallback",
        "gate": "native hash primitive plus cache invalidation parity tests",
    },
    {
        "primitive": "diff/hunk parsing",
        "status": "fallback",
        "gate": "native diff scanner with identical hunk decisions",
    },
    {
        "primitive": "verify preparation",
        "status": "fallback",
        "gate": "native sandbox copy/profile preparation timing under load",
    },
    {
        "primitive": "heavy workspace scans",
        "status": "fallback",
        "gate": "target-host scan worker that preserves Arduino compatibility",
    },
)


class NativeHelperBoundary:
    """Single reporting boundary for Talos native acceleration.

    The raw bridge may keep platform-specific ctypes and fallback details. Product
    code should use this boundary when it needs capability/timing reports.
    """

    def __init__(self) -> None:
        self._timings_ms: dict[str, float] = {}

    def native_capabilities(self) -> dict[str, bool]:
        available = native_bridge.native_available()
        return {
            "library": available,
            "window_titles": available,
            "window_rows": available and bool(getattr(native_bridge, "_HAS_NATIVE_WINDOW_ROWS", False)),
            "process_rows": available and bool(getattr(native_bridge, "_HAS_NATIVE_PROCESS_ROWS", False)),
            "ino_extract": available,
        }

    def measure_candidate(self, operation: str, loader: Callable[[], T]) -> T:
        start = time.perf_counter()
        try:
            return loader()
        finally:
            self._timings_ms[operation] = round((time.perf_counter() - start) * 1000, 3)

    def list_window_titles(self) -> list[str]:
        return self.measure_candidate("detection.window_titles", native_bridge.list_window_titles)

    def list_window_rows(self) -> list[dict[str, object]]:
        return self.measure_candidate("detection.window_rows", native_bridge.list_window_rows)

    def list_arduino_tool_processes(self) -> list[dict[str, object]]:
        return self.measure_candidate("detection.arduino_processes", native_bridge.list_arduino_tool_processes)

    def list_arduino_open_workspaces(self) -> dict[str, dict[str, object]]:
        return self.measure_candidate("scan.open_workspaces", native_bridge.list_arduino_open_workspaces)

    def list_arduino_workspace_boards(self) -> dict[str, dict[str, str]]:
        return self.measure_candidate("scan.workspace_boards", native_bridge.list_arduino_workspace_boards)

    def report(self) -> dict[str, Any]:
        capabilities = self.native_capabilities()
        operations: dict[str, dict[str, Any]] = {}
        for operation in OPERATIONS:
            native_backed = bool(operation.native_capability and capabilities.get(operation.native_capability))
            operations[operation.key] = {
                "label": operation.label,
                "category": operation.category,
                "native_backed": native_backed,
                "fallback_backed": operation.fallback_backed,
                "backend": "native" if native_backed else "fallback",
                "last_ms": self._timings_ms.get(operation.key),
            }
        return {
            "available": capabilities["library"],
            "capabilities": capabilities,
            "operations": operations,
            "migration_gates": list(MIGRATION_GATES),
        }


NATIVE_HELPER = NativeHelperBoundary()


def native_boundary_report() -> dict[str, Any]:
    return NATIVE_HELPER.report()


def native_available() -> bool:
    return NATIVE_HELPER.native_capabilities()["library"]


def list_window_rows() -> list[dict[str, object]]:
    return NATIVE_HELPER.list_window_rows()


def list_arduino_tool_processes() -> list[dict[str, object]]:
    return NATIVE_HELPER.list_arduino_tool_processes()


def list_arduino_open_workspaces() -> dict[str, dict[str, object]]:
    return NATIVE_HELPER.list_arduino_open_workspaces()


def list_arduino_workspace_boards() -> dict[str, dict[str, str]]:
    return NATIVE_HELPER.list_arduino_workspace_boards()
