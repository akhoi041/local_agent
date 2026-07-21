# Talos 0.6.0 Evidence

## Baseline

- Source branch: `develop/0.6.0`
- Baseline commit: `ddf0744` (`Complete Talos 0.5.5 architecture slimming`)
- Closed prior release markers:
  - `develop/0.5.5`
  - `release/0.5.5-beta`
  - `v0.5.5-beta`

## Scope

0.6.0 is the architecture foundation release. It should define and validate the long-term contracts before new target products are added.

Stage completion rule:

- A stage is not complete with documentation alone unless the stage is explicitly a release-document task.
- Each architecture stage must record implementation artifacts, validation, and a conclusion.
- Evidence should name the changed modules/config/scripts, the tests or measurable checks run, and the remaining risk.

Required evidence for completion:

- Desktop shell boundary and migration decision recorded with parity checks.
- Core runtime boundary implemented and covered by state/orchestration tests.
- Local API/IPC contract implemented, versioned, and covered by compatibility tests.
- Target-adapter contract implemented and covered by tests.
- Runtime provider contract implemented with credential-safe metadata checks.
- Python responsibilities classified into bridge, fallback, or legacy-removal paths, with at least one boundary cleanup landed.
- Native-helper boundary exposed through code with benchmark/timing gates recorded.
- Existing Arduino workflow passes smoke/regression checks after boundary work.

## Stage 0 - Baseline And Version Open

Status: complete.

Baseline:

- Source branch: `develop/0.6.0`
- Starting commit checked during Stage 0: `d495677`
- Worktree state at Stage 0 validation: clean before the Stage 0 pipeline/evidence update.
- App identity: `Talos 0.6.0 Beta`
- Release notes: `docs/RELEASE_NOTES.md` contains `0.6.0 Beta (In Development)`.
- Source/debug launcher: `desktop_app.py`

Validation:

- `git branch --show-current`
- `git status --short`
- `git rev-parse --short HEAD`
- `python -B -m py_compile desktop_app.py`
- `python -B -c "from talos.core import load_app_identity; i=load_app_identity(); print(i['version'], i['channel'], i['display_name'])"`

Controls:

- No commit, tag, merge, or push was performed during this stage.
- Non-Arduino targets remain blocked until the 0.6.0 architecture boundaries are real.
- 0.6.0 is a rebuild-foundation release, not a target-expansion release.

Conclusion: 0.6.0 is open from a known baseline with the correct version identity, a working source/debug launcher, and an explicit no-silent-push/no-new-target rule.

## Earlier Architecture Draft Notes

The target-adapter and local API notes below came from the earlier 0.6.0 draft order. They remain useful as historical implementation notes, but the active `TALOS_PIPELINE_060.md` now starts with the shell boundary so the rebuild can remove pywebview coupling before widening core/runtime/target contracts.

## Stage 1 - Shell Boundary Scaffold

Status: complete.

Implementation:

- Added `talos/shell/profile.py` for launch profile ownership: app identity, icon lookup, static UI root, webview storage path, window size limits, and port selection.
- Added `talos/shell/pywebview_provider.py` as the active source/debug shell provider, containing pywebview startup, window API behavior, close handling, event watcher lifecycle, and server lifecycle.
- Added `talos/shell/__init__.py` as a clean shell package export without importing the provider, avoiding circular imports between server and shell startup.
- Reduced `desktop_app.py` to a thin debug launcher that delegates shell behavior to `run_pywebview_shell()`.
- Moved static frontend root and port selection out of `talos/server.py` into the shell profile boundary.
- Defined future provider slots for `tauri-rust` and `electron` as explicit future options, without pretending either production shell exists in 0.6.0.

Validation:

- `python -B -m py_compile desktop_app.py talos\server.py talos\shell\__init__.py talos\shell\profile.py talos\shell\pywebview_provider.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 125 tests passed.

Conclusion: Stage 1 is implemented in code. Talos still launches from `desktop_app.py`, while app identity, icon lookup, port selection, frontend hosting, pywebview startup, and window behavior now sit behind a shell provider boundary.

## Stage 2 - Core Runtime Boundary

Status: complete.

Implementation:

- Added `talos/runtime_core.py` as the backend orchestration boundary for state payloads, target state, Arduino context/profile/projects/events, workspace updates, verify/cancel/cache-clear, Codex runtime health/status, context packages, message flow, reconnect/cancel/conversation handling, diagnostics/support/run history, and release evidence.
- Updated `talos/server.py` so product HTTP/local API workflows delegate through `RUNTIME_CORE` instead of directly reaching scattered helper-module state.
- Updated `talos/state_service.py` so state payload construction can receive runtime-owned config, target, verify, and Codex runtime status data.
- Moved task/cancellation-facing operations for Arduino verify and Codex turns behind the runtime core boundary while keeping existing compatibility endpoints stable.
- Kept Python as the implementation bridge for this stage only; the product contract is now the runtime boundary that a later non-Python shell/core can replace.

Validation:

- `python -B -m py_compile talos\runtime_core.py talos\state_service.py talos\server.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 127 tests passed.

Conclusion: Stage 2 is implemented in code. Server endpoints now route core product workflows through `RUNTIME_CORE`, while existing state, Arduino workspace/verify, Codex package/message, and settings behavior remain covered by regression tests.

## Stage 3 - Versioned Local API And IPC Contract

Status: complete.

Implementation:

- Expanded `talos/contracts.py` with explicit contract serializers for workspace maps, source files, verify results, runtime status, settings, command palette, and existing state/target/Codex/diagnostics/evidence surfaces.
- Added `api_version` and compatibility metadata to UI/runtime-facing contract payloads so future Tauri/Rust IPC can distinguish additive changes from breaking ones.
- Routed server/runtime outputs for source file reads/writes, Arduino verify, Codex patch verify, runtime status, settings save, and command palette through contract boundaries.
- Added `/api/command_palette` as a versioned local API surface for shell/menu integrations.
- Preserved current Arduino endpoint paths as compatibility wrappers instead of forcing frontend churn during the architecture rebuild.

Versioning rules:

- Additive fields may remain on `talos.local-api.v1`.
- Removing, renaming, or changing the meaning of UI/runtime-facing fields requires a new local API version.
- Raw helper dictionaries should not cross the local API/IPC boundary without a serializer in `talos/contracts.py`.

Validation:

- `python -B -m py_compile talos\contracts.py talos\runtime_core.py talos\server.py tests\test_desktop_app.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 129 tests passed.

Conclusion: Stage 3 is implemented in code. Talos now has explicit local API contracts for the current frontend/runtime boundary while retaining Arduino compatibility endpoints for the active UI.

## Stage 4 - Target Host Skeleton

Status: complete.

Implementation:

- Expanded `talos/targets.py` from basic target metadata into a shared target host skeleton with target actions, implemented/placeholder status, and registry blocking for unsupported adapters.
- Expanded `talos/arduino_adapter.py` so Arduino is the first concrete compatibility target with workspace identity, source artifact identity, profile identity, context package, verify, write, rollback, and diagnostics hooks.
- Preserved Arduino-specific endpoints while keeping `/api/targets` as the generic target metadata surface for future MATLAB, STM32CubeIDE, KiCad, and SolidWorks adapters.
- Added regression coverage for Arduino generic target representation and for blocking unimplemented target stubs from claiming support.

Validation:

- `python -B -m py_compile talos\targets.py talos\arduino_adapter.py talos\runtime_core.py talos\server.py tests\test_desktop_app.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 130 tests passed.

Conclusion: Stage 4 is implemented in code. Arduino now runs as the first real adapter on a shared target host, and future target apps have a concrete integration shape without being allowed to report support prematurely.

## Previous Draft - Target Adapter Foundation

Status: complete.

Implementation:

- Added `talos/targets.py` with generic target workspace, source file, profile, context, adapter, and registry types.
- Added `talos/arduino_adapter.py` so Arduino IDE is now the first concrete target adapter instead of the permanent hard-coded app model.
- Updated `talos/server.py` to register the Arduino adapter and expose `GET /api/targets`.
- Updated `talos/state_service.py` so `/api/state` includes generic target metadata/context and lists `GET /api/targets`.
- Preserved the existing Arduino endpoints for backward compatibility while routing shared behavior through the adapter boundary.

Validation:

