from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from talos.native_boundary import NATIVE_HELPER, NativeHelperBoundary

DETECTION_OPERATIONS: tuple[tuple[str, str], ...] = (
    ("arduino_processes", "detection.arduino_processes"),
    ("window_rows", "detection.window_rows"),
)

def _operation_report(report: Mapping[str, Any], operation_key: str) -> Mapping[str, Any]:
    operations = report.get("operations")
    if not isinstance(operations, Mapping):
        return {}
    operation = operations.get(operation_key)
    return operation if isinstance(operation, Mapping) else {}

def _operation_state(operation: Mapping[str, Any]) -> dict[str, Any]:
    backend = str(operation.get("backend") or "fallback")
    native_backed = bool(operation.get("native_backed"))
    fallback_backed = bool(operation.get("fallback_backed", True))
    last_ms = operation.get("last_ms")
    return {
        "backend": "native" if backend == "native" and native_backed else "fallback",
        "native_backed": native_backed,
        "fallback_backed": fallback_backed,
        "last_ms": last_ms if isinstance(last_ms, (int, float)) else 0,
    }

def detection_state_from_report(
    report: Mapping[str, Any],
    *,
    process_rows: Sequence[Mapping[str, Any]] | None = None,
    window_rows: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize process/window detection without performing another scan."""

    operations = {
        short_key: _operation_state(_operation_report(report, operation_key))
        for short_key, operation_key in DETECTION_OPERATIONS
    }
    labels = [
        f"{short_key}:{operation['backend']}"
        for short_key, operation in operations.items()
    ]
    timings_ms = {
        short_key: operation["last_ms"]
        for short_key, operation in operations.items()
    }
    fallback_used = any(operation["backend"] != "native" for operation in operations.values())
    native_backed = bool(operations) and all(
        operation["backend"] == "native" for operation in operations.values()
    )

    return {
        "backend": "native" if native_backed else "fallback",
        "native_available": bool(report.get("available")),
        "native_backed": native_backed,
        "fallback_used": fallback_used,
        "labels": labels,
        "timings_ms": timings_ms,
        "operations": operations,
        "counts": {
            "arduino_processes": len(process_rows or ()),
            "window_rows": len(window_rows or ()),
        },
    }

def arduino_detection_snapshot(
    boundary: NativeHelperBoundary | None = None,
) -> dict[str, Any]:
    """Capture Arduino process/window rows through the native boundary."""

    helper = boundary or NATIVE_HELPER
    process_rows = helper.list_arduino_tool_processes()
    window_rows = helper.list_window_rows()
    return {
        "process_rows": process_rows,
        "window_rows": window_rows,
        "state": detection_state_from_report(
            helper.report(),
            process_rows=process_rows,
            window_rows=window_rows,
        ),
    }
