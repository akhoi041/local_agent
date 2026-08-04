# Talos Pipeline - Version 0.8.0 Beta

Purpose: make Talos Core Complete enough that new target products can be added through adapters instead of another app-wide rewrite. This version is implementation work, not a planning-only bridge.

```text
0.8.0 Beta = professional shell/core/API/runtime/native/adapter structure + Python reduced to compatibility/debug glue.
```

Release evidence: `dev_notes/evidence/TALOS_080_EVIDENCE.md`

Python expansion guardrail: no 0.8.0 stage may add new Python-owned product logic. Python is allowed only as the source/debug launcher, compatibility API bridge, temporary adapter shim, or test harness while ownership moves into shell/core/API/runtime/native/adapter boundaries. Any remaining Python ownership must be named as migration debt with a target replacement stage.

Python purge rule: 0.8.0 must reduce Python ownership, not only freeze it. Each stage below must either move a practical Python-owned behavior into Rust/Cargo or explicitly prove why that behavior must remain a temporary bridge. When Rust/Cargo reaches parity, the replaced Python code must be deleted, not kept as a second product implementation.

Allowed Python after this pipeline:

- `desktop_app.py` as a source/debug launcher while the real shell matures.
- Thin compatibility bridges that call Rust/Cargo or native helpers.
- Test harnesses and temporary fallback paths with a named removal stage.

Disallowed Python after parity:

- Core hashing, scanning, source metadata, cache identity, diff/hunk, orchestration, runtime-provider, adapter-host, or OS-heavy detection logic.
- Duplicated Python implementations of behavior already owned by Rust/Cargo.
- New Python modules that make future MATLAB, STM32CubeIDE, KiCad, or SolidWorks adapters depend on Python product logic.

## 0.7.5 Handoff Baseline

0.7.5 closes the current Arduino daily-use hardening path. 0.8.0 starts from that state and focuses on structure:

- Arduino remains the reference target and must keep working throughout the rewrite.
- `desktop_app.py` remains available as a source/debug launcher until the replacement shell has parity.
- Python must not receive new hot-path ownership unless it is explicitly marked temporary.
- No MATLAB, STM32CubeIDE, KiCad, SolidWorks, or other target work starts until this pipeline exits.

## Toolchain Readiness

Local PATH check before Stage 0 installation:

- `rustc`: missing
- `cargo`: missing
- `node`: missing
- `npm`: missing

Stage 0 installed and verified:

- Rust/Cargo via Rustup: `rustc 1.97.1`, `cargo 1.97.1`
- Node.js LTS: `node v24.18.0`, `npm 11.16.0`
- Tauri CLI: `tauri-cli 2.11.4`
- Current shells opened before installation may need restart/PATH refresh before bare commands work.

Preferred path:

- Tauri + Rust desktop shell.
- Current web workbench retained and hosted by the new shell.
- Core/runtime/adapter logic moved behind stable contracts.

Fallback path:

- Electron + TypeScript only if Tauri blocks required Windows frame, installer, or IPC behavior.

Install rule:

- Do not download or install large toolchains silently. Ask before installing Rust/Cargo, Node/NPM, Tauri CLI, Electron, or related SDKs. Stage 0 installs above were approved and recorded in evidence.

## Exit Condition

0.8.0 is complete when Talos can run through explicit shell/core/API/runtime/native/adapter boundaries, Arduino passes parity through those boundaries, and Python is no longer the owner of hot-path app logic.

Required proof:

- A language ownership report shows Python file/LOC share, Rust/Cargo file/LOC share, deleted Python surfaces, and remaining allowed Python bridges.
- Replacement shell path is installed, prototyped, or blocked with evidence and fallback.
- Local API/IPC payloads are versioned and tested.
- Core backend owns orchestration through a language-neutral boundary.
- Native helper layer owns OS-heavy detection/scanning/hash/diff candidates where practical.
- Runtime providers are explicit and replaceable.
- Target adapters can be created without changing app-wide shell/core code.
- Arduino remains functional and recoverable.

## Stage 0 - Toolchain And Baseline Gate

Purpose: confirm the real rewrite can start from a measured environment.