- `python -B -m py_compile talos\targets.py talos\arduino_adapter.py talos\server.py talos\state_service.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 121 tests passed.

Conclusion: Stage 1 is implemented in code, not only documented. Future targets can now begin from the `TargetAdapter` boundary instead of copying Arduino-specific server logic.

## Previous Draft - Local API And IPC Contract

Status: complete.

Implementation:

- Added `talos/contracts.py` with `talos.local-api.v1` metadata helpers and named contracts for state, targets, target context, Codex context packages, verify results, diagnostics, and evidence payloads.
- Added `require_contract()` compatibility guards so tests and future bridge code can reject missing, mismatched, or unsupported local API contracts.
- Routed `/api/state`, `/api/targets`, `/api/arduino_context`, `/api/codex_context_package`, `/api/arduino_verify`, `/api/diagnostics_export`, and `/api/release_evidence` through contract serializers.
- Updated `ArduinoTargetAdapter.context()` to accept precomputed summary/profile/readiness/workspace-map snapshots, preventing internal helper calls from leaking or repeating at the public API boundary.
- Preserved existing Arduino payload fields while adding top-level contract metadata for forward-compatible UI/runtime consumption.

Versioning rules:

- Additive fields may remain on `talos.local-api.v1`.
- Removing or renaming UI/runtime-facing fields requires a new local API version.
- Internal helper dictionaries must cross HTTP/local IPC through a serializer in `talos/contracts.py`.

Validation:

- `python -B -m py_compile talos\contracts.py talos\targets.py talos\arduino_adapter.py talos\state_service.py talos\server.py tests\test_desktop_app.py`
- `python -B -m unittest tests.test_desktop_app`
- `python -B scripts\architecture_health.py --json --iterations 1`
- Result: 123 tests passed; architecture health passed with no failures.
- Timing note: `state_refresh` averaged `1069.872 ms`, under the `2000 ms` guardrail, after reusing one Arduino process/window snapshot for contract serialization.

Conclusion: Stage 2 now has a real versioned local contract layer. The frontend and future runtime/target adapters can consume stable payloads without depending on raw Python helper shapes.

## Stage 5 - Runtime Provider Boundary

Status: complete.

Implementation:

- Added `talos/runtime_provider.py` as the runtime-provider boundary with a Codex provider, provider registry, placeholder runtime providers, and safe runtime metadata sanitization.
- Routed Codex state, runtime discovery/health, pinning, app-server status, message sending, reconnect/cancel/conversation handling, review restore/discard, support evidence, and shutdown through `TalosRuntimeCore.codex_provider`.
- Kept Codex message/review result payloads intact for user-visible chat and patch data, while runtime metadata display is allowlisted.
- Marked VS Code extension-adjacent runtime discovery as `extension_adjacent_candidate_only`, a fallback candidate policy rather than the product foundation.

Validation:

- `python -B -m py_compile talos\runtime_provider.py talos\runtime_core.py tests\test_desktop_app.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 133 tests passed.

Safety conclusion:

- `talos/runtime_provider.py` drops token, cookie, session, password, authorization, API key, bearer, refresh, and secret metadata keys.
- Provider metadata explicitly reports that Talos stores no runtime credentials, tokens, or cookies.
- `talos/runtime_core.py` no longer imports or calls `CODEX_BRIDGE` directly; Codex actions are routed through `CodexRuntimeProvider`.

Conclusion: Stage 5 is implemented in code. Runtime behavior is provider-owned, Codex is the first real provider, future providers are placeholders, metadata display is credential-safe, and VS Code extension-adjacent runtime paths are treated only as fallback candidates.

## Stage 6 - Python Compatibility Bridge

Status: complete.

Implementation:

- Added `talos/python_ownership.py` with a code-owned Python module ownership map covering launcher, shell provider, core implementation, target adapter, runtime provider, diagnostics, native fallback, storage, API bridge, and migration-candidate modules.
- Marked 0.6.5 migration hot paths explicitly: process/window discovery, file watching, hashing/cache keys, diff/hunk parsing, task orchestration, and heavy workspace scans.
- Added `boundary_check()` to freeze the current `talos.server` compatibility import baseline, so new direct server access to internal helpers is caught by tests before Python reduction work begins.
- Declared no stale Python path safe to remove in Stage 6 without changing current runtime behavior. Future stale paths must be marked with `role="stale"` and will fail the boundary check until archived or removed.
- Preserved fallback policy: Python remains available as bridge/fallback while native/core boundaries are introduced, and missing native helper support remains non-fatal.

