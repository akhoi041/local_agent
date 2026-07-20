from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from talos.core import CODEX_RUNTIME_DEFAULTS, load_config, now

RUNTIME_CONFIG_KEY = "codex_runtime"
PROVIDER_STANDALONE_PATH = "standalone_path"
PROVIDER_USER_SELECTED_PATH = "user_selected_path"
PROVIDER_EXTENSION_ADJACENT = "vscode_extension_adjacent"
PROVIDER_NONE = "none"
FALLBACK_EXTENSION_ADJACENT = "extension_adjacent"
FALLBACK_NONE = "none"

_HEALTH_CACHE: dict[tuple[str, str, float], dict[str, Any]] = {}

def _safe_items(items: Any, limit: int, item_limit: int) -> list[str]:
    values = items if isinstance(items, list) else []
    return [str(item)[:item_limit] for item in values[:limit]]


def runtime_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    source = config if isinstance(config, dict) else {}
    runtime = source.get(RUNTIME_CONFIG_KEY) if isinstance(source.get(RUNTIME_CONFIG_KEY), dict) else {}
    merged = CODEX_RUNTIME_DEFAULTS | runtime
    try:
        timeout = float(merged.get("health_timeout_sec", CODEX_RUNTIME_DEFAULTS["health_timeout_sec"]))
    except (TypeError, ValueError):
        timeout = float(CODEX_RUNTIME_DEFAULTS["health_timeout_sec"])
    fallback = str(merged.get("fallback_policy") or FALLBACK_EXTENSION_ADJACENT).strip()
    if fallback not in {FALLBACK_EXTENSION_ADJACENT, FALLBACK_NONE}:
        fallback = FALLBACK_EXTENSION_ADJACENT
    return {
        "selected_path": str(merged.get("selected_path") or "").strip(),
        "pinned_path": str(merged.get("pinned_path") or "").strip(),
        "pinned_hash": str(merged.get("pinned_hash") or "").strip().lower(),
        "pinned_version": str(merged.get("pinned_version") or "").strip(),
        "fallback_policy": fallback,
        "extension_adjacent_path": str(merged.get("extension_adjacent_path") or "").strip(),
        "health_timeout_sec": max(0.2, min(10.0, timeout)),
    }

def with_runtime_defaults(config: dict[str, Any] | None = None) -> dict[str, Any]:
    source = dict(config) if isinstance(config, dict) else {}
    source[RUNTIME_CONFIG_KEY] = runtime_config(source)
    return source

def file_sha256(path_text: str) -> str:
    path = Path(path_text)
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return ""

def redact_path(path_text: str) -> str:
    if not str(path_text or "").strip():
        return ""
    name = Path(path_text).name or "<runtime>"
    return f"...\\{name}" if os.name == "nt" else f".../{name}"

def _existing_path(path_text: str, path_exists: Callable[[str], bool]) -> str:
    value = str(path_text or "").strip().strip('"')
    if not value:
        return ""
    try:
        candidate = str(Path(value).expanduser().resolve())
    except OSError:
        candidate = value
    return candidate if path_exists(candidate) else ""

def _candidate(provider: str, path_text: str, source: str, warnings: list[str] | None = None) -> dict[str, Any]:
    digest = file_sha256(path_text)
    return {
        "provider": provider,
        "path": path_text,
        "display_path": redact_path(path_text),
        "source": source,
        "version": "",
        "hash": digest,
        "hash_short": digest[:12],
        "warnings": warnings or [],
        "limitations": [],
    }

def discover_runtime_candidates(
    config: dict[str, Any] | None = None,
    *,
    path_exists: Callable[[str], bool] | None = None,
    which_func: Callable[[str], str | None] | None = None,
) -> list[dict[str, Any]]:
    settings = runtime_config(config or {})
    exists = path_exists or (lambda path_text: Path(path_text).exists())
    which = which_func or shutil.which
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(provider: str, path_text: str, source: str, warnings: list[str] | None = None) -> None:
        path_value = _existing_path(path_text, exists)
        if not path_value:
            return
        key = path_value.lower()
        if key in seen:
            return
        seen.add(key)
        candidates.append(_candidate(provider, path_value, source, warnings))

    add(PROVIDER_STANDALONE_PATH, which("codex") or "", "PATH")
    add(PROVIDER_USER_SELECTED_PATH, settings["selected_path"], "user_config")
    if settings["fallback_policy"] == FALLBACK_EXTENSION_ADJACENT:
        add(
            PROVIDER_EXTENSION_ADJACENT,
            settings["extension_adjacent_path"],
            "extension_adjacent",
            ["extension_adjacent_fallback"],
        )
    return candidates

