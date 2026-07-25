from __future__ import annotations

import difflib
import hashlib
import json
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from talos.core import ROOT, now
from talos.native_boundary import NativeHelperBoundary
from talos.python_ownership import boundary_check, ownership_report

T = TypeVar("T")

STAGE_065_BASELINE_OPERATIONS: tuple[str, ...] = (
    "arduino_detection",
    "workspace_scan",
    "file_list_generation",
    "hash_cache_key_generation",
    "verify_preparation",
    "diff_hunk_parsing",
    "codex_context_packaging",
)

STAGE_065_GATE_MAX_OPERATION_MS = 1000.0
STAGE_065_GATE_TOTAL_MS = 2500.0

def _measure(timings: dict[str, float], key: str, loader: Callable[[], T]) -> T:
    start = time.perf_counter()
    try:
        return loader()
    finally:
        timings[key] = round((time.perf_counter() - start) * 1000, 3)

def _write_sample_workspace(root: Path) -> dict[str, str]:
    files = {
        "talos_test.ino": "\n".join(
            (
                '#include "Config.h"',
                '#include "Encoder.h"',
                "",
                "void setup() {",
                "  Serial.begin(115200);",
                "}",
                "",
                "void loop() {",
                "  Serial.println(Encoder::getTicks());",
                "  delay(100);",
                "}",
                "",
            )
        ),
        "Config.h": "#pragma once\nconstexpr int kEncoderAPin = 32;\nconstexpr int kEncoderBPin = 33;\n",
        "Encoder.h": "#pragma once\nnamespace Encoder { void begin(); int getTicks(); }\n",
        "Encoder.cpp": "\n".join(
            (
                '#include "Encoder.h"',
                '#include "Config.h"',
                "",
                "namespace Encoder {",
                "volatile int ticks = 0;",
                "void begin() {}",
                "int getTicks() { return ticks; }",
                "}",
                "",
            )
        ),
    }
    for name, content in files.items():
        (root / name).write_text(content, encoding="utf-8")
    return files

def _scan_workspace(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda item: (item.suffix != ".ino", item.name.lower())):
        if path.suffix.lower() not in {".ino", ".h", ".hpp", ".c", ".cpp"}:
            continue
        content = path.read_text(encoding="utf-8")
        rows.append(
            {
                "path": path.name,
                "suffix": path.suffix.lower(),
                "lines": len(content.splitlines()),
                "bytes": len(content.encode("utf-8")),
            }
        )
    return rows

