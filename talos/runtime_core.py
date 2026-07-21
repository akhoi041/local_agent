from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from talos.arduino_adapter import ArduinoTargetAdapter
from talos.contracts import (
    command_palette_contract,
    codex_context_contract,
    diagnostics_contract,
    evidence_contract,
    runtime_status_contract,
    settings_contract,
    target_context_contract,
    targets_contract,
    verify_result_contract,
    workspace_map_contract,
)
from talos.core import (
    load_app_identity,
    load_build_metadata,
    load_config,
    now,
    save_config,
)
from talos.diagnostics import diagnostics_export, record_diagnostic
from talos.event_bus import arduino_event_status, log_event
from talos.performance import performance_guardrails
from talos.run_history import (
    filtered_run_history,
    latest_verify_for_workspace,
    record_codex_turn,
    record_patch_verification,
    record_release_evidence,
    record_verify,
    support_bundle,
)
from talos.runtime_provider import CodexRuntimeProvider, PlaceholderRuntimeProvider, RuntimeProviderRegistry
from talos.runtime_service import record_runtime_status as record_runtime_status_service, runtime_event_detail
from talos.state_service import state_payload as build_state_payload
from talos.targets import TargetRegistry

COMMAND_PALETTE_COMMANDS: tuple[dict[str, str], ...] = (
    {"id": "workspace.refresh", "title": "Refresh Workspace", "shortcut": "F5", "scope": "workspace"},
    {"id": "file.save", "title": "Save File", "shortcut": "Ctrl+S", "scope": "editor"},
    {"id": "file.save_verify", "title": "Save + Verify", "shortcut": "Ctrl+Shift+S", "scope": "editor"},
    {"id": "file.undo_saved", "title": "Undo Saved File", "shortcut": "Ctrl+Z", "scope": "editor"},
    {"id": "editor.find", "title": "Find In File", "shortcut": "Ctrl+F", "scope": "editor"},
    {"id": "arduino.verify", "title": "Verify Sandbox", "shortcut": "F6", "scope": "arduino"},
    {"id": "arduino.cancel_verify", "title": "Cancel Verify", "shortcut": "", "scope": "arduino"},
    {"id": "codex.open", "title": "Open Codex Panel", "shortcut": "", "scope": "codex"},
    {"id": "support.bundle", "title": "Copy Support Bundle", "shortcut": "", "scope": "support"},
    {"id": "settings.open", "title": "Open Settings", "shortcut": "", "scope": "settings"},
)

