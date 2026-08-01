# Talos Shell Boundary

Version: 0.8.0

Talos now treats the desktop shell as a Rust/Cargo-owned product boundary. The existing Python WebView launcher stays available for source/debug runs, but it must not grow into the permanent product shell.

## Rust/Cargo Shell Responsibilities

- Own window lifecycle: launch, close, restore, resize, minimize, maximize, and snap-friendly frame policy.
- Own app identity: application name, icon, publisher identity, storage path, and platform metadata.
- Own native frame policy: prefer native Windows behavior unless a later native shell can match it fully.
- Own workbench hosting: load the local Talos web workbench and connect it to the local API.
- Own product shell hooks: tray, installer integration, update entry points, and release channel display.
- Expose a shell adapter contract that the web workbench can consume without depending on PyWebView behavior.

## Python Allowed Surface

- `desktop_app.py` remains a tiny source/debug launcher.
- `talos/shell/pywebview_provider.py` remains a temporary compatibility provider for local debugging.
- Python may start the local HTTP bridge while replacement shell parity matures.
- Python must not become the owner of product window state, shell menus, native frame policy, installer hooks, or update hooks.

## Deletion Plan

1. Keep `desktop_app.py` as the developer launcher.
2. Replace `talos/shell/pywebview_provider.py` after the Rust shell launches the same local URL and closes the local API cleanly.
3. Move `WindowApi` lifecycle behavior into the Rust shell or a native shell adapter.
4. Delete obsolete Python shell lifecycle helpers only after launch, close, resize, theme handoff, and local API connection are proven from the Rust shell path.

Current implementation: `shell/talos_shell` is the Stage 2 Rust shell contract skeleton. It validates shell ownership and prints a manifest for tests, installers, and later shell hosts.