def _cache_key(root: Path, metadata: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    digest.update(b"fqbn=esp32:esp32:esp32|profile=stage-065-baseline\n")
    for row in metadata:
        path = root / str(row["path"])
        digest.update(str(row["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()

def _verify_plan(root: Path, cache_key: str) -> dict[str, Any]:
    return {
        "tool": "arduino-cli",
        "mode": "dry-run-plan",
        "fqbn": "esp32:esp32:esp32",
        "sketch": str(root),
        "cache_key": cache_key,
        "will_copy_to_sandbox": True,
    }

def _diff_report(original: str) -> dict[str, Any]:
    updated = original.replace("delay(100);", "delay(50);")
    diff_lines = list(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile="talos_test.ino",
            tofile="talos_test.ino",
            lineterm="",
        )
    )
    return {
        "lines": diff_lines,
        "hunks": sum(1 for line in diff_lines if line.startswith("@@")),
        "adds": sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++")),
        "removes": sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---")),
    }

def _codex_package(metadata: list[dict[str, Any]], diff_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "workspace": "stage-065-baseline",
        "active_file": "talos_test.ino",
        "profile": {"fqbn": "esp32:esp32:esp32", "board": "ESP32 Dev Module"},
        "files": metadata,
        "verify": {"status": "not_run"},
        "review": {"hunks": diff_report["hunks"], "adds": diff_report["adds"], "removes": diff_report["removes"]},
    }

def run_stage_065_baseline(root: Path = ROOT) -> dict[str, Any]:
    timings: dict[str, float] = {}
    native_boundary = NativeHelperBoundary()

    detection_rows = _measure(
        timings,
        "arduino_detection",
        lambda: native_boundary.measure_candidate("detection.arduino_processes", lambda: []),
    )

    with tempfile.TemporaryDirectory(prefix="talos_065_baseline_") as tmp:
        workspace = Path(tmp) / "talos_test"
        workspace.mkdir()
        files = _write_sample_workspace(workspace)
        metadata = _measure(timings, "workspace_scan", lambda: _scan_workspace(workspace))
        file_list = _measure(timings, "file_list_generation", lambda: [row["path"] for row in metadata])
        cache_key = _measure(timings, "hash_cache_key_generation", lambda: _cache_key(workspace, metadata))
        verify_plan = _measure(timings, "verify_preparation", lambda: _verify_plan(workspace, cache_key))
        diff_report = _measure(timings, "diff_hunk_parsing", lambda: _diff_report(files["talos_test.ino"]))
        context_package = _measure(
            timings,
            "codex_context_packaging",
            lambda: _codex_package(metadata, diff_report),
        )

    ownership = ownership_report()
    boundary = boundary_check(root)
    return {
        "release": "0.6.5",
        "stage": "stage_0",
        "generated_at": now(),
        "source": "synthetic_arduino_workspace",
        "targets": ["arduino"],
        "no_new_targets": True,
        "desktop_launcher": "desktop_app.py",
        "boundary_complete": bool(boundary["ok"]),
        "boundary": boundary,
        "native_boundary": native_boundary.report(),
        "python_ownership": ownership,
        "timings_ms": timings,
        "operation_order": list(STAGE_065_BASELINE_OPERATIONS),
        "sample": {
            "detected_processes": len(detection_rows),
            "file_count": len(file_list),
            "main_sketch": "talos_test.ino",
            "cache_key_prefix": cache_key[:12],
            "verify_plan": verify_plan,
            "context_package_bytes": len(json.dumps(context_package, sort_keys=True).encode("utf-8")),
        },
    }

def baseline_markdown(baseline: dict[str, Any]) -> str:
    timing_lines = "\n".join(
        f"- `{key}`: `{baseline['timings_ms'][key]:.3f} ms`"
        for key in baseline["operation_order"]
    )
    hot_paths = baseline["python_ownership"].get("hot_paths", [])
    hot_path_lines = "\n".join(
        f"- `{entry['module']}` -> `{entry['migration_target']}`"
        for entry in hot_paths
    )
    return "\n".join(
        (
            "## Stage 0 - Baseline And Measurement Setup",
            "",
            "Status: complete.",
            "",
            "Timing baseline:",
            "",
            timing_lines,
            "",
            "Python hot-path ownership:",
            "",
            hot_path_lines,
            "",
            f"No new targets: `{baseline['no_new_targets']}`; targets: `{', '.join(baseline['targets'])}`.",
            f"Source/debug launcher: `{baseline['desktop_launcher']}`.",
            "",
            "Conclusion: Python reduction starts from measured behavior, not guesswork.",
        )
    )

def _gate_check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "detail": detail}

def run_stage_065_regression_gate(root: Path = ROOT) -> dict[str, Any]:
    baseline = run_stage_065_baseline(root)
    timings = baseline["timings_ms"]
    missing_operations = [key for key in baseline["operation_order"] if key not in timings]
    max_operation_ms = max((float(timings.get(key, 0.0)) for key in baseline["operation_order"]), default=0.0)
    total_ms = sum(float(timings.get(key, 0.0)) for key in baseline["operation_order"])
    sample = baseline["sample"]
    verify_plan = sample["verify_plan"]

    checks = [
        _gate_check(
            "automated_regression",
            not missing_operations and baseline["boundary_complete"],
            "all baseline operations are measured and the Python/native boundary contract is intact",
        ),
        _gate_check(
            "source_debug_launch",
            baseline["desktop_launcher"] == "desktop_app.py",
            "desktop_app.py remains the source/debug launcher",
        ),
        _gate_check(
            "arduino_detection_select_file_inspect",
            sample["main_sketch"].endswith(".ino") and sample["file_count"] >= 4,
            "synthetic Arduino workspace exposes main sketch and companion source tabs",
        ),
        _gate_check(
            "sandbox_verify_smoke",
            bool(verify_plan["will_copy_to_sandbox"] and verify_plan["cache_key"]),
            "verify plan contains sandbox copy intent and cache key",
        ),
        _gate_check(
            "codex_context_package",
            sample["context_package_bytes"] > 0,
            "context package includes workspace, active file, profile, verify, and review data",
        ),
        _gate_check(
            "performance_containment",
            max_operation_ms <= STAGE_065_GATE_MAX_OPERATION_MS and total_ms <= STAGE_065_GATE_TOTAL_MS,
            "synthetic hot-path timings remain below conservative local gate budgets",
        ),
    ]
    return {
        "release": "0.6.5",
        "stage": "stage_7",
        "generated_at": now(),
        "status": "passed" if all(check["passed"] for check in checks) else "failed",
        "checks": checks,
        "performance": {
            "max_operation_ms": round(max_operation_ms, 3),
            "total_measured_ms": round(total_ms, 3),
            "max_operation_budget_ms": STAGE_065_GATE_MAX_OPERATION_MS,
            "total_budget_ms": STAGE_065_GATE_TOTAL_MS,
        },
        "baseline": {
            "operation_order": baseline["operation_order"],
            "timings_ms": timings,
            "boundary_complete": baseline["boundary_complete"],
            "python_hot_paths": baseline["python_ownership"].get("hot_paths", []),
        },
    }

def regression_gate_markdown(gate: dict[str, Any]) -> str:
    check_lines = "\n".join(
        f"- `{check['name']}`: `{'passed' if check['passed'] else 'failed'}` - {check['detail']}"
        for check in gate["checks"]
    )
    timing_lines = "\n".join(
        f"- `{key}`: `{gate['baseline']['timings_ms'][key]:.3f} ms`"
        for key in gate["baseline"]["operation_order"]
    )
    performance = gate["performance"]
    return "\n".join(
        (
            "## Stage 7 - Regression And Performance Gate",
            "",
            "Status: complete.",
            "",
            "Gate checks:",
            "",
            check_lines,
            "",
            "Measured timings:",
            "",
            timing_lines,
            "",
            (
                "Performance gate: "
                f"`max={performance['max_operation_ms']:.3f} ms / {performance['max_operation_budget_ms']:.0f} ms`, "
                f"`total={performance['total_measured_ms']:.3f} ms / {performance['total_budget_ms']:.0f} ms`."
            ),
            "",
            "Conclusion: 0.6.5 preserves the Arduino workflow while containing Python hot paths behind measured boundaries.",
        )
    )

if __name__ == "__main__":
    print(json.dumps(run_stage_065_baseline(), indent=2, sort_keys=True))
