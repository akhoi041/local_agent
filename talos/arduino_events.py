from __future__ import annotations

import ctypes
import os
import threading
import time
from ctypes import wintypes
from typing import Callable

EVENT_OBJECT_CREATE = 0x8000
EVENT_OBJECT_DESTROY = 0x8001
EVENT_OBJECT_SHOW = 0x8002
EVENT_OBJECT_HIDE = 0x8003
EVENT_OBJECT_NAMECHANGE = 0x800C
OBJID_WINDOW = 0
WINEVENT_OUTOFCONTEXT = 0
WINEVENT_SKIPOWNPROCESS = 0x0002
WM_QUIT = 0x0012

def is_arduino_window_title(title: str) -> bool:
    normalized = str(title or "").casefold()
    return "arduino ide" in normalized or ("arduino" in normalized and ".ino" in normalized)

class ArduinoEventWatcher:
    """Listen for Arduino window changes and notify Talos without replacing polling."""

    def __init__(self, notify: Callable[[str], None], debounce_seconds: float = 0.15) -> None:
        self._notify = notify
        self._debounce_seconds = debounce_seconds
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._hook = None
        self._callback = None
        self._last_signal_at = 0.0
        self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def start(self) -> bool:
        if os.name != "nt" or self._thread is not None:
            return self._available
        self._thread = threading.Thread(target=self._run, name="talos-arduino-events", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stop.set()
        if os.name == "nt" and self._thread_id:
            try:
                ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            except (AttributeError, OSError):
                pass
        if self._thread is not None:
            self._thread.join(timeout=1)
        self._thread = None
        self._available = False

    def _signal(self, title: str) -> None:
        if not is_arduino_window_title(title):
            return
        with self._lock:
            now = time.monotonic()
            if now - self._last_signal_at < self._debounce_seconds:
                return
            self._last_signal_at = now
        self._notify("window")

    def _run(self) -> None:
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            callback_type = ctypes.WINFUNCTYPE(
                None,
                wintypes.HANDLE,
                wintypes.DWORD,
                wintypes.HWND,
                wintypes.LONG,
                wintypes.LONG,
                wintypes.DWORD,
                wintypes.DWORD,
            )

            def callback(_hook, _event, hwnd, object_id, _child_id, _thread_id, _time) -> None:
                if object_id != OBJID_WINDOW or not hwnd:
                    return
                length = user32.GetWindowTextLengthW(hwnd)
                if length <= 0:
                    return
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                self._signal(buffer.value)

            self._callback = callback_type(callback)
            self._thread_id = int(kernel32.GetCurrentThreadId())
            self._hook = user32.SetWinEventHook(
                EVENT_OBJECT_CREATE,
                EVENT_OBJECT_NAMECHANGE,
                None,
                self._callback,
                0,
                0,
                WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
            )
            if not self._hook:
                return
            self._available = True
            message = wintypes.MSG()
            while not self._stop.is_set() and user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(message))
                user32.DispatchMessageW(ctypes.byref(message))
        except (AttributeError, OSError):
            return
        finally:
            if self._hook:
                try:
                    ctypes.windll.user32.UnhookWinEvent(self._hook)
                except (AttributeError, OSError):
                    pass
            self._hook = None
            self._callback = None
            self._thread_id = 0
            self._available = False
