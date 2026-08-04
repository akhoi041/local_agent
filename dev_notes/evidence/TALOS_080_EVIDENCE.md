# Talos 0.8.0 Evidence

Status: Stage 1 complete.

Purpose: track proof that 0.8.0 actually moves Talos toward the professional shell/core/API/runtime/native/adapter structure and reduces Python to compatibility/debug glue.

Initial toolchain check before installation:

- `rustc`: missing from PATH.
- `cargo`: missing from PATH.
- `node`: missing from PATH.
- `npm`: missing from PATH.

Install note: large toolchains must not be downloaded silently. Rust/Cargo, Node/NPM, and Tauri CLI were installed only after explicit approval.

## Stage 0 - Toolchain And Baseline Gate

Date: 2026-07-31.

### Branch And Version

- Branch: `develop/0.8.0`, tracking `origin/develop/0.8.0`.
- App identity: `config/app_identity.json` updated to `0.8.0`.
- Channel: `Beta`.

### Toolchain Status

- Rustup/Rust installed:
  - `rustc 1.97.1 (8bab26f4f 2026-07-14)`
  - `cargo 1.97.1 (c980f4866 2026-06-30)`
  - Detected at `%USERPROFILE%\.cargo\bin`.
- Node.js LTS installed:
  - `node v24.18.0`
  - `npm 11.16.0`
  - Detected at `C:\Program Files\nodejs`.
- Tauri CLI installed:
  - `tauri-cli 2.11.4`
  - Detected at `%APPDATA%\npm\tauri.cmd`.
- Current PowerShell session still needs PATH refresh for bare `rustc`, `cargo`, `node`, `npm`, and `tauri` commands. Verified successfully by temporarily prepending `%USERPROFILE%\.cargo\bin`, `C:\Program Files\nodejs`, and `%APPDATA%\npm`.
- PowerShell execution policy blocks `.ps1` launchers, so Stage 0 verification used `npm.cmd` and `tauri.cmd`; no policy change was required.

### Python Ownership Baseline

Current ownership map carried forward from 0.6.5, 0.7.0, and 0.7.5 evidence:

- `desktop_app.py`: source/debug launcher only.
- `talos.server`: compatibility local API bridge; must become thin request routing.
- `talos.arduino` and `talos.arduino_adapter`: temporary Arduino adapter shim and reference target behavior.
- `talos.codex_bridge`, `talos.codex_runtime`, `talos.runtime_discovery`: runtime bridge/provider compatibility layer; credentials remain outside Talos.
- `talos.runtime_core`, `talos.state_service`, `talos.task_orchestrator`: current Python orchestration ownership to migrate behind the new core boundary.
- `talos.workspace_scanner`, `talos.cache_keys`, `talos.diff_hunks`, `talos.diagnostics`, `talos.run_history`, `talos.checkpoints`: current logic/helper ownership to evaluate for core/native extraction.
- `talos.native_bridge`, `talos.native_boundary`, `native/talos_native.c`: native helper boundary already present, still limited.
- `tests/`: Python test harness remains acceptable during migration.

Migration rule: new product behavior must land in shell/core/API/runtime/native/adapter boundaries, not as expanded Python ownership.

### Arduino Smoke Baseline

- Command: `python -B -c "from talos.arduino_smoke import run_arduino_compatibility_smoke; ..."`
- Result: passed.
- Main sketch: `Stage8Smoke.ino`.
- Source tabs: synthetic smoke workspace generated successfully.
- Checks passed: detect open sketches, inspect source tabs, verify profile, context package, apply/save safe path, reject safe path.

### Compile Baseline

- Command: `python -B -m py_compile desktop_app.py talos\arduino_smoke.py talos\server.py`
- Result: passed.

Conclusion: Stage 0 exit condition is met. 0.8.0 starts from a known branch/version, installed Rust/Node/Tauri shell toolchain, explicit Python ownership debt, and a working Arduino baseline.

## Stage 1 - Rust Core Primitive Migration And Python Bridge Reduction

Date: 2026-07-31.

### Implemented Boundary

- Added `core/talos_core`, a Rust crate that owns Stage 1 cache identity/source scan primitives and the Python ownership manifest.
- Added `talos_core_audit`, a local audit command for summary, manifest, hashing, workspace hashing, and source scanning output.
- Added `talos/core_bridge.py`, a thin Python bridge that invokes the built Cargo binary or `cargo run` when the binary is not present or is older than Rust source files.
- Routed `talos/cache_keys.py` through the Rust bridge for stable text hashing, file hashing, workspace identity hashing, source-file scanning, and source metadata collection.
- Kept Python fallback behavior only for source/debug execution or missing Rust core.
- Reported `hash.cache_keys` in `talos/native_boundary.py` as the Rust `core_hashing` capability, including boundary metadata for UI/API audit output.
- Added `scripts/check_core_boundary.ps1` to run the Rust boundary tests and audit in one focused step.
- Removed the obsolete `talos/python_ownership.py` mirror after Rust became the source of truth for Python ownership classification.
- Added `target/` and `core/**/target/` ignores so Rust build artifacts do not enter source control.

