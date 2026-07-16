from __future__ import annotations

import threading
import uuid
from typing import Any

from talos.core import APP_DATA_ROOT, migrate_state_document, now, read_json_file, write_json_file

RUN_HISTORY_PATH = APP_DATA_ROOT / "run_history.json"
RUN_HISTORY_LIMIT = 40
RUN_HISTORY_SCHEMA_VERSION = 1
SUPPORT_HISTORY_LIMIT = 20
RUN_HISTORY_LOCK = threading.Lock()

def _load_events() -> list[dict[str, Any]]:
    data = read_json_file(RUN_HISTORY_PATH, {})
    state = migrate_state_document(
        RUN_HISTORY_PATH,
        data,
        collection_key="events",
        target_schema_version=RUN_HISTORY_SCHEMA_VERSION,
        label="history-migration",
    )
    events = state["events"]
    return [event for event in (events or []) if isinstance(event, dict)][-RUN_HISTORY_LIMIT:]

def _store_event(event: dict[str, Any]) -> dict[str, Any]:
    with RUN_HISTORY_LOCK:
        events = _load_events()
        events.append(event)
        write_json_file(RUN_HISTORY_PATH, {"events": events[-RUN_HISTORY_LIMIT:]})
    return event

def record_verify(result: dict[str, Any], source: str = "manual") -> dict[str, Any]:
    summary = result.get("summary") if isinstance(result.get("summary"), dict) else {}
    event = {
        "id": f"verify-{uuid.uuid4().hex}",
        "type": "verify",
        "time": now(),
        "source": source if source in {"manual", "codex_patch"} else "manual",
        "workspace": str(summary.get("path") or ""),
        "main_sketch": str(summary.get("main_sketch") or ""),
        "fqbn": str(summary.get("fqbn") or ""),
        "status": str(result.get("status") or ("passed" if result.get("ok") else "failed")),
        "ok": bool(result.get("ok")),
        "result": {
            "ok": bool(result.get("ok")),
            "status": str(result.get("status") or ""),
            "command": str(result.get("command") or "")[:12000],
            "sandbox": str(result.get("sandbox") or ""),
            "output": str(result.get("output") or "")[:50000],
            "memory": result.get("memory") or {},
            "libraries": result.get("libraries") or [],
            "platforms": result.get("platforms") or [],
            "issues": result.get("issues") or [],
            "issue_context": str(result.get("issue_context") or "")[:12000],
            "profile_readiness": result.get("profile_readiness") or {},
            "timings": result.get("timings") or {},
            "cache": result.get("cache") or {},
        },
    }
    return _store_event(event)

def record_release_evidence(
    workspace_map: dict[str, Any],
    profile_readiness: dict[str, Any],
    verify_result: dict[str, Any],
    blocked_cases: list[str] | None = None,
    release: str = "0.4.0-pre-alpha",
) -> dict[str, Any]:
    summary = verify_result.get("summary") if isinstance(verify_result.get("summary"), dict) else {}
    result = verify_result.get("result") if isinstance(verify_result.get("result"), dict) else verify_result
    event = {
        "id": f"release-evidence-{uuid.uuid4().hex}",
        "type": "release_evidence",
        "schema_version": 1,
        "release": str(release or "0.4.0-pre-alpha"),
        "time": now(),
        "workspace": str(workspace_map.get("workspace") or summary.get("path") or ""),
        "main_sketch": str(workspace_map.get("main_sketch") or summary.get("main_sketch") or ""),
        "status": str(result.get("status") or ("passed" if result.get("ok") else "failed")),
        "ok": bool(result.get("ok")),
        "profile_ready": bool(profile_readiness.get("ready")),
        "workspace_map": workspace_map,
        "profile_readiness": profile_readiness,
        "verify_summary": {
            "status": str(result.get("status") or ""),
            "ok": bool(result.get("ok")),
            "memory": result.get("memory") or {},
            "libraries": result.get("libraries") or [],
            "platforms": result.get("platforms") or [],
            "issues": result.get("issues") or [],
            "timings": result.get("timings") or {},
            "cache": result.get("cache") or {},
        },
        "blocked_cases": [str(item) for item in (blocked_cases or []) if str(item).strip()],
    }
    return _store_event(event)

