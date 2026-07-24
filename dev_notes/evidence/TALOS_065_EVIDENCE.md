# Talos 0.6.5 Evidence

Version: 0.6.5 Beta

Scope: Python decomposition, native/core extraction, performance parity, and compatibility fallback.

## Stage 0 - Baseline And Measurement Setup

Status: complete.

Stage 0 establishes the measured baseline before any Python hot-path reduction. The baseline uses a synthetic Arduino sketch workspace so it can run quickly and without touching the user's real Arduino projects or requiring `arduino-cli`.

### Boundary Confirmation

- 0.6.0 boundary implementation confirmed through `talos.python_ownership.boundary_check`.
- Boundary status: complete.
- No new target work starts in 0.6.5; Arduino remains the only active target.
- `desktop_app.py` remains the source/debug launcher.

### Timing Baseline

- `arduino_detection`: `0.009 ms`
- `workspace_scan`: `6.546 ms`
- `file_list_generation`: `0.002 ms`
- `hash_cache_key_generation`: `0.357 ms`
- `verify_preparation`: `0.002 ms`
- `diff_hunk_parsing`: `0.073 ms`
- `codex_context_packaging`: `0.001 ms`

Baseline sample:

- Main sketch: `talos_test.ino`
- Source files: `4`
- Context package size: `501 bytes`
- Detection sample: no real process touched; synthetic boundary measurement only.

### Python Hot-Path Ownership

Current hot paths recorded from the 0.6.0 ownership map:

- `talos.runtime_core` -> `native core`
- `talos.state_service` -> `native core`
- `talos.arduino` -> `target host`
- `talos.arduino_events` -> `target host`
- `talos.codex_runtime` -> `runtime host`
- `talos.codex_bridge` -> `runtime host`
- `talos.native_bridge` -> `native helper`
- `talos.native_boundary` -> `native helper`
- `talos.run_history` -> `storage`
- `talos.event_bus` -> `event bus`

### Validation

- `python -B -m py_compile talos\stage_baseline.py tests\test_desktop_app.py`: passed.
- `python -B -c "from talos.stage_baseline import run_stage_065_baseline; ..."`: passed.

Conclusion: Python reduction starts from measured behavior, not guesswork.

## Stage 1 - Process And Window Detection Extraction

Status: complete.

Stage 1 moves Arduino process/window detection reporting behind a small detection contract while preserving the native helper boundary and safe Python fallback. The app still scans process/window rows only once per state payload; the new state block summarizes which backend was used, whether fallback is active, row counts, and measured timings.

### Implementation

- Added `talos/detection.py` for detection summaries and native/fallback labels.
- Added `/api/state` field `detection` with:
  - `backend`
  - `native_backed`
  - `fallback_used`
  - `labels`
  - `timings_ms`
  - `counts`
- Kept existing `native_boundary` report intact for diagnostics compatibility.

### Validation

- Native-backed detection snapshot test: passed.
- Fallback detection snapshot test: passed.
- State payload detection summary test: passed.
- Single-scan state payload behavior remains covered.

Conclusion: detection is native-backed when possible, explicit about fallback when native support is absent, and ready for later native extraction work.

## Stage 2 - Workspace Scan And File Metadata Extraction

Status: complete.

Stage 2 centralizes Arduino workspace source metadata behind `talos.workspace_scanner`. The scanner reports file rows, main sketch identity, source count, timing, and cache/debounce state while keeping the existing public file ordering stable for UI and compatibility tests.

### Implementation

- Added `talos/workspace_scanner.py`.
- Routed `iter_source_files()` and `workspace_summary()` through the scanner boundary.
- Preserved existing alphabetic source-file ordering while identifying the Arduino main sketch separately.
- Added cache invalidation by workspace path, source extension set, ignored directory set, relative path, file size, and mtime.
- Exposed scan timing and cache metadata in `workspace_summary()["scan"]`.

### Validation

- Scanner ordering and main-sketch identity test: passed.
- Scanner cache hit and invalidation test: passed.
- Mixed `.ino`, `.h`, and `.cpp` workspace summary/map test: passed.
- `python -B -m py_compile talos\workspace_scanner.py talos\arduino.py tests\test_desktop_app.py`: passed.
- `python -B -m unittest -q tests.test_desktop_app`: passed, 145 tests.

Conclusion: Arduino source metadata now crosses a reusable scanner boundary and records measurable timing without changing the existing UI/API file order.

## Stage 3 - Hashing And Cache-Key Extraction

Status: complete.

Stage 3 centralizes workspace identity hashing and Arduino compile cache-key construction behind `talos.cache_keys`. The cache payload is deterministic and now records all inputs that should invalidate a verify result: workspace identity, board/FQBN properties, environment profile/build flags/build properties, CLI identity, source file metadata/content hashes, and staged file overrides.

### Implementation

- Added `talos/cache_keys.py`.
- Routed `talos.arduino.compile_cache_key()` through the new helper boundary.
- Routed diagnostics workspace hashing through `workspace_identity_hash()` so support/debug payloads keep local paths sanitized.
- Kept clear-cache behavior explicit through the existing Arduino cache clear functions.
- Added fallback source scanning inside the cache-key boundary for legacy callers that pass a minimal summary without `files`.

### Validation

- `python -B -m py_compile talos\cache_keys.py talos\arduino.py talos\diagnostics.py tests\test_desktop_app.py`: passed.
- `python -B -m unittest -q tests.test_desktop_app`: passed, 148 tests.

Conclusion: cache keys are stable, source-sensitive, profile-sensitive, board-sensitive, and no longer scattered across Python helpers.

## Stage 4 - Diff And Hunk Helper Extraction

Status: complete.

Stage 4 extracts review diff/hunk behavior into `talos.diff_hunks` so future adapters can reuse the same change-review primitives without depending on Codex bridge internals.

### Implementation

- Added `talos/diff_hunks.py`.
- Moved workspace snapshot diffing, patch hunk construction, staged patch file generation, applied-hunk materialization, review summaries, and large-file hunk timing into the helper boundary.
- Kept `talos.codex_bridge` as the workflow owner for Codex turns, review state, conflict handling, and save/apply operations.
- Preserved legacy imports from `talos.codex_bridge` by importing the helper functions there.

### Validation

- Helper tests cover add/delete/equal fast paths, update hunks, rejected hunks, partial apply, and large-file timing.
- Existing bridge tests continue to cover selected-hunk apply, apply-all, reject flows, conflict handling, and save-after-apply.

Conclusion: diff/hunk behavior is now target-neutral while the visible Codex review workflow remains unchanged.

## Stage 5 - Task Orchestration Cleanup

Status: complete.

Stage 5 centralizes long-running verify and Codex operation state behind `talos.task_orchestrator`.

### Implementation

- Added in-process task lifecycle tracking for verify, cache clear, cancellation, Codex turn, and Codex reconnect operations.
- Runtime core owns task start/finish boundaries and exposes the task snapshot through `/api/state`.
- Codex runtime-blocked, retry, and exception paths record `manual_send_required` replay guards so Talos does not replay a user turn automatically.
- Normal task tracking contains no PowerShell/CMD spawning.

### Validation

- `python -B -m py_compile talos\task_orchestrator.py talos\runtime_core.py talos\state_service.py tests\test_desktop_app.py`: passed.
- `python -B -m unittest -q tests.test_desktop_app`: passed, 154 tests.

Conclusion: task orchestration is centralized and does not leak transient process behavior into the user experience.
