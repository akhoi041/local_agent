from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable

from talos.arduino_adapter import ArduinoTargetAdapter
from talos import codex_bridge
from talos.codex_bridge import CodexBridge

VerifyRunner = Callable[[dict[str, Any]], dict[str, Any]]


def run_arduino_compatibility_smoke(
    root: str | Path | None = None,
    *,
    adapter: ArduinoTargetAdapter | None = None,
    bridge: CodexBridge | None = None,
    verify_runner: VerifyRunner | None = None,
) -> dict[str, Any]:
    """Exercise the Arduino product path across the 0.6.0 boundaries.

    The smoke uses a synthetic sketch so CI and local checks do not need an open
    Arduino IDE, hardware, or a live Codex runtime. A caller may inject a real
    verify runner when an Arduino CLI environment is available.
    """
    if root is None:
        with TemporaryDirectory() as tmp:
            return _run_smoke(Path(tmp), adapter, bridge, verify_runner)
    return _run_smoke(Path(root), adapter, bridge, verify_runner)


def _run_smoke(
    root: Path,
    adapter: ArduinoTargetAdapter | None,
    bridge: CodexBridge | None,
    verify_runner: VerifyRunner | None,
) -> dict[str, Any]:
    workspace = _create_stage8_workspace(root)
    staging_root = root / ".talos_smoke_staging"
    config = {
        "arduino_workspace_path": str(workspace),
        "arduino_fqbn": "arduino:avr:uno",
        "arduino_profiles": {
            str(workspace): {
                "serial_port": "COM3",
                "baud_rate": 115200,
                "build_flags": ["-DSTAGE8_SMOKE"],
                "build_properties": [],
                "library_metadata": "Smoke fixture",
            },
        },
    }
    adapter = adapter or ArduinoTargetAdapter()
    bridge = bridge or CodexBridge(persist_reviews=False)
    previous_staging_root = codex_bridge.STAGING_ROOT
    codex_bridge.STAGING_ROOT = staging_root

    try:
        projects = adapter.discover_projects(config, ino_paths=[str(workspace / "Stage8Smoke.ino")])
        summary = adapter.workspace_summary(config)
        files = adapter.artifact_identities(config)
        file_names = [item.name for item in files]
        reads = {name: adapter.read_file(config, name) for name in file_names}
        verify_result = (verify_runner or _synthetic_verify)(config)
        active_file = reads["Driver.cpp"]
        context_package = adapter.context_package(
            config,
            active_file,
            str(verify_result.get("output") or ""),
            True,
            "Stage 8 Arduino compatibility smoke.",
            verify_result,
        )

        updated_driver = str(active_file["content"]).replace("return value + 1;", "return value + 2;")
        staged = bridge.create_smoke_patch(str(workspace), "Driver.cpp", updated_driver)
        applied = bridge.apply_patch(staged["patch"]["id"], str(workspace), "Driver.cpp") if staged.get("ok") else staged
        editor_content = str((applied.get("file") or {}).get("editor_content") or "")
        saved = adapter.write_file(config, "Driver.cpp", editor_content) if applied.get("ok") else applied
        marked_saved = bridge.mark_patch_saved(str(workspace), "Driver.cpp") if saved.get("ok") else saved

        rejected_source = str(reads["Driver.h"]["content"]).replace("int driver(int value);", "int driver(long value);")
        staged_reject = bridge.create_smoke_patch(str(workspace), "Driver.h", rejected_source)
        rejected = (
            bridge.reject_patch(staged_reject["patch"]["id"], "Driver.h")
            if staged_reject.get("ok")
            else staged_reject
        )
    finally:
        codex_bridge.STAGING_ROOT = previous_staging_root

    checks = {
        "detect_open_sketches": bool(projects and projects[0].get("sketch") == "Stage8Smoke.ino"),
        "inspect_source_tabs": {".ino", ".h", ".cpp"}.issubset({Path(name).suffix for name in file_names}),
        "verify_profile": bool(verify_result.get("ok") and verify_result.get("profile") == "arduino:avr:uno"),
        "context_package": bool(
            context_package.get("coverage", {}).get("active_file")
            and context_package.get("coverage", {}).get("workspace_map")
        ),
        "apply_save_safe": bool(
            marked_saved.get("saved")
            and "return value + 2;" in (workspace / "Driver.cpp").read_text(encoding="utf-8")
        ),
        "reject_safe": bool(rejected.get("ok") and "long value" not in (workspace / "Driver.h").read_text(encoding="utf-8")),
    }
    return {
        "ok": all(checks.values()),
        "workspace": str(workspace),
        "main_sketch": summary.get("main_sketch"),
        "source_files": file_names,
        "verify": verify_result,
        "context_coverage": context_package.get("coverage", {}),
        "patch": {
            "apply_status": (marked_saved.get("file") or {}).get("review_status"),
            "reject_status": (rejected.get("file") or {}).get("review_status"),
        },
        "checks": checks,
    }


def _synthetic_verify(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "status": "passed",
        "profile": str(config.get("arduino_fqbn") or ""),
        "output": "Synthetic Arduino compile passed for Stage 8 smoke.",
        "timings": {"prepare": 0.0, "sandbox_copy": 0.0, "compile": 0.0, "total": 0.0},
    }


def _create_stage8_workspace(root: Path) -> Path:
    workspace = root / "Stage8Smoke"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "Stage8Smoke.ino").write_text(
        '#include "Driver.h"\n\nvoid setup() {}\nvoid loop() { driver(1); }\n',
        encoding="utf-8",
    )
    (workspace / "Driver.h").write_text(
        "#pragma once\n\nint driver(int value);\n",
        encoding="utf-8",
    )
    (workspace / "Driver.cpp").write_text(
        '#include "Driver.h"\n\nint driver(int value) {\n  return value + 1;\n}\n',
        encoding="utf-8",
    )
    return workspace
