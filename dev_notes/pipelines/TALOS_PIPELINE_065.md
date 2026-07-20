# Talos Pipeline - Version 0.6.5 Beta

Purpose: reduce Python from hot-path and mixed-ownership app logic after 0.6.0 establishes shell/core/API/runtime/target boundaries. This is a decomposition release, not a feature-expansion release.

```text
0.6.5 Beta = Python decomposition + native/core extraction + performance parity + compatibility fallback.
```

Release evidence: `dev_notes/evidence/TALOS_065_EVIDENCE.md`

## Exit Condition

0.6.5 is complete when the heaviest Python-owned paths are either moved behind native/core boundaries or explicitly scheduled with measured risk, the source/debug launcher still works, Arduino behavior is unchanged, and later Arduino hardening can proceed without depending on Python-only shortcuts.

Stage completion rule: every migration stage must include a before/after measurement, a fallback path, or a regression test.

## Stage 0 - Baseline And Measurement Setup

Purpose: measure before changing implementation ownership.

- [ ] Confirm 0.6.0 boundary implementation is complete.
- [ ] Record current timings for Arduino detection, workspace scan, file list generation, hash/cache key generation, verify preparation, diff/hunk parsing, and Codex context packaging.
- [ ] Record current Python module ownership from the 0.6.0 map.
- [ ] Confirm no new target work starts in this release.
- [ ] Keep `desktop_app.py` as the debug/source launcher.

Exit condition: Python reduction starts from measured behavior, not guesswork.

## Stage 1 - Process And Window Detection Extraction

Purpose: reduce Python cost and fragility in external-app detection.

- [ ] Route Arduino process/window detection through the native helper boundary when available.
- [ ] Keep Python fallback detection for unsupported environments.
- [ ] Add timing and fallback labels to state/diagnostics.
- [ ] Test detection with native available and native missing.

Exit condition: detection is native-backed when possible and remains safe when native support is absent.

## Stage 2 - Workspace Scan And File Metadata Extraction

Purpose: move repeated file enumeration and metadata collection away from ad hoc Python loops.

- [ ] Add a core/native-backed workspace scanner interface.
- [ ] Preserve source file ordering and Arduino tab behavior.
- [ ] Add debounce/cache invalidation rules for file changes.
- [ ] Test `.ino`, `.h`, `.cpp`, and mixed sketch-folder cases.
- [ ] Record scan timing before and after.

Exit condition: file metadata is collected through a reusable scanner boundary with fallback behavior.

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
