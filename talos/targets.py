from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

TARGET_ADAPTER_REQUIRED_METHODS = (
    "discover_projects",
    "workspace_summary",
    "workspace_identity",
    "file_metadata",
    "active_file",
    "profile_identity",
    "profile_payload",
    "verify_plan",
    "verify",
    "cancel_verify",
    "clear_verify_cache",
    "context_package",
    "read_file",
    "write_file",
    "rollback_file",
    "context",
)

@dataclass(frozen=True)
class TargetAction:
    id: str
    label: str
    kind: str
    implemented: bool = True
    destructive: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "kind": self.kind,
            "implemented": self.implemented,
            "destructive": self.destructive,
            "metadata": dict(self.metadata),
        }

@dataclass(frozen=True)
class TargetFile:
    path: str
    name: str
    kind: str = "source"
    lines: int = 0
    bytes: int = 0
    role: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "kind": self.kind,
            "lines": self.lines,
            "bytes": self.bytes,
            "role": self.role,
            "metadata": dict(self.metadata),
        }

@dataclass(frozen=True)
class TargetWorkspace:
    id: str
    name: str
    root: str
    valid: bool
    main_file: str = ""
    files: tuple[TargetFile, ...] = ()
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "root": self.root,
            "valid": self.valid,
            "main_file": self.main_file,
            "files": [item.to_dict() for item in self.files],
            "message": self.message,
            "metadata": dict(self.metadata),
        }

@dataclass(frozen=True)
class TargetProfile:
    display_name: str
    fqbn: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    readiness: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "display_name": self.display_name,
            "fqbn": self.fqbn,
            "properties": dict(self.properties),
            "readiness": dict(self.readiness),
        }

@dataclass(frozen=True)
class TargetContext:
    target_id: str
    target_name: str
    capabilities: tuple[str, ...]
    actions: tuple[TargetAction, ...] = ()
    workspaces: tuple[TargetWorkspace, ...] = ()
    selected_workspace: TargetWorkspace | None = None
    profile: TargetProfile | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_name": self.target_name,
            "capabilities": list(self.capabilities),
            "actions": [item.to_dict() for item in self.actions],
            "workspaces": [item.to_dict() for item in self.workspaces],
            "selected_workspace": self.selected_workspace.to_dict() if self.selected_workspace else None,
            "profile": self.profile.to_dict() if self.profile else None,
            "diagnostics": dict(self.diagnostics),
            "raw": dict(self.raw),
        }

class TargetAdapter(Protocol):
    target_id: str
    target_name: str
    capabilities: tuple[str, ...]
    actions: tuple[TargetAction, ...]
    implemented: bool

    def discover_projects(self, config: dict[str, Any], **kwargs: Any) -> list[dict[str, Any]]:
        ...

    def workspace_summary(self, config: dict[str, Any]) -> dict[str, Any]:
        ...

    def workspace_identity(self, config: dict[str, Any]) -> TargetWorkspace | None:
        ...

    def file_metadata(self, config: dict[str, Any]) -> tuple[TargetFile, ...]:
        ...

    def active_file(self, config: dict[str, Any], path: str | None = None) -> TargetFile | None:
        ...

    def profile_identity(self, config: dict[str, Any]) -> TargetProfile:
        ...

    def profile_payload(
        self,
        config: dict[str, Any],
        workspace_path: str = "",
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def verify_plan(self, config: dict[str, Any], overrides: dict[str, str] | None = None) -> dict[str, Any]:
        ...

    def verify(self, config: dict[str, Any], overrides: dict[str, str] | None = None) -> dict[str, Any]:
        ...

    def cancel_verify(self) -> dict[str, Any]:
        ...

    def clear_verify_cache(self) -> dict[str, Any]:
        ...

    def context_package(
        self,
        config: dict[str, Any],
        active_file: dict[str, Any],
        verify_context: str,
        allow_edits: bool,
        message: str,
        latest_verify: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ...

    def read_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        ...

    def write_file(self, config: dict[str, Any], path: str, content: str) -> dict[str, Any]:
        ...

    def rollback_file(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        ...

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
        ...

def target_adapter_contract(adapter: Any) -> dict[str, Any]:
    missing_methods = [
        name for name in TARGET_ADAPTER_REQUIRED_METHODS
        if not callable(getattr(adapter, name, None))
    ]
    missing_metadata = [
        name for name in ("target_id", "target_name", "capabilities", "actions", "implemented")
        if not hasattr(adapter, name)
    ]
    return {
        "ok": not missing_methods and not missing_metadata,
        "required_methods": list(TARGET_ADAPTER_REQUIRED_METHODS),
        "missing_methods": missing_methods,
        "missing_metadata": missing_metadata,
    }

def require_target_adapter_contract(adapter: Any) -> dict[str, Any]:
    report = target_adapter_contract(adapter)
    if not report["ok"]:
        target_id = getattr(adapter, "target_id", adapter.__class__.__name__)
        missing = report["missing_methods"] + report["missing_metadata"]
        raise ValueError(f"Target adapter '{target_id}' does not satisfy contract: {', '.join(missing)}")
    return report

class TargetRegistry:
    def __init__(self) -> None:
        self._items: dict[str, TargetAdapter] = {}

    def register(self, adapter: TargetAdapter, *, allow_placeholder: bool = False) -> None:
        implemented = bool(getattr(adapter, "implemented", False))
        if not implemented and not allow_placeholder:
            raise ValueError(f"Target adapter '{adapter.target_id}' is not implemented.")
        if implemented:
            require_target_adapter_contract(adapter)
        self._items[adapter.target_id] = adapter

    def get(self, target_id: str) -> TargetAdapter | None:
        return self._items.get(target_id)

    def all(self) -> list[TargetAdapter]:
        return list(self._items.values())

    def metadata(self) -> list[dict[str, Any]]:
        return [
            {
                "id": adapter.target_id,
                "name": adapter.target_name,
                "capabilities": list(adapter.capabilities),
                "actions": [item.to_dict() for item in getattr(adapter, "actions", ())],
                "implemented": bool(getattr(adapter, "implemented", False)),
                "status": "supported" if bool(getattr(adapter, "implemented", False)) else "placeholder",
                "contract": target_adapter_contract(adapter),
            }
            for adapter in self.all()
        ]
