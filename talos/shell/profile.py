from __future__ import annotations

import socket
import sys
from dataclasses import dataclass
from pathlib import Path

from talos.core import (
    APP_DATA_ROOT,
    BUNDLE_ROOT,
    ROOT,
    WEBVIEW_MIN_HEIGHT,
    WEBVIEW_MIN_WIDTH,
    load_app_identity,
)

@dataclass(frozen=True)
class ShellProviderSlot:
    provider_id: str
    label: str
    status: str
    notes: str

@dataclass(frozen=True)
class LaunchProfile:
    host: str
    port: int
    url: str
    app_name: str
    identity: dict[str, str]
    icon_path: str | None
    storage_path: Path
    static_root: Path
    width: int = 1280
    height: int = 840
    min_width: int = WEBVIEW_MIN_WIDTH
    min_height: int = WEBVIEW_MIN_HEIGHT
    background_color: str = "#ffffff"

SHELL_PROVIDER_SLOTS: tuple[ShellProviderSlot, ...] = (
    ShellProviderSlot(
        provider_id="pywebview-debug",
        label="pywebview source/debug shell",
        status="active",
        notes="Compatibility shell used by desktop_app.py during the rebuild.",
    ),
    ShellProviderSlot(
        provider_id="tauri-rust",
        label="Tauri/Rust shell",
        status="future",
        notes="Future production shell candidate; not implemented in 0.6.0.",
    ),
    ShellProviderSlot(
        provider_id="electron",
        label="Electron shell",
        status="future",
        notes="Fallback candidate for full custom chrome parity; not implemented in 0.6.0.",
    ),
)

def static_ui_root() -> Path:
    if getattr(sys, "frozen", False):
        return BUNDLE_ROOT / "web_frontend"
    return ROOT / "ui" / "web_frontend"

def existing_icon_path(identity: dict[str, str]) -> str | None:
    icon_path = ROOT / identity.get("icon_ico", "")
    if icon_path.exists():
        return str(icon_path)
    bundled_icon = BUNDLE_ROOT / identity.get("icon_ico", "")
    if bundled_icon.exists():
        return str(bundled_icon)
    return None

def set_windows_app_id(identity: dict[str, str]) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        app_id = identity.get("app_id") or f"{identity['publisher']}.{identity['app_name']}.{identity['channel']}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str(app_id))
    except Exception:
        pass

def find_port(host: str, start_port: int) -> int:
    for port in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((host, port))
            except OSError:
                continue
            return port
    raise OSError(f"No free port found from {start_port} to {start_port + 19}")

def build_launch_profile(host: str = "127.0.0.1", start_port: int = 8787) -> LaunchProfile:
    identity = load_app_identity()
    port = find_port(host, start_port)
    storage_path = APP_DATA_ROOT / "webview"
    return LaunchProfile(
        host=host,
        port=port,
        url=f"http://{host}:{port}",
        app_name=identity["display_name"],
        identity=identity,
        icon_path=existing_icon_path(identity),
        storage_path=storage_path,
        static_root=static_ui_root(),
    )