Validation:

- `python -B -m py_compile talos\python_ownership.py tests\test_desktop_app.py`
- `python -B -m unittest -q tests.test_desktop_app`
- Result: 135 tests passed.

Conclusion: Stage 6 is implemented in code. Python now has explicit ownership, hot-path migration targets, and a boundary check, so 0.6.5 can reduce Python without guessing or breaking fallback behavior.

## Stage 7 - Native Helper Boundary

Status: complete.

Implementation:

- Added `talos/native_boundary.py` as the single reporting and measurement boundary for native acceleration.
- Kept `talos/native_bridge.py` as the raw platform bridge and fallback layer; product state now consumes native status through the boundary.
- Exposed native capability status for library presence, window titles, window rows, process rows, and `.ino` extraction.
- Exposed operation reports for detection, scan, hash, diff, and verify-preparation candidates with `native_backed`, `fallback_backed`, selected backend, and last timing.
- Added migration gates for hashing/cache keys, diff/hunk parsing, verify preparation, and heavy workspace scans that are not ready to move yet.
- Added `talos.native_boundary` to the Python ownership map as the native adapter boundary.

Validation:

- `python -B -m py_compile talos\native_boundary.py talos\state_service.py talos\python_ownership.py tests\test_desktop_app.py`
- `python -B -m unittest -q tests.test_desktop_app`
- Result: 138 tests passed.

Conclusion: Stage 7 is implemented in code. Native acceleration now has a single product-facing boundary with measurable fallback behavior, and missing native helper support remains non-fatal.

## Stage 8 - Arduino Compatibility Smoke

Status: complete.

Implementation:

- Added `talos/arduino_smoke.py` as a real smoke path over the rebuilt boundaries.
- The smoke creates a synthetic Arduino sketch with `Stage8Smoke.ino`, `Driver.h`, and `Driver.cpp`.
- It exercises Arduino project detection, workspace/source inspection, selected board/profile verify payload, context package coverage, Codex patch staging, apply-to-editor, save-to-workspace, and reject safety.
- Codex staging is redirected to a temporary smoke folder during validation so AppData, user settings, and real sketches are not modified.

Validation:

- `python -B -m py_compile talos\arduino_smoke.py tests\test_desktop_app.py`
- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_060_arduino_compatibility_smoke_exercises_product_flow`
- `python -B -m unittest -q tests.test_desktop_app`
- Result: 139 tests passed.

Conclusion: Stage 8 is implemented in code. Arduino remains usable through the new shell, core, contract, target, runtime, Python-bridge, and native-boundary structure, with apply/reject/save behavior covered by an automated compatibility smoke.

## Stage 9 - 0.6.5 Handoff

Status: complete.

Completed 0.6.0 boundaries:

- Shell provider boundary for desktop launch/window behavior.
- Core runtime boundary for state and orchestration ownership.
- Versioned local API contract for UI/runtime-facing payloads.
- Target host boundary with Arduino as the first real adapter.
- Runtime provider boundary for Codex-compatible provider behavior and credential-safe metadata.
- Python ownership map that marks bridge/fallback/migration code explicitly.
- Native helper boundary with measurable fallback behavior.
- Arduino compatibility smoke over detection, source inspection, context packaging, apply/reject/save, and verify payload behavior.

Remaining Python migration candidates for 0.6.5:

- Process/window detection.
- File watching and workspace scanning.
- Hashing and cache-key generation.
- Diff and hunk parsing.
- Verify preparation.
- Task orchestration and cancellation state.
- Runtime discovery health and repeated subprocess/window churn.

0.6.5 pipeline check:

- `dev_notes/pipelines/TALOS_PIPELINE_065.md` matches the actual 0.6.0 result.
- It starts with baseline measurement before implementation changes.
- It keeps `desktop_app.py` as the source/debug launcher.
- It preserves the no-new-target rule.
- It frames Python decomposition as behavior-preserving optimization, not feature expansion.

Validation:

- `python -B -m unittest -q tests.test_desktop_app`
- Result: 139 tests passed.

Conclusion: Stage 9 is complete. 0.6.5 can start reducing Python hot paths without changing product behavior.
