# Talos Release Notes

## 0.5.5 Beta

Talos 0.5.5 Beta is an architecture-slimming release. It keeps the working Arduino/Codex workflow intact while making the codebase easier to migrate away from Python-heavy app logic over time.

### Highlights

- Clarifies the documentation taxonomy by separating user/release docs from internal pipelines, roadmap notes, and evidence.
- Splits server responsibilities behind clearer service boundaries for event state, state composition, Codex runtime readiness, and architecture health checks.
- Starts the frontend module split without introducing a Node.js build requirement.
- Adds architecture-health guardrails so Python growth, shell/runtime assumptions, and native-helper boundaries stay visible.
- Records the long-term direction: keep Python as the compatibility bridge for now, move OS hot paths and future app-shell work behind stable adapter boundaries, and harden Arduino before adding other targets.

### Known Limitations

- Python still owns the source/debug launcher, local HTTP bridge, Arduino/Codex orchestration, and compatibility fallbacks.
- Codex runtime independence is not complete. Talos can discover and pin a local runtime, but authentication remains owned by that runtime.
- Arduino remains the only supported target in this release.
- Hosted telemetry is still not included. Diagnostics remain local and opt-in.
- Manual Arduino/Codex smoke testing is still required before treating a rebuilt package as release-ready.

### Upgrade Notes

- Existing app data under `%LOCALAPPDATA%\T-Engine\Talos` is reused.
- No Node.js build step is introduced.
- Talos does not store OpenAI credentials, Codex session tokens, or inferred subscription plan data.

## 0.5.0 Beta

Talos 0.5.0 Beta adds the Codex Runtime Manager so Talos can discover, explain, pin, and health-check the local Codex runtime it uses.

### Highlights

- Adds runtime discovery for standalone `codex` on `PATH`, user-selected runtime paths, and VS Code extension-adjacent fallback runtimes.
- Adds explicit runtime metadata: provider, display path, version, short hash, pin state, health, auth readiness, app-server readiness, warnings, and limitations.
- Adds Settings and Server UI for runtime readiness, pin/clear actions, health refresh, and safe runtime/account metadata display.
- Routes Codex bridge startup and reconnect through the selected runtime boundary instead of blindly assuming `codex` is available.
- Blocks Codex user turns when the selected runtime is missing, changed, or unhealthy while keeping Arduino review, verify, diagnostics, and support workflows available.
- Adds redacted runtime evidence to support bundles and runtime lifecycle events to run history for easier debugging.

### Known Limitations

- Arduino remains the only supported target in this release; MATLAB and other app integrations are intentionally deferred.
- Codex authentication remains owned by the user's Codex runtime. Talos does not provide a separate Codex login, store OpenAI credentials, or infer subscription plan.
- Runtime auth/app-server readiness depends on what the selected runtime exposes locally.
- Talos may use a VS Code extension-adjacent runtime only as a fallback provider, not as the intended long-term product dependency.
- Hosted telemetry is still not included. Diagnostics remain local and opt-in.
- The Beta installer may be unsigned until code signing is configured; Windows may show SmartScreen or unknown-publisher warnings.

### Upgrade Notes

- Existing 0.4.0 app data under `%LOCALAPPDATA%\T-Engine\Talos` is reused.
- If a pinned Codex runtime changes after update, Talos warns instead of silently sending Codex turns.
- Open Settings > Codex Runtime to refresh health, pin a known-good runtime, clear a stale pin, or select a runtime path.

## 0.4.0 Pre-Alpha

Talos 0.4.0 Pre-Alpha focuses on product readiness for broader Arduino/Codex testing.

### Highlights

- Adds user-facing documentation for first run, troubleshooting, support bundles, diagnostics, install lifecycle, recovery, and UI/UX smoke checks.
- Adds local-only opt-in diagnostics with previewable redacted exports. Diagnostics are disabled by default and do not upload to a server in 0.4.0.
- Refreshes the workbench toward a VS Code-inspired developer-tool layout with a compact activity bar, Explorer, editor/review surface, bottom output panel, Codex column, menu bar, command palette, and status bar.
- Clarifies that Arduino IDE remains the saved-source owner while Talos stages, reviews, verifies, and optionally saves changes back to the sketch folder.
- Improves release-readiness evidence for clean install, upgrade, uninstall, app-data lifecycle, support bundle review, and distribution checklist gates.

### Known Limitations

- Arduino remains the only supported target in this release; MATLAB and other app integrations are intentionally deferred.
- Codex reasoning runs through the user's authenticated Codex environment. Talos does not include, replace, or embed an AI model.
- Hardware upload and serial workflows are not yet treated as commercial-release guarantees.
- Diagnostics are local-only in 0.4.0. Hosted opt-in feedback belongs to a later version after policy and consent are complete.
- The Pre-Alpha/Beta installer may be unsigned until code signing is configured; Windows may show SmartScreen or unknown-publisher warnings.
- Talos 0.4.0 uses an available Codex runtime and may fall back to the VS Code extension runtime. First-class runtime discovery, pinning, and sign-in readiness move to the 0.5.0 Runtime Manager.

### Upgrade Notes

- Existing 0.3.0 runtime data under `%LOCALAPPDATA%\T-Engine\Talos` is reused.
- The 0.4.0 diagnostics feature is disabled by default. Users must explicitly enable it in Settings before new diagnostics are recorded.
- Use `docs/TALOS_FIRST_RUN_CHECKLIST.md`, `docs/TALOS_TROUBLESHOOTING.md`, and `docs/TALOS_SUPPORT_DEBUG.md` when handing this build to external testers.
- Pending review, checkpoint, history, and workspace profile data should remain under the per-user Talos app-data folder.

## 0.3.0 Beta

Talos 0.3.0 Beta focuses on maturing the Codex-Arduino workflow after the packaged 0.2.0 baseline.

### Highlights

- Improves Codex context packaging with clearer workspace, active-file, profile, verify, and edit-scope previews.
- Adds stronger Codex task history and reconnect/cancel state so interrupted turns are visible without replaying user requests automatically.
- Refines staged change review with explicit hunk decisions, file-level review summaries, conflict choices, and apply-to-editor behavior.
- Makes Save + Verify safer by compiling the current Talos editor draft before writing back to the Arduino sketch folder.
- Adds per-sketch run-history filters for verify results, Codex turns, saved changes, conflicts, rollbacks, and release evidence.
- Adds a redacted support bundle for debugging without manually copying scattered UI panels.
- Keeps Arduino IDE as the saved-source owner while Talos acts as review, verification, support, and Codex coordination layer.

### Known Limitations

- Arduino remains the only supported target in this release; MATLAB and other app integrations are intentionally deferred.
- Codex reasoning still runs through the user's authenticated Codex environment. Talos does not include or replace an AI model.
- Hardware upload and serial workflows are not yet treated as commercial-release guarantees.
- Manual Arduino/Codex smoke checks still depend on the user's installed Arduino IDE, board packages, and available FQBNs.
- The Beta installer may be unsigned until code signing is configured.

### Upgrade Notes

- Existing 0.2.0 runtime data under `%LOCALAPPDATA%\T-Engine\Talos` is reused.
- Pending Codex reviews remain restorable after restart; conflicting Arduino edits require an explicit recovery decision.
- Support bundles redact local paths by default. Use full-path bundles only for private debugging.

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
