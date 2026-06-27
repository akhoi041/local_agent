# Talos Third-Party Notices

Version: 0.1.0 Beta

Talos uses third-party software and tools. Keep this file with binary distributions.

## Direct Python Dependencies

| Component | Purpose | License |
| --- | --- | --- |
| pywebview | Desktop WebView shell | BSD 3-Clause |
| PyInstaller | Windows executable packaging | GPLv2-or-later with PyInstaller special exception |
| Pillow | Icon generation | MIT-CMU |

## Platform And Tooling

| Component | Purpose | Notes |
| --- | --- | --- |
| Python | Runtime/build environment | Governed by the Python Software Foundation License. |
| Inno Setup | Windows installer generation | Used to build the installer; not bundled as part of Talos. |
| Arduino IDE / Arduino CLI | External Arduino tooling | Required for Arduino workflows; governed by their own licenses and installation terms. |
| Codex | AI reasoning and chat surface | Not bundled in Talos; used through the user's authenticated Codex environment. |

## Native Code

Talos includes `native/talos_native.c`, a project-owned Windows helper library for local Arduino IDE/window detection.

## Notes For Commercial Review

Before public commercial distribution, verify the complete packaged dependency list from the final build environment and update this file if PyInstaller hooks add additional redistributable components.

