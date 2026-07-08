# Talos Pipeline - Version 0.3.0 Beta

## Final Goal For 0.3.0

Talos 0.3.0 Beta should make the Codex-Arduino workflow feel mature, predictable, and low-friction on top of the completed 0.2.0 packaged Arduino foundation.

This version is not a MATLAB release and not the final 1.0.0 Alpha. It focuses on the core product value:

```text
0.3.0 Beta = clearer Codex context, safer change review, faster save/verify decisions.
```

## Baseline

```text
Roadmap: docs/TALOS_ROADMAP.md
Previous completed pipeline: docs/TALOS_PIPELINE_020.md
Current active pipeline: docs/TALOS_PIPELINE_030.md
Target version: 0.3.0 Beta
```

Talos 0.2.0 Beta already completed packaged Arduino reliability, installed-app validation, sketch/board/profile detection, responsive verify, workbench UX, safety recovery, installer smoke, installed-app smoke, and full manual Arduino smoke confirmation. Version 0.3.0 should preserve those guarantees while improving the Codex-facing workflow.

## 0.3.0 Release Criteria

Talos 0.3.0 Beta is ready only when these are true:

- A user can understand exactly what Arduino context Codex receives before sending a request.
- Codex task, conversation, reconnect, cancel, and recovery states are clear and do not replay user turns accidentally.
- Staged Codex changes are easy to inspect by file and hunk, then apply, reject, verify, or save without ambiguity.
- Verify-before-save remains the recommended path for Codex-generated edits.
- Talos still never writes Codex changes into the real Arduino sketch unless the user explicitly saves.
- Per-sketch Codex/run history is useful for debugging, support, and restoring context after restart.
- The 0.2.0 packaging, installer, installed-app, and manual Arduino smoke guarantees still pass.

## Non-Goals For 0.3.0

- No MATLAB or second-app integration.
- No commercial-grade hardware upload or serial-monitor guarantee.
- No plugin SDK or marketplace.
- No auto-update infrastructure.
- No AI model hosting inside Talos; Codex remains the external reasoning layer.
- No rewrite of the Arduino detection, staging, or packaging foundations unless required to fix a concrete 0.3.0 blocker.

## Progress Rules

