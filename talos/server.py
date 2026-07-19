from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from talos.core import (
    ROOT,
    load_build_metadata,
    load_app_identity,
    load_config,
    now,
    save_config,
)
from talos.arduino import (
    cancel_arduino_compile,
    clear_arduino_compile_cache_result,
    codex_context_package,
    delete_workspace_file,
    discover_arduino_projects,
    environment_profile,
    profile_readiness,
    read_workspace_file,
    run_arduino_compile,
    save_environment_profile,
    workspace_context,
    workspace_map,
    workspace_summary,
    write_workspace_file,
)
from talos.codex_bridge import CODEX_BRIDGE
from talos.diagnostics import diagnostics_export, diagnostics_settings, record_diagnostic
from talos.codex_runtime import (
    runtime_status,
    support_bundle_runtime_evidence,
    update_runtime_pin,
)
from talos.event_bus import EVENTS, arduino_event_status, log_event, start_arduino_event_watcher, stop_arduino_event_watcher
from talos.performance import performance_guardrails
from talos.checkpoints import (
    create_before_save_checkpoint,
    discard_checkpoint,
    latest_saved_checkpoint,
    mark_checkpoint_saved,
    rollback_last_checkpoint,
)
from talos.native_bridge import (
    native_available,
)
from talos.run_history import (
    filtered_run_history,
    latest_verify_for_workspace,
    record_codex_turn,
    record_patch_transition,
    record_patch_verification,
    record_release_evidence,
    record_rollback,
    record_runtime_event,
    record_verify,
    run_history,
    support_bundle,
)
from talos.runtime_service import (
    codex_status_payload,
    record_runtime_status,
    runtime_event_detail,
    runtime_gate,
    runtime_outcomes,
    selected_runtime_payload,
)
from talos.state_service import state_payload

ASSET_ROOT = Path(getattr(sys, "_MEIPASS", ROOT))
FRONTEND = ASSET_ROOT / "web_frontend" if getattr(sys, "frozen", False) else ROOT / "ui" / "web_frontend"