### Ownership Audit

`talos-core-audit summary`:

- Python modules classified: 34.
- Bridge/debug/temporary surfaces: 17.
- Logic owners still to migrate: 17.
- Hot paths still to migrate: 17.
- Stage 1 gate: `stage1_exit_ready=true`.

Remaining Python ownership is explicit migration debt:

- Shell/debug: `desktop_app.py`, `talos/shell/*`.
- API bridge: `talos/server.py`, `talos/client.py`, `talos/contracts.py`.
- Core compatibility bridge: `talos/core_bridge.py`, `talos/cache_keys.py`.
- Core candidates still to migrate: `talos/core.py`, `talos/runtime_core.py`, `talos/state_service.py`, `talos/task_orchestrator.py`, `talos/diff_hunks.py`, `talos/event_bus.py`.
- Native/helper candidates: `talos/arduino_events.py`, `talos/workspace_scanner.py`, `talos/detection.py`, `talos/native_bridge.py`, `talos/native_boundary.py`.
- Runtime host candidates: `talos/codex_bridge.py`, `talos/codex_runtime.py`, `talos/runtime_discovery.py`, `talos/runtime_provider.py`, `talos/runtime_service.py`.
- Target adapter candidates: `talos/arduino.py`, `talos/arduino_adapter.py`, `talos/targets.py`.
- Storage/diagnostics candidates: `talos/checkpoints.py`, `talos/run_history.py`, `talos/diagnostics.py`, `talos/performance.py`.

### Migrated Rust-Owned Primitives

- `stable_text_hash`: Rust SHA-256 short-hash primitive for deterministic cache keys.
- `stable_file_hash`: Rust file hash primitive used by source metadata.
- `workspace_identity_hash_core`: Rust workspace/profile/source identity hash used by `talos/cache_keys.py`.
- `scan_source_files`: Rust source scanner with project-noise filtering for `.git`, `.vscode`, `.vs`, `__pycache__`, `.cache`, `.pio`, `build`, `dist`, and `node_modules`.
- `source_file_metadata`: Rust source metadata with line-count parity against the former Python scanner.

### Checks

- Rust command: `cargo fmt --manifest-path core\talos_core\Cargo.toml`: passed.
- Rust command: `cargo build --manifest-path core\talos_core\Cargo.toml`: passed.
- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml`: 7 passed.
- Rust command: `cargo run --manifest-path core\talos_core\Cargo.toml --quiet -- summary`: passed with counts above.
- `python -B -m py_compile desktop_app.py talos\server.py talos\core_bridge.py`: passed.
- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_core_bridge_workspace_hash_matches_cache_bridge tests.test_desktop_app.TalosArduinoTests.test_stage_080_core_bridge_scans_source_files_with_filters tests.test_desktop_app.TalosArduinoTests.test_stage_080_native_boundary_reports_core_hashing`: 3 passed.
- Focused stale-binary/parity regression: `test_stage_060_python_ownership_marks_hot_paths_and_fallbacks`, `test_stage_065_baseline_records_measurements_before_python_reduction`, and `test_stage_065_workspace_scanner_cache_invalidates_on_file_change`: 3 passed after ownership moved to the Rust manifest.
- Full regression: `python -B -m unittest -q tests.test_desktop_app`: 186 passed.
- `git diff --check`: passed with existing CRLF warnings only.

Conclusion: Stage 1 exit condition is met. Python has not been fully removed yet, but it no longer owns cache identity/source scanning in production paths. The first real non-Python core boundary exists, is exercised from Python through a thin bridge, keeps fallback parity, classifies remaining Python modules, blocks Python logic expansion by role, and gives later 0.8.0 stages concrete migration targets.

### Python Purge Correction

- Removed `talos/python_ownership.py`; the Rust `PYTHON_MODULES` manifest is now the ownership source.
- Removed `talos/stage_baseline.py`; 0.6.5 baseline data is retained in `dev_notes/evidence/TALOS_065_EVIDENCE.md` instead of runtime Python.
- Updated Python tests to read the Rust manifest through `talos/core_bridge.py`.
- Remaining Python modules are active launch, bridge, compatibility shim, diagnostics, or adapter surfaces scheduled for later migration rather than Stage 1 product logic.

## Stage 2 - Desktop Shell Boundary Implementation

Date: 2026-08-01.

### Implemented Boundary

