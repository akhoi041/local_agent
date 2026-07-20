from __future__ import annotations

from typing import Any

from talos.arduino import workspace_summary
from talos.codex_bridge import CODEX_BRIDGE
from talos.codex_runtime import PROVIDER_NONE, runtime_state_summary, runtime_status
from talos.core import load_config
from talos.diagnostics import record_diagnostic
from talos.run_history import record_runtime_event

def runtime_gate(runtime_summary: dict[str, Any]) -> dict[str, Any]:
    health = runtime_summary.get("health") if isinstance(runtime_summary.get("health"), dict) else {}
    provider = str(runtime_summary.get("provider") or PROVIDER_NONE)
    health_status = str(health.get("status") or "unknown")
    warnings = runtime_summary.get("warnings") if isinstance(runtime_summary.get("warnings"), list) else []
    base = {
        "ready": False,
        "blocked": True,
        "retryable": True,
        "reconnect_allowed": False,
        "manual_replay_required": True,
        "warnings": list(warnings),
    }
    if provider == PROVIDER_NONE:
        return {
            **base,
            "code": "runtime_missing",
            "title": "Codex runtime missing",
            "detail": "Select or pin a Codex runtime in Settings before sending a Codex turn.",
        }
    if runtime_summary.get("changed"):
        return {
            **base,
            "code": "runtime_changed",
            "title": "Codex runtime changed",
            "detail": "The pinned Codex runtime changed. Review and pin the runtime again before sending.",
        }
    if not bool(health.get("ready")):
        return {
            **base,
            "code": f"runtime_{health_status}",
            "title": "Codex runtime not ready",
            "detail": f"Runtime health is {health_status}. Refresh health or select another runtime before sending.",
        }
    readiness_warnings = list(warnings)
    if not bool(health.get("auth_ready")):
        readiness_warnings.append("auth_readiness_unverified")
    if not bool(health.get("app_server_ready")):
        readiness_warnings.append("app_server_readiness_unverified")
    return {
        "ready": True,
        "blocked": False,
        "retryable": False,
        "reconnect_allowed": True,
        "manual_replay_required": True,
        "code": "runtime_ready",
        "title": "Codex runtime ready",
        "detail": "Runtime executable is selected. Auth and app-server readiness are verified when the runtime exposes them.",
        "warnings": readiness_warnings,
    }

def selected_runtime_payload(
    config: dict[str, Any] | None = None,
    *,
    force: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    config = config if config is not None else load_config()
    full_status = runtime_status(config, force=force)
    summary = runtime_state_summary(full_status)
    gate = runtime_gate(summary)
    active = full_status.get("active") if isinstance(full_status.get("active"), dict) else {}
    CODEX_BRIDGE.set_runtime_path(str(active.get("path") or ""))
    return full_status, summary, gate

def runtime_event_detail(status: dict[str, Any]) -> dict[str, Any]:
    active = status.get("active") if isinstance(status.get("active"), dict) else {}
    health = status.get("health") if isinstance(status.get("health"), dict) else {}
    candidates = status.get("candidates") if isinstance(status.get("candidates"), list) else []
    warning_sources = [
        active.get("warnings") if isinstance(active.get("warnings"), list) else [],
        status.get("warnings") if isinstance(status.get("warnings"), list) else [],
        health.get("warnings") if isinstance(health.get("warnings"), list) else [],
    ]
    warnings = sorted({str(item) for source in warning_sources for item in source if str(item).strip()})
    return {
        "provider": str(active.get("provider") or PROVIDER_NONE),
        "display_path": str(active.get("display_path") or ""),
        "version": str(active.get("version") or health.get("version") or ""),
        "hash_short": str(active.get("hash_short") or ""),
        "pinned": bool(active.get("pinned")),
        "changed": bool(active.get("changed")),
        "candidate_count": len(candidates),
        "health_status": str(health.get("status") or "unknown"),
        "ready": bool(health.get("ready")),
        "warnings": warnings[:12],
    }

def runtime_outcomes(status: dict[str, Any]) -> list[tuple[str, str]]:
    active = status.get("active") if isinstance(status.get("active"), dict) else {}
    health = status.get("health") if isinstance(status.get("health"), dict) else {}
    provider = str(active.get("provider") or PROVIDER_NONE)
    health_status = str(health.get("status") or "unknown")
    warnings = set(runtime_event_detail(status)["warnings"])
    outcomes: list[tuple[str, str]] = []
    if provider == PROVIDER_NONE or health_status == "missing":
        outcomes.append(("runtime_missing", "codex_runtime_missing"))
    if bool(active.get("changed")):
        outcomes.append(("runtime_changed", "codex_runtime_changed"))
    if health_status == "cancelled":
        outcomes.append(("runtime_health_cancelled", "codex_runtime_health_cancelled"))
    elif provider != PROVIDER_NONE and not bool(health.get("ready")):
        outcomes.append(("runtime_health_failed", "codex_runtime_health_failed"))
    if provider == "vscode_extension_adjacent" or "extension_adjacent_fallback" in warnings:
        outcomes.append(("runtime_fallback_used", "codex_runtime_fallback_used"))
    return outcomes

def record_runtime_status(config: dict[str, Any], status: dict[str, Any], action: str = "") -> None:
    workspace = str(workspace_summary(config).get("path") or "")
    detail = runtime_event_detail(status)
    if action:
        record_runtime_event(workspace, action, detail)
    for outcome, diagnostic in runtime_outcomes(status):
        record_runtime_event(workspace, outcome, detail)
        record_diagnostic(config, diagnostic, detail)

def codex_status_payload(*, start: bool = True, force_runtime: bool = False) -> dict[str, Any]:
    _, runtime_summary, gate = selected_runtime_payload(load_config(), force=force_runtime)
    status = CODEX_BRIDGE.status(start=start and not gate["blocked"])
    status["codex_runtime"] = runtime_summary
    status["runtime_gate"] = gate
    if gate["blocked"]:
        connection = status.get("connection") if isinstance(status.get("connection"), dict) else {}
        status["ok"] = False
        status["runtime_blocked"] = True
        status["error"] = gate["detail"]
        status["connection"] = {
            **connection,
            "state": "runtime_blocked",
            "runtime_code": gate["code"],
            "can_retry_now": bool(gate.get("retryable")),
        }
        task_state = status.get("task_state") if isinstance(status.get("task_state"), dict) else {}
        status["task_state"] = {
            **task_state,
            "state": "runtime_blocked",
            "detail": gate["detail"],
            "replay_guard": "manual_send_required",
        }
    return status