class TalosWebHandler(BaseHTTPRequestHandler):
    server_version = "TalosWeb/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if self.path == "/api/state":
            self.send_json(state_payload())
            return
        if parsed.path == "/api/health":
            app_identity = load_app_identity()
            build_metadata = load_build_metadata(app_identity)
            self.send_json({
                "ok": True,
                "service": app_identity["display_name"],
                "role": "Codex local control layer",
                "app": app_identity,
                "build": build_metadata,
            })
            return
        if parsed.path == "/api/arduino_context":
            config = load_config()
            summary = workspace_summary(config)
            self.send_json({
                "ok": True,
                "context": workspace_context(config),
                "arduino": summary,
                "workspace_map": workspace_map(config, latest_verify_for_workspace(str(summary.get("path") or ""))),
            })
            return
        if parsed.path == "/api/arduino_events":
            self.send_json({"ok": True, **arduino_event_status()})
            return
        if parsed.path == "/api/arduino_profile":
            config = load_config()
            workspace_path = query.get("path", [str(config.get("arduino_workspace_path") or "")])[0]
            self.send_json({"ok": True, "profile": environment_profile(config, workspace_path)})
            return
        if parsed.path == "/api/arduino_projects":
            config = load_config()
            self.send_json({"ok": True, "projects": discover_arduino_projects(config)})
            return
        if parsed.path == "/api/arduino_file":
            result = read_workspace_file(load_config(), query.get("path", [""])[0])
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/arduino_checkpoint":
            result = latest_saved_checkpoint(load_config(), query.get("path", [""])[0])
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/codex_status":
            self.send_json(codex_status_payload())
            return
        if parsed.path == "/api/codex_runtime":
            config = load_config()
            force = query.get("force", ["0"])[0] in {"1", "true", "True", "yes"}
            self.send_json({"ok": True, "runtime": runtime_status(config, force=force)})
            return
        if parsed.path == "/api/run_history":
            self.send_json({
                "ok": True,
                "events": filtered_run_history(
                    workspace=query.get("workspace", [""])[0],
                    sketch=query.get("sketch", [""])[0],
                    kind=query.get("kind", ["all"])[0],
                ),
            })
            return
        if parsed.path == "/api/support_bundle":
            config = load_config()
            app_identity = load_app_identity()
            build_metadata = load_build_metadata(app_identity)
            summary = workspace_summary(config)
            workspace = str(summary.get("path") or "")
            latest_verify = latest_verify_for_workspace(workspace)
            redacted = query.get("redact", ["1"])[0] not in {"0", "false", "False"}
            bundle = support_bundle(
                app=app_identity,
                build=build_metadata,
                workspace_summary=summary,
                profile=environment_profile(config, workspace),
                profile_readiness=profile_readiness(config),
                latest_verify=latest_verify,
                history=filtered_run_history(workspace=workspace),
                redact=redacted,
            )
            bundle["performance"] = performance_guardrails()
            bundle["codex_runtime"] = support_bundle_runtime_evidence(runtime_status(config))
            self.send_json({"ok": True, "bundle": bundle})
            return
        if parsed.path == "/api/diagnostics_export":
            config = load_config()
            app_identity = load_app_identity()
            build_metadata = load_build_metadata(app_identity)
            self.send_json({"ok": True, "diagnostics": diagnostics_export(config, app_identity, build_metadata)})
            return
        if parsed.path == "/api/performance_guardrails":
            self.send_json({"ok": True, "performance": performance_guardrails()})
            return
        path = parsed.path
        if path == "/":
            path = "/index.html"
        self.send_static(path)

    def do_POST(self) -> None:
        payload = self.read_json()
        if self.path == "/api/settings":
            config = load_config()
            for key in ("theme", "arduino_workspace_path", "arduino_fqbn"):
                if key in payload:
                    config[key] = str(payload[key]).strip()
            if isinstance(payload.get("diagnostics"), dict):
                diagnostics = payload["diagnostics"]
                config["diagnostics"] = {
                    "enabled": bool(diagnostics.get("enabled")),
                    "allow_remote_upload": False,
                }
            save_config(config)
            log_event(f"{now()} saved settings")
            self.send_json({"ok": True, "config": load_config()})
            return
        if self.path == "/api/codex_runtime_pin":
            config = load_config()
            result = update_runtime_pin(
                config,
                path_text=str(payload.get("path") or ""),
                clear=bool(payload.get("clear")),
            )
            if not result.get("ok"):
                self.send_json(result, HTTPStatus.BAD_REQUEST)
                return
            save_config(result["config"])
            status = runtime_status(load_config(), force=True)
            action = str(result.get("action") or "updated")
            log_event(f"{now()} codex runtime pin {action}")
            record_runtime_status(result["config"], status, f"pin_{action}")
            record_diagnostic(result["config"], "codex_runtime_pin_changed", runtime_event_detail(status))
            self.send_json({"ok": True, "action": action, "runtime": status})
            return
        if self.path == "/api/codex_runtime_health":
            config = load_config()
            status = runtime_status(config, force=True)
            log_event(f"{now()} codex runtime health: {status.get('health', {}).get('status', 'unknown')}")
            record_runtime_status(config, status, "health_checked")
            self.send_json({"ok": True, "runtime": status})
            return
        if self.path == "/api/diagnostics_event":
            config = load_config()
            result = record_diagnostic(
                config,
                str(payload.get("event") or ""),
                payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
            )
            self.send_json(result, HTTPStatus.OK if result.get("ok") or not result.get("recorded") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_workspace":
            config = load_config()
            config["arduino_workspace_path"] = str(payload.get("path", "")).strip()
            config["arduino_fqbn"] = str(payload.get("fqbn", config.get("arduino_fqbn", ""))).strip()
            save_config(config)
            summary = workspace_summary(config)
            log_event(f"{now()} configured Arduino workspace: {summary.get('path') or 'none'}")
            self.send_json({"ok": summary["valid"], "arduino": summary})
            return
        if self.path == "/api/arduino_profile":
            config = load_config()
            workspace_path = str(payload.get("path", config.get("arduino_workspace_path", ""))).strip()
            result = save_environment_profile(config, workspace_path, payload)
            if not result.get("ok"):
                self.send_json(result, HTTPStatus.BAD_REQUEST)
                return
            if str(config.get("arduino_workspace_path") or "").strip() == workspace_path:
                profile_fqbn = str(result["profile"].get("fqbn") or "")
                if profile_fqbn:
                    config["arduino_fqbn"] = profile_fqbn
            save_config(config)
            log_event(f"{now()} saved Arduino environment profile: {result.get('path')}")
            self.send_json(result)
            return
        if self.path == "/api/arduino_verify":
            config = load_config()
            if "path" in payload:
                config["arduino_workspace_path"] = str(payload.get("path", "")).strip()
            if "fqbn" in payload:
                config["arduino_fqbn"] = str(payload.get("fqbn", "")).strip()
            save_config(config)
            source = str(payload.get("source") or "manual")
            override = payload.get("editor_override") if isinstance(payload.get("editor_override"), dict) else {}
            override_path = str(override.get("path") or "").replace("\\", "/") if override else ""
            overrides = {override_path: str(override.get("content") or "")} if override_path else None
            result = run_arduino_compile(config, overrides=overrides)
            summary = workspace_summary(config)
            result["verify_context"] = {
                "source": source,
                "workspace": str(summary.get("path") or ""),
                "active_file": override_path or str(payload.get("active_file") or ""),
                "fqbn": str(summary.get("fqbn") or ""),
                "editor_override": bool(override_path),
            }
            record_verify(result, source)
            if source == "codex_patch":
                record_patch_verification(str(workspace_summary(config).get("path") or ""), result)
            status = "passed" if result.get("ok") else result.get("status", "failed")
            record_diagnostic(config, "verify_passed" if result.get("ok") else "verify_failed", {
                "workspace": summary.get("path", ""),
                "main_sketch": summary.get("main_sketch", ""),
                "fqbn_family": ":".join(str(summary.get("fqbn") or "").split(":")[:3]),
                "status": status,
                "source": source,
                "timings": result.get("timings") or {},
                "cache": result.get("cache") or {},
                "issue_count": len(result.get("issues") or []),
                "profile_ready": bool((result.get("profile_readiness") or {}).get("ready")),
            })
            log_event(f"{now()} Arduino verify {status}")
            self.send_json(result)
            return
        if self.path == "/api/arduino_verify_cancel":
            result = cancel_arduino_compile()
            if result.get("ok"):
                log_event(f"{now()} Arduino verify cancellation requested")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.CONFLICT)
            return
        if self.path == "/api/arduino_verify_cache_clear":
            result = clear_arduino_compile_cache_result()
            log_event(f"{now()} cleared Arduino compile cache ({result.get('cleared')} entries)")
            self.send_json(result)
            return
        if self.path == "/api/release_evidence":
            config = load_config()
            summary = workspace_summary(config)
            workspace = str(summary.get("path") or "")
            latest_verify = latest_verify_for_workspace(workspace)
            verify_result = payload.get("verify_result") if isinstance(payload.get("verify_result"), dict) else latest_verify
            if not isinstance(verify_result, dict):
                self.send_json({"ok": False, "error": "Run Verify Sandbox before recording release evidence."}, HTTPStatus.BAD_REQUEST)
                return
            readiness = profile_readiness(config)
            arduino_map = workspace_map(config, latest_verify)
            evidence = record_release_evidence(
                arduino_map,
                readiness,
                verify_result,
                payload.get("blocked_cases") if isinstance(payload.get("blocked_cases"), list) else [],
                str(payload.get("release") or "0.4.0-pre-alpha"),
            )
            log_event(f"{now()} recorded Arduino release evidence: {evidence.get('status')}")
            self.send_json({"ok": True, "evidence": evidence})
            return
        if self.path == "/api/arduino_file":
            config = load_config()
            checkpoint_result = create_before_save_checkpoint(config, str(payload.get("path", "")))
            if not checkpoint_result.get("ok"):
                self.send_json(checkpoint_result, HTTPStatus.BAD_REQUEST)
                return
            result = write_workspace_file(
                config,
                str(payload.get("path", "")),
                str(payload.get("content", "")),
            )
            checkpoint = checkpoint_result.get("checkpoint") if isinstance(checkpoint_result.get("checkpoint"), dict) else {}
            checkpoint_id = str(checkpoint.get("id") or "")
            if result.get("ok"):
                checkpoint_saved = mark_checkpoint_saved(checkpoint_id, str(payload.get("content", "")))
                result["checkpoint"] = checkpoint_saved.get("checkpoint") if checkpoint_saved.get("ok") else None
                workspace = workspace_summary(config)
                patch_result = CODEX_BRIDGE.mark_patch_saved(str(workspace.get("path") or ""), str(result.get("path") or ""))
                if patch_result.get("saved"):
                    record_patch_transition(patch_result.get("patch") or {}, "saved", str(result.get("path") or ""))
                log_event(f"{now()} wrote Arduino file: {result.get('path')}")
            elif checkpoint_id:
                discard_checkpoint(checkpoint_id)
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_rollback":
            config = load_config()
            result = rollback_last_checkpoint(config, str(payload.get("path", "")))
            if result.get("ok"):
                record_rollback(str(workspace_summary(config).get("path") or ""), str(result.get("path") or ""))
                log_event(f"{now()} rolled back Arduino file: {result.get('path')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_delete":
            result = delete_workspace_file(load_config(), str(payload.get("path", "")))
            if result.get("ok"):
                log_event(f"{now()} deleted Arduino file: {result.get('path')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_context_package":
            workspace = workspace_summary(load_config())
            latest_verify = latest_verify_for_workspace(str(workspace.get("path") or ""))
            package = codex_context_package(
                load_config(),
                payload.get("active_file") if isinstance(payload.get("active_file"), dict) else {},
                str(payload.get("verify_context", "")),
                bool(payload.get("allow_edits", True)),
                str(payload.get("message", "")),
                latest_verify,
            )
            self.send_json({"ok": True, "package": package})
            return
        if self.path == "/api/codex_message":
            config = load_config()
            _, runtime_summary, gate = selected_runtime_payload(config)
            workspace = workspace_summary(config)
            if gate["blocked"]:
                result = {
                    "ok": False,
                    "error": gate["detail"],
                    "runtime_blocked": True,
                    "runtime_gate": gate,
                    "codex_runtime": runtime_summary,
                    "status": codex_status_payload(start=False),
                }
                record_codex_turn(
                    str(workspace.get("path") or ""),
                    str(payload.get("message", "")),
                    "runtime_blocked",
                    {
                        "runtime_code": gate["code"],
                        "runtime_detail": gate["detail"],
                        "context_replay_guard": "manual_send_required",
                    },
                )
                self.send_json(result, HTTPStatus.BAD_REQUEST)
                return
            workspace["map"] = workspace_map(
                config,
                latest_verify_for_workspace(str(workspace.get("path") or "")),
            )
            active_file = payload.get("active_file")
            if not isinstance(active_file, dict):
                active_file = {}
            context_package = codex_context_package(
                config,
                active_file,
                str(payload.get("verify_context", "")),
                bool(payload.get("allow_edits", True)),
                str(payload.get("message", "")),
                latest_verify_for_workspace(str(workspace.get("path") or "")),
            )
            active_file = context_package.get("active_file") if isinstance(context_package.get("active_file"), dict) else {}
            result = CODEX_BRIDGE.send_message(
                str(payload.get("message", "")),
                workspace,
                active_file,
                str(payload.get("verify_context", "")),
                bool(payload.get("allow_edits", True)),
            )
            record_codex_turn(
                str(workspace.get("path") or ""),
                str(payload.get("message", "")),
                "started" if result.get("ok") else "blocked",
                {
                    "allow_edits": bool(payload.get("allow_edits", True)),
                    "active_file": str(active_file.get("path") or ""),
                    "context_active_file_included": bool(active_file.get("included")),
                    "context_replay_guard": "manual_send_required",
                    "profile_fqbn": str(workspace.get("fqbn") or ""),
                    "error": str(result.get("error") or ""),
                },
            )
            if result.get("ok"):
                log_event(f"{now()} started Codex turn")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/smoke/codex_patch":
            if os.environ.get("TALOS_SMOKE_HARNESS") != "1":
                self.send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
                return
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.create_smoke_patch(
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
                str(payload.get("content", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "smoke-staged", str(payload.get("path") or ""))
                log_event(f"{now()} prepared smoke Codex patch: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_reconnect":
            config = load_config()
            _, runtime_summary, gate = selected_runtime_payload(config, force=True)
            workspace = workspace_summary(config)
            if gate["blocked"]:
                result = {
                    "ok": False,
                    "error": gate["detail"],
                    "status": "runtime_blocked",
                    "runtime_blocked": True,
                    "runtime_gate": gate,
                    "codex_runtime": runtime_summary,
                }
                record_codex_turn(
                    str(workspace.get("path") or ""),
                    "",
                    "runtime_reconnect_blocked",
                    {
                        "runtime_code": gate["code"],
                        "runtime_detail": gate["detail"],
                        "replay_guard": "manual_send_required",
                    },
                )
                self.send_json(result, HTTPStatus.BAD_REQUEST)
                return
            result = CODEX_BRIDGE.reconnect()
            if result.get("ok"):
                record_codex_turn(
                    str(workspace.get("path") or ""),
                    "",
                    "reconnect",
                    {
                        "status": str(result.get("status") or ""),
                        "replay_guard": "manual_send_required",
                    },
                )
                log_event(f"{now()} Codex reconnect requested")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_restore_reviews":
            result = CODEX_BRIDGE.restore_reviews()
            if result.get("ok"):
                log_event(f"{now()} restored unfinished Codex reviews")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_discard_reviews":
            result = CODEX_BRIDGE.discard_reviews()
            if result.get("ok"):
                log_event(f"{now()} discarded unfinished Codex reviews")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_apply_patch":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.apply_patch(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "editor-applied", str(payload.get("path") or ""))
                log_event(f"{now()} applied Codex patch to Talos editor: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_apply_hunk":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.apply_hunk(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
                str(payload.get("hunk_id", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "hunk-applied", str(payload.get("path") or ""), {"hunk_id": str(payload.get("hunk_id") or "")})
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_reject_hunk":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.reject_hunk(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
                str(payload.get("hunk_id", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "hunk-rejected", str(payload.get("path") or ""), {"hunk_id": str(payload.get("hunk_id") or "")})
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_apply_all":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.apply_all(str(payload.get("id", "")), str(workspace.get("path") or ""))
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "turn-applied")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_reject_all":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.reject_all(str(payload.get("id", "")), str(workspace.get("path") or ""))
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "turn-rejected")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_verify_patch":
            config = load_config()
            workspace = workspace_summary(config)
            staged = CODEX_BRIDGE.staged_sandbox_overrides(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
            )
            if not staged.get("ok"):
                self.send_json(staged, HTTPStatus.BAD_REQUEST)
                return
            result = run_arduino_compile(config, overrides=staged.get("overrides") or {})
            result["patch_id"] = str(payload.get("id") or "")
            record_verify(result, "codex_patch")
            record_patch_transition(
                staged.get("patch") or {},
                "staged-verified",
                detail={"status": str(result.get("status") or "failed"), "ok": bool(result.get("ok"))},
            )
            log_event(f"{now()} staged Codex patch verify {result.get('status', 'failed')}")
            self.send_json(result)
            return
        if self.path == "/api/codex_review_patch":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.review_patch(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok"):
                log_event(f"{now()} opened Codex change review: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_save_patch":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.mark_patch_saved(
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok") and result.get("saved") is not False:
                log_event(f"{now()} saved Codex change: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_reject_patch":
            result = CODEX_BRIDGE.reject_patch(str(payload.get("id", "")), str(payload.get("path", "")))
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "rejected", str(payload.get("path") or ""))
                log_event(f"{now()} rejected Codex patch: {payload.get('id', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_apply_conflict":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.apply_conflict_to_editor(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "conflict-applied-to-editor", str(payload.get("path") or ""))
                log_event(f"{now()} applied Codex conflict to Talos editor: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_keep_external":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.keep_external_conflict(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "kept-external", str(payload.get("path") or ""))
                log_event(f"{now()} kept external Arduino file for Codex conflict: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_merge_draft":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.draft_conflict_merge(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
                str(payload.get("path", "")),
            )
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "merge-draft", str(payload.get("path") or ""))
                log_event(f"{now()} created Codex merge draft: {payload.get('path', '')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_thread":
            result = CODEX_BRIDGE.new_thread()
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_cancel":
            workspace = workspace_summary(load_config())
            result = CODEX_BRIDGE.cancel_turn()
            if result.get("ok"):
                record_codex_turn(
                    str(workspace.get("path") or ""),
                    "",
                    "cancelled",
                    {"replay_guard": "manual_send_required"},
                )
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_conversation":
            result = CODEX_BRIDGE.select_conversation(str(payload.get("id", "")))
            if result.get("ok"):
                workspace = workspace_summary(load_config())
                record_codex_turn(
                    str(workspace.get("path") or ""),
                    "",
                    "conversation_loaded",
                    {"conversation_id": str(payload.get("id", ""))},
                )
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_static(self, raw_path: str) -> None:
        relative = unquote(raw_path.lstrip("/"))
        path = (FRONTEND / relative).resolve()
        frontend_root = FRONTEND.resolve()
        try:
            path.relative_to(frontend_root)
        except ValueError:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.name == "index.html":
            theme = str(load_config().get("theme", "light"))
            data = path.read_text(encoding="utf-8").replace("__TALOS_THEME__", theme).encode("utf-8")
        else:
            data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, _format: str, *_args: Any) -> None:
        return

def find_port(host: str, start_port: int) -> int:
    for port in range(start_port, start_port + 20):
        try:
            server = ThreadingHTTPServer((host, port), TalosWebHandler)
        except OSError:
            continue
        server.server_close()
        return port
    raise RuntimeError(f"No available port found from {start_port}.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Talos web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    args = parser.parse_args()

    port = find_port(args.host, args.port)
    server = ThreadingHTTPServer((args.host, port), TalosWebHandler)
    start_arduino_event_watcher()
    print(f"Talos Web UI: http://{args.host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_arduino_event_watcher()
        CODEX_BRIDGE.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()
