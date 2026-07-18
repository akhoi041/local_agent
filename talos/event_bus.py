from __future__ import annotations

import threading
from typing import Any

from talos.arduino_events import ArduinoEventWatcher
from talos.core import now

EVENTS: list[str] = []
_EVENT_LOCK = threading.Lock()
_ARDUINO_SIGNAL_LOCK = threading.Lock()
_ARDUINO_SIGNAL_REVISION = 0
_ARDUINO_SIGNAL_TIME = ""
_ARDUINO_EVENT_WATCHER: ArduinoEventWatcher | None = None


def log_event(message: str) -> None:
    with _EVENT_LOCK:
        EVENTS.append(message)
        del EVENTS[:-200]


def notify_arduino_event(reason: str = "window") -> None:
    del reason
    global _ARDUINO_SIGNAL_REVISION, _ARDUINO_SIGNAL_TIME
    with _ARDUINO_SIGNAL_LOCK:
        _ARDUINO_SIGNAL_REVISION += 1
        _ARDUINO_SIGNAL_TIME = now()


def arduino_event_status() -> dict[str, Any]:
    with _ARDUINO_SIGNAL_LOCK:
        return {
            "revision": _ARDUINO_SIGNAL_REVISION,
            "time": _ARDUINO_SIGNAL_TIME,
            "event_assisted": bool(_ARDUINO_EVENT_WATCHER and _ARDUINO_EVENT_WATCHER.available),
        }


def start_arduino_event_watcher() -> None:
    global _ARDUINO_EVENT_WATCHER
    if _ARDUINO_EVENT_WATCHER is None:
        _ARDUINO_EVENT_WATCHER = ArduinoEventWatcher(notify_arduino_event)
        _ARDUINO_EVENT_WATCHER.start()


def stop_arduino_event_watcher() -> None:
    global _ARDUINO_EVENT_WATCHER
    if _ARDUINO_EVENT_WATCHER is not None:
        _ARDUINO_EVENT_WATCHER.stop()
    _ARDUINO_EVENT_WATCHER = None
