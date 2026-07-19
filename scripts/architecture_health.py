from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from talos import native_bridge
from talos.arduino import (
    cached_compile_result,
    clear_arduino_compile_cache,
    environment_profile,
    store_compile_result,
    workspace_summary,
)
from talos.core import load_app_identity, load_build_metadata, load_config
from talos.diagnostics import diagnostics_export
from talos.performance import THRESHOLDS
from talos.run_history import latest_verify_for_workspace, support_bundle
from talos.state_service import state_payload

SCHEMA_VERSION = 1

MODULE_LIMITS: dict[str, dict[str, Any]] = {
    "desktop_app.py": {"max_lines": 260, "owner": "desktop debug launcher and pywebview bootstrap"},
    "talos/server.py": {"max_lines": 950, "owner": "HTTP route glue only; service modules own mechanics"},
    "talos/arduino.py": {"max_lines": 1900, "owner": "Arduino compatibility adapter until target extraction"},
    "talos/codex_bridge.py": {"max_lines": 2150, "owner": "Codex compatibility bridge until runtime manager hardening"},
    "ui/web_frontend/app.js": {"max_lines": 4900, "owner": "workbench orchestration; feature modules grow out of it"},
    "ui/web_frontend/styles.css": {"max_lines": 5000, "owner": "component/layout CSS; tokens stay in tokens.css"},
    "ui/web_frontend/js/state.js": {"max_lines": 260, "owner": "frontend state only"},
    "ui/web_frontend/js/config.js": {"max_lines": 620, "owner": "frontend constants and command metadata only"},
    "ui/web_frontend/js/dom.js": {"max_lines": 260, "owner": "DOM and API helpers only"},
    "ui/web_frontend/styles/tokens.css": {"max_lines": 520, "owner": "theme, contrast, density, and editor tokens only"},
}

TIMING_LIMITS_MS: dict[str, float] = {
    "startup_imports": 500.0,
    "state_refresh": max(float(THRESHOLDS["ui_refresh_ms"]), 2000.0),
    "arduino_detection": float(THRESHOLDS["native_detection_ms"]),
    "verify_cache_lookup": float(THRESHOLDS["verify_cache_lookup_ms"]),
    "support_bundle_generation": float(THRESHOLDS["support_bundle_seconds"]) * 1000.0,
    "diagnostics_export": float(THRESHOLDS["diagnostics_export_seconds"]) * 1000.0,
}

SHELL_RUNTIME_PARITY_GATES = [
    "source_debug_launcher",
    "packaged_app_launcher",
    "app_identity_and_icon",
    "native_binary_loading",
    "static_ui_serving",
    "settings_persistence",
    "arduino_detection",
    "sandbox_verify",
    "codex_runtime_readiness",
    "diagnostics_and_support_bundle",
]


def _line_count(path: Path) -> int:
    if not path.exists():
        return -1
    return len(path.read_text(encoding="utf-8").splitlines())


def check_module_size() -> dict[str, Any]:
    modules: list[dict[str, Any]] = []
    failures: list[str] = []
    for relative, limit in MODULE_LIMITS.items():
        lines = _line_count(ROOT / relative)
        ok = lines >= 0 and lines <= int(limit["max_lines"])
        if not ok:
            failures.append(relative)
        modules.append(
            {
                "path": relative,
                "lines": lines,
                "max_lines": limit["max_lines"],
                "owner": limit["owner"],
                "ok": ok,
            }
        )
    return {
        "ok": not failures,
        "modules": modules,
        "failures": failures,
        "policy": "Large modules must justify ownership or be split before release.",
    }


def _measure_ms(fn: Callable[[], Any], iterations: int) -> dict[str, Any]:
    timings: list[float] = []
    result_preview = ""
    for _ in range(max(1, iterations)):
        start = time.perf_counter()
        result = fn()
        timings.append((time.perf_counter() - start) * 1000.0)
        if result_preview == "" and result is not None:
            result_preview = type(result).__name__
    return {
        "min_ms": round(min(timings), 3),
        "max_ms": round(max(timings), 3),
        "avg_ms": round(sum(timings) / len(timings), 3),
        "iterations": len(timings),
        "result": result_preview,
    }


def _startup_imports() -> str:
    for name in ("talos.server", "talos.arduino", "talos.codex_bridge", "talos.state_service"):
        importlib.import_module(name)
    return "imports_ok"


