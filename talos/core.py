from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent.parent
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", ROOT))

APP_DATA_ENV = "TALOS_APP_DATA_DIR"

def _default_app_data_root() -> Path:
    override = os.environ.get(APP_DATA_ENV)
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / "T-Engine" / "Talos"
        return Path.home() / "AppData" / "Local" / "T-Engine" / "Talos"
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / "Talos"
    return Path.home() / ".local" / "share" / "Talos"

APP_DATA_ROOT = _default_app_data_root()
RUNTIME_ROOT = APP_DATA_ROOT / "runtime"
CONFIG_PATH = APP_DATA_ROOT / "config.json"
LEGACY_CONFIG_PATH = ROOT / "config" / "config.json"
APP_IDENTITY_PATH = ROOT / "config" / "app_identity.json"
DEFAULT_CONFIG_PATH = BUNDLE_ROOT / "config" / "default_config.json"
BUNDLED_APP_IDENTITY_PATH = BUNDLE_ROOT / "config" / "app_identity.json"
RELEASE_MANIFEST_PATH = ROOT / "release_manifest.json"
CONFIG_SCHEMA_VERSION = 1
WEBVIEW_MIN_WIDTH = 520
WEBVIEW_MIN_HEIGHT = 420

CODEX_RUNTIME_DEFAULTS: dict[str, Any] = {
    "selected_path": "",
    "pinned_path": "",
    "pinned_hash": "",
    "pinned_version": "",
    "fallback_policy": "extension_adjacent",
    "extension_adjacent_path": "",
    "health_timeout_sec": 2.0,
}

DEFAULT_APP_IDENTITY: dict[str, str] = {
    "app_name": "Talos",
    "display_name": "Talos",
    "publisher": "T-Engine",
    "version": "0.4.0",
    "channel": "Pre-Alpha",
    "support": "",
    "app_id": "T-Engine.Talos.PreAlpha",
    "icon_source": "talos_icon.png",
    "icon_ico": "assets/icons/talos.ico",
    "icon_png_dir": "assets/icons",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": CONFIG_SCHEMA_VERSION,
    "theme": "light",
    "arduino_workspace_path": "",
    "arduino_fqbn": "",
    "arduino_profiles": {},
    "codex_runtime": CODEX_RUNTIME_DEFAULTS.copy(),
    "diagnostics": {
        "enabled": False,
        "allow_remote_upload": False,
    },
}

def _read_json(path: Path, fallback: Any, encoding: str = "utf-8") -> tuple[Any, bool]:
    if not path.exists():
        return fallback, True
    try:
        with path.open("r", encoding=encoding) as stream:
            return json.load(stream), True
    except (OSError, json.JSONDecodeError):
        return fallback, False

def read_json_file(path: Path, fallback: Any, encoding: str = "utf-8") -> Any:
    return _read_json(path, fallback, encoding)[0]

def write_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_path, path)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass

def backup_json_file(path: Path, label: str) -> Path | None:
    """Preserve the original user state before a schema migration changes it."""
    if not path.exists() or not path.is_file():
        return None
    backup_dir = path.parent / "backups"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = backup_dir / f"{path.stem}.{label}.{stamp}{path.suffix}"
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
    except OSError:
        return None
    return backup_path

