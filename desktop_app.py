from __future__ import annotations

import sys
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from tkinter import messagebox
from typing import Any

from talos.core import ROOT, WEBVIEW_MIN_HEIGHT, WEBVIEW_MIN_WIDTH, load_app_identity

def _existing_icon_path(identity: dict[str, str]) -> str | None:
    icon_path = ROOT / identity.get("icon_ico", "")
    if icon_path.exists():
        return str(icon_path)
    bundle_value = getattr(sys, "_MEIPASS", "")
    if bundle_value:
        bundle_root = Path(bundle_value)
        bundled_icon = bundle_root / identity.get("icon_ico", "")
        if bundled_icon.exists():
            return str(bundled_icon)
    return None

def _set_windows_app_id(identity: dict[str, str]) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        app_id = identity.get("app_id") or f"{identity['publisher']}.{identity['app_name']}.{identity['channel']}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(str(app_id))
    except Exception:
        pass

def run_desktop_shell() -> None:
    try:
        import webview  # type: ignore[import-not-found]
    except ImportError:
        messagebox.showerror(
            "Talos",
            "Desktop WebView runtime is missing.\n\nRun:\npython -m pip install pywebview",
        )
        return

    from talos.server import (
        CODEX_BRIDGE,
        LocalAgentWebHandler,
        find_port,
        start_arduino_event_watcher,
        stop_arduino_event_watcher,
    )

    app_identity = load_app_identity()
    app_name = app_identity["display_name"]
    icon_path = _existing_icon_path(app_identity)
    _set_windows_app_id(app_identity)
    host = "127.0.0.1"
    port = find_port(host, 8787)
    server = ThreadingHTTPServer((host, port), LocalAgentWebHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    start_arduino_event_watcher()
    window_ref: dict[str, Any] = {"window": None, "maximized": False}

    class WindowApi:
        def minimize(self) -> None:
            window = window_ref["window"]
            if window is not None:
                window.minimize()

        def toggle_maximize(self) -> bool:
            window = window_ref["window"]
            if window is None:
                return False
            state = str(getattr(window, "state", ""))
            if window_ref["maximized"] or "maximized" in state.lower():
                window.restore()
                window_ref["maximized"] = False
            else:
                window.maximize()
                window_ref["maximized"] = True
            return window_ref["maximized"]

        def get_window_state(self) -> dict[str, Any]:
            window = window_ref["window"]
            state = str(getattr(window, "state", "")) if window is not None else ""
            maximized = window_ref["maximized"] or "maximized" in state.lower()
            window_ref["maximized"] = maximized
            return {"maximized": maximized, "state": state}

        def snap_to(self, x: int, y: int, width: int, height: int) -> dict[str, Any]:
            window = window_ref["window"]
            if window is None:
                return {"maximized": False}
            window.restore()
            window_ref["maximized"] = False
            window.move(int(x), int(y))
            window.resize(max(WEBVIEW_MIN_WIDTH, int(width)), max(WEBVIEW_MIN_HEIGHT, int(height)))
            return {"maximized": False}

        def close(self) -> None:
            window = window_ref["window"]
            if window is not None:
                window.destroy()

    def on_closed() -> None:
        stop_arduino_event_watcher()
        CODEX_BRIDGE.shutdown()
        server.shutdown()
        server.server_close()

    window = webview.create_window(
        app_name,
        f"http://{host}:{port}",
        width=1280,
        height=840,
        min_size=(WEBVIEW_MIN_WIDTH, WEBVIEW_MIN_HEIGHT),
        background_color="#ffffff",
        frameless=False,
        easy_drag=False,
        js_api=WindowApi(),
    )
    window_ref["window"] = window
    window.events.closed += on_closed
    webview.start(debug="--debug-webview" in sys.argv, icon=icon_path)

if __name__ == "__main__":
    try:
        run_desktop_shell()
    except Exception as exc:
        messagebox.showerror(load_app_identity()["display_name"], str(exc))