def _arduino_detection() -> dict[str, int]:
    windows = native_bridge.list_window_rows()
    processes = native_bridge.list_arduino_process_rows_native()
    return {"windows": len(windows), "processes": len(processes)}


def _verify_cache_lookup() -> dict[str, Any] | None:
    clear_arduino_compile_cache()
    key = "architecture-health-cache-key"
    store_compile_result(key, {"ok": True, "status": "passed", "output": "", "timings": {}})
    cached = cached_compile_result(key, lookup_seconds=0.0)
    clear_arduino_compile_cache()
    return cached


def _support_bundle_generation() -> dict[str, Any]:
    config = load_config()
    app = load_app_identity()
    build = load_build_metadata(app)
    workspace = workspace_summary(config)
    profile = environment_profile(config, str(workspace.get("path") or ""))
    latest_verify = latest_verify_for_workspace(str(workspace.get("path") or ""))
    return support_bundle(
        app=app,
        build=build,
        workspace_summary=workspace,
        profile=profile,
        profile_readiness={"ready": True, "source": "architecture_health"},
        latest_verify=latest_verify,
        history=[],
        redact=True,
    )


def _diagnostics_export() -> dict[str, Any]:
    config = load_config()
    app = load_app_identity()
    build = load_build_metadata(app)
    return diagnostics_export(config, app, build)


def check_timing(iterations: int = 3) -> dict[str, Any]:
    probes: dict[str, Callable[[], Any]] = {
        "startup_imports": _startup_imports,
        "state_refresh": state_payload,
        "arduino_detection": _arduino_detection,
        "verify_cache_lookup": _verify_cache_lookup,
        "support_bundle_generation": _support_bundle_generation,
        "diagnostics_export": _diagnostics_export,
    }
    results: dict[str, Any] = {}
    failures: list[str] = []
    for name, probe in probes.items():
        measured = _measure_ms(probe, iterations)
        limit_ms = TIMING_LIMITS_MS[name]
        measured["limit_ms"] = limit_ms
        measured["ok"] = measured["max_ms"] <= limit_ms
        if not measured["ok"]:
            failures.append(name)
        results[name] = measured
    return {
        "ok": not failures,
        "timings": results,
        "failures": failures,
        "policy": "Timings are compared with 0.5.5 baseline guardrails, not hard-coded release promises.",
    }


def check_shell_runtime_guardrails() -> dict[str, Any]:
    return {
        "ok": True,
        "replacement_shell_allowed": False,
        "parity_gates": SHELL_RUNTIME_PARITY_GATES,
        "blocked_case_handling": (
            "A new shell/runtime path stays blocked until every gate has source/debug, "
            "packaged-app, and Arduino reference-target evidence."
        ),
    }


def architecture_health_report(iterations: int = 3) -> dict[str, Any]:
    sections = {
        "module_size": check_module_size(),
        "timing": check_timing(iterations=iterations),
        "shell_runtime_migration": check_shell_runtime_guardrails(),
    }
    failures = [name for name, result in sections.items() if not result.get("ok")]
    return {
        "schema_version": SCHEMA_VERSION,
        "version_scope": "0.5.5",
        "ok": not failures,
        "failures": failures,
        **sections,
    }


def _print_text(report: dict[str, Any]) -> None:
    print("Talos architecture health")
    print(f"scope: {report['version_scope']}")
    print(f"status: {'OK' if report['ok'] else 'FAILED'}")
    print("")
    print("Module size guardrails")
    for item in report["module_size"]["modules"]:
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status} {item['path']}: {item['lines']} / {item['max_lines']} lines")
    print("")
    print("Timing guardrails")
    for name, item in report["timing"]["timings"].items():
        status = "OK" if item["ok"] else "FAIL"
        print(f"- {status} {name}: max {item['max_ms']} ms / limit {item['limit_ms']} ms")
    print("")
    print("Shell/runtime migration guardrail")
    print(f"- replacement_shell_allowed: {report['shell_runtime_migration']['replacement_shell_allowed']}")
    print(f"- parity gates: {len(report['shell_runtime_migration']['parity_gates'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report Talos architecture health guardrails.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    parser.add_argument("--iterations", type=int, default=3, help="Timing probe iterations.")
    args = parser.parse_args()

    report = architecture_health_report(iterations=args.iterations)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