def record_patch(patch: dict[str, Any]) -> dict[str, Any]:
    with RUN_HISTORY_LOCK:
        events = _load_events()
        event = _upsert_patch_event(events, patch)
        _store_events(events)
    return event

def record_patch_transition(
    patch: dict[str, Any],
    action: str,
    relative_path: str = "",
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with RUN_HISTORY_LOCK:
        events = _load_events()
        event = _upsert_patch_event(events, patch)
        entry = {"time": now(), "action": action}
        if relative_path:
            entry["path"] = relative_path
        if detail:
            entry["detail"] = detail
        event.setdefault("timeline", []).append(entry)
        event["time"] = entry["time"]
        _store_events(events)
    return event

def record_codex_turn(
    workspace: str,
    message: str,
    outcome: str,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "id": f"codex-turn-{uuid.uuid4().hex}",
        "type": "codex_turn",
        "time": now(),
        "source": "codex",
        "workspace": str(workspace or ""),
        "status": str(outcome or "unknown"),
        "message": str(message or "")[:2000],
        "detail": detail or {},
    }
    return _store_event(event)

def record_patch_verification(workspace: str, result: dict[str, Any]) -> dict[str, Any] | None:
    with RUN_HISTORY_LOCK:
        events = _load_events()
        event = next(
            (
                item for item in reversed(events)
                if item.get("type") == "patch" and item.get("workspace") == workspace
            ),
            None,
        )
        if event is None:
            return None
        entry = {
            "time": now(),
            "action": "verified",
            "detail": {"status": str(result.get("status") or "failed"), "ok": bool(result.get("ok"))},
        }
        event.setdefault("timeline", []).append(entry)
        event["time"] = entry["time"]
        _store_events(events)
    return event

def record_rollback(workspace: str, relative_path: str) -> dict[str, Any] | None:
    with RUN_HISTORY_LOCK:
        events = _load_events()
        event = next(
            (
                item for item in reversed(events)
                if item.get("type") == "patch"
                and item.get("workspace") == workspace
                and any(file.get("path") == relative_path for file in item.get("files") or [])
            ),
            None,
        )
        if event is None:
            return None
        entry = {"time": now(), "action": "rolled-back", "path": relative_path}
        event.setdefault("timeline", []).append(entry)
        event["time"] = entry["time"]
        _store_events(events)
    return event

def _patch_files(patch: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": str(file.get("path") or ""),
            "kind": str(file.get("kind") or "update"),
            "status": str(file.get("review_status") or "staged"),
            "hunks": len(file.get("hunks") or []),
        }
        for file in (patch.get("files") or [])
        if isinstance(file, dict)
    ]

def _upsert_patch_event(events: list[dict[str, Any]], patch: dict[str, Any]) -> dict[str, Any]:
    patch_id = str(patch.get("id") or "")
    event = next((item for item in reversed(events) if item.get("type") == "patch" and item.get("patch_id") == patch_id), None)
    if event is None:
        event = {
            "id": f"patch-event-{uuid.uuid4().hex}",
            "type": "patch",
            "time": str(patch.get("time") or now()),
            "source": "codex",
            "workspace": str(patch.get("workspace") or ""),
            "patch_id": patch_id,
            "turn_id": str(patch.get("turn_id") or ""),
            "timeline": [{"time": str(patch.get("time") or now()), "action": "staged"}],
        }
        events.append(event)
    event["status"] = str(patch.get("review_status") or "staged")
    event["files"] = _patch_files(patch)
    return event

def _store_events(events: list[dict[str, Any]]) -> None:
    write_json_file(RUN_HISTORY_PATH, {
        "schema_version": RUN_HISTORY_SCHEMA_VERSION,
        "events": events[-RUN_HISTORY_LIMIT:],
    })

def run_history() -> list[dict[str, Any]]:
    with RUN_HISTORY_LOCK:
        return list(reversed(_load_events()))

def _event_matches_workspace(event: dict[str, Any], workspace: str) -> bool:
    target = str(workspace or "").strip().lower()
    if not target:
        return True
    return str(event.get("workspace") or "").strip().lower() == target

