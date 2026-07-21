from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

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

class TargetRegistry:
    def __init__(self) -> None:
        self._items: dict[str, TargetAdapter] = {}

    def register(self, adapter: TargetAdapter, *, allow_placeholder: bool = False) -> None:
        if not bool(getattr(adapter, "implemented", False)) and not allow_placeholder:
            raise ValueError(f"Target adapter '{adapter.target_id}' is not implemented.")
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
            }
            for adapter in self.all()
        ]
