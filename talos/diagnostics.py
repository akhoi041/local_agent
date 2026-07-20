from __future__ import annotations

import hashlib
import platform
import uuid
from typing import Any

from talos.codex_runtime import runtime_status, support_bundle_runtime_evidence
from talos.core import APP_DATA_ROOT, now, read_json_file, write_json_file

DIAGNOSTICS_PATH = APP_DATA_ROOT / "diagnostics.json"
DIAGNOSTICS_SCHEMA_VERSION = 1
DIAGNOSTICS_LIMIT = 120

SENSITIVE_KEYS = {
    "content",
    "source",
    "chat",
    "message",
    "prompt",
    "email",
    "account",
    "token",
    "secret",
    "absolute_path",
}

ALLOWED_EVENTS = {
    "app_started",
    "arduino_detected",
    "arduino_missing",
    "workspace_selected",
    "profile_ready",
    "profile_not_ready",
    "verify_passed",
    "verify_failed",
    "verify_cancelled",
    "codex_connected",
    "codex_disconnected",
    "codex_turn_completed",
    "codex_turn_failed",
    "codex_runtime_missing",
    "codex_runtime_changed",
    "codex_runtime_health_failed",
    "codex_runtime_health_cancelled",
    "codex_runtime_pin_changed",
    "codex_runtime_fallback_used",
    "support_bundle_copied",
    "installed_app_smoke",
    "installer_smoke",
    "uninstall_result",
    "crash_marker",
}

def diagnostics_settings(config: dict[str, Any]) -> dict[str, Any]:
    settings = config.get("diagnostics") if isinstance(config.get("diagnostics"), dict) else {}
    return {
        "enabled": bool(settings.get("enabled")),
        "allow_remote_upload": False,
        "storage": str(DIAGNOSTICS_PATH),
        "schema_version": DIAGNOSTICS_SCHEMA_VERSION,
    }

def normalize_event_name(name: str) -> str:
    value = str(name or "").strip().lower().replace("-", "_").replace(" ", "_")
    return value if value in ALLOWED_EVENTS else "app_started"

def _safe_string(value: Any, limit: int = 240) -> str:
    return str(value or "").strip()[:limit]

def _workspace_hash(path_text: str) -> str:
    value = str(path_text or "").strip().lower()
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()[:16]

def sanitize_payload(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    source = payload if isinstance(payload, dict) else {}
    sanitized: dict[str, Any] = {}
    for key, value in source.items():
        clean_key = str(key or "").strip()
        if not clean_key:
            continue
        lowered = clean_key.lower()
        if lowered in SENSITIVE_KEYS:
            continue
        if lowered in {"workspace", "path", "sketch_path"}:
            sanitized["workspace_hash"] = _workspace_hash(str(value))
            continue
        if lowered in {"main_sketch", "sketch", "project"}:
            sanitized["sketch_ext"] = "." + str(value).rsplit(".", 1)[-1].lower() if "." in str(value) else ""
            continue
        if isinstance(value, bool):
            sanitized[clean_key] = value
        elif isinstance(value, (int, float)):
            sanitized[clean_key] = value
        elif isinstance(value, list):
            sanitized[clean_key] = [_safe_string(item, 80) for item in value[:20]]
        elif isinstance(value, dict):
            sanitized[clean_key] = {
                str(inner_key)[:80]: _safe_string(inner_value, 120)
                for inner_key, inner_value in list(value.items())[:20]
                if str(inner_key).lower() not in SENSITIVE_KEYS
            }
        else:
            sanitized[clean_key] = _safe_string(value)
    return sanitized

def _load_state() -> dict[str, Any]:
    data = read_json_file(DIAGNOSTICS_PATH, {})
    if not isinstance(data, dict):
        return {"schema_version": DIAGNOSTICS_SCHEMA_VERSION, "events": []}
    events = data.get("events") if isinstance(data.get("events"), list) else []
    return {"schema_version": DIAGNOSTICS_SCHEMA_VERSION, "events": [event for event in events if isinstance(event, dict)][-DIAGNOSTICS_LIMIT:]}

def record_diagnostic(config: dict[str, Any], event: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    settings = diagnostics_settings(config)
    if not settings["enabled"]:
        return {"ok": False, "recorded": False, "reason": "diagnostics_disabled"}
    state = _load_state()
    entry = {
        "id": f"diag-{uuid.uuid4().hex}",
        "time": now(),
        "event": normalize_event_name(event),
        "payload": sanitize_payload(payload),
    }
    state["events"].append(entry)
    state["events"] = state["events"][-DIAGNOSTICS_LIMIT:]
    write_json_file(DIAGNOSTICS_PATH, state)
    return {"ok": True, "recorded": True, "event": entry}

def diagnostics_export(config: dict[str, Any], app: dict[str, Any], build: dict[str, Any]) -> dict[str, Any]:
    settings = diagnostics_settings(config)
    state = _load_state()
    return {
        "schema_version": DIAGNOSTICS_SCHEMA_VERSION,
        "generated_at": now(),
        "consent": {
            "enabled": settings["enabled"],
            "remote_upload": False,
            "user_preview_required": True,
        },
        "data_policy": {
            "contains_source_code": False,
            "contains_codex_chat": False,
            "contains_account_identifier": False,
            "contains_raw_absolute_paths": False,
            "redacted": True,
        },
        "app": {
            "name": app.get("display_name") or app.get("app_name") or "Talos",
            "version": app.get("version", ""),
            "channel": app.get("channel", ""),
            "publisher": app.get("publisher", ""),
        },
        "runtime": {
            "mode": build.get("mode", ""),
            "version": build.get("version", ""),
            "channel": build.get("channel", ""),
            "platform": platform.platform(),
            "python": build.get("python", ""),
        },
        "codex_runtime": support_bundle_runtime_evidence(runtime_status(config)),
        "events": state["events"],
        "event_count": len(state["events"]),
    }
