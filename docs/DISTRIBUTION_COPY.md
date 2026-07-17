# Talos Distribution Copy

Version: 0.5.0 Beta

Use this copy when describing Talos to testers or in release materials.

## Short Description

Talos is a local Codex control layer for Arduino IDE. It detects the active Arduino sketch, prepares safe workspace context for Codex, stages suggested code changes, runs sandbox verification with Arduino CLI, and lets the user decide when to save changes back to the real sketch folder.

## What Talos Is

- Arduino-first local bridge software.
- A Codex-authenticated review, verification, and support layer between Codex and Arduino IDE.
- A tool that keeps Arduino IDE as the saved-source owner.
- A way to package workspace context, active file content, verify results, and profile readiness for Codex.
- A safer path for reviewing Codex changes before writing them into the real sketch folder.

## What Talos Is Not

- Talos is not an embedded AI model.
- Not a replacement for Arduino IDE.
- Not a hardware upload or serial-monitor guarantee in 0.5.0.
- Not a hidden telemetry client.
- Talos does not silently upload sketch source, Codex chat content, account identifiers, or raw local paths.

## Trust And Privacy Copy

Talos runs a local server bound to `127.0.0.1` and stores runtime data under the user's Talos app-data folder. Diagnostics are disabled by default in 0.5.0. If enabled, diagnostics stay local and can be previewed as a redacted export before the user shares them.

Codex reasoning happens through the user's authenticated Codex environment. Talos does not include a separate AI model and does not bypass Codex authentication.

## Signing Copy

Talos 0.5.0 Beta may be unsigned while T-Engine prepares a code-signing certificate. Unsigned builds must include explicit `signing_status.json` evidence, and Windows may show SmartScreen or unknown-publisher warnings on first launch.

## Tester-Facing Limitation Copy

This release is intended for Arduino/Codex workflow testing. Users should review all code before saving it, keep backups of important sketches, and confirm board, port, and compile results before using generated code on hardware.
