from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Any, Callable

from talos.core import CODEX_RUNTIME_DEFAULTS

RUNTIME_CONFIG_KEY = "codex_runtime"
PROVIDER_STANDALONE_PATH = "standalone_path"
PROVIDER_USER_SELECTED_PATH = "user_selected_path"
PROVIDER_EXTENSION_ADJACENT = "vscode_extension_adjacent"
PROVIDER_NONE = "none"
FALLBACK_EXTENSION_ADJACENT = "extension_adjacent"
FALLBACK_NONE = "none"


def _enabled(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off"}
    return default


def _safe_commands(items: Any) -> list[str]:
    values = items if isinstance(items, list) else []
    commands = [str(item).strip()[:80] for item in values[:8] if str(item).strip()]
    return commands or ["codex"]


def _provider_config(runtime: dict[str, Any]) -> dict[str, dict[str, Any]]:
    defaults = CODEX_RUNTIME_DEFAULTS.get("candidate_providers", {})
    raw = runtime.get("candidate_providers") if isinstance(runtime.get("candidate_providers"), dict) else {}
    providers: dict[str, dict[str, Any]] = {}
    for provider, fallback in defaults.items():
        source = raw.get(provider) if isinstance(raw.get(provider), dict) else {}
        provider_settings: dict[str, Any] = {
            "enabled": _enabled(source.get("enabled"), bool(fallback.get("enabled", True))),
        }
        if provider == PROVIDER_STANDALONE_PATH:
            provider_settings["commands"] = _safe_commands(source.get("commands", fallback.get("commands")))
        providers[provider] = provider_settings
    return providers


def runtime_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    source = config if isinstance(config, dict) else {}
    runtime = source.get(RUNTIME_CONFIG_KEY) if isinstance(source.get(RUNTIME_CONFIG_KEY), dict) else {}
    merged = CODEX_RUNTIME_DEFAULTS | runtime
    try:
        timeout = float(merged.get("health_timeout_sec", CODEX_RUNTIME_DEFAULTS["health_timeout_sec"]))
    except (TypeError, ValueError):
        timeout = float(CODEX_RUNTIME_DEFAULTS["health_timeout_sec"])
    fallback = str(merged.get("fallback_policy") or FALLBACK_EXTENSION_ADJACENT).strip()
    if fallback not in {FALLBACK_EXTENSION_ADJACENT, FALLBACK_NONE}:
        fallback = FALLBACK_EXTENSION_ADJACENT
    return {
        "selected_path": str(merged.get("selected_path") or "").strip(),
        "pinned_path": str(merged.get("pinned_path") or "").strip(),
        "pinned_hash": str(merged.get("pinned_hash") or "").strip().lower(),
        "pinned_version": str(merged.get("pinned_version") or "").strip(),
        "fallback_policy": fallback,
        "extension_adjacent_path": str(merged.get("extension_adjacent_path") or "").strip(),
        "health_timeout_sec": max(0.2, min(10.0, timeout)),
        "candidate_providers": _provider_config(merged),
    }


def with_runtime_defaults(config: dict[str, Any] | None = None) -> dict[str, Any]:
    source = dict(config) if isinstance(config, dict) else {}
    source[RUNTIME_CONFIG_KEY] = runtime_config(source)
    return source


def file_sha256(path_text: str) -> str:
    path = Path(path_text)
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return ""


def redact_path(path_text: str) -> str:
    if not str(path_text or "").strip():
        return ""
    name = Path(path_text).name or "<runtime>"
    return f"...\\{name}" if os.name == "nt" else f".../{name}"


def _existing_path(path_text: str, path_exists: Callable[[str], bool]) -> str:
    value = str(path_text or "").strip().strip('"')
    if not value:
        return ""
    try:
        candidate = str(Path(value).expanduser().resolve())
    except OSError:
        candidate = value
    return candidate if path_exists(candidate) else ""


def _candidate(provider: str, path_text: str, source: str, warnings: list[str] | None = None) -> dict[str, Any]:
    digest = file_sha256(path_text)
    return {
        "provider": provider,
        "path": path_text,
        "display_path": redact_path(path_text),
        "source": source,
        "version": "",
        "hash": digest,
        "hash_short": digest[:12],
        "warnings": warnings or [],
        "limitations": [],
    }


def discover_runtime_candidates(
    config: dict[str, Any] | None = None,
    *,
    path_exists: Callable[[str], bool] | None = None,
    which_func: Callable[[str], str | None] | None = None,
) -> list[dict[str, Any]]:
    settings = runtime_config(config or {})
    providers = settings["candidate_providers"]
    exists = path_exists or (lambda path_text: Path(path_text).exists())
    which = which_func or shutil.which
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(provider: str, path_text: str, source: str, warnings: list[str] | None = None) -> None:
        path_value = _existing_path(path_text, exists)
        if not path_value:
            return
        key = path_value.lower()
        if key in seen:
            return
        seen.add(key)
        candidates.append(_candidate(provider, path_value, source, warnings))

    standalone = providers.get(PROVIDER_STANDALONE_PATH, {})
    if standalone.get("enabled"):
        for command in standalone.get("commands", ["codex"]):
            add(PROVIDER_STANDALONE_PATH, which(str(command)) or "", "PATH")

    user_selected = providers.get(PROVIDER_USER_SELECTED_PATH, {})
    if user_selected.get("enabled"):
        add(PROVIDER_USER_SELECTED_PATH, settings["selected_path"], "user_config")

    extension_adjacent = providers.get(PROVIDER_EXTENSION_ADJACENT, {})
    if extension_adjacent.get("enabled") and settings["fallback_policy"] == FALLBACK_EXTENSION_ADJACENT:
        add(
            PROVIDER_EXTENSION_ADJACENT,
            settings["extension_adjacent_path"],
            "extension_adjacent",
            ["extension_adjacent_fallback"],
        )
    return candidates
