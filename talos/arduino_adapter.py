from __future__ import annotations

from pathlib import Path
from typing import Any

from talos import arduino
from talos.checkpoints import rollback_last_checkpoint
from talos.targets import TargetAction, TargetContext, TargetFile, TargetProfile, TargetWorkspace

class ArduinoTargetAdapter:
    target_id = "arduino"
    target_name = "Arduino IDE"
    implemented = True
    capabilities = (
        "detect_projects",
        "open_sketches",
        "active_file",
        "workspace_identity",
        "resolve_workspace",
        "workspace_map",
        "artifact_identity",
        "file_metadata",
        "source_inventory",
        "read_file",
        "write_file",
        "rollback",
        "delete_file",
        "verify_plan",
        "verify",
        "cancel_verify",
        "clear_verify_cache",
        "context_package",
        "environment_profile",
        "profile_payload",
        "release_evidence",
        "diagnostics",
    )
    actions = (
        TargetAction("context", "Build context package", "context"),
        TargetAction("verify", "Verify sketch", "verify"),
        TargetAction("write", "Write source file", "write"),
        TargetAction("rollback", "Rollback saved file", "rollback"),
        TargetAction("diagnostics", "Collect diagnostics", "diagnostics"),
    )

    def discover_projects(self, config: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        return arduino.discover_arduino_projects(config, **kwargs)

    def open_sketches(self, config: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        return self.discover_projects(config, **kwargs)

    def workspace_summary(self, config: dict[str, Any]) -> dict[str, Any]:
        return arduino.workspace_summary(config)

    def resolve_workspace(
        self,
        config: dict[str, Any],
        project: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not project:
            return self.workspace_summary(config)
        root = str(project.get("path") or project.get("folder") or "").strip()
        if not root:
            return self.workspace_summary(config)
        project_config = dict(config)
        project_config["arduino_workspace_path"] = root
        if project.get("fqbn"):
            project_config["arduino_fqbn"] = str(project.get("fqbn") or "")
        return self.workspace_summary(project_config)

    def workspace_context(self, config: dict[str, Any]) -> str:
        return arduino.workspace_context(config)

    def workspace_identity(self, config: dict[str, Any]) -> TargetWorkspace | None:
        summary = self.workspace_summary(config)
        if not summary.get("path"):
            return None
        return self._workspace_from_summary(summary)

    def artifact_identities(self, config: dict[str, Any]) -> tuple[TargetFile, ...]:
        workspace = self.workspace_identity(config)
        return workspace.files if workspace else ()

    def file_metadata(self, config: dict[str, Any]) -> tuple[TargetFile, ...]:
        return self.artifact_identities(config)

    def source_inventory(self, config: dict[str, Any]) -> tuple[TargetFile, ...]:
        return self.file_metadata(config)

    def active_file(self, config: dict[str, Any], path: str | None = None) -> TargetFile | None:
        requested = str(path or config.get("arduino_active_file") or "").replace("\\", "/").strip()
        workspace = self.workspace_identity(config)
        if not workspace:
            return None
        if not requested:
            requested = workspace.main_file.replace("\\", "/")
        for item in workspace.files:
            item_path = item.path.replace("\\", "/")
            if requested in {item_path, item.name, Path(item_path).name}:
                return item
        return None

    def profile_identity(self, config: dict[str, Any]) -> TargetProfile:
        summary = self.workspace_summary(config)
        return self._profile_from_config(config, str(summary.get("path") or ""))

    def verify_plan(self, config: dict[str, Any], overrides: dict[str, str] | None = None) -> dict[str, Any]:
        summary = self.workspace_summary(config)
        profile = self.profile_identity(config)
        readiness = self.profile_readiness(config)
        properties = dict(profile.properties)
        board = self._board_payload(profile)
        fqbn = str((overrides or {}).get("fqbn") or profile.fqbn)
        workspace_path = str(summary.get("path") or "")
        return {
            "target": self.target_id,
            "workspace": workspace_path,
            "main_file": str(summary.get("main_sketch") or ""),
            "fqbn": fqbn,
            "board": board,
            "profile": profile.to_dict(),
            "profile_ready": bool(readiness.get("ready")),
            "serial_port": str(properties.get("serial_port") or ""),
            "baud_rate": self._int_property(properties.get("baud_rate")),
            "build_flags": self._list_property(properties.get("build_flags")),
            "build_properties": self._list_property(properties.get("build_properties")),
            "libraries": self._list_property(properties.get("libraries")),
            "ready": bool(summary.get("valid")) and bool(readiness.get("ready")) and bool(fqbn),
            "readiness": dict(readiness),
            "uses_python_fallback": True,
        }

    def workspace_map(
        self,
        config: dict[str, Any],
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return arduino.workspace_map(config, latest_verify)

    def environment_profile(self, config: dict[str, Any], workspace_path: str) -> dict[str, Any]:
        return arduino.environment_profile(config, workspace_path)

    def profile_readiness(self, config: dict[str, Any]) -> dict[str, Any]:
        return arduino.profile_readiness(config)

    def profile_payload(
        self,
        config: dict[str, Any],
        workspace_path: str = "",
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        effective_config = dict(config)
        if workspace_path:
            effective_config["arduino_workspace_path"] = str(workspace_path)
        summary = self.workspace_summary(effective_config)
        resolved_workspace = str(
            summary.get("path")
            or workspace_path
            or effective_config.get("arduino_workspace_path")
            or ""
        )
        if resolved_workspace:
            effective_config["arduino_workspace_path"] = resolved_workspace
        profile_data = self.environment_profile(effective_config, resolved_workspace)
        readiness = self.profile_readiness(effective_config)
        profile = self._profile_from_config(
            effective_config,
            resolved_workspace,
            profile=profile_data,
            readiness=readiness,
        )
        workspace = self._workspace_from_summary(summary) if summary.get("path") else None
        workspace_map = self.workspace_map(effective_config, latest_verify)
        verify_plan = self.verify_plan(effective_config)
        return {
            "target": self.target_id,
            "workspace_path": resolved_workspace,
            "workspace": workspace.to_dict() if workspace else None,
            "board": self._board_payload(profile),
            "profile": profile.to_dict(),
            "environment_profile": dict(profile_data),
            "profile_readiness": dict(readiness),
            "workspace_map": workspace_map,
            "verify_plan": verify_plan,
            "ready": bool(verify_plan.get("ready")),
        }

    def read_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        return arduino.read_workspace_file(config, path)

    def write_file(self, config: dict[str, Any], path: str, content: str) -> dict[str, Any]:
        return arduino.write_workspace_file(config, path, content)

    def rollback_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        return rollback_last_checkpoint(config, path)

    def delete_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        return arduino.delete_workspace_file(config, path)

    def verify(self, config: dict[str, Any], overrides: dict[str, str] | None = None) -> dict[str, Any]:
        plan = self.verify_plan(config, overrides=overrides)
        result = dict(arduino.run_arduino_compile(config, overrides=overrides))
        result["verify_plan"] = plan
        result.setdefault("profile_readiness", plan.get("readiness") or {})
        result.setdefault("cache", {})
        result.setdefault("timings", {})
        result.setdefault("issues", [])
        result["summary"] = self._verify_summary(result)
        return result

    def diagnostics_hook(
        self,
        config: dict[str, Any],
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        summary = self.workspace_summary(config)
        readiness = self.profile_readiness(config)
        return {
            "target": self.target_id,
            "workspace_ready": bool(summary.get("valid")),
            "workspace": str(summary.get("path") or ""),
            "main_file": str(summary.get("main_sketch") or ""),
            "profile_ready": bool(readiness.get("ready")),
            "latest_verify_status": str((latest_verify or {}).get("status") or ""),
        }

    def cancel_verify(self) -> dict[str, Any]:
        return arduino.cancel_arduino_compile()

    def clear_verify_cache(self) -> dict[str, Any]:
        return arduino.clear_arduino_compile_cache_result()

    def save_environment_profile(
        self,
        config: dict[str, Any],
        workspace_path: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return arduino.save_environment_profile(config, workspace_path, payload)

    def context_package(
        self,
        config: dict[str, Any],
        active_file: dict[str, Any],
        verify_context: str,
        allow_edits: bool,
        message: str,
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        latest = latest_verify if isinstance(latest_verify, dict) else {}
        edit_permission = "stage_changes_in_talos" if allow_edits else "read_only"
        base = arduino.codex_context_package(
            config,
            active_file,
            verify_context,
            allow_edits,
            message,
            latest,
        )
        summary = self.workspace_summary(config)
        workspace_path = str(summary.get("path") or config.get("arduino_workspace_path") or "")
        effective_config = dict(config)
        if workspace_path:
            effective_config["arduino_workspace_path"] = workspace_path

        profile_payload = self.profile_payload(effective_config, workspace_path, latest)
        workspace_map_payload = profile_payload.get("workspace_map")
        if not isinstance(workspace_map_payload, dict):
            workspace_map_payload = self.workspace_map(effective_config, latest)
        profile = profile_payload.get("profile")
        readiness = profile_payload.get("profile_readiness")
        legacy_verify = base.get("verify") if isinstance(base.get("verify"), dict) else {}
        active_payload = base.get("active_file") if isinstance(base.get("active_file"), dict) else {}
        coverage = dict(base.get("coverage") or {})
        coverage.update(
            {
                "adapter_payload": True,
                "workspace_map": bool(workspace_map_payload.get("valid")),
                "active_file": bool(active_payload.get("included")),
                "profile": isinstance(profile, dict) and bool(profile),
                "verify_output": bool(verify_context or latest),
                "edit_permission": True,
            }
        )
        scope = dict(base.get("scope") or {})
        scope["adapter_owned"] = True

        base.update(
            {
                "version": "0.7.0",
                "target": self.target_id,
                "adapter": {
                    "id": self.target_id,
                    "name": self.target_name,
                    "owns": [
                        "workspace_map",
                        "active_file",
                        "verify_output",
                        "profile",
                        "edit_permission",
                    ],
                },
                "workspace_map": workspace_map_payload,
                "profile": profile if isinstance(profile, dict) else {},
                "profile_payload": profile_payload,
                "profile_readiness": readiness if isinstance(readiness, dict) else {},
                "verify": {
                    "summary": legacy_verify.get("summary") or {},
                    "context": verify_context,
                    "latest": latest,
                },
                "verify_output": latest,
                "edit_permission": edit_permission,
                "edit_permission_payload": {
                    "allow_edits": bool(allow_edits),
                    "mode": edit_permission,
                    "save_required": True,
                    "scope": "selected Arduino sketch folder only",
                },
                "coverage": coverage,
                "scope": scope,
            }
        )
        return base

    def context(
        self,
        config: dict[str, Any],
        latest_verify: dict[str, Any] | None = None,
        projects: list[dict[str, Any]] | None = None,
        summary: dict[str, Any] | None = None,
        profile: dict[str, Any] | None = None,
        profile_readiness: dict[str, Any] | None = None,
        workspace_map: dict[str, Any] | None = None,
    ) -> TargetContext:
        summary_data = summary if summary is not None else self.workspace_summary(config)
        workspace_path = str(summary_data.get("path") or "")
        selected = self._workspace_from_summary(summary_data) if summary_data.get("path") else None
        profile_data = self._profile_from_config(
            config,
            workspace_path,
            profile=profile,
            readiness=profile_readiness,
        )
        workspace_map_data = workspace_map if workspace_map is not None else self.workspace_map(config, latest_verify)
        return TargetContext(
            target_id=self.target_id,
            target_name=self.target_name,
            capabilities=self.capabilities,
            actions=self.actions,
            workspaces=tuple(self._workspace_from_project(item) for item in (projects if projects is not None else self.open_sketches(config))),
            selected_workspace=selected,
            profile=profile_data,
            diagnostics=self.diagnostics_hook(config, latest_verify),
            raw={
                "workspace_summary": summary_data,
                "workspace_map": workspace_map_data,
            },
        )

    def _workspace_from_summary(self, summary: dict[str, Any]) -> TargetWorkspace:
        root = str(summary.get("path") or "")
        files = tuple(self._file_from_summary_item(item, str(summary.get("main_sketch") or "")) for item in summary.get("files", []))
        main_file = str(summary.get("main_sketch") or "")
        return TargetWorkspace(
            id=root or main_file,
            name=main_file or Path(root).name,
            root=root,
            valid=bool(summary.get("valid")),
            main_file=main_file,
            files=files,
            message=str(summary.get("message") or ""),
            metadata={
                "fqbn": str(summary.get("fqbn") or ""),
                "file_count": int(summary.get("file_count") or len(files)),
            },
        )

    def _workspace_from_project(self, project: dict[str, Any]) -> TargetWorkspace:
        root = str(project.get("path") or project.get("folder") or "")
        main_file = str(project.get("sketch") or project.get("main_sketch") or "")
        return TargetWorkspace(
            id=root or main_file or str(project.get("title") or ""),
            name=main_file or Path(root).name,
            root=root,
            valid=bool(project.get("valid", True)),
            main_file=main_file,
            files=(),
            message=str(project.get("message") or ""),
            metadata=dict(project),
        )

    def _file_from_summary_item(self, item: dict[str, Any], main_file: str) -> TargetFile:
        path = str(item.get("path") or item.get("name") or "")
        name = str(item.get("name") or Path(path).name)
        suffix = Path(name).suffix.lower().lstrip(".") or "source"
        return TargetFile(
            path=path,
            name=name,
            kind=suffix,
            lines=int(item.get("lines") or 0),
            bytes=int(item.get("bytes") or 0),
            role="main" if name == main_file or path == main_file else "tab",
            metadata={key: value for key, value in item.items() if key not in {"path", "name", "lines", "bytes"}},
        )

    @staticmethod
    def _list_property(value: Any) -> list[Any]:
        if isinstance(value, list):
            return list(value)
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        return []

    @staticmethod
    def _int_property(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def _board_payload(self, profile: TargetProfile) -> dict[str, Any]:
        base_fqbn = arduino.board_identity(profile.fqbn)
        display_name = profile.display_name or base_fqbn or profile.fqbn or "Arduino board"
        return {
            "display_name": display_name,
            "fqbn": profile.fqbn,
            "base_fqbn": base_fqbn,
            "has_fqbn_options": bool(profile.fqbn and profile.fqbn != base_fqbn),
        }

    @staticmethod
    def _verify_summary(result: dict[str, Any]) -> dict[str, Any]:
        existing = result.get("summary")
        if isinstance(existing, dict):
            return dict(existing)
        cache = result.get("cache") if isinstance(result.get("cache"), dict) else {}
        runtime = result.get("runtime") if isinstance(result.get("runtime"), dict) else {}
        issues = result.get("issues") if isinstance(result.get("issues"), list) else []
        return {
            "ok": bool(result.get("ok")),
            "status": str(result.get("status") or ""),
            "cache_hit": bool(cache.get("hit")),
            "cache_key": str(cache.get("key") or ""),
            "runtime_status": str(runtime.get("status") or ""),
            "issue_count": len(issues),
            "program": result.get("program"),
            "dynamic": result.get("dynamic"),
        }

    def _profile_from_config(
        self,
        config: dict[str, Any],
        workspace_path: str,
        profile: dict[str, Any] | None = None,
        readiness: dict[str, Any] | None = None,
    ) -> TargetProfile:
        profile_data = profile if profile is not None else self.environment_profile(config, workspace_path)
        readiness_data = readiness if readiness is not None else self.profile_readiness(config)
        fqbn = str(profile_data.get("fqbn") or config.get("arduino_fqbn") or "")
        display_name = str(
            profile_data.get("board_name")
            or profile_data.get("board")
            or config.get("arduino_board_name")
            or arduino.board_identity(fqbn)
            or fqbn
            or "Arduino board"
        )
        return TargetProfile(
            display_name=display_name,
            fqbn=fqbn,
            properties=dict(profile_data),
            readiness=dict(readiness_data),
        )
