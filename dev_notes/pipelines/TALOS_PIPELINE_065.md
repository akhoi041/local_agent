# Talos Pipeline - Version 0.6.5 Beta

Purpose: reduce Python from hot-path and mixed-ownership app logic after 0.6.0 establishes shell/core/API/runtime/target boundaries. This is a decomposition release, not a feature-expansion release.

```text
0.6.5 Beta = Python decomposition + native/core extraction + performance parity + compatibility fallback.
```

Release evidence: `dev_notes/evidence/TALOS_065_EVIDENCE.md`

## 0.6.0 Handoff Baseline

0.6.0 completed the real architecture foundation that 0.6.5 depends on:

- `desktop_app.py` remains the source/debug launcher.
- Shell ownership, core runtime ownership, local API contracts, target hosting, runtime providers, Python ownership, native helper access, and Arduino compatibility smoke now have explicit boundaries.
- Python is still allowed as bridge/fallback/migration code, but the known hot paths are documented and measurable.
- 0.6.5 must not add new target products. It must reduce or contain Python hot paths while preserving current Arduino behavior.

## Exit Condition

0.6.5 is complete when the heaviest Python-owned paths are either moved behind native/core boundaries or explicitly scheduled with measured risk, the source/debug launcher still works, Arduino behavior is unchanged, and later Arduino hardening can proceed without depending on Python-only shortcuts.

Stage completion rule: every migration stage must include a before/after measurement, a fallback path, or a regression test.

## Stage 0 - Baseline And Measurement Setup

Purpose: measure before changing implementation ownership.

- [x] Confirm 0.6.0 boundary implementation is complete.
- [x] Record current timings for Arduino detection, workspace scan, file list generation, hash/cache key generation, verify preparation, diff/hunk parsing, and Codex context packaging.
- [x] Record current Python module ownership from the 0.6.0 map.
- [x] Confirm no new target work starts in this release.
- [x] Keep `desktop_app.py` as the debug/source launcher.

Exit condition: Python reduction starts from measured behavior, not guesswork.

Stage 0 implementation note: added `talos/stage_baseline.py` to capture a repeatable synthetic Arduino baseline without touching user sketches. Evidence is recorded in `dev_notes/evidence/TALOS_065_EVIDENCE.md`.

## Stage 1 - Process And Window Detection Extraction

Purpose: reduce Python cost and fragility in external-app detection.

- [x] Route Arduino process/window detection through the native helper boundary when available.
- [x] Keep Python fallback detection for unsupported environments.
- [x] Add timing and fallback labels to state/diagnostics.
- [x] Test detection with native available and native missing.

Exit condition: detection is native-backed when possible and remains safe when native support is absent.

Stage 1 implementation:

- Added `talos.detection` as the state-facing detection contract for Arduino process/window rows.
- `/api/state` now reports detection backend labels, fallback status, row counts, and timing without performing a second scan.
- Native and fallback behavior are covered by targeted tests.

## Stage 2 - Workspace Scan And File Metadata Extraction

Purpose: move repeated file enumeration and metadata collection away from ad hoc Python loops.

- [x] Add a core/native-backed workspace scanner interface.
- [x] Preserve source file ordering and Arduino tab behavior.
- [x] Add debounce/cache invalidation rules for file changes.
- [x] Test `.ino`, `.h`, `.cpp`, and mixed sketch-folder cases.
- [x] Record scan timing before and after.

Exit condition: file metadata is collected through a reusable scanner boundary with fallback behavior.

Stage 2 implementation note:

- Added `talos.workspace_scanner` as the single source metadata scanner boundary.
- Kept the existing public file ordering stable for UI/API compatibility while still identifying the main sketch.
- Added scan cache hit/debounce metadata and cache invalidation by file path, size, and mtime.
- Routed Arduino workspace summary and source-file iteration through the scanner.

## Stage 3 - Hashing And Cache-Key Extraction

Purpose: make verify/context caching fast and deterministic.

- [ ] Route workspace hash and cache-key generation through one helper boundary.
- [ ] Include board/profile/build flags/source file state in cache keys.
- [ ] Keep clear cache behavior explicit.
- [ ] Add tests for cache hit, cache miss, source change, board change, and profile change.

Exit condition: cache keys are stable, fast, and no longer scattered across Python helpers.

## Stage 4 - Diff And Hunk Helper Extraction

Purpose: make review/apply behavior reusable for future code and design targets.

- [ ] Move diff/hunk parsing behind a helper interface.
- [ ] Preserve current apply/reject/all hunk semantics.
- [ ] Keep editor-visible review behavior unchanged.
- [ ] Add tests for add/update/delete hunks, rejected hunks, partial apply, and save-after-apply.
- [ ] Record timing for large files.

Exit condition: diff/hunk behavior is target-neutral and ready for future adapters.

## Stage 5 - Task Orchestration Cleanup

Purpose: reduce Python global-state coupling in verify, Codex, and file operations.

- [ ] Move long-running operation state into the core runtime boundary.
- [ ] Keep cancellation, status, and event history consistent.
- [ ] Prevent repeated PowerShell/CMD window churn during checks.
- [ ] Add tests for verify start/cancel/cache-clear and Codex reconnect/retry status.
- [ ] Record before/after UI responsiveness notes.

Exit condition: task orchestration is centralized and does not leak transient process behavior into the user experience.

## Stage 6 - Runtime Provider Cleanup

Purpose: make runtime integration independent from Python-only discovery assumptions.

- [ ] Move runtime discovery candidates behind provider configuration.
- [ ] Keep manually pinned runtime path behavior.
- [ ] Keep missing-runtime state informational, not a broken Arduino state.
- [ ] Confirm no credentials or token material are persisted.
- [ ] Add tests for missing, pinned, invalid, and healthy runtime metadata.

Exit condition: runtime provider behavior is clean enough for later independence work.

## Stage 7 - Regression And Performance Gate

Purpose: prove the decomposition did not damage product behavior.

- [ ] Run automated regression.
- [ ] Run source/debug launch check.
- [ ] Run Arduino detection/select/file inspect smoke.
- [ ] Run sandbox verify smoke.
- [ ] Run Codex context package smoke without requiring credential capture.
- [ ] Record performance comparison in `dev_notes/evidence/TALOS_065_EVIDENCE.md`.

Exit condition: 0.6.5 improves or contains Python hot paths while preserving the working app.

## Stage 8 - 0.7.0 Handoff

Purpose: hand the decomposed architecture to the Arduino adapter-port release.

- [ ] Update roadmap status for 0.6.5 completion.
- [ ] Prepare or update `dev_notes/pipelines/TALOS_PIPELINE_070.md` based on actual architecture state.
- [ ] List any remaining Python-only paths that are acceptable during 0.7.0.
- [ ] Record final evidence in `dev_notes/evidence/TALOS_065_EVIDENCE.md`.

Exit condition: 0.7.0 can focus on Arduino adapter/product behavior rather than architecture cleanup.