- Keep `docs/TALOS_PIPELINE_010.md` and `docs/TALOS_PIPELINE_020.md` as frozen history records.
- Track all 0.3.0 work in this file.
- Every completed 0.3.0 task must update this file.
- Do not add MATLAB or unrelated app targets to this pipeline.
- Use the pipeline status checker with this file:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1 -Path docs\TALOS_PIPELINE_030.md
```

## Stage 0 - 0.3.0 Pipeline Setup

Purpose: establish 0.3.0 as the active version-specific Codex workflow pipeline.

- [x] Preserve the completed 0.2.0 Beta pipeline as `docs/TALOS_PIPELINE_020.md`.
- [x] Create a dedicated 0.3.0 Beta pipeline as `docs/TALOS_PIPELINE_030.md`.
- [x] Update `docs/TALOS_ROADMAP.md` so 0.2.0 is complete and 0.3.0 is active.
- [ ] Decide whether project docs and helper scripts should default to pipeline 0.3.0 during development.

Exit condition: 0.3.0 has its own active pipeline and no 0.2.0 release-history file needs to be edited for new implementation work.

## Stage 1 - 0.2.0 Baseline Lock

Purpose: make sure 0.3.0 starts from a stable 0.2.0 foundation instead of accidentally regressing packaging or Arduino reliability.

- [ ] Run `scripts/check.ps1` and record the result.
- [ ] Run pipeline status for `docs/TALOS_PIPELINE_030.md`.
- [ ] Confirm the 0.2.0 release artifacts remain available for comparison.
- [ ] Review current dirty/uncommitted files and separate 0.2.0 release fixes from new 0.3.0 work.
- [ ] Add or update a short 0.3.0 baseline note if any known carry-over risk exists.

Exit condition: automated checks pass and the repository has a clear 0.3.0 starting point.

## Stage 2 - Codex Context Package Maturity

Purpose: make pre-send context compact, inspectable, and trustworthy.

- [ ] Show a concise context preview before sending: workspace map, active file, selected sketch, board/profile, verify status, and edit permission.
- [ ] Add a compact workspace-map summary that distinguishes main sketch, headers, sources, docs, and ignored files.
- [ ] Add context size/coverage indicators so users understand whether Codex receives the active file, all files, or a reduced summary.
- [ ] Add copy/export for the exact context package used in the next Codex turn.
- [ ] Add regression coverage that context packaging stays scoped to the selected Arduino sketch folder.

Exit condition: users can inspect and copy the Codex context package before a turn, and tests prove it cannot leak outside the selected sketch.

## Stage 3 - Codex Conversation And Task State

Purpose: make the Codex panel behave like a dependable task workspace rather than a loose chat box.

- [ ] Improve visible states for new conversation, active conversation, pending turn, cancelled turn, failed turn, retry/reconnect, and recovered review.
- [ ] Keep per-sketch conversation/task history easy to scan and reopen.
- [ ] Prevent automatic replay of a user turn after reconnect unless the user explicitly sends it again.
- [ ] Add clear empty states when Codex is unavailable, disconnected, or missing context.
- [ ] Record Codex turn lifecycle events with enough data for support debugging.

Exit condition: a user can tell what Codex is doing, recover from transient failures, and continue without duplicate or hidden turns.

## Stage 4 - Staged Change Review Ergonomics

Purpose: reduce friction when reviewing Codex edits while keeping Arduino IDE as the saved-source owner.

- [ ] Make file-level and hunk-level review states visually clear: pending, applied to editor, rejected, saved, conflict, and recovered.
- [ ] Improve apply/reject controls for one hunk, one file, or a full Codex turn.
- [ ] Keep diff highlighting readable for small sketches and multi-file `.h/.cpp` projects.
- [ ] Make conflict choices explicit: keep Arduino version, draft merge, reject Codex, or apply to Talos editor only.
- [ ] Add tests for review state transitions across restart and active-file switching.

Exit condition: users can review and decide on Codex edits without guessing what will change in Talos or Arduino IDE.

## Stage 5 - Verify-Before-Save Loop

Purpose: make the safest Codex workflow fast: apply to Talos editor, verify sandbox, then save to Arduino IDE.

- [ ] Make `Save & Verify` behavior explicit for normal edits and Codex-applied edits.
- [ ] Warn when a user tries to save Codex-generated changes without a current successful verify result.
- [ ] Keep verify output tied to the active file/sketch so old results do not look current.
- [ ] Preserve cancellation, cache clear, timing, and one-current-result behavior from 0.2.0.
- [ ] Add regression coverage for save, save-and-verify, verify cache, and external Arduino edits during the loop.

Exit condition: verify-before-save is clear, fast, and still protected against external Arduino edits.

## Stage 6 - History, Evidence, And Supportability

Purpose: make Codex/Arduino workflow history useful for debugging and user support.

- [ ] Add per-sketch filters for run history, verify results, Codex turns, saved changes, conflicts, and rollbacks.
- [ ] Add copy/export for a support bundle containing app/build metadata, selected workspace summary, profile, latest verify result, and recent Codex/change history.
- [ ] Keep sensitive local paths visible enough for debugging but easy to redact before sharing.
- [ ] Add release evidence entries for key 0.3.0 manual workflow checks.
- [ ] Document the support/debug workflow in project docs.

Exit condition: a user can provide enough local evidence to debug a Codex-Arduino issue without manually copying scattered UI panels.

## Stage 7 - 0.3.0 Release Gate

Purpose: package and validate the completed 0.3.0 Beta.

- [ ] Run full automated checks.
- [ ] Run manual Codex-Arduino workflow smoke tests for simple `.ino`, multi-file `.h/.cpp`, AVR board, ESP32 board, conflict recovery, and reconnect/cancel behavior.
- [ ] Build final 0.3.0 Beta release artifacts.
- [ ] Sign artifacts or explicitly mark unsigned Beta status.
- [ ] Run installer smoke and installed-app smoke.
- [ ] Generate final 0.3.0 distribution checklist with `-RequireReady`.
- [ ] Bump app identity, release manifest naming, and release notes from 0.2.0 to 0.3.0 only at the final release gate.
- [ ] Update release notes with 0.3.0 workflow fixes, known limitations, and upgrade notes.

Exit condition: Talos 0.3.0 Beta can be installed, run outside the development environment, provide a mature Codex-Arduino workflow, and ship with release evidence.

## Deferred Until After 0.3.0

- MATLAB target integration.
- Hardware upload and serial-monitor guarantees.
- Auto-update infrastructure.
- Public plugin/target SDK.
- 1.0.0 Alpha release gate.
