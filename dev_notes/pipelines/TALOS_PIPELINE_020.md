# Talos Pipeline - Version 0.2.0 Beta

## Final Goal For 0.2.0

Talos 0.2.0 Beta should turn the completed 0.1.0 technical MVP into a more reliable Arduino-first Beta that can be installed, tested outside the source tree, and used repeatedly with real Arduino sketches.

This version is not a MATLAB release and not the final 1.0.0 Alpha. It focuses on the next logical product step:

```text
0.2.0 Beta = packaged Arduino reliability and daily-use readiness.
```

## Baseline

```text
Roadmap: dev_notes/roadmap/TALOS_ROADMAP.md
Previous completed pipeline: dev_notes/pipelines/TALOS_PIPELINE_010.md
Current active pipeline: dev_notes/pipelines/TALOS_PIPELINE_020.md
Target version: 0.2.0 Beta
```

Talos 0.1.0 Beta already completed the Arduino MVP, Codex bridge, staged change review, sandbox verify, native Windows detection, release packaging scripts, installer smoke tooling, and distribution checklist tooling. Version 0.2.0 should not redesign those foundations unless a reliability issue requires it.

## 0.2.0 Release Criteria

Talos 0.2.0 Beta is ready only when these are true:

- It can be built, installed, launched outside the source tree, smoke-tested, and uninstalled with release evidence.
- It can repeatedly detect live saved Arduino sketches without keeping stale closed sketches in the active list.
- It can keep board/profile information synchronized for the selected sketch when Arduino IDE exposes usable metadata.
- It can verify sandbox builds without stale output accumulation and with clear cache/cancel behavior.
- It remains usable in normal, maximized, and narrow desktop windows without fixed-layout failures.
- It preserves the 0.1.0 safety contract: Codex changes never write directly to the real Arduino sketch, and external Arduino edits are not silently overwritten.

## Non-Goals For 0.2.0

- No MATLAB or second-app integration.
- No commercial-grade upload or serial-monitor guarantee.
- No plugin SDK or marketplace.
- No auto-update infrastructure.
- No rewrite of the Codex bridge, staging workspace, or native detection layer unless required to fix a concrete reliability bug.

## Progress Rules

