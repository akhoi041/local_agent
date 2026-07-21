from __future__ import annotations

import argparse
import json
import mimetypes
import os
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
from talos.arduino_adapter import ArduinoTargetAdapter
from talos.codex_bridge import CODEX_BRIDGE
from talos.contracts import (
    codex_context_contract,
    diagnostics_contract,
    evidence_contract,
    source_file_contract,
    target_context_contract,
    targets_contract,
    verify_result_contract,
)
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
from talos.runtime_core import RUNTIME_CORE
from talos.shell.profile import find_port, static_ui_root
from talos.state_service import state_payload
from talos.targets import TargetRegistry

FRONTEND = static_ui_root()
ARDUINO_TARGET = RUNTIME_CORE.arduino_target
TARGET_REGISTRY = RUNTIME_CORE.target_registry

def target_state(config: dict[str, Any]) -> dict[str, Any]:
    return RUNTIME_CORE.target_state(config)

class TalosWebHandler(BaseHTTPRequestHandler):
    server_version = "TalosWeb/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if self.path == "/api/state":
            self.send_json(RUNTIME_CORE.state_payload())
            return
        if parsed.path == "/api/targets":
            self.send_json(RUNTIME_CORE.targets_payload())
            return
        if parsed.path == "/api/command_palette":
            self.send_json(RUNTIME_CORE.command_palette_payload())
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
            self.send_json(RUNTIME_CORE.arduino_context_payload())
            return
        if parsed.path == "/api/arduino_events":
            self.send_json(RUNTIME_CORE.arduino_events_payload())
            return
        if parsed.path == "/api/arduino_profile":
            self.send_json(RUNTIME_CORE.arduino_profile_payload(query.get("path", [""])[0]))
            return
        if parsed.path == "/api/arduino_projects":
            self.send_json(RUNTIME_CORE.arduino_projects_payload())
            return
        if parsed.path == "/api/arduino_file":
            result = ARDUINO_TARGET.read_file(load_config(), query.get("path", [""])[0])
            self.send_json(source_file_contract(result), HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/arduino_checkpoint":
            result = latest_saved_checkpoint(load_config(), query.get("path", [""])[0])
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/codex_status":
            self.send_json(RUNTIME_CORE.codex_status_payload())
            return
        if parsed.path == "/api/codex_runtime":
            force = query.get("force", ["0"])[0] in {"1", "true", "True", "yes"}
            self.send_json(RUNTIME_CORE.codex_runtime_payload(force=force))
            return
        if parsed.path == "/api/run_history":
            self.send_json(RUNTIME_CORE.run_history_payload(
                workspace=query.get("workspace", [""])[0],
                sketch=query.get("sketch", [""])[0],
                kind=query.get("kind", ["all"])[0],
            ))
            return
        if parsed.path == "/api/support_bundle":
            redacted = query.get("redact", ["1"])[0] not in {"0", "false", "False"}
            self.send_json(RUNTIME_CORE.support_bundle_payload(redact=redacted))
            return
        if parsed.path == "/api/diagnostics_export":
            self.send_json(RUNTIME_CORE.diagnostics_export_payload())
            return
        if parsed.path == "/api/performance_guardrails":
            self.send_json(RUNTIME_CORE.performance_guardrails_payload())
            return
        path = parsed.path
        if path == "/":
            path = "/index.html"
        self.send_static(path)

    def do_POST(self) -> None:
        payload = self.read_json()
        if self.path == "/api/settings":
            self.send_json(RUNTIME_CORE.update_settings(payload))
            return
        if self.path == "/api/codex_runtime_pin":
            result, ok = RUNTIME_CORE.update_runtime_pin(payload)
            self.send_json(result, HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_runtime_health":
            self.send_json(RUNTIME_CORE.runtime_health_payload())
            return
        if self.path == "/api/diagnostics_event":
            result = RUNTIME_CORE.record_diagnostics_event(payload)
            self.send_json(result, HTTPStatus.OK if result.get("ok") or not result.get("recorded") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_workspace":
            self.send_json(RUNTIME_CORE.update_arduino_workspace(payload))
            return
        if self.path == "/api/arduino_profile":
            result = RUNTIME_CORE.update_arduino_profile(payload)
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_verify":
            self.send_json(verify_result_contract(RUNTIME_CORE.verify_arduino(payload)))
            return
        if self.path == "/api/arduino_verify_cancel":
            result = RUNTIME_CORE.cancel_verify()
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.CONFLICT)
            return
        if self.path == "/api/arduino_verify_cache_clear":
            self.send_json(RUNTIME_CORE.clear_verify_cache())
            return
        if self.path == "/api/release_evidence":
            result = RUNTIME_CORE.record_release_evidence(payload)
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_file":
            config = load_config()
            checkpoint_result = create_before_save_checkpoint(config, str(payload.get("path", "")))
            if not checkpoint_result.get("ok"):
                self.send_json(source_file_contract(checkpoint_result), HTTPStatus.BAD_REQUEST)
                return
            result = ARDUINO_TARGET.write_file(
                config,
                str(payload.get("path", "")),
                str(payload.get("content", "")),
            )
            checkpoint = checkpoint_result.get("checkpoint") if isinstance(checkpoint_result.get("checkpoint"), dict) else {}
            checkpoint_id = str(checkpoint.get("id") or "")
            if result.get("ok"):
                checkpoint_saved = mark_checkpoint_saved(checkpoint_id, str(payload.get("content", "")))
                result["checkpoint"] = checkpoint_saved.get("checkpoint") if checkpoint_saved.get("ok") else None
                workspace = ARDUINO_TARGET.workspace_summary(config)
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
                record_rollback(str(ARDUINO_TARGET.workspace_summary(config).get("path") or ""), str(result.get("path") or ""))
                log_event(f"{now()} rolled back Arduino file: {result.get('path')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/arduino_delete":
            result = ARDUINO_TARGET.delete_file(load_config(), str(payload.get("path", "")))
            if result.get("ok"):
                log_event(f"{now()} deleted Arduino file: {result.get('path')}")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_context_package":
            self.send_json(RUNTIME_CORE.codex_context_package(payload))
            return
        if self.path == "/api/codex_message":
            result, ok = RUNTIME_CORE.codex_message(payload)
            self.send_json(result, HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/smoke/codex_patch":
            if os.environ.get("TALOS_SMOKE_HARNESS") != "1":
                self.send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
                return
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            result, ok = RUNTIME_CORE.codex_reconnect()
            self.send_json(result, HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_restore_reviews":
            result = RUNTIME_CORE.restore_codex_reviews()
            self.send_json(source_file_contract(result), HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_discard_reviews":
            result = RUNTIME_CORE.discard_codex_reviews()
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_apply_patch":
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
            result = CODEX_BRIDGE.apply_all(str(payload.get("id", "")), str(workspace.get("path") or ""))
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "turn-applied")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_reject_all":
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
            result = CODEX_BRIDGE.reject_all(str(payload.get("id", "")), str(workspace.get("path") or ""))
            if result.get("ok"):
                record_patch_transition(result.get("patch") or {}, "turn-rejected")
            self.send_json(result, HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_verify_patch":
            config = load_config()
            workspace = ARDUINO_TARGET.workspace_summary(config)
            staged = CODEX_BRIDGE.staged_sandbox_overrides(
                str(payload.get("id", "")),
                str(workspace.get("path") or ""),
            )
            if not staged.get("ok"):
                self.send_json(staged, HTTPStatus.BAD_REQUEST)
                return
            result = ARDUINO_TARGET.verify(config, overrides=staged.get("overrides") or {})
            result["patch_id"] = str(payload.get("id") or "")
            record_verify(result, "codex_patch")
            record_patch_transition(
                staged.get("patch") or {},
                "staged-verified",
                detail={"status": str(result.get("status") or "failed"), "ok": bool(result.get("ok"))},
            )
            log_event(f"{now()} staged Codex patch verify {result.get('status', 'failed')}")
            self.send_json(verify_result_contract(result))
            return
        if self.path == "/api/codex_review_patch":
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            workspace = ARDUINO_TARGET.workspace_summary(load_config())
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
            result, ok = RUNTIME_CORE.cancel_codex_turn()
            self.send_json(result, HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)
            return
        if self.path == "/api/codex_conversation":
            result, ok = RUNTIME_CORE.codex_conversation(str(payload.get("id", "")))
            self.send_json(result, HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST)
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
        RUNTIME_CORE.shutdown()
        server.server_close()

if __name__ == "__main__":
    main()