- Added `shell/talos_shell`, a Rust/Cargo shell contract skeleton for the future product shell.
- Defined shell lifecycle ownership for window lifecycle, tray, app identity, native frame policy, installer hooks, update hooks, and web workbench hosting.
- Kept `desktop_app.py` as the source/debug launcher and explicitly prevented Python from being treated as the product shell owner.
- Added `dev_notes/architecture/TALOS_SHELL_BOUNDARY.md` with the allowed Python surface and deletion plan for obsolete PyWebView lifecycle helpers.

### Checks

- Rust command: `cargo fmt --manifest-path shell\talos_shell\Cargo.toml`: passed.
- Rust command: `cargo test --manifest-path shell\talos_shell\Cargo.toml`: 3 passed.
- Rust command: `cargo run --manifest-path shell\talos_shell\Cargo.toml --quiet`: passed and printed the shell ownership manifest.
- `git diff --check -- shell\talos_shell dev_notes\architecture\TALOS_SHELL_BOUNDARY.md dev_notes\pipelines\TALOS_PIPELINE_080.md`: passed with the existing CRLF warning only.

Conclusion: Stage 2 exit condition is met for the focused boundary step. Talos now has a real non-Python shell path skeleton and a validated shell contract. The Python WebView launcher remains available for debug/source use while later stages replace runtime hosting and lifecycle behavior behind the Rust/Cargo shell boundary.

## Stage 3 - Local API And IPC Contract Freeze

Date: 2026-08-01.

### Implemented Boundary

- Added Rust-owned local API contract definitions in `core/talos_core/src/contracts.rs`.
- Added `talos-core-audit api-contracts` so compatibility bridges can read the Rust manifest without making Python the schema owner.
- Marked `talos/contracts.py` as a compatibility shim and exposed Rust contract source status.
- Documented breaking-change rules in `dev_notes/architecture/TALOS_API_CONTRACTS.md`.

### Checks

- Rust contract tests cover required Stage 3 payloads, metadata fields, and manifest output.
- Python compatibility test confirms `talos.core_bridge.core_api_contract_manifest()` exposes the Rust-owned payload manifest.

Conclusion: Stage 3 exit condition is met for the focused API boundary. The stable local API surfaces are versioned in Rust/Cargo, while Python remains a temporary serializer/bridge for existing HTTP handlers.

## Stage 4 - Core Backend Ownership Reduction

Date: 2026-08-01.

### Implemented Boundary

- Added Rust-owned backend service registry in `core/talos_core/src/backend.rs`.
- Added `talos-core-audit backend-services` and Stage 4 readiness metadata.
- Exposed backend service metadata to Python through `talos/core_bridge.py` as a bridge-only read path.
- Recorded workspace state, task queue, policy/permissions, diagnostics, adapter orchestration, cancellation, cache invalidation, and support evidence as Rust-owned backend services.

### Checks

- Rust command: `cargo fmt --manifest-path core\talos_core\Cargo.toml`: passed.
- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`: 13 passed.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_backend_services_are_rust_owned`: passed.

Conclusion: Stage 4 exit condition is met for the focused backend ownership step. Python still hosts compatibility HTTP handlers for the current desktop/debug path, but backend ownership is declared and audited from Rust/Cargo, and Python consumes it as bridge metadata rather than acting as the backend service owner.

## Stage 5 - Native Helper Expansion

Date: 2026-08-03.

### Implemented Boundary

- Added Rust-owned native/helper registry in `core/talos_core/src/native_helpers.rs`.
- Added `talos-core-audit native-helpers` so compatibility bridges can inspect helper ownership without making Python the source of truth.
- Exposed native/helper metadata through `talos/core_bridge.py` as a bridge-only read path.
- Recorded process/window detection, file watching, hashing, workspace scanning, diff/hunk preparation, filesystem operations, performance telemetry, and fallback compatibility as Rust-owned helper boundaries.
- Quarantined existing Python scanners/watchers as fallback-only migration debt; new production ownership belongs to Rust/Cargo.

### Checks

- Rust command: `cargo fmt --manifest-path core\talos_core\Cargo.toml`: passed.
- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`: 16 passed.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_native_helpers_are_rust_owned`: passed.
- Git whitespace check: `git diff --check`: no whitespace errors; existing CRLF warnings only.

Conclusion: Stage 5 exit condition is met for the focused native helper step. Python remains allowed only as a bridge/fallback surface for these helper domains until native parity permits safe deletion.

## Stage 6 - Runtime Provider Boundary Hardening

Date: 2026-08-03.

### Implemented Boundary

