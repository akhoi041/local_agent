from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

from talos.core import load_config, now
from talos.runtime_discovery import (
    FALLBACK_EXTENSION_ADJACENT,
    FALLBACK_NONE,
    PROVIDER_EXTENSION_ADJACENT,
    PROVIDER_NONE,
    PROVIDER_STANDALONE_PATH,
    PROVIDER_USER_SELECTED_PATH,
    RUNTIME_CONFIG_KEY,
    discover_runtime_candidates,
    file_sha256,
    redact_path,
    runtime_config,
    with_runtime_defaults,
)

_HEALTH_CACHE: dict[tuple[str, str, float], dict[str, Any]] = {}

def _safe_items(items: Any, limit: int = 8, width: int = 120) -> list[str]:
    source = items if isinstance(items, list) else []
    return [str(item).strip()[:width] for item in source[:limit] if str(item).strip()]

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
