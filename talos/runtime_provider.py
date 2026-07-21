from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from talos.codex_bridge import CODEX_BRIDGE
from talos.codex_runtime import (
    runtime_state_summary,
    runtime_status,
    support_bundle_runtime_evidence,
    update_runtime_pin,
)
from talos.core import load_config
from talos.runtime_service import runtime_gate

SAFE_RUNTIME_METADATA_KEYS = frozenset({
    "account",
    "active",
    "app_server",
    "app_server_ready",
    "auth",
    "auth_ready",
    "available",
    "blocked",
    "candidate_count",
    "candidates",
    "changed",
    "checked_at",
    "code",
    "config",
    "connected",
    "detail",
    "display_name",
    "display_path",
    "email",
    "error",
    "fallback_policy",
    "generated_at",
    "hash",
    "hash_short",
    "health",
    "implemented",
    "label",
    "login",
    "manual_replay_required",
    "message",
    "name",
    "ok",
    "path",
    "plan",
    "placeholder",
    "provider",
    "providers",
    "ready",
    "reconnect_allowed",
    "retryable",
    "runtime_blocked",
    "runtime_code",
    "runtime_id",
    "runtime_name",
    "selected",
    "source",
    "state",
    "status",
    "stores_cookies",
    "stores_credentials",
    "stores_tokens",
    "supported",
    "title",
    "version",
    "warnings",
})

SENSITIVE_RUNTIME_METADATA_KEYS = frozenset({
    "access_key",
    "apikey",
    "api_key",
    "authorization",
    "bearer",
    "cookie",
    "credentials",
    "credential",
    "openai_credentials",
    "password",
    "refresh",
    "secret",
    "session",
    "token",
})

def _is_sensitive_runtime_key(key: str) -> bool:
    lowered = key.lower()
    if lowered == "credential_policy":
        return False
    return lowered in SENSITIVE_RUNTIME_METADATA_KEYS or any(part in lowered for part in SENSITIVE_RUNTIME_METADATA_KEYS)

def sanitize_runtime_metadata(value: Any) -> Any:
    """Keep only safe runtime metadata that Talos may display or persist."""

    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _is_sensitive_runtime_key(key_text):
                continue
            if key_text not in SAFE_RUNTIME_METADATA_KEYS and key_text != "credential_policy":
                continue
            safe[key_text] = sanitize_runtime_metadata(item)
        return safe
    if isinstance(value, list):
        return [sanitize_runtime_metadata(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)

@dataclass
class PlaceholderRuntimeProvider:
    runtime_id: str
    runtime_name: str
    implemented: bool = False

    def metadata(self) -> dict[str, Any]:
        return {
            "runtime_id": self.runtime_id,
            "runtime_name": self.runtime_name,
            "implemented": False,
            "placeholder": True,
            "status": "placeholder",
            "credential_policy": {
                "stores_credentials": False,
                "stores_tokens": False,
                "stores_cookies": False,
            },
        }

@dataclass
class CodexRuntimeProvider:
    bridge: Any = CODEX_BRIDGE
    runtime_id: str = "codex"
    runtime_name: str = "Codex"
    fallback_policy: str = "extension_adjacent_candidate_only"

    def metadata(self) -> dict[str, Any]:
        return {
            "runtime_id": self.runtime_id,
            "runtime_name": self.runtime_name,
            "implemented": True,
            "fallback_policy": self.fallback_policy,
            "credential_policy": {
                "stores_credentials": False,
                "stores_tokens": False,
                "stores_cookies": False,
            },
        }

    def bridge_state(self) -> dict[str, Any]:
        return self.bridge.state()

    def status(self, config: dict[str, Any] | None = None, *, force: bool = False) -> dict[str, Any]:
        return sanitize_runtime_metadata(runtime_status(config, force=force))

    def selected_payload(
        self,
        config: dict[str, Any] | None = None,
        *,
        force: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        status = self.status(config if config is not None else load_config(), force=force)
        summary = sanitize_runtime_metadata(runtime_state_summary(status))
        gate = sanitize_runtime_metadata(runtime_gate(summary))
        return status, summary, gate

    def app_server_status(self, *, config: dict[str, Any] | None = None, start: bool = True) -> dict[str, Any]:
        _, runtime_summary, gate = self.selected_payload(config if config is not None else load_config())
        blocked = bool(gate.get("blocked"))
        status = self.bridge.status(start=start and not blocked)
        status["codex_runtime"] = runtime_summary
        status["runtime_gate"] = gate
        if blocked:
            connection = status.get("connection") if isinstance(status.get("connection"), dict) else {}
            status["ok"] = False
            status["runtime_blocked"] = True
            status["error"] = gate.get("detail", "Runtime is not ready.")
            status["connection"] = {
                **connection,
                "state": "runtime_blocked",
                "runtime_code": gate.get("code", "runtime_blocked"),
                "can_retry_now": bool(gate.get("retryable")),
            }
            task_state = status.get("task_state") if isinstance(status.get("task_state"), dict) else {}
            status["task_state"] = {
                **task_state,
                "state": "runtime_blocked",
                "detail": gate.get("detail", "Runtime is not ready."),
                "replay_guard": "manual_send_required",
            }
        return status

    def pin(self, config: dict[str, Any], *, path_text: str = "", clear: bool = False) -> dict[str, Any]:
        return update_runtime_pin(config, path_text=path_text, clear=clear)

    def support_evidence(self, config: dict[str, Any] | None = None) -> dict[str, Any]:
        return sanitize_runtime_metadata(support_bundle_runtime_evidence(self.status(config)))

    def send_message(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.bridge.send_message(*args, **kwargs)

    def reconnect(self) -> dict[str, Any]:
        return self.bridge.reconnect()

    def cancel_turn(self) -> dict[str, Any]:
        return self.bridge.cancel_turn()

    def select_conversation(self, conversation_id: str) -> dict[str, Any]:
        return self.bridge.select_conversation(conversation_id)

    def restore_reviews(self) -> dict[str, Any]:
        return self.bridge.restore_reviews()

    def discard_reviews(self) -> dict[str, Any]:
        return self.bridge.discard_reviews()

    def shutdown(self) -> None:
        self.bridge.shutdown()

@dataclass
class RuntimeProviderRegistry:
    providers: dict[str, CodexRuntimeProvider | PlaceholderRuntimeProvider] = field(default_factory=dict)

    def register(self, provider: CodexRuntimeProvider | PlaceholderRuntimeProvider) -> None:
        self.providers[provider.runtime_id] = provider

    def metadata(self) -> dict[str, Any]:
        return {provider_id: provider.metadata() for provider_id, provider in self.providers.items()}