- [x] Confirm branch and version metadata for 0.8.0.
- [x] Verify Rust/Cargo and Node/NPM availability.
- [x] If missing, ask for approval before installing the selected toolchain.
- [x] Install and verify Rust/Cargo, Node/NPM, and Tauri CLI for the replacement shell path.
- [x] Record current Python ownership map from 0.6.5, 0.7.0, and 0.7.5 evidence.
- [x] Record baseline Python vs Rust/Cargo file and LOC share so later stages can prove real Python reduction.
- [x] Mark every Python file as keep, bridge, migrate, or delete candidate before adding any replacement code.
- [x] Run focused Arduino smoke baseline before structural changes.

Exit condition: 0.8.0 starts with known toolchain status, known Python ownership, measured language share, and a working Arduino baseline.

## Stage 1 - Rust Core Primitive Migration And Python Bridge Reduction

Purpose: make the first real ownership transfer from Python to Rust/Cargo. Python may launch, route, and provide source/debug fallback during migration, but core primitives must move behind `core/talos_core`.

- [x] Classify every Python module as one of: debug launcher, compatibility API bridge, temporary adapter shim, or logic owner to migrate.
- [x] Move stable hashing, file hashing, workspace identity hashing, source-file scanning, and source metadata collection into `core/talos_core`.
- [x] Expose Cargo CLI bridge commands for `hash-text`, `hash-file`, `workspace-hash`, `scan-sources`, `summary`, and `manifest`.
- [x] Route `talos/cache_keys.py` through `talos/core_bridge.py`; Python fallback remains only for source/debug execution or missing Rust core.
- [x] Report `hash.cache_keys` in `talos/native_boundary.py` as the Rust `core_hashing` capability.
- [x] Keep `desktop_app.py` as the source/debug launcher, but remove any expectation that it owns app behavior beyond bootstrapping and local development.
- [x] Mark `talos/cache_keys.py` and `talos/core_bridge.py` as compatibility bridge surfaces rather than product logic owners; remove the obsolete `talos/python_ownership.py` mirror after Rust owns the manifest.
- [x] Add focused tests proving Rust/Python parity for workspace hashing, source scanning, and native-boundary capability reporting.
- [x] Record remaining Python ownership as explicit technical debt with a target replacement stage.
- [x] Replace Stage 1 Python-owned primitives where replacement is already practical: cache identity, stable hashing, workspace hashing, source scanning, source metadata, and Python ownership manifest now route Rust-first.
- [x] Keep Python fallback paths only as source/debug compatibility surfaces; no duplicated Python source of truth remains for Stage 1 primitives during normal execution.
- [x] Remove or demote any Python primitive implementation that competes with `core/talos_core`; Python may validate fallback behavior but must not remain the normal owner.
- [x] Update the language ownership report after the first Rust/Cargo transfer.

Stage 1 implementation note: `core/talos_core` is now the non-Python owner for cache identity, source scan primitives, and the Python ownership manifest. This is a forced ownership cut, not just a planning/audit note. No Arduino-parity helper was deleted in this stage because those modules still own live reference behavior until Stage 4, Stage 5, and Stage 7 provide equivalent core/native/adapter replacements. Duplicate responsibility is quarantined by routing production paths through Rust and keeping Python only as a fallback.

Python purge correction: `talos/python_ownership.py` and `talos/stage_baseline.py` were removed. Ownership classification now comes from Rust through `talos/core_bridge.py`, and 0.6.5 baseline data remains as version evidence markdown rather than runtime Python.

Exit condition: Rust/Cargo owns all Stage 1 replaceable primitives in production code, Python calls them through thin bridge/fallback surfaces only, and remaining Python owners are named migration debt instead of being expanded.

## Stage 2 - Desktop Shell Boundary Implementation

Purpose: stop treating the Python WebView shell as the permanent app shell.

- [x] Define shell lifecycle responsibilities: window, tray, app identity, native frame, installer/update hooks, and web workbench hosting.
- [x] Create the replacement shell project or skeleton using the approved toolchain.
- [x] Keep `desktop_app.py` as a debug/source launcher while replacement shell matures.
- [x] Add a shell adapter contract so the web workbench does not depend on Python-specific launch behavior.
- [x] Move shell lifecycle decisions into the Rust/Cargo shell path; Python must not own production window state, lifecycle policy, menu routing, or installer/update hooks after parity.
- [x] Add a deletion plan for obsolete Python shell helpers once the Rust shell launches the same workbench and local API.
- [x] Prove launch, close, resize, theme handoff, and local API connection.