def choose_runtime(config: dict[str, Any] | None, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    settings = runtime_config(config or {})
    warnings: list[str] = []
    if not candidates:
        return {
            "provider": PROVIDER_NONE,
            "path": "",
            "display_path": "",
            "source": "none",
            "version": "",
            "hash": "",
            "hash_short": "",
            "pinned": False,
            "changed": False,
            "warnings": ["missing_runtime"],
            "limitations": ["No Codex runtime was discovered."],
        }

    pinned_path = settings["pinned_path"]
    pinned_hash = settings["pinned_hash"]
    pinned_version = settings["pinned_version"]
    selected = candidates[0]
    pinned = False
    if pinned_path:
        pinned_key = str(Path(pinned_path).expanduser()).lower()
        for candidate in candidates:
            if str(Path(candidate["path"]).expanduser()).lower() == pinned_key:
                selected = candidate
                pinned = True
                break
        if not pinned:
            warnings.append("pinned_runtime_missing")
    changed = bool(
        pinned
        and (
            (pinned_hash and pinned_hash != str(selected.get("hash") or "").lower())
            or (pinned_version and pinned_version != str(selected.get("version") or ""))
        )
    )
    if changed:
        warnings.append("runtime_changed")
    result = dict(selected)
    result["pinned"] = pinned
    result["changed"] = changed
    result["warnings"] = [*result.get("warnings", []), *warnings]
    return result

def _hidden_subprocess_flags() -> dict[str, Any]:
    flags: dict[str, Any] = {}
    if os.name == "nt":
        flags["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return flags

def run_runtime_health(
    active: dict[str, Any],
    *,
    timeout_sec: float,
    runner: Callable[[str, float], dict[str, Any]] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    path = str(active.get("path") or "")
    started = time.monotonic()
    if cancel_check and cancel_check():
        return {
            "checked_at": now(),
            "duration_ms": 0,
            "status": "cancelled",
            "ready": False,
            "auth_ready": False,
            "app_server_ready": False,
            "version": "",
            "message": "Runtime health check was cancelled before launch.",
            "warnings": ["codex_runtime_health_cancelled"],
        }
    if not path:
        return {
            "checked_at": now(),
            "duration_ms": 0,
            "status": "missing",
            "ready": False,
            "auth_ready": False,
            "app_server_ready": False,
            "version": "",
            "message": "No runtime selected.",
            "warnings": ["missing_runtime"],
        }
    try:
        if runner:
            result = runner(path, timeout_sec)
        else:
            completed = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                shell=False,
                **_hidden_subprocess_flags(),
            )
            result = {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
        code = int(result.get("returncode", 1))
        stdout = str(result.get("stdout") or "").strip()
        stderr = str(result.get("stderr") or "").strip()
        version = stdout.splitlines()[0][:120] if stdout else ""
        ready = code == 0
        return {
            "checked_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
            "status": "ready" if ready else "failed",
            "ready": ready,
            "auth_ready": False,
            "app_server_ready": False,
            "version": version,
            "message": version or stderr[:160] or ("Runtime responded." if ready else "Runtime health check failed."),
            "warnings": [] if ready else ["codex_runtime_health_failed"],
        }
    except (TimeoutError, subprocess.TimeoutExpired):
        return {
            "checked_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
            "status": "timeout",
            "ready": False,
            "auth_ready": False,
            "app_server_ready": False,
            "version": "",
            "message": "Runtime health check timed out.",
            "warnings": ["codex_runtime_health_timeout"],
        }
    except OSError as exc:
        return {
            "checked_at": now(),
            "duration_ms": int((time.monotonic() - started) * 1000),
            "status": "failed",
            "ready": False,
            "auth_ready": False,
            "app_server_ready": False,
            "version": "",
            "message": str(exc)[:160],
            "warnings": ["codex_runtime_health_failed"],
        }

def runtime_status(
    config: dict[str, Any] | None = None,
    *,
    force: bool = False,
    runner: Callable[[str, float], dict[str, Any]] | None = None,
    cancel_check: Callable[[], bool] | None = None,
    path_exists: Callable[[str], bool] | None = None,
    which_func: Callable[[str], str | None] | None = None,
) -> dict[str, Any]:
    source_config = config if config is not None else load_config()
    settings = runtime_config(source_config)
    candidates = discover_runtime_candidates(source_config, path_exists=path_exists, which_func=which_func)
    active = choose_runtime(source_config, candidates)
    cache_key = (str(active.get("path") or ""), str(active.get("hash") or ""), float(settings["health_timeout_sec"]))
    if force or cache_key not in _HEALTH_CACHE:
        _HEALTH_CACHE[cache_key] = run_runtime_health(
            active,
            timeout_sec=float(settings["health_timeout_sec"]),
            runner=runner,
            cancel_check=cancel_check,
        )
    health = dict(_HEALTH_CACHE[cache_key])
    if health.get("version") and not active.get("version"):
        active["version"] = health["version"]
    return {
        "schema_version": 1,
        "generated_at": now(),
        "config": settings,
        "active": active,
        "candidates": candidates,
        "health": health,
        "warnings": sorted(set([*active.get("warnings", []), *health.get("warnings", [])])),
    }

def runtime_state_summary(status: dict[str, Any]) -> dict[str, Any]:
    active = status.get("active") if isinstance(status.get("active"), dict) else {}
    health = status.get("health") if isinstance(status.get("health"), dict) else {}
    candidates = status.get("candidates") if isinstance(status.get("candidates"), list) else []
    return {
        "schema_version": 1,
        "provider": active.get("provider", PROVIDER_NONE),
        "display_path": active.get("display_path", ""),
        "source": active.get("source", ""),
        "version": active.get("version") or health.get("version", ""),
        "hash_short": active.get("hash_short", ""),
        "pinned": bool(active.get("pinned")),
        "changed": bool(active.get("changed")),
        "candidate_count": len(candidates),
        "health": {
            "status": health.get("status", "unknown"),
            "ready": bool(health.get("ready")),
            "auth_ready": bool(health.get("auth_ready")),
            "app_server_ready": bool(health.get("app_server_ready")),
            "checked_at": health.get("checked_at", ""),
            "duration_ms": int(health.get("duration_ms") or 0),
        },
        "warnings": _safe_items(status.get("warnings", []), 12, 80),
        "limitations": _safe_items(active.get("limitations", []), 6, 120),
    }

def clear_runtime_health_cache() -> None:
    _HEALTH_CACHE.clear()

def _path_key(path_text: str) -> str:
    value = str(path_text or "").strip()
    if not value:
        return ""
    try:
        return str(Path(value).expanduser()).lower()
    except OSError:
        return value.lower()

def update_runtime_pin(
    config: dict[str, Any] | None,
    *,
    path_text: str = "",
    clear: bool = False,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    updated = with_runtime_defaults(config)
    settings = runtime_config(updated)
    if clear:
        settings["pinned_path"] = ""
        settings["pinned_hash"] = ""
        settings["pinned_version"] = ""
        updated[RUNTIME_CONFIG_KEY] = settings
        clear_runtime_health_cache()
        return {"ok": True, "action": "cleared", "config": updated}

    current_status = status if isinstance(status, dict) else runtime_status(updated)
    active = current_status.get("active") if isinstance(current_status.get("active"), dict) else {}
    candidates = current_status.get("candidates") if isinstance(current_status.get("candidates"), list) else []
    target_path = str(path_text or active.get("path") or "").strip()
    if not target_path:
        return {
            "ok": False,
            "error": {
                "code": "runtime_pin_missing_target",
                "message": "No Codex runtime path was provided or selected.",
            },
        }

    target_key = _path_key(target_path)
    target = None
    for candidate in candidates:
        if isinstance(candidate, dict) and _path_key(str(candidate.get("path") or "")) == target_key:
            target = candidate
            break
    if target is None and _path_key(str(active.get("path") or "")) == target_key:
        target = active
    if target is None:
        return {
            "ok": False,
            "error": {
                "code": "runtime_pin_unknown_candidate",
                "message": "The requested Codex runtime is not in the discovered runtime candidate list.",
            },
        }

    settings["selected_path"] = str(target.get("path") or target_path)
    settings["pinned_path"] = str(target.get("path") or target_path)
    settings["pinned_hash"] = str(target.get("hash") or "").lower()
    settings["pinned_version"] = str(target.get("version") or current_status.get("health", {}).get("version") or "")
    updated[RUNTIME_CONFIG_KEY] = settings
    clear_runtime_health_cache()
    return {"ok": True, "action": "pinned", "config": updated}

def support_bundle_runtime_evidence(status: dict[str, Any]) -> dict[str, Any]:
    active = status.get("active") if isinstance(status.get("active"), dict) else {}
    health = status.get("health") if isinstance(status.get("health"), dict) else {}
    candidates = status.get("candidates") if isinstance(status.get("candidates"), list) else []
    return {
        "schema_version": 1,
        "provider": active.get("provider", PROVIDER_NONE),
        "display_path": active.get("display_path", ""),
        "version": active.get("version") or health.get("version", ""),
        "hash_short": active.get("hash_short", ""),
        "pinned": bool(active.get("pinned")),
        "changed": bool(active.get("changed")),
        "health": {
            "status": health.get("status", "unknown"),
            "ready": bool(health.get("ready")),
            "auth_ready": bool(health.get("auth_ready")),
            "app_server_ready": bool(health.get("app_server_ready")),
            "checked_at": health.get("checked_at", ""),
            "duration_ms": int(health.get("duration_ms") or 0),
        },
        "warnings": _safe_items(status.get("warnings", []), 20, 80),
        "limitations": _safe_items(active.get("limitations", []), 10, 120),
        "candidates": [
            {
                "provider": str(candidate.get("provider") or ""),
                "display_path": str(candidate.get("display_path") or ""),
                "hash_short": str(candidate.get("hash_short") or ""),
                "warnings": [str(item)[:80] for item in candidate.get("warnings", [])[:10]],
            }
            for candidate in candidates[:10]
            if isinstance(candidate, dict)
        ],
    }
