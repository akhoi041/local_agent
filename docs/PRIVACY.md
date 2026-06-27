# Talos Privacy Notes

Version: 0.1.0 Beta

Talos is designed as a local tool layer between Codex and external development tools such as Arduino IDE.

## Local Data

Talos stores user-writable runtime data under `%LOCALAPPDATA%\T-Engine\Talos` by default. This can include:

- UI settings and selected workspace profile data.
- Arduino sketch folder paths and board/FQBN values.
- Verify history, compile summaries, and checkpoint metadata.
- Disposable sandbox copies and Codex staging/review state.

## Network Behavior

Talos runs a local HTTP server bound to `127.0.0.1`. It does not intentionally expose its API to the public network.

Talos does not include its own cloud AI model. When you use the Codex panel, Codex runs through the user's authenticated Codex environment. The selected workspace context, active file content, verify result, and any message you type may be sent to Codex according to the Codex/OpenAI product surface you are using.

## Arduino And Local Tools

Talos may call local tools such as `arduino-cli`, inspect local Arduino IDE process/window metadata, and read or write files inside the selected sketch folder when you explicitly save or approve a change.

## Data Removal

Uninstalling Talos removes installer-owned program files. It does not automatically delete user runtime data under `%LOCALAPPDATA%\T-Engine\Talos`. Remove that folder manually if you want to delete local Talos settings, history, checkpoints, sandbox data, and staging data.