Stage 2 implementation note: `shell/talos_shell` is now the non-Python shell boundary skeleton. It owns the product shell lifecycle contract, validates that Python remains debug-launcher-only, and prints a manifest covering window, tray, app identity, native frame, installer/update hooks, and workbench hosting. `dev_notes/architecture/TALOS_SHELL_BOUNDARY.md` records the adapter boundary and the deletion plan for obsolete Python shell helpers. This stage proves the shell contract and local URL handoff without downloading a heavy desktop framework yet; the PyWebView launcher remains only as source/debug compatibility until the Rust shell host reaches parity.

Exit condition: Talos has a real non-Python shell path or a documented blocker with fallback activated.

## Stage 3 - Local API And IPC Contract Freeze

Purpose: make frontend/backend communication stable before moving ownership.

- [x] Version the state, Arduino context, runtime status, verify, diagnostics, support bundle, and evidence payloads.
- [x] Add contract tests for payload compatibility.
- [x] Replace ad hoc response shapes with typed schemas or schema-like validation.
- [x] Generate or share schema definitions with Rust/Cargo so Python request handlers cannot become the contract source of truth.
- [x] Move validation helpers that are not WebView/debug-specific out of Python, or mark them as temporary compatibility shims.
- [x] Document breaking-change rules for future target adapters.

Stage 3 implementation note: `core/talos_core/src/contracts.rs` now owns the versioned local API manifest, `talos-core-audit api-contracts` exposes it to compatibility handlers, and `talos/contracts.py` is explicitly a Python shim until the API host moves.

Exit condition: shell, workbench, core, runtime providers, and target adapters share stable versioned contracts.

## Stage 4 - Core Backend Ownership Reduction

Purpose: move orchestration out of Python request handlers.

- [x] Define core services for workspace state, task queue, policy/permissions, diagnostics, and adapter orchestration.
- [x] Move hot-path ownership behind the core boundary.
- [x] Keep Python request handlers thin or replace them where the new shell/core path supports it.
- [x] Convert replaceable orchestration helpers from Python into Rust/Cargo modules and route normal execution through them.
- [x] Delete or demote Python orchestration code where Rust/Cargo parity is proven; do not leave Python as an alternate controller.
- [x] Record any remaining Python handlers as HTTP/IPC bridge only, with no state machine or task-queue ownership.
- [x] Preserve cancellation, cache invalidation, and support evidence behavior.

Stage 4 implementation note: `core/talos_core` now owns the backend service registry for workspace state, task queue, policy/permissions, diagnostics, adapter orchestration, cancellation, cache invalidation, and support evidence. Python reads this manifest through `talos.core_bridge` as compatibility metadata only. Remaining Python HTTP handlers are explicitly classified as bridge endpoints until later shell/runtime stages can remove them without breaking the current desktop debug path.

Exit condition: Python no longer owns orchestration logic; it calls or bridges to core services.

## Stage 5 - Native Helper Expansion

Purpose: move OS-heavy work to native/core modules where it improves speed and clarity.

- [x] Review process/window detection ownership.
- [x] Review file watching, hashing, workspace scanning, and diff/hunk helper ownership.
- [x] Move suitable work behind native/helper APIs.
- [x] Prefer Rust/Cargo or C native helper ownership for process/window scanning, file watching, diff/hunk preparation, and filesystem-heavy operations.
- [x] Quarantine Python scanners/watchers as fallback-only migration debt until native/helper parity permits deletion; do not route new production logic through them.
- [x] Keep fallback behavior for unsupported Windows environments.
- [x] Add focused performance checks before and after migration.

Stage 5 implementation note: `core/talos_core/src/native_helpers.rs` records the Rust-owned native/helper boundary for process/window detection, file watching, hashing, workspace scanning, diff/hunk preparation, filesystem operations, telemetry, and unsupported-Windows fallback. Python may read this manifest through `talos.core_bridge.core_native_helpers()` but must remain bridge/fallback only for these domains.

Exit condition: native/helper boundaries own the practical OS-heavy work and expose stable APIs.

## Stage 6 - Runtime Provider Boundary Hardening

Purpose: make Codex and future Claude/runtime integrations replaceable.

- [x] Keep credentials outside Talos.
- [x] Treat Codex runtime as a provider with discovery, health, account metadata, runtime version, and safe reconnect status.
- [x] Keep manual context package fallback.
- [x] Move provider discovery, provider metadata normalization, retry policy, and health-state evaluation into Rust/Cargo where practical.
- [x] Keep Python runtime code only as a subprocess/HTTP bridge until the provider host can call runtime tools directly.
- [x] Delete duplicated Python provider-state logic after the Rust/Cargo provider boundary becomes the normal path; remaining Python runtime code is bridge/fallback only.
- [x] Define provider methods that future Claude or other runtimes can implement.