- Keep `dev_notes/pipelines/TALOS_PIPELINE_010.md` as the frozen 0.1.0 Beta comparison record.
- Track all 0.2.0 work in this file.
- Every completed 0.2.0 task must update this file.
- Do not add MATLAB or unrelated app targets to this pipeline.
- Use the pipeline status checker with this file:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1 -Path dev_notes\pipelines\TALOS_PIPELINE_020.md
```

## Stage 0 - 0.2.0 Pipeline Setup

Purpose: establish this file as the active version-specific pipeline.

- [x] Preserve the completed 0.1.0 Beta pipeline as `dev_notes/pipelines/TALOS_PIPELINE_010.md`.
- [x] Create a dedicated 0.2.0 Beta pipeline as `dev_notes/pipelines/TALOS_PIPELINE_020.md`.
- [x] Update documentation and pipeline status defaults to use the active 0.2.0 pipeline.
- [x] Remove obsolete generic pipeline filenames after references are migrated.

Exit condition: the repository has a version-specific 0.1.0 history pipeline and a version-specific active 0.2.0 pipeline, with no active workflow depending on generic `TALOS_PIPELINE.md` or `TALOS_PIPELINE_NEXT.md`.

## Stage 1 - Release Candidate Validation

Purpose: prove that the current app can be built, installed, launched, and uninstalled outside the development folder before deeper 0.2.0 reliability work begins.

- [x] Build a clean release folder without `-AllowDirty`.
- [x] Build the Windows installer from the clean release output.
- [x] Record signing status as signed or explicit unsigned Beta.
- [x] Run installer install/uninstall smoke and record `installer_smoke.json`.
- [x] Run installed-app smoke outside the source tree and record `installed_app_smoke.json`.
- [x] Generate `DISTRIBUTION_CHECKLIST.md` with `-RequireReady`.
- [x] Confirm `desktop_app.py` still launches the source app for debug.
- [x] Record packaging/runtime issues found during release-candidate validation.

Stage evidence: `dev_notes/evidence/TALOS_020_STAGE1_VALIDATION.md`.

Exit condition: the app can be installed and launched outside the source tree, uninstalled cleanly, and represented by complete release evidence.

## Stage 2 - Arduino Detection Reliability

Purpose: make live Arduino IDE detection more dependable across real-world sketch/window workflows.

- [x] Test multiple Arduino IDE windows with saved sketches on different folders.
- [x] Test closing a sketch/window and confirm Talos removes stale candidates quickly.
- [x] Test switching focus between `.ino`, `.h`, and `.cpp` tabs without losing the real sketch folder.
- [x] Improve board-to-sketch mapping for common AVR and ESP32 boards when multiple IDE windows are open.
- [x] Add diagnostics for missing or ambiguous board/FQBN detection.
- [x] Add regression coverage for stale sketch and stale board cases found during manual testing.

Exit condition: Talos reliably lists only live saved sketches and keeps the selected sketch's board/profile synchronized when Arduino IDE exposes enough metadata.

## Stage 3 - Verify And Runtime Responsiveness

Purpose: make sandbox verification fast, cancellable, and predictable enough for repeated daily use.

- [x] Validate verify cache invalidation for source edits, profile edits, board changes, CLI path changes, and build-property changes.
- [x] Tune verify cancellation and clear-cache feedback so users understand what happened.
- [x] Keep verify output from accumulating stale passed/failed cards after a new verify starts.
- [x] Review sandbox copy exclusions for common Arduino build/cache folders.
- [x] Add timing thresholds or telemetry checks for prepare, copy, compile, and total verify time.

Exit condition: Verify Sandbox provides one current result, clear cancellation/cache behavior, and actionable timing data without blocking the workbench.

## Stage 4 - Arduino Workbench UX Polish

Purpose: reduce friction in the Arduino workbench while preserving Arduino IDE as the owner of the real sketch.

- [x] Polish responsive layout at normal, maximized, and narrow desktop sizes.
- [x] Make Explorer, Change Workspace, Verify Output, and Codex panes resizable where useful without fixed-pixel layout failures.
- [x] Keep active-file highlighting in the Files list as the primary file location signal.
- [x] Simplify labels around Review, Edit in Talos, Save File, Save And Verify, Rollback, and Verify Sandbox.
- [x] Add first-run or empty-state hints explaining Arduino IDE ownership and Talos save boundaries.

Exit condition: a user can understand and operate the Arduino workflow without reading developer notes, and the UI remains usable outside maximized windows.

## Stage 5 - Codex Context And Change Loop Stability

Purpose: make the Codex side of the Arduino loop clear, recoverable, and useful without expanding scope beyond Arduino.

- [x] Ensure pre-send context clearly shows workspace map, active file, profile, verify result, and edit permission.
- [x] Improve Codex panel states for tasks, active conversation, pending turn, cancellation, reconnect, and recovery.
- [x] Keep staged changes grouped by file, hunk, and Codex turn.
- [x] Recommend verify-before-save for Codex-generated changes.
- [x] Record Codex turn outcomes by sketch in run history for debugging and support.

Exit condition: a user can ask Codex for an Arduino change, understand what context was sent, review the result, verify it, and decide whether to save it.

## Stage 6 - Safety And Recovery Hardening

Purpose: protect real Arduino sketches from accidental overwrite during normal Talos/Codex usage.

- [x] Expand conflict tests for external Arduino IDE edits while Talos has staged or editor-applied changes. Added regression coverage for staged Codex files and editor-applied Codex files becoming conflict state after external Arduino edits.
- [x] Test restart recovery during pending review, staged verify, save, and rollback flows. Existing restart/recovery, staged verify, save checkpoint, and guarded rollback tests pass in the full regression suite.
- [x] Make restore/discard decisions for unfinished reviews clear after restart. Recovery UI now labels `Restore Reviews` and `Discard Reviews` with explicit Arduino-workspace safety text.
- [x] Confirm rollback refuses to overwrite files changed after the saved checkpoint. Guarded rollback regression confirms Talos refuses rollback after an external file change.
- [x] Document the safest manual recovery path when a user edits both Arduino IDE and Talos at the same time. Added `docs/TALOS_RECOVERY_GUIDE.md` and linked it from the README.

Exit condition: no normal Talos/Codex path can silently overwrite external Arduino changes, and recovery is understandable after restart.

## Stage 7 - 0.2.0 Release Gate

Purpose: package and validate the completed 0.2.0 Beta.

- [x] Run full automated checks. `scripts/check.ps1` passes native build/export checks, native benchmark, unit tests, release recovery smoke, and pipeline status.
- [x] Run manual Arduino smoke tests for simple `.ino`, multi-file `.h/.cpp`, AVR board, and ESP32 board cases. Installed-app auto Arduino/Codex harness passed with `arduino:avr:uno`; user manual confirmation passed for the full smoke matrix.
  - [x] Simple `.ino` sketch opens in Arduino IDE, appears in Talos Open Sketches, can be selected, and does not remain listed after the Arduino window is closed.
  - [x] Multi-file sketch with `.ino`, `.h`, and `.cpp` tabs appears as one sketch, shows all source files in Files, and opens each file content correctly in Talos.
  - [x] AVR board case, for example Arduino Uno/Nano, shows the correct board/profile, saves workspace profile, and `Verify Sandbox` passes or reports a clear actionable Arduino CLI error.
  - [x] ESP32 board case shows the correct board/profile, saves workspace profile, and `Verify Sandbox` passes or reports a clear actionable Arduino CLI error.
  - [x] Edit-in-Talos flow: enable editing, change a harmless line/comment, `Save File`, confirm Arduino IDE reflects the saved change, then `Save & Verify` works.
  - [x] Codex flow: ask for a small safe change, review the proposed change, apply to Talos editor, confirm Arduino IDE is not modified before Save File, then save and verify.
  - [x] Safety/recovery flow: while Talos has a pending Codex/editor change, edit the same file in Arduino IDE and confirm Talos blocks silent overwrite or shows conflict/recovery choices.
  - [x] Runtime UX: during 15-20 minutes of normal use, Talos should not repeatedly flash PowerShell/CMD windows, should not accumulate stale verify output, and should remain responsive.
  - [x] Installed-app sanity: launch from Start Menu/installed executable, confirm packaged app data is used, close/reopen Talos, and confirm selected profile/history recovery behavior is understandable.
- [x] Build final 0.2.0 Beta release artifacts. `releases/Talos-0.2.0-beta/` contains the standalone executable, installer, release manifest, and release docs.
- [x] Sign artifacts or explicitly mark unsigned Beta status. `signing_status.json` records an explicit unsigned Beta according to `config/signing_policy.json`.
- [x] Run installer smoke and installed-app smoke. `installer_smoke.json` passed install/uninstall checks; `installed_app_smoke.json` passed packaged launch, health, and auto Arduino/Codex harness checks.
- [x] Generate final 0.2.0 distribution checklist with `-RequireReady`. `DISTRIBUTION_CHECKLIST.md` was generated successfully in the 0.2.0 release folder.
- [x] Bump app identity, release manifest naming, and release notes from 0.1.0 to 0.2.0 only at the final release gate. `config/app_identity.json`, Inno fallback metadata, and release docs now target 0.2.0 Beta.
- [x] Update release notes with 0.2.0 fixes, known limitations, and upgrade notes.

Exit condition: Talos 0.2.0 Beta can be installed, run outside the development environment, operate reliably with real Arduino sketches, and ship with release evidence.

## Deferred Until After 0.2.0

- MATLAB target integration.
- Hardware upload and serial-monitor guarantees.
- Auto-update infrastructure.
- Public plugin/target SDK.
- 1.0.0 Alpha release gate.
