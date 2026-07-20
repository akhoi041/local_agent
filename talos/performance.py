from __future__ import annotations

import os
from typing import Any

from talos.arduino import VERIFY_SLOW_COMPILE_SECONDS, VERIFY_SLOW_TOTAL_SECONDS
from talos.core import now
from talos.native_bridge import native_available

PERFORMANCE_SCHEMA_VERSION = 1

THRESHOLDS: dict[str, float] = {
    "native_detection_ms": 250.0,
    "verify_cache_lookup_ms": 150.0,
    "verify_total_seconds": VERIFY_SLOW_TOTAL_SECONDS,
    "verify_compile_seconds": VERIFY_SLOW_COMPILE_SECONDS,
    "support_bundle_seconds": 2.0,
    "diagnostics_export_seconds": 1.0,
    "ui_refresh_ms": 750.0,
    "installed_app_health_seconds": 3.0,
}

def performance_guardrails() -> dict[str, Any]:
    return {
        "schema_version": PERFORMANCE_SCHEMA_VERSION,
        "generated_at": now(),
        "thresholds": THRESHOLDS.copy(),
        "process_policy": {
            "windows_hidden_subprocesses": os.name == "nt",
            "no_interactive_powershell_during_normal_use": True,
            "no_interactive_cmd_during_normal_use": True,
            "native_detection_preferred": native_available(),
            "powershell_detection_fallback": True,
        },
        "codex_runtime_040": {
            "runtime_manager_available": False,
            "dependency_model": "available Codex runtime; VS Code extension runtime may be used as fallback",
            "planned_runtime_manager_version": "0.5.0",
        },
    }