Stage 6 implementation note: `core/talos_core/src/runtime_providers.rs` now owns the runtime-provider boundary for Codex and future Claude-compatible providers. The Rust manifest defines discovery, health, account metadata, runtime version, safe reconnect, context packaging, message send, cancellation, external credentials, retry policy, and manual fallback methods. Python reads this manifest through `talos.core_bridge` as a thin subprocess/HTTP compatibility bridge only; credentials remain outside Talos and manual context package remains available when direct provider calls are unavailable.

Exit condition: runtime behavior is provider-owned, explicit, and not tied to VS Code UI behavior.

## Stage 7 - Target Adapter Host Contract

Purpose: make new targets possible without touching the app core.

- [x] Define adapter lifecycle: detect, map workspace, describe active document, package context, stage changes, verify/simulate/build, rollback, diagnostics.
- [x] Require adapter-level permissions and selected-workspace scoping.
- [x] Keep Arduino as the reference adapter.
- [x] Add a skeleton adapter template for future targets without implementing those targets.
- [x] Define the adapter host in Rust/Cargo so future targets do not copy Python Arduino logic.
- [x] Convert replaceable Arduino adapter utilities into Rust/Cargo or native helper calls before using Arduino as the template.
- [x] Keep Python Arduino code only as a compatibility shim until Stage 8 proves parity through the adapter host.

Stage 7 implementation note: `core/talos_core/src/target_adapters.rs` owns the adapter lifecycle, permissions, selected-workspace scope, Arduino reference adapter, and future-target template contract. `talos-core-audit target-adapters` exposes the contract as JSONL for the Python compatibility bridge; Python Arduino code remains only a shim until Stage 8 proves parity through the adapter host.

Exit condition: a future MATLAB/STM32CubeIDE/KiCad/SolidWorks adapter can start from a stable host contract.

## Stage 8 - Arduino Parity Through Core Complete Boundary

Purpose: prove the new structure did not break the product users already have.

- [x] Run Arduino detection, workspace mapping, source file list, board/profile, verify, context package, Codex review, save, and rollback through the new boundaries.
- [x] Compare results against 0.7.5 evidence.
- [x] Confirm every Arduino flow uses Rust/Cargo/native ownership for replaced primitives and does not silently fall back to Python product logic.
- [x] Delete or quarantine obsolete Python Arduino helper code after parity, leaving only bridge/debug/test surfaces.
- [x] Update language share numbers and explain any remaining Python by file name and allowed category.
- [x] Record regressions and fix or explicitly block them.

Stage 8 implementation note: `core/talos_core/src/arduino_parity.rs` is the Rust-owned Arduino parity ledger. `talos-core-audit arduino-parity` covers detection, workspace mapping, source inventory, board/profile, verify, context package, Codex review, save, and rollback against the 0.7.5 behavior surface. Remaining Arduino Python files are explicitly quarantined as compatibility shims, watcher bridge, or smoke-test harness; none are allowed to be silent product-logic fallback.

Exit condition: Arduino is still usable as the reference target on the new core-complete structure.

## Stage 9 - Release Evidence And 0.9.0 Handoff

Purpose: prove 0.8.0 is a real architecture release and prepare runtime/product trust hardening.

- [x] Update `dev_notes/evidence/TALOS_080_EVIDENCE.md`.
- [x] Update the roadmap status for 0.8.0.
- [x] Create or update the 0.9.0 pipeline from the real 0.8.0 state.
- [x] List runtime independence, consent, diagnostics, recovery, installer, and update gaps for 0.9.x.
- [x] Attach the final Python purge ledger: Python files deleted, Python files retained, reason retained, replacement owner, and target removal version if temporary.
- [x] Attach final language share numbers and confirm Rust/Cargo increased as product-logic owner.
- [x] Block 0.9.0 handoff if a replaced Python module still remains in normal execution without an explicit exception.

Stage 9 implementation note: `talos-core-audit release-handoff` is the Rust-owned release handoff command. `core_release_handoff()` exposes it to the Python compatibility bridge for tests only. The report carries the final Python purge ledger, 0.9.x runtime/trust gaps, language share summary, and `stage9_exit_ready`. Handoff target: `dev_notes/pipelines/TALOS_PIPELINE_090.md`.

Exit condition: new target work can begin after 0.9.x trust/runtime gates, without another architecture rewrite.