def _event_matches_sketch(event: dict[str, Any], sketch: str) -> bool:
    target = str(sketch or "").strip().lower()
    if not target:
        return True
    if str(event.get("main_sketch") or "").strip().lower() == target:
        return True
    for file in event.get("files") or []:
        if isinstance(file, dict) and str(file.get("path") or "").strip().lower() == target:
            return True
    detail = event.get("detail") if isinstance(event.get("detail"), dict) else {}
    return str(detail.get("active_file") or "").strip().lower() == target

def _event_matches_kind(event: dict[str, Any], kind: str) -> bool:
    target = str(kind or "all").strip().lower()
    if target in {"", "all"}:
        return True
    event_type = str(event.get("type") or "")
    if target == "verify":
        return event_type == "verify"
    if target in {"codex", "codex_turn"}:
        return event_type == "codex_turn"
    if target in {"saved", "conflict", "rollback"}:
        return event_type == "patch" and any(
            str(entry.get("action") or "").lower() in {
                "saved" if target == "saved" else "",
                "rolled-back" if target == "rollback" else "",
                "conflict-applied-to-editor" if target == "conflict" else "",
            }
            or (target == "conflict" and "conflict" in str(entry.get("action") or "").lower())
            for entry in event.get("timeline") or []
            if isinstance(entry, dict)
        )
    if target == "patch":
        return event_type == "patch"
    if target == "release":
        return event_type == "release_evidence"
    return event_type == target

def filtered_run_history(
    *,
    workspace: str = "",
    sketch: str = "",
    kind: str = "all",
    limit: int = RUN_HISTORY_LIMIT,
) -> list[dict[str, Any]]:
    events = [
        event for event in run_history()
        if _event_matches_workspace(event, workspace)
        and _event_matches_sketch(event, sketch)
        and _event_matches_kind(event, kind)
    ]
    return events[:max(1, min(int(limit or RUN_HISTORY_LIMIT), RUN_HISTORY_LIMIT))]

def latest_verify_for_workspace(workspace: str) -> dict[str, Any] | None:
    target = str(workspace or "")
    if not target:
        return None
    with RUN_HISTORY_LOCK:
        return next(
            (
                event for event in reversed(_load_events())
                if event.get("type") == "verify" and event.get("workspace") == target
            ),
            None,
        )

def _redact_value(value: Any, tokens: dict[str, str]) -> Any:
    if isinstance(value, str):
        result = value
        for raw, replacement in sorted(tokens.items(), key=lambda item: len(item[0]), reverse=True):
            if raw:
                result = result.replace(raw, replacement)
        return result
    if isinstance(value, list):
        return [_redact_value(item, tokens) for item in value]
    if isinstance(value, dict):
        return {key: _redact_value(item, tokens) for key, item in value.items()}
    return value

def support_bundle(
    *,
    app: dict[str, Any],
    build: dict[str, Any],
    workspace_summary: dict[str, Any],
    profile: dict[str, Any],
    profile_readiness: dict[str, Any],
    latest_verify: dict[str, Any] | None,
    history: list[dict[str, Any]] | None = None,
    redact: bool = True,
) -> dict[str, Any]:
    workspace = str(workspace_summary.get("path") or "")
    events = history if history is not None else filtered_run_history(workspace=workspace, limit=SUPPORT_HISTORY_LIMIT)
    bundle = {
        "schema_version": 1,
        "generated_at": now(),
        "redacted": bool(redact),
        "support_scope": {
            "workspace_scoped": bool(workspace),
            "history_limit": SUPPORT_HISTORY_LIMIT,
            "privacy_default": "redacted" if redact else "full-paths",
            "includes_source_code": False,
            "includes_codex_chat": False,
        },
        "included_history_filters": ["verify", "codex", "saved", "conflict", "rollback", "release"],
        "app": app,
        "build": build,
        "workspace": workspace_summary,
        "profile": profile,
        "profile_readiness": profile_readiness,
        "latest_verify": latest_verify or {},
        "recent_history": events[:SUPPORT_HISTORY_LIMIT],
        "sharing_note": "Paths are redacted by default. Use full paths only when debugging requires exact local locations.",
    }
    if not redact:
        return bundle
    tokens = {
        workspace: "<workspace>",
        str(build.get("root") or ""): "<app-root>",
        str(build.get("bundle_root") or ""): "<bundle-root>",
        str(build.get("app_data") or ""): "<app-data>",
        str(build.get("executable") or ""): "<python-executable>",
    }
    return _redact_value(bundle, tokens)
