from __future__ import annotations

import threading
import uuid
from typing import Any

from talos.core import ROOT, now, read_json_file, write_json_file

RUN_HISTORY_PATH = ROOT / "config" / "run_history.json"
RUN_HISTORY_LIMIT = 40
RUN_HISTORY_LOCK = threading.Lock()

def _load_events() -> list[dict[str, Any]]:
    data = read_json_file(RUN_HISTORY_PATH, {})
    events = data.get("events") if isinstance(data, dict) else []
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
        },
    }
    return _store_event(event)

def record_patch(patch: dict[str, Any]) -> dict[str, Any]:
    event = {
        "id": f"patch-event-{uuid.uuid4().hex}",
        "type": "patch",
        "time": str(patch.get("time") or now()),
        "source": "codex",
        "workspace": str(patch.get("workspace") or ""),
        "status": "applied",
        "patch_id": str(patch.get("id") or ""),
        "files": [
            {
                "path": str(file.get("path") or ""),
                "kind": str(file.get("kind") or "update"),
            }
            for file in (patch.get("files") or [])
            if isinstance(file, dict)
        ],
    }
    return _store_event(event)

def run_history() -> list[dict[str, Any]]:
    with RUN_HISTORY_LOCK:
        return list(reversed(_load_events()))