- Added Rust-owned runtime provider registry in `core/talos_core/src/runtime_providers.rs`.
- Added `talos-core-audit runtime-providers` so provider behavior is declared by Rust/Cargo, not Python or VS Code UI assumptions.
- Defined Codex as the current provider and Claude as a future-compatible provider contract.
- Kept credentials outside Talos and kept manual context package as the safe fallback.
- Exposed provider metadata through `talos/core_bridge.py` as a bridge-only read path.
- Marked Python runtime surfaces as subprocess/HTTP compatibility bridges until the provider host can call runtime tools directly.

### Checks

- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`: 19 passed.
- Rust command: `cargo run --manifest-path core\talos_core\Cargo.toml --quiet -- runtime-providers`: passed and printed Codex/Claude provider manifests.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_runtime_providers_are_rust_owned`: passed.

Conclusion: Stage 6 exit condition is met for the focused runtime-provider boundary step. Runtime behavior is provider-owned and explicit in Rust/Cargo; Python remains a bridge/fallback surface, credentials stay outside Talos, and the design is no longer tied to VS Code UI behavior.

## Stage 7 - Target Adapter Host Contract

Date: 2026-08-03.

### Implemented Boundary

- Added Rust-owned target adapter host contract in `core/talos_core/src/target_adapters.rs`.
- Added `talos-core-audit target-adapters` so compatibility bridges can inspect adapter lifecycle, permissions, scope policy, and replacement targets without making Python the source of truth.
- Kept Arduino as the reference adapter contract.
- Added a future-target template contract for MATLAB, STM32CubeIDE, KiCad, and SolidWorks without implementing those targets.
- Marked Python Arduino modules as compatibility shims until Stage 8 proves parity through the adapter host.

### Checks

- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`.
- Rust command: `cargo run --manifest-path core\talos_core\Cargo.toml --quiet -- target-adapters`.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_target_adapters_are_rust_owned`.

Conclusion: Stage 7 exit condition is met for the focused adapter-host step. Future target adapters now have a stable Rust/Cargo contract to start from, while existing Python Arduino code is explicitly temporary compatibility debt for Stage 8 parity validation.

## Stage 8 - Arduino Parity Through Core Complete Boundary

Date: 2026-08-03.

### Implemented Boundary

- Added Rust-owned Arduino parity ledger in `core/talos_core/src/arduino_parity.rs`.
- Added `talos-core-audit arduino-parity` as the focused parity gate for the reference Arduino target.
- Exposed the parity report through `talos/core_bridge.py` as bridge-only metadata.
- Covered detection, workspace mapping, source file list, board/profile, verify, context package, Codex review, save, and rollback.
- Compared the active Arduino behavior surface against the 0.7.5 reference evidence and recorded no regressions.
- Quarantined remaining Arduino Python files by allowed category:
  - `talos/arduino.py`: temporary adapter shim.
  - `talos/arduino_adapter.py`: temporary adapter shim.
  - `talos/arduino_events.py`: native watcher bridge.
  - `talos/arduino_smoke.py`: test harness.

### Checks

- Rust command: `cargo fmt --manifest-path core\talos_core\Cargo.toml`.
- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`.
- Rust command: `cargo run --manifest-path core\talos_core\Cargo.toml --quiet -- arduino-parity`.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_arduino_parity_is_core_owned`.

Conclusion: Stage 8 exit condition is met for the focused Arduino parity step. Arduino remains the reference usable target while the ownership boundary is now Rust/Cargo-audited; remaining Python is explicitly named compatibility, bridge, or test surface rather than product logic.

## Stage 9 - Release Evidence And 0.9.0 Handoff

Date: 2026-08-04.

### Implemented Boundary

- Added Rust-owned release handoff report through `talos-core-audit release-handoff`.
- Exposed handoff metadata through `core_release_handoff()` as bridge-only test access.
- Created `dev_notes/pipelines/TALOS_PIPELINE_090.md` from the measured 0.8.0 state.
- Listed 0.9.x gates for runtime independence, consent, diagnostics, recovery, installer/update trust, Python purge closure, and next-target readiness.
- Attached the final Python purge ledger from Rust-owned `PYTHON_MODULES`; every normal-execution Python item has a retained reason, replacement owner, and target removal version.
- Confirmed Rust/Cargo is the product-logic owner for shell/core/API/runtime/native/adapter boundaries while Python remains launcher/debug/compatibility glue.

### Checks

- Rust command: `cargo fmt --manifest-path core\talos_core\Cargo.toml`.
- Rust command: `cargo test --manifest-path core\talos_core\Cargo.toml --quiet`.
- Python command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_080_release_handoff_is_core_owned`.
- Git whitespace check: `git diff --check`.

Conclusion: Stage 9 exit condition is met for the focused 0.8.0 release handoff. 0.9.0 can begin from a Rust-owned architecture ledger instead of another planning-only reset.