@dataclass
class TalosRuntimeCore:
    """Central owner for Talos app state and orchestration.

    The current implementation is still Python, but server handlers now depend on
    this boundary instead of directly coordinating Arduino, Codex, diagnostics,
    config, and run-history helpers.
    """

    codex_provider: CodexRuntimeProvider = field(default_factory=CodexRuntimeProvider)
    arduino_target: ArduinoTargetAdapter = field(default_factory=ArduinoTargetAdapter)
    target_registry: TargetRegistry = field(default_factory=TargetRegistry)
    runtime_registry: RuntimeProviderRegistry = field(default_factory=RuntimeProviderRegistry)

    def __post_init__(self) -> None:
        self.target_registry.register(self.arduino_target)
        self.runtime_registry.register(self.codex_provider)
        self.runtime_registry.register(PlaceholderRuntimeProvider("claude", "Claude"))

    def load_config(self) -> dict[str, Any]:
        return load_config()

    def save_config(self, config: dict[str, Any]) -> None:
        save_config(config)

    def latest_verify_for_workspace(self, workspace: str) -> dict[str, Any] | None:
        return latest_verify_for_workspace(workspace)

    def codex_state(self) -> dict[str, Any]:
        return self.codex_provider.bridge_state()

    def codex_runtime_status(self, config: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
        return self.codex_provider.status(config, force=force)

    def state_payload(self) -> dict[str, Any]:
        return build_state_payload(self)

    def target_state(self, config: dict[str, Any] | None = None) -> dict[str, Any]:
        config = config or self.load_config()
        summary = self.arduino_target.workspace_summary(config)
        latest_verify = self.latest_verify_for_workspace(str(summary.get("path") or ""))
        return {
            "active": self.arduino_target.target_id,
            "registered": self.target_registry.metadata(),
            "contexts": [self.arduino_target.context(config, latest_verify).to_dict()],
        }

    def targets_payload(self) -> dict[str, Any]:
        return targets_contract({"ok": True, "targets": self.target_state()})

    def arduino_context_payload(self) -> dict[str, Any]:
        config = self.load_config()
        summary = self.arduino_target.workspace_summary(config)
        workspace_path = str(summary.get("path") or "")
        latest_verify = self.latest_verify_for_workspace(workspace_path)
        workspace_map = self.arduino_target.workspace_map(config, latest_verify)
        profile = self.arduino_target.environment_profile(config, workspace_path)
        profile_readiness = self.arduino_target.profile_readiness(config)
        return target_context_contract({
            "ok": True,
            "context": self.arduino_target.workspace_context(config),
            "arduino": summary,
            "workspace_map": workspace_map,
            "workspace_map_contract": workspace_map_contract({"ok": True, "workspace_map": workspace_map}),
            "target": self.arduino_target.context(
                config,
                latest_verify,
                summary=summary,
                profile=profile,
                profile_readiness=profile_readiness,
                workspace_map=workspace_map,
            ).to_dict(),
        })

    def arduino_profile_payload(self, workspace_path: str = "") -> dict[str, Any]:
        config = self.load_config()
        path = workspace_path or str(config.get("arduino_workspace_path") or "")
        return {"ok": True, "profile": self.arduino_target.environment_profile(config, path)}

    def arduino_projects_payload(self) -> dict[str, Any]:
        config = self.load_config()
        return {"ok": True, "projects": self.arduino_target.discover_projects(config)}

    def arduino_events_payload(self) -> dict[str, Any]:
        return {"ok": True, **arduino_event_status()}

    def codex_status_payload(self, *, start: bool = False) -> dict[str, Any]:
        return self.codex_provider.app_server_status(start=start)

    def codex_runtime_payload(self, *, force: bool = False) -> dict[str, Any]:
        return runtime_status_contract({
            "ok": True,
            "runtime": self.codex_runtime_status(self.load_config(), force=force),
            "providers": self.runtime_registry.metadata(),
        })

    def command_palette_payload(self) -> dict[str, Any]:
        return command_palette_contract({"ok": True, "commands": [dict(command) for command in COMMAND_PALETTE_COMMANDS]})

    def run_history_payload(self, *, workspace: str = "", sketch: str = "", kind: str = "all") -> dict[str, Any]:
        return {"ok": True, "events": filtered_run_history(workspace=workspace, sketch=sketch, kind=kind)}

    def support_bundle_payload(self, *, redact: bool = True) -> dict[str, Any]:
        config = self.load_config()
        app_identity = load_app_identity()
        build_metadata = load_build_metadata(app_identity)
        summary = self.arduino_target.workspace_summary(config)
        workspace = str(summary.get("path") or "")
        latest_verify = self.latest_verify_for_workspace(workspace)
        bundle = support_bundle(
            app=app_identity,
            build=build_metadata,
            workspace_summary=summary,
            profile=self.arduino_target.environment_profile(config, workspace),
            profile_readiness=self.arduino_target.profile_readiness(config),
            latest_verify=latest_verify,
            history=filtered_run_history(workspace=workspace),
            redact=redact,
        )
        bundle["performance"] = performance_guardrails()
        bundle["codex_runtime"] = self.codex_provider.support_evidence(config)
        return {"ok": True, "bundle": bundle}

    def diagnostics_export_payload(self) -> dict[str, Any]:
        config = self.load_config()
        app_identity = load_app_identity()
        build_metadata = load_build_metadata(app_identity)
        return diagnostics_contract({
            "ok": True,
            "diagnostics": diagnostics_export(config, app_identity, build_metadata),
        })

    def performance_guardrails_payload(self) -> dict[str, Any]:
        return {"ok": True, "performance": performance_guardrails()}

    def update_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        for key in ("theme", "arduino_workspace_path", "arduino_fqbn"):
            if key in payload:
                config[key] = str(payload[key]).strip()
        if isinstance(payload.get("diagnostics"), dict):
            diagnostics = payload["diagnostics"]
            config["diagnostics"] = {
                "enabled": bool(diagnostics.get("enabled")),
                "allow_remote_upload": False,
            }
        self.save_config(config)
        log_event(f"{now()} saved settings")
        saved_config = self.load_config()
        return settings_contract({"ok": True, "config": saved_config, "settings": saved_config})

    def update_runtime_pin(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        config = self.load_config()
        result = self.codex_provider.pin(
            config,
            path_text=str(payload.get("path") or ""),
            clear=bool(payload.get("clear")),
        )
        if not result.get("ok"):
            return result, False
        self.save_config(result["config"])
        status = self.codex_provider.status(self.load_config(), force=True)
        action = str(result.get("action") or "updated")
        log_event(f"{now()} codex runtime pin {action}")
        record_runtime_status_service(result["config"], status, f"pin_{action}")
        record_diagnostic(result["config"], "codex_runtime_pin_changed", runtime_event_detail(status))
        return runtime_status_contract({"ok": True, "action": action, "runtime": status}), True

    def runtime_health_payload(self) -> dict[str, Any]:
        config = self.load_config()
        status = self.codex_provider.status(config, force=True)
        log_event(f"{now()} codex runtime health: {status.get('health', {}).get('status', 'unknown')}")
        record_runtime_status_service(config, status, "health_checked")
        return runtime_status_contract({"ok": True, "runtime": status})

    def record_diagnostics_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        return record_diagnostic(
            self.load_config(),
            str(payload.get("event") or ""),
            payload.get("payload") if isinstance(payload.get("payload"), dict) else {},
        )

    def update_arduino_workspace(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        config["arduino_workspace_path"] = str(payload.get("path", "")).strip()
        config["arduino_fqbn"] = str(payload.get("fqbn", config.get("arduino_fqbn", ""))).strip()
        self.save_config(config)
        summary = self.arduino_target.workspace_summary(config)
        log_event(f"{now()} configured Arduino workspace: {summary.get('path') or 'none'}")
        return {"ok": summary["valid"], "arduino": summary}

    def update_arduino_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        workspace_path = str(payload.get("path", config.get("arduino_workspace_path", ""))).strip()
        result = self.arduino_target.save_environment_profile(config, workspace_path, payload)
        if not result.get("ok"):
            return result
        if str(config.get("arduino_workspace_path") or "").strip() == workspace_path:
            profile_fqbn = str(result["profile"].get("fqbn") or "")
            if profile_fqbn:
                config["arduino_fqbn"] = profile_fqbn
        self.save_config(config)
        log_event(f"{now()} saved Arduino environment profile: {result.get('path')}")
        return verify_result_contract(result)

    def verify_arduino(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        if "path" in payload:
            config["arduino_workspace_path"] = str(payload.get("path", "")).strip()
        if "fqbn" in payload:
            config["arduino_fqbn"] = str(payload.get("fqbn", "")).strip()
        self.save_config(config)
        source = str(payload.get("source") or "manual")
        override = payload.get("editor_override") if isinstance(payload.get("editor_override"), dict) else {}
        override_path = str(override.get("path") or "").replace("\\", "/") if override else ""
        overrides = {override_path: str(override.get("content") or "")} if override_path else None
        result = self.arduino_target.verify(config, overrides=overrides)
        summary = self.arduino_target.workspace_summary(config)
        result["verify_context"] = {
            "source": source,
            "workspace": str(summary.get("path") or ""),
            "active_file": override_path or str(payload.get("active_file") or ""),
            "fqbn": str(summary.get("fqbn") or ""),
            "editor_override": bool(override_path),
        }
        record_verify(result, source)
        if source == "codex_patch":
            record_patch_verification(str(summary.get("path") or ""), result)
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
        return result

    def cancel_verify(self) -> dict[str, Any]:
        result = self.arduino_target.cancel_verify()
        if result.get("ok"):
            log_event(f"{now()} Arduino verify cancellation requested")
        return result

    def clear_verify_cache(self) -> dict[str, Any]:
        result = self.arduino_target.clear_verify_cache()
        log_event(f"{now()} cleared Arduino compile cache ({result.get('cleared')} entries)")
        return result

    def record_release_evidence(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        summary = self.arduino_target.workspace_summary(config)
        workspace = str(summary.get("path") or "")
        latest_verify = self.latest_verify_for_workspace(workspace)
        verify_result = payload.get("verify_result") if isinstance(payload.get("verify_result"), dict) else latest_verify
        if not isinstance(verify_result, dict):
            return evidence_contract({"ok": False, "error": "Run Verify Sandbox before recording release evidence."})
        readiness = self.arduino_target.profile_readiness(config)
        arduino_map = self.arduino_target.workspace_map(config, latest_verify)
        evidence = record_release_evidence(
            arduino_map,
            readiness,
            verify_result,
            payload.get("blocked_cases") if isinstance(payload.get("blocked_cases"), list) else [],
            str(payload.get("release") or "0.4.0-pre-alpha"),
        )
        log_event(f"{now()} recorded Arduino release evidence: {evidence.get('status')}")
        return evidence_contract({"ok": True, "evidence": evidence})

    def codex_context_package(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        workspace = self.arduino_target.workspace_summary(config)
        latest_verify = self.latest_verify_for_workspace(str(workspace.get("path") or ""))
        package = self.arduino_target.context_package(
            config,
            payload.get("active_file") if isinstance(payload.get("active_file"), dict) else {},
            str(payload.get("verify_context", "")),
            bool(payload.get("allow_edits", True)),
            str(payload.get("message", "")),
            latest_verify,
        )
        return codex_context_contract({"ok": True, "package": package})

    def codex_message(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        config = self.load_config()
        _, runtime_summary, gate = self.codex_provider.selected_payload(config)
        workspace = self.arduino_target.workspace_summary(config)
        if gate["blocked"]:
            result = {
                "ok": False,
                "error": gate["detail"],
                "runtime_blocked": True,
                "runtime_gate": gate,
                "codex_runtime": runtime_summary,
                "status": self.codex_provider.app_server_status(config=config, start=False),
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
            return result, False
        workspace["map"] = self.arduino_target.workspace_map(
            config,
            self.latest_verify_for_workspace(str(workspace.get("path") or "")),
        )
        active_file = payload.get("active_file") if isinstance(payload.get("active_file"), dict) else {}
        context_package = self.arduino_target.context_package(
            config,
            active_file,
            str(payload.get("verify_context", "")),
            bool(payload.get("allow_edits", True)),
            str(payload.get("message", "")),
            self.latest_verify_for_workspace(str(workspace.get("path") or "")),
        )
        active_context = context_package.get("active_file") if isinstance(context_package.get("active_file"), dict) else {}
        result = self.codex_provider.send_message(
            str(payload.get("message", "")),
            workspace,
            active_context,
            str(payload.get("verify_context", "")),
            bool(payload.get("allow_edits", True)),
        )
        record_codex_turn(
            str(workspace.get("path") or ""),
            str(payload.get("message", "")),
            "started" if result.get("ok") else "blocked",
            {
                "allow_edits": bool(payload.get("allow_edits", True)),
                "active_file": str(active_context.get("path") or ""),
                "context_active_file_included": bool(active_context.get("included")),
                "context_replay_guard": "manual_send_required",
                "profile_fqbn": str(workspace.get("fqbn") or ""),
                "error": str(result.get("error") or ""),
            },
        )
        if result.get("ok"):
            log_event(f"{now()} started Codex turn")
        return result, bool(result.get("ok"))

    def codex_reconnect(self) -> tuple[dict[str, Any], bool]:
        config = self.load_config()
        _, runtime_summary, gate = self.codex_provider.selected_payload(config, force=True)
        workspace = self.arduino_target.workspace_summary(config)
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
            return result, False
        result = self.codex_provider.reconnect()
        if result.get("ok"):
            record_codex_turn(
                str(workspace.get("path") or ""),
                "",
                "reconnect",
                {"status": str(result.get("status") or ""), "replay_guard": "manual_send_required"},
            )
            log_event(f"{now()} Codex reconnect requested")
        return result, bool(result.get("ok"))

    def cancel_codex_turn(self) -> tuple[dict[str, Any], bool]:
        workspace = self.arduino_target.workspace_summary(self.load_config())
        result = self.codex_provider.cancel_turn()
        if result.get("ok"):
            record_codex_turn(str(workspace.get("path") or ""), "", "cancelled", {"replay_guard": "manual_send_required"})
        return result, bool(result.get("ok"))

    def codex_conversation(self, conversation_id: str) -> tuple[dict[str, Any], bool]:
        result = self.codex_provider.select_conversation(conversation_id)
        if result.get("ok"):
            workspace = self.arduino_target.workspace_summary(self.load_config())
            record_codex_turn(str(workspace.get("path") or ""), "", "conversation_loaded", {"conversation_id": conversation_id})
        return result, bool(result.get("ok"))

    def restore_codex_reviews(self) -> dict[str, Any]:
        result = self.codex_provider.restore_reviews()
        if result.get("ok"):
            log_event(f"{now()} restored unfinished Codex reviews")
        return result

    def discard_codex_reviews(self) -> dict[str, Any]:
        result = self.codex_provider.discard_reviews()
        if result.get("ok"):
            log_event(f"{now()} discarded unfinished Codex reviews")
        return result

    def shutdown(self) -> None:
        self.codex_provider.shutdown()

RUNTIME_CORE = TalosRuntimeCore()
