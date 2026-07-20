from __future__ import annotations

from pathlib import Path
from typing import Any

from talos import arduino
from talos.targets import TargetContext, TargetFile, TargetProfile, TargetWorkspace

class ArduinoTargetAdapter:
    target_id = "arduino"
    target_name = "Arduino IDE"
    capabilities = (
        "detect_projects",
        "workspace_map",
        "source_inventory",
        "read_file",
        "write_file",
        "delete_file",
        "verify",
        "cancel_verify",
        "clear_verify_cache",
        "context_package",
        "environment_profile",
        "release_evidence",
    )

    def discover_projects(self, config: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        return arduino.discover_arduino_projects(config, **kwargs)

    def workspace_summary(self, config: dict[str, Any]) -> dict[str, Any]:
        return arduino.workspace_summary(config)

    def workspace_context(self, config: dict[str, Any]) -> str:
        return arduino.workspace_context(config)

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

    def read_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        return arduino.read_workspace_file(config, path)

    def write_file(self, config: dict[str, Any], path: str, content: str) -> dict[str, Any]:
        return arduino.write_workspace_file(config, path, content)

    def delete_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        return arduino.delete_workspace_file(config, path)

    def verify(self, config: dict[str, Any], overrides: dict[str, str] | None = None) -> dict[str, Any]:
        return arduino.run_arduino_compile(config, overrides=overrides)

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
        return arduino.codex_context_package(
            config,
            active_file,
            verify_context,
            allow_edits,
            message,
            latest_verify,
        )

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
            workspaces=tuple(self._workspace_from_project(item) for item in (projects if projects is not None else self.discover_projects(config))),
            selected_workspace=selected,
            profile=profile_data,
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
        display_name = str(profile_data.get("board_name") or profile_data.get("board") or fqbn or "Arduino board")
        return TargetProfile(
            display_name=display_name,
            fqbn=fqbn,
            properties=dict(profile_data),
            readiness=dict(readiness_data),
        )
