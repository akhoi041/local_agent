from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from talos.core_bridge import core_file_hash, core_scan_sources, core_text_hash, core_workspace_hash

CACHE_KEY_VERSION = 2
SOURCE_SUFFIXES = {".ino", ".h", ".hpp", ".c", ".cpp", ".s", ".S"}
IGNORED_DIRS = {".git", ".vs", ".vscode", "__pycache__", ".cache", ".pio", "build", "dist", "node_modules"}

def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), default=str)

def _short_hash(value: str, length: int = 16) -> str:
    if not value:
        return ""
    return core_text_hash(value, length) or hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:length]

def workspace_identity_hash(path_text: str, length: int = 16) -> str:
    value = str(path_text or "").strip()
    if not value:
        return ""
    native_hash = core_workspace_hash(value, length)
    if native_hash:
        return native_hash
    try:
        value = str(Path(value).expanduser().resolve())
    except OSError:
        pass
    return _short_hash(value.replace("\\", "/").lower(), length)

def _profile_payload(profile: dict[str, Any] | None) -> dict[str, Any]:
    source = profile if isinstance(profile, dict) else {}
    return {
        "fqbn": str(source.get("fqbn") or ""),
        "serial_port": str(source.get("serial_port") or ""),
        "baud_rate": source.get("baud_rate") or "",
        "build_flags": list(source.get("build_flags") or []),
        "build_properties": list(source.get("build_properties") or []),
        "libraries": list(source.get("libraries") or []),
    }

def _cli_payload(cli: str) -> dict[str, Any]:
    path_text = str(cli or "")
    payload: dict[str, Any] = {"path": path_text, "mtime_ns": None, "bytes": None}
    try:
        stat = Path(path_text).stat()
    except OSError:
        return payload
    payload["mtime_ns"] = stat.st_mtime_ns
    payload["bytes"] = stat.st_size
    return payload

def _fallback_source_rows(workspace: Path) -> list[dict[str, Any]]:
    native_rows = core_scan_sources(workspace)
    if native_rows:
        return native_rows
    rows: list[dict[str, Any]] = []
    if not workspace.exists():
        return rows
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.relative_to(workspace).parts)
        if parts & IGNORED_DIRS:
            continue
        if path.name.startswith(".talos_") or path.suffix not in SOURCE_SUFFIXES:
            continue
        try:
            content = path.read_bytes()
            stat = path.stat()
        except OSError:
            continue
        relative = path.relative_to(workspace).as_posix()
        rows.append({
            "path": relative,
            "bytes": stat.st_size,
            "lines": content.count(b"\n") + (1 if content and not content.endswith(b"\n") else 0),
            "mtime_ns": stat.st_mtime_ns,
        })
    return rows

def _source_payload(workspace: Path, summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = summary.get("files") if isinstance(summary.get("files"), list) else []
    if not rows:
        rows = _fallback_source_rows(workspace)
    payload: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        relative = str(row.get("path") or "").replace("\\", "/").strip("/")
        if not relative:
            continue
        file_path = workspace / relative
        content_hash = core_file_hash(file_path, 64)
        try:
            if not content_hash:
                content_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        except OSError:
            content_hash = "<unreadable>"
        payload.append({
            "path": relative,
            "bytes": int(row.get("bytes") or 0),
            "lines": int(row.get("lines") or 0),
            "mtime_ns": int(row.get("mtime_ns") or 0),
            "sha256": content_hash,
        })
    return sorted(payload, key=lambda item: item["path"].lower())

def _override_payload(overrides: dict[str, str | None] | None) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for path, content in sorted((overrides or {}).items()):
        text = "" if content is None else str(content)
        payload.append({
            "path": str(path).replace("\\", "/"),
            "deleted": content is None,
            "bytes": 0 if content is None else len(text.encode("utf-8")),
            "sha256": "<deleted>" if content is None else core_text_hash(text, 64) or hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    return payload

def compile_cache_payload(
    workspace: Path,
    summary: dict[str, Any],
    profile: dict[str, Any],
    cli: str,
    overrides: dict[str, str | None] | None,
) -> dict[str, Any]:
    workspace_path = Path(workspace)
    try:
        workspace_path = workspace_path.resolve()
    except OSError:
        pass
    return {
        "version": CACHE_KEY_VERSION,
        "workspace": {
            "path_hash": workspace_identity_hash(str(workspace_path)),
            "name": workspace_path.name,
            "main_sketch": str(summary.get("main_sketch") or ""),
        },
        "board": {
            "fqbn": str(summary.get("fqbn") or ""),
            "board_name": str(summary.get("board_name") or ""),
            "fqbn_properties": str(summary.get("fqbn_properties") or ""),
        },
        "profile": _profile_payload(profile),
        "cli": _cli_payload(cli),
        "sources": _source_payload(workspace_path, summary),
        "overrides": _override_payload(overrides),
    }

def compile_cache_key(
    workspace: Path,
    summary: dict[str, Any],
    profile: dict[str, Any],
    cli: str,
    overrides: dict[str, str | None] | None,
) -> str:
    return _short_hash(_stable_json(compile_cache_payload(workspace, summary, profile, cli, overrides)), 64)