def schema_version(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0

def migrate_state_document(
    path: Path,
    data: Any,
    *,
    collection_key: str,
    target_schema_version: int = 1,
    label: str,
) -> dict[str, Any]:
    """Normalize a persisted list document and back up legacy or malformed data first."""
    source = dict(data) if isinstance(data, dict) else {}
    source_version = schema_version(source.get("schema_version"))
    collection = source.get(collection_key)
    if not isinstance(collection, list):
        collection = []
    if source_version > target_schema_version:
        return {**source, collection_key: collection}
    migrated = dict(source)
    migrated["schema_version"] = target_schema_version
    migrated[collection_key] = collection
    if path.exists() and migrated != data:
        backup_json_file(path, label)
        try:
            write_json_file(path, migrated)
        except OSError:
            pass
    return migrated

def _normalize_config(data: Any) -> dict[str, Any]:
    source = dict(data) if isinstance(data, dict) else {}
    config = DEFAULT_CONFIG | source
    if schema_version(source.get("schema_version")) > CONFIG_SCHEMA_VERSION:
        return config
    config["schema_version"] = CONFIG_SCHEMA_VERSION
    if str(config.get("theme", "light")) not in {"light", "dark", "neutral"}:
        config["theme"] = "light"
    for key in ("arduino_workspace_path", "arduino_fqbn"):
        config[key] = str(config.get(key) or "").strip()
    if not isinstance(config.get("arduino_profiles"), dict):
        config["arduino_profiles"] = {}
    diagnostics = config.get("diagnostics") if isinstance(config.get("diagnostics"), dict) else {}
    config["diagnostics"] = {
        "enabled": bool(diagnostics.get("enabled")),
        "allow_remote_upload": False,
    }
    runtime = config.get("codex_runtime") if isinstance(config.get("codex_runtime"), dict) else {}
    timeout = runtime.get("health_timeout_sec", CODEX_RUNTIME_DEFAULTS["health_timeout_sec"])
    try:
        timeout_value = float(timeout)
    except (TypeError, ValueError):
        timeout_value = float(CODEX_RUNTIME_DEFAULTS["health_timeout_sec"])
    config["codex_runtime"] = {
        "selected_path": str(runtime.get("selected_path") or "").strip(),
        "pinned_path": str(runtime.get("pinned_path") or "").strip(),
        "pinned_hash": str(runtime.get("pinned_hash") or "").strip().lower(),
        "pinned_version": str(runtime.get("pinned_version") or "").strip(),
        "fallback_policy": str(runtime.get("fallback_policy") or CODEX_RUNTIME_DEFAULTS["fallback_policy"]).strip(),
        "extension_adjacent_path": str(runtime.get("extension_adjacent_path") or "").strip(),
        "health_timeout_sec": max(0.2, min(10.0, timeout_value)),
    }
    if config["codex_runtime"]["fallback_policy"] not in {"extension_adjacent", "none"}:
        config["codex_runtime"]["fallback_policy"] = CODEX_RUNTIME_DEFAULTS["fallback_policy"]
    return config

def load_config() -> dict[str, Any]:
    fallback = read_json_file(DEFAULT_CONFIG_PATH, {}, encoding="utf-8-sig")
    source_path = CONFIG_PATH
    data, valid = _read_json(CONFIG_PATH, fallback, encoding="utf-8-sig")
    if not CONFIG_PATH.exists() and LEGACY_CONFIG_PATH.exists():
        source_path = LEGACY_CONFIG_PATH
        data, valid = _read_json(LEGACY_CONFIG_PATH, fallback, encoding="utf-8-sig")
    config = _normalize_config(data)
    can_migrate = not isinstance(data, dict) or schema_version(data.get("schema_version")) <= CONFIG_SCHEMA_VERSION
    if source_path.exists() and can_migrate and (source_path != CONFIG_PATH or not valid or config != data):
        if source_path == CONFIG_PATH:
            backup_json_file(CONFIG_PATH, "migration")
        try:
            write_json_file(CONFIG_PATH, config)
        except OSError:
            pass
    return config

def save_config(config: dict[str, Any]) -> None:
    write_json_file(CONFIG_PATH, _normalize_config(config))

def load_app_identity() -> dict[str, str]:
    fallback = read_json_file(BUNDLED_APP_IDENTITY_PATH, {}, encoding="utf-8-sig")
    data = read_json_file(APP_IDENTITY_PATH, fallback, encoding="utf-8-sig")
    identity = DEFAULT_APP_IDENTITY | data if isinstance(data, dict) else DEFAULT_APP_IDENTITY.copy()
    return {key: str(value).strip() for key, value in identity.items()}

def load_build_metadata(identity: dict[str, str] | None = None) -> dict[str, Any]:
    app_identity = identity or load_app_identity()
    manifest = read_json_file(RELEASE_MANIFEST_PATH, {}, encoding="utf-8-sig")
    manifest_data = manifest if isinstance(manifest, dict) else {}
    artifacts = manifest_data.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = []
    return {
        "schema_version": 1,
        "mode": "packaged" if getattr(sys, "frozen", False) else "source",
        "frozen": bool(getattr(sys, "frozen", False)),
        "app_name": app_identity.get("display_name") or app_identity.get("app_name") or "Talos",
        "publisher": app_identity.get("publisher", ""),
        "version": app_identity.get("version", ""),
        "channel": app_identity.get("channel", ""),
        "app_id": app_identity.get("app_id", ""),
        "release": str(manifest_data.get("release") or ""),
        "built_at": str(manifest_data.get("built_at") or ""),
        "installer_built_at": str(manifest_data.get("installer_built_at") or ""),
        "artifacts": artifacts,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": str(Path(sys.executable).resolve()),
        "root": str(ROOT),
        "bundle_root": str(BUNDLE_ROOT),
        "app_data": str(APP_DATA_ROOT),
    }

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
