from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from talos.core import now

MAX_RECENT_TASKS = 25

def _copy_task(task: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(task)

@dataclass
class TaskOrchestrator:
    """In-process task state for long-running Talos operations.

    This boundary deliberately tracks state only; it does not spawn shells or
    own subprocess execution. Runtime/target providers remain responsible for
    the actual work.
    """

    max_recent: int = MAX_RECENT_TASKS
    _lock: Lock = field(default_factory=Lock)
    _counter: int = 0
    _active: dict[str, dict[str, Any]] = field(default_factory=dict)
    _recent: list[dict[str, Any]] = field(default_factory=list)

    def start(self, kind: str, label: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        timestamp = now()
        with self._lock:
            self._counter += 1
            task = {
                "id": f"task-{self._counter}",
                "kind": kind,
                "label": label,
                "state": "running",
                "status": "running",
                "started_at": timestamp,
                "updated_at": timestamp,
                "metadata": dict(metadata or {}),
                "events": [],
            }
            self._active[task["id"]] = task
            return _copy_task(task)

    def finish(
        self,
        task_id: str,
        status: str,
        detail: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        timestamp = now()
        with self._lock:
            task = self._active.pop(task_id, None)
            if task is None:
                task = {
                    "id": task_id,
                    "kind": "unknown",
                    "label": "Unknown task",
                    "started_at": timestamp,
                    "metadata": {},
                    "events": [],
                }
            task["status"] = status
            task["state"] = self._state_for_status(status)
            task["detail"] = detail
            task["finished_at"] = timestamp
            task["updated_at"] = timestamp
            if metadata:
                task["metadata"].update(metadata)
            self._recent.insert(0, task)
            del self._recent[self.max_recent:]
            return _copy_task(task)

    def event(
        self,
        kind: str,
        status: str,
        label: str,
        detail: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        task = self.start(kind, label, metadata)
        return self.finish(task["id"], status, detail, metadata)

    def request_cancel(
        self,
        kind: str,
        detail: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        timestamp = now()
        affected: list[dict[str, Any]] = []
        with self._lock:
            for task in self._active.values():
                if task.get("kind") != kind:
                    continue
                task["cancel_requested"] = True
                task["updated_at"] = timestamp
                event = {
                    "status": "cancel_requested",
                    "detail": detail,
                    "timestamp": timestamp,
                    "metadata": dict(metadata or {}),
                }
                task.setdefault("events", []).append(event)
                affected.append(_copy_task(task))
        if affected:
            return affected
        return [
            self.event(
                kind,
                "cancel_requested",
                f"Cancel {kind}",
                detail,
                metadata,
            )
        ]

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            active = [_copy_task(task) for task in self._active.values()]
            recent = [_copy_task(task) for task in self._recent]
        return {
            "schema_version": 1,
            "active": active,
            "recent": recent,
            "counts": {
                "active": len(active),
                "recent": len(recent),
            },
        }

    @staticmethod
    def _state_for_status(status: str) -> str:
        normalized = status.lower()
        if "cancel" in normalized:
            return "cancelled"
        if normalized in {"failed", "error", "runtime_blocked", "blocked"}:
            return "failed"
        return "completed"

TASK_ORCHESTRATOR = TaskOrchestrator()
