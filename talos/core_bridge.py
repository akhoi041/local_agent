from __future__ import annotations

"""Thin compatibility bridge to the Rust Talos core.

Python may call this module while the 0.8.x rewrite is in progress, but product
logic should live in `core/talos_core`. Empty return values mean the Rust path is
unavailable and the caller may use its compatibility fallback.
"""

import json
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_MANIFEST = ROOT / "core" / "talos_core" / "Cargo.toml"
CORE_SOURCE_DIR = ROOT / "core" / "talos_core" / "src"
CORE_BINARY_NAMES = (
    ("talos_core_audit.exe", "talos-core-audit.exe")
    if sys.platform == "win32"
    else ("talos_core_audit", "talos-core-audit")
)
CORE_BINARIES = tuple(
    ROOT / "core" / "talos_core" / "target" / "debug" / name
    for name in CORE_BINARY_NAMES
)
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

@lru_cache(maxsize=1)
def _cargo() -> str:
    return shutil.which("cargo") or ""

def _binary_is_fresh(binary: Path) -> bool:
    try:
        binary_mtime = binary.stat().st_mtime
    except OSError:
        return False
    for source in CORE_SOURCE_DIR.glob("*.rs"):
        try:
            if source.stat().st_mtime > binary_mtime:
                return False
        except OSError:
            return False
    return True

def _core_command(args: list[str]) -> list[str]:
    for binary in CORE_BINARIES:
        if binary.exists() and _binary_is_fresh(binary):
            return [str(binary), *args]
    cargo = _cargo()
    if cargo and CORE_MANIFEST.exists():
        return [cargo, "run", "--manifest-path", str(CORE_MANIFEST), "--quiet", "--", *args]
    return []

def _run_core(args: list[str], timeout: float = 8.0) -> str:
    command = _core_command(args)
    if not command:
        return ""
    kwargs: dict[str, Any] = {
        "cwd": ROOT,
        "capture_output": True,
        "text": True,
        "timeout": timeout,
        "check": False,
    }
    if CREATE_NO_WINDOW:
        kwargs["creationflags"] = CREATE_NO_WINDOW
    try:
        completed = subprocess.run(command, **kwargs)
    except (OSError, subprocess.SubprocessError):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()

@lru_cache(maxsize=1)
def native_core_available() -> bool:
    return bool(_run_core(["summary"], timeout=12.0))

def core_text_hash(text: str, length: int = 16) -> str:
    return _run_core(["hash-text", str(text or ""), str(length)])

def core_file_hash(path: str | Path, length: int = 64) -> str:
    return _run_core(["hash-file", str(Path(path)), str(length)])

def core_workspace_hash(path: str | Path, length: int = 16) -> str:
    return _run_core(["workspace-hash", str(path or ""), str(length)])

def core_scan_sources(workspace: str | Path) -> list[dict[str, Any]]:
    output = _run_core(["scan-sources", str(Path(workspace))], timeout=12.0)
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows

@lru_cache(maxsize=1)
def _core_python_manifest_cached() -> tuple[dict[str, Any], ...]:
    output = _run_core(["manifest-json"], timeout=12.0)
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return tuple(rows)

def core_python_manifest() -> list[dict[str, Any]]:
    return [dict(row) for row in _core_python_manifest_cached()]

def core_version_summary() -> str:
    return _run_core(["summary"], timeout=12.0)

def core_api_contract_manifest() -> str:
    return _run_core(["api-contracts"], timeout=12.0)

@lru_cache(maxsize=1)
def _core_backend_services_cached() -> tuple[dict[str, Any], ...]:
    output = _run_core(["backend-services"], timeout=12.0)
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return tuple(rows)

def core_backend_services() -> list[dict[str, Any]]:
    return [dict(row) for row in _core_backend_services_cached()]

def core_backend_service_manifest() -> str:
    return _run_core(["backend-services"], timeout=12.0)
