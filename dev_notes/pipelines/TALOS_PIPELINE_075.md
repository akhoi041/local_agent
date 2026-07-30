# Talos Pipeline - Version 0.7.5 Beta

Purpose: harden the Arduino workflow now that 0.7.0 moved Arduino behavior behind the target-adapter/core contracts. This release is for daily-use reliability, not new target products or another architecture rewrite.

```text
0.7.5 Beta = Arduino workflow hardening + recovery polish + low-friction daily use.
```

Release evidence: `dev_notes/evidence/TALOS_075_EVIDENCE.md`

## 0.7.0 Handoff Baseline

0.7.0 completed the Arduino adapter port:

- Arduino discovery, workspace mapping, board/profile payloads, verify plans, Codex context packaging, and change-review boundaries are adapter-owned.
- `desktop_app.py` remains the source/debug launcher.
- Missing Codex runtime is informational and must not block Arduino workspace readiness.
- Python is still allowed as compatibility/debug bridge, but new Arduino behavior should enter through target adapter/core boundaries.
- No MATLAB, STM32CubeIDE, KiCad, SolidWorks, or runtime-independence work belongs in 0.7.5.

## Exit Condition

0.7.5 is complete when Arduino can be used repeatedly in normal development sessions with stable detection, save/verify/review/recovery behavior, clear runtime status, and concise support evidence.

Stage completion rule: every stage must include a manual smoke item, an automated regression item, or an evidence note. Prefer focused local tests before full regression.

Version handoff rule: this pipeline must end with a handoff stage for 0.8.0.

## Stage 0 - Baseline Refresh

Purpose: start hardening from measured 0.7.0 behavior.

- [x] Confirm current branch and version metadata.
- [x] Record current Arduino adapter status from 0.7.0 evidence.
- [x] Run focused Stage 070 adapter smoke as the baseline.
- [x] Record blocked items, if any, in `dev_notes/evidence/TALOS_075_EVIDENCE.md`.

Exit condition: 0.7.5 starts from a known 0.7.0 adapter state.

Stage 0 implementation note: local branch is `develop/0.7.5`, app identity is `0.7.5 Beta`, and the 0.7.0 adapter state is recorded in the 0.7.5 evidence file. No blocked items were found.

## Stage 1 - Daily Arduino Detection Hardening

Purpose: make open-sketch detection reliable under normal user behavior.

- [x] Test open/close/reopen Arduino IDE windows without stale sketches.
- [x] Test multiple sketches and source tabs from different parent folders.
- [x] Keep event-assisted refresh with polling fallback.
- [x] Record detection timing and stale-state behavior.

Exit condition: sketch list updates quickly and does not resurrect closed sketches.

Stage 1 implementation note: Arduino discovery now drops stale process-sourced `.ino` paths when live Arduino window titles resolve to different saved sketch folders. Focused Stage 1 tests cover reopen replacement, multi-folder source-tab detection, event debounce fallback, and a local refresh timing budget. Full local regression passed.

## Stage 2 - Workspace And File Sync Hardening

Purpose: keep Talos review/editor state aligned with Arduino-owned files.

- [x] Verify selected file highlight, line numbers, and active-file status after scrolling and switching files.
- [x] Verify save writes remain explicit and atomic.
- [x] Verify Arduino external edits are detected without overwriting user work.
- [x] Keep Talos editor in review/local-edit mode, not as an Arduino IDE replacement.

Exit condition: file state remains understandable and user-owned.

Stage 2 focused implementation note: Arduino file reads now include a content hash, Save File sends the loaded hash and mtime back to the backend, and stale saves are rejected before the atomic replace if Arduino IDE changed the file externally. The UI marks the active file as conflicted instead of overwriting user-owned Arduino edits.

## Stage 3 - Verify Workflow Hardening

Purpose: make sandbox verify fast, cancellable, and easy to read.

- [ ] Validate cache hit/miss labels and clear-cache behavior.
- [ ] Validate cancel behavior during compile.
- [ ] Keep verify output concise by default with copyable details.
- [ ] Record timing telemetry for prepare, sandbox copy, compile, and total time.

Exit condition: verify is predictable and recoverable during normal use.

## Stage 4 - Codex Runtime UX Hardening

Purpose: make missing or disconnected runtime states clear without blocking Arduino work.

- [ ] Keep runtime missing as a Codex-only status.
- [ ] Validate reconnect/status messaging without replaying user turns.
- [ ] Keep context package copy available for manual fallback.
- [ ] Confirm no credential capture is added.

Exit condition: users know whether Codex can act, and Arduino remains usable when it cannot.

## Stage 5 - Change Review And Recovery Hardening

Purpose: make Codex edits safe to inspect, apply, save, verify, or roll back.

- [ ] Validate hunk apply/reject/apply-all/reject-all.
- [ ] Validate save acknowledgement and rollback history.
- [ ] Validate pending review persistence across restart where possible.
- [ ] Keep Arduino Version as the non-destructive default for external conflicts.

Exit condition: Codex changes never silently overwrite Arduino-owned work.

## Stage 6 - UI Daily-Use Polish

Purpose: remove friction from the current Arduino workbench.

- [ ] Validate command palette, status bar, menu bar, keyboard shortcuts, and find behavior.
- [ ] Validate normal/maximized/resized layouts with Explorer and Codex panels open/closed.
- [ ] Keep toolbar actions grouped and non-overlapping during verify/Codex activity.
- [ ] Record any UI items deferred beyond 0.7.5.

Exit condition: a tester can use the Arduino workflow for a full session without layout confusion.

## Stage 7 - Support Evidence And Release Gate

Purpose: prove 0.7.5 is ready to hand to the core-complete release.

- [ ] Generate concise support bundle/evidence for one daily-use smoke run.
- [ ] Run automated regression.
- [ ] Run manual Arduino smoke from open sketch through verify and save/recovery.
- [ ] Update `dev_notes/evidence/TALOS_075_EVIDENCE.md`.

Exit condition: 0.7.5 daily-use hardening is validated.

## Stage 8 - 0.8.0 Handoff

Purpose: hand the hardened Arduino workflow to the Talos Core Complete release.

- [ ] Update roadmap status for 0.7.5 completion.
- [ ] Create or update `dev_notes/pipelines/TALOS_PIPELINE_080.md` from the real 0.7.5 state.
- [ ] List remaining adapter/core gaps that 0.8.0 must close before new target products.
- [ ] Confirm no new target product work starts before 0.8.0 completes the core gate.

Exit condition: 0.8.0 can focus on core completeness rather than Arduino daily-use bugs.
