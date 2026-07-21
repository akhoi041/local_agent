from __future__ import annotations

from talos.shell.pywebview_provider import run_pywebview_shell, show_desktop_shell_error

def run_desktop_shell() -> None:
    run_pywebview_shell()

if __name__ == "__main__":
    try:
        run_desktop_shell()
    except Exception as exc:
        show_desktop_shell_error(exc)
