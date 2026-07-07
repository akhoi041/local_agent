# Talos Release Notes

## 0.2.0 Beta

Talos 0.2.0 Beta focuses on packaged Arduino reliability and daily-use readiness.

### Highlights

- Strengthens installer and installed-app validation for running Talos outside the source tree.
- Improves Arduino sketch detection with event-assisted refresh, stale-sketch cleanup, and multi-file sketch visibility.
- Improves sandbox verify responsiveness with cancellation, cache controls, timing output, and clearer result reset behavior.
- Refines the Arduino workbench layout for normal, maximized, and narrower Windows desktop sizes.
- Adds richer Codex context preview, thread/reconnect state, staged change review, and recovery evidence.
- Adds guarded checkpoints, rollback refusal for externally changed files, and a recovery guide for Arduino IDE/Talos edit conflicts.
- Keeps runtime data, staging, sandbox output, checkpoints, and review state in the per-user Talos app-data folder.

### Known Limitations

- Arduino remains the only supported target in this release; MATLAB and other app integrations are intentionally deferred.
- Codex reasoning still runs through the user's authenticated Codex environment. Talos does not include or replace an AI model.
- Hardware upload and serial workflows are not yet treated as commercial-release guarantees.
- Arduino IDE metadata can still be unavailable when Arduino IDE exposes only an unsaved sketch or limited process/window data.
- The Beta installer may be unsigned until code signing is configured.

### Upgrade Notes

- Existing 0.1.0 runtime data under `%LOCALAPPDATA%\T-Engine\Talos` is reused and migrated when needed.
- If a pending Codex review is found after restart, Talos now asks whether to restore or discard the review before continuing.
- If Arduino IDE changed a file while Talos had a pending Codex review or checkpoint, Talos blocks silent overwrite and requires an explicit recovery decision.

## 0.1.0 Beta

Talos 0.1.0 Beta is the first packaged Arduino-focused release.

### Highlights

- Detects live Arduino IDE sketches and resolves the real sketch folder.
- Reads `.ino`, `.h`, `.hpp`, `.c`, `.cpp`, `.S`, `.txt`, and `.md` files inside the selected sketch.
- Detects board/FQBN data when available from Arduino IDE processes.
- Runs sandbox verification with `arduino-cli` without compiling the real sketch folder.
- Provides a Codex workbench for selected workspace context, staged changes, review, save, verify, rollback, and recovery.
- Stores user-writable state under the per-user Talos app-data folder.
- Ships as a Windows Beta executable and installer with Start Menu and optional Desktop shortcuts.

### Known Limitations

- Arduino is the only supported target in this release; MATLAB and other app integrations are intentionally paused.
- Codex reasoning still runs through the user's authenticated Codex environment. Talos does not include or replace an AI model.
- Hardware upload and serial workflows are not yet treated as commercial-release guarantees.
- Some Arduino IDE metadata can be unavailable when Arduino IDE does not expose a saved sketch or language-server process.
- The Beta installer may be unsigned until code signing is configured.

### Upgrade Notes

- Existing source-tree runtime data is treated as legacy. Talos now writes runtime config, history, checkpoints, sandbox data, and Codex review state under `%LOCALAPPDATA%\T-Engine\Talos`.
- If a legacy `config/config.json` exists beside the source checkout, Talos can migrate it to the per-user app-data config on first run.
