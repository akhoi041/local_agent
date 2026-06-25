from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = ROOT / "config" / "config.json"
APP_IDENTITY_PATH = ROOT / "config" / "app_identity.json"
CONFIG_SCHEMA_VERSION = 1
WEBVIEW_MIN_WIDTH = 520
WEBVIEW_MIN_HEIGHT = 420

DEFAULT_APP_IDENTITY: dict[str, str] = {
    "app_name": "Talos",
    "display_name": "Talos",
    "publisher": "T-Engine",
    "version": "0.1.0",
    "channel": "Beta",
    "support": "",
    "icon_source": "talos_icon.png",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": CONFIG_SCHEMA_VERSION,
    "theme": "light",
    "arduino_workspace_path": "",
    "arduino_fqbn": "",
    "arduino_profiles": {},
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
    return config

def load_config() -> dict[str, Any]:
    data, valid = _read_json(CONFIG_PATH, {}, encoding="utf-8-sig")
    config = _normalize_config(data)
    can_migrate = not isinstance(data, dict) or schema_version(data.get("schema_version")) <= CONFIG_SCHEMA_VERSION
    if CONFIG_PATH.exists() and can_migrate and (not valid or config != data):
        backup_json_file(CONFIG_PATH, "migration")
        try:
            write_json_file(CONFIG_PATH, config)
        except OSError:
            pass
    return config

def save_config(config: dict[str, Any]) -> None:
    write_json_file(CONFIG_PATH, _normalize_config(config))

def load_app_identity() -> dict[str, str]:
    data = read_json_file(APP_IDENTITY_PATH, {}, encoding="utf-8-sig")
    identity = DEFAULT_APP_IDENTITY | data if isinstance(data, dict) else DEFAULT_APP_IDENTITY.copy()
    return {key: str(value).strip() for key, value in identity.items()}

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
