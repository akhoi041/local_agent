from __future__ import annotations

from typing import Any

from talos.arduino import (
    arduino_ide_status,
    discover_arduino_projects,
    environment_profile,
    profile_readiness,
    workspace_map,
    workspace_summary,
)
from talos.codex_runtime import runtime_state_summary, runtime_status
from talos.core import APP_DATA_ROOT, ROOT, load_app_identity, load_build_metadata, load_config
from talos.diagnostics import diagnostics_settings
from talos.event_bus import EVENTS, arduino_event_status
from talos.native_bridge import (
    list_arduino_ide_processes,
    list_arduino_open_workspaces,
    list_arduino_tool_processes,
    list_arduino_workspace_boards,
    list_window_rows,
    native_available,
)
from talos.run_history import latest_verify_for_workspace


def state_payload() -> dict[str, Any]:
    config = load_config()
    app_identity = load_app_identity()
    build_metadata = load_build_metadata(app_identity)
    ide_processes = list_arduino_ide_processes()
    tool_processes = list_arduino_tool_processes()
    window_rows = list_window_rows()
    window_titles = [
        str(row.get("title") or "")
        for row in window_rows
        if str(row.get("title") or "").strip()
    ]
    arduino_projects = discover_arduino_projects(
        config,
        ide_processes=ide_processes,
        tool_processes=tool_processes,
        window_rows=window_rows,
        open_workspaces=list_arduino_open_workspaces(),
        workspace_boards=list_arduino_workspace_boards(),
    )
    arduino_summary = workspace_summary(config)
    arduino_profile = environment_profile(config, str(arduino_summary.get("path") or ""))
    arduino_profile_readiness = profile_readiness(config)
    arduino_map = workspace_map(config, latest_verify_for_workspace(str(arduino_summary.get("path") or "")))
    codex_runtime_status = runtime_status(config)
    return {
        "name": app_identity["display_name"],
        "role": "Codex local control layer",
        "root": str(ROOT),
        "app_data": str(APP_DATA_ROOT),
        "app": app_identity,
        "build": build_metadata,
        "native_available": native_available(),
        "config": {
            "theme": config.get("theme", "light"),
            "arduino_workspace_path": config.get("arduino_workspace_path", ""),
            "arduino_fqbn": config.get("arduino_fqbn", ""),
            "arduino_profiles": config.get("arduino_profiles", {}),
            "diagnostics": diagnostics_settings(config),
        },
        "arduino": arduino_summary,
        "arduino_profile": arduino_profile,
        "arduino_profile_readiness": arduino_profile_readiness,
        "arduino_workspace_map": arduino_map,
        "arduino_ide": arduino_ide_status(
            processes=ide_processes,
            tool_processes=tool_processes,
            titles=window_titles,
        ),
        "arduino_projects": arduino_projects,
        "arduino_events": arduino_event_status(),
        "codex_runtime": runtime_state_summary(codex_runtime_status),
        "tools": [
            "GET /api/state",
            "GET /api/arduino_context",
            "GET /api/arduino_events?since=...",
            "GET /api/arduino_profile",
            "GET /api/arduino_projects",
            "GET /api/arduino_file?path=...",
            "GET /api/arduino_checkpoint?path=...",
            "POST /api/arduino_file",
            "POST /api/arduino_rollback",
            "POST /api/arduino_delete",
            "POST /api/arduino_verify",
            "POST /api/arduino_verify_cancel",
            "POST /api/arduino_verify_cache_clear",
            "POST /api/arduino_profile",
            "POST /api/release_evidence",
            "GET /api/codex_status",
            "GET /api/codex_runtime",
            "GET /api/run_history",
            "GET /api/support_bundle",
            "GET /api/diagnostics_export",
            "GET /api/performance_guardrails",
            "POST /api/codex_reconnect",
            "POST /api/codex_runtime_pin",
            "POST /api/codex_runtime_health",
            "POST /api/codex_context_package",
            "POST /api/codex_message",
            "POST /api/codex_restore_reviews",
            "POST /api/codex_discard_reviews",
            "POST /api/codex_review_patch",
            "POST /api/codex_apply_patch",
            "POST /api/codex_apply_hunk",
            "POST /api/codex_reject_hunk",
            "POST /api/codex_apply_all",
            "POST /api/codex_reject_all",
            "POST /api/codex_verify_patch",
            "POST /api/codex_save_patch",
            "POST /api/codex_reject_patch",
            "POST /api/codex_apply_conflict",
            "POST /api/codex_keep_external",
            "POST /api/codex_merge_draft",
            "POST /api/codex_cancel",
            "POST /api/codex_thread",
            "POST /api/codex_conversation",
        ],
        "events": list(EVENTS),
    }
