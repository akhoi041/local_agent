from __future__ import annotations

import sys
import threading
from http.server import ThreadingHTTPServer
from tkinter import messagebox
from typing import Any

from talos.codex_bridge import CODEX_BRIDGE
from talos.core import load_app_identity
from talos.event_bus import start_arduino_event_watcher, stop_arduino_event_watcher
from talos.server import TalosWebHandler

from .profile import LaunchProfile, build_launch_profile, set_windows_app_id

class WindowApi:
    def __init__(self, window_ref: dict[str, Any], profile: LaunchProfile) -> None:
        self._window_ref = window_ref
        self._profile = profile

    @property
    def _window(self) -> Any:
        return self._window_ref.get("window")

    def minimize(self) -> None:
        if self._window is not None:
            self._window.minimize()

    def toggle_maximize(self) -> bool:
        if self._window is None:
            return False
        state = str(getattr(self._window, "state", ""))
        if self._window_ref["maximized"] or "maximized" in state.lower():
            self._window.restore()
            self._window_ref["maximized"] = False
        else:
            self._window.maximize()
            self._window_ref["maximized"] = True
        return bool(self._window_ref["maximized"])

    def restore(self) -> bool:
        if self._window is not None:
            self._window.restore()
        self._window_ref["maximized"] = False
        return False

    def get_window_state(self) -> dict[str, Any]:
        state = str(getattr(self._window, "state", "")) if self._window is not None else ""
        maximized = bool(self._window_ref["maximized"] or "maximized" in state.lower())
        self._window_ref["maximized"] = maximized
        return {"maximized": maximized, "state": state}

    def get_window_bounds(self) -> dict[str, Any]:
        if self._window is None:
            return {
                "x": 0,
                "y": 0,
                "width": self._profile.min_width,
                "height": self._profile.min_height,
                "maximized": False,
            }
        state = self.get_window_state()
        return {
            "x": int(getattr(self._window, "x", 0) or 0),
            "y": int(getattr(self._window, "y", 0) or 0),
            "width": int(getattr(self._window, "width", self._profile.min_width) or self._profile.min_width),
            "height": int(getattr(self._window, "height", self._profile.min_height) or self._profile.min_height),
            "maximized": bool(state["maximized"]),
        }

    def set_window_bounds(self, x: int, y: int, width: int, height: int) -> dict[str, Any]:
        if self._window is None:
            return {"maximized": False}
        if self._window_ref["maximized"]:
            self._window.restore()
            self._window_ref["maximized"] = False
        next_width = max(self._profile.min_width, int(width))
        next_height = max(self._profile.min_height, int(height))
        self._window.move(int(x), int(y))
        self._window.resize(next_width, next_height)
        return {"x": int(x), "y": int(y), "width": next_width, "height": next_height, "maximized": False}

    def snap_to(self, x: int, y: int, width: int, height: int) -> dict[str, Any]:
        if self._window is None:
            return {"maximized": False}
        self._window.restore()
        self._window_ref["maximized"] = False
        self._window.move(int(x), int(y))
        self._window.resize(max(self._profile.min_width, int(width)), max(self._profile.min_height, int(height)))
        return {"maximized": False}

    def close(self) -> None:
        if self._window is not None:
            self._window.destroy()

def _show_missing_webview_runtime() -> None:
    messagebox.showerror(
        "Talos",
        "Desktop WebView runtime is missing.\n\nRun:\npython -m pip install pywebview",
    )

def run_pywebview_shell(debug: bool | None = None) -> None:
    try:
        import webview  # type: ignore[import-not-found]
    except ImportError:
        _show_missing_webview_runtime()
        return

    profile = build_launch_profile()
    profile.storage_path.mkdir(parents=True, exist_ok=True)
    set_windows_app_id(profile.identity)

    server = ThreadingHTTPServer((profile.host, profile.port), TalosWebHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    start_arduino_event_watcher()

    window_ref: dict[str, Any] = {"window": None, "maximized": False}
    window_api = WindowApi(window_ref, profile)

    def on_closed() -> None:
        stop_arduino_event_watcher()
        CODEX_BRIDGE.shutdown()
        server.shutdown()
        server.server_close()

    window = webview.create_window(
        profile.app_name,
        profile.url,
        width=profile.width,
        height=profile.height,
        min_size=(profile.min_width, profile.min_height),
        background_color=profile.background_color,
        frameless=True,
        easy_drag=False,
        js_api=window_api,
    )
    window_ref["window"] = window
    window.events.closed += on_closed
    webview.start(
        debug=("--debug-webview" in sys.argv) if debug is None else debug,
        icon=profile.icon_path,
        private_mode=False,
        storage_path=str(profile.storage_path),
    )

def show_desktop_shell_error(exc: Exception) -> None:
    messagebox.showerror(load_app_identity()["display_name"], str(exc))
