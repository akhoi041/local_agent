# Talos Pipeline - Version 0.8.0 Beta

Purpose: make Talos Core Complete enough that new target products can be added through adapters instead of another app-wide rewrite. This version is implementation work, not a planning-only bridge.

```text
0.8.0 Beta = professional shell/core/API/runtime/native/adapter structure + Python reduced to compatibility/debug glue.
```

Release evidence: `dev_notes/evidence/TALOS_080_EVIDENCE.md`

Python expansion guardrail: no 0.8.0 stage may add new Python-owned product logic. Python is allowed only as the source/debug launcher, compatibility API bridge, temporary adapter shim, or test harness while ownership moves into shell/core/API/runtime/native/adapter boundaries. Any remaining Python ownership must be named as migration debt with a target replacement stage.

## 0.7.5 Handoff Baseline

0.7.5 closes the current Arduino daily-use hardening path. 0.8.0 starts from that state and focuses on structure:

- Arduino remains the reference target and must keep working throughout the rewrite.
- `desktop_app.py` remains available as a source/debug launcher until the replacement shell has parity.
- Python must not receive new hot-path ownership unless it is explicitly marked temporary.
- No MATLAB, STM32CubeIDE, KiCad, SolidWorks, or other target work starts until this pipeline exits.

## Toolchain Readiness

Local PATH check before this pipeline was created:

- `rustc`: missing
- `cargo`: missing
- `node`: missing
- `npm`: missing

Preferred path:

- Tauri + Rust desktop shell.
- Current web workbench retained and hosted by the new shell.
- Core/runtime/adapter logic moved behind stable contracts.

Fallback path:

- Electron + TypeScript only if Tauri blocks required Windows frame, installer, or IPC behavior.

Install rule:

- Do not download or install large toolchains silently. Ask before installing Rust/Cargo, Node/NPM, Tauri CLI, Electron, or related SDKs.

## Exit Condition

0.8.0 is complete when Talos can run through explicit shell/core/API/runtime/native/adapter boundaries, Arduino passes parity through those boundaries, and Python is no longer the owner of hot-path app logic.

Required proof:

- Replacement shell path is installed, prototyped, or blocked with evidence and fallback.
- Local API/IPC payloads are versioned and tested.
- Core backend owns orchestration through a language-neutral boundary.
- Native helper layer owns OS-heavy detection/scanning/hash/diff candidates where practical.
- Runtime providers are explicit and replaceable.
- Target adapters can be created without changing app-wide shell/core code.
- Arduino remains functional and recoverable.

## Stage 0 - Toolchain And Baseline Gate

Purpose: confirm the real rewrite can start from a measured environment.

- [ ] Confirm branch and version metadata for 0.8.0.
- [ ] Verify Rust/Cargo and Node/NPM availability.
- [ ] If missing, ask for approval before installing the selected toolchain.
- [ ] Record current Python ownership map from 0.6.5, 0.7.0, and 0.7.5 evidence.
- [ ] Run focused Arduino smoke baseline before structural changes.

Exit condition: 0.8.0 starts with known toolchain status, known Python ownership, and a working Arduino baseline.

## Stage 1 - Python Legacy Reduction And Bridge Boundary

Purpose: reduce the existing Python code to the minimum bridge surface before the new shell/core path starts owning product behavior.

- [ ] Classify every Python module as one of: debug launcher, compatibility API bridge, temporary adapter shim, or logic owner to migrate.
- [ ] Move only critical logic-owner paths into the new core/native/adapter boundary plan: workspace scanning, verify scheduling, runtime state, diagnostics export, task orchestration, and file/change coordination.
- [ ] Keep `desktop_app.py` as the source/debug launcher, but remove any expectation that it owns app behavior beyond bootstrapping and local development.
- [ ] Replace Python-only internal assumptions with language-neutral interfaces where the new core will call back into existing code during migration.
- [ ] Delete or quarantine Python helpers that duplicate the intended core/native/adapter responsibility and are not required for Arduino parity.
- [ ] Add focused tests proving Python request handlers and bridges are thin pass-through surfaces, not owners of business logic.
- [ ] Record remaining Python ownership as explicit technical debt with a target replacement stage.

Exit condition: the old Python code is trimmed and mapped so Python can act as a compatibility/debug bridge during the rewrite, not the default owner of core app logic.

## Stage 2 - Desktop Shell Boundary Implementation

Purpose: stop treating the Python WebView shell as the permanent app shell.

- [ ] Define shell lifecycle responsibilities: window, tray, app identity, native frame, installer/update hooks, and web workbench hosting.
- [ ] Create the replacement shell project or skeleton using the approved toolchain.
- [ ] Keep `desktop_app.py` as a debug/source launcher while replacement shell matures.
- [ ] Add a shell adapter contract so the web workbench does not depend on Python-specific launch behavior.
- [ ] Prove launch, close, resize, theme handoff, and local API connection.

Exit condition: Talos has a real non-Python shell path or a documented blocker with fallback activated.

## Stage 3 - Local API And IPC Contract Freeze

Purpose: make frontend/backend communication stable before moving ownership.

- [ ] Version the state, Arduino context, runtime status, verify, diagnostics, support bundle, and evidence payloads.
- [ ] Add contract tests for payload compatibility.
- [ ] Replace ad hoc response shapes with typed schemas or schema-like validation.
- [ ] Document breaking-change rules for future target adapters.

Exit condition: shell, workbench, core, runtime providers, and target adapters share stable versioned contracts.

## Stage 4 - Core Backend Ownership Reduction

Purpose: move orchestration out of Python request handlers.

- [ ] Define core services for workspace state, task queue, policy/permissions, diagnostics, and adapter orchestration.
- [ ] Move hot-path ownership behind the core boundary.
- [ ] Keep Python request handlers thin or replace them where the new shell/core path supports it.
- [ ] Preserve cancellation, cache invalidation, and support evidence behavior.

Exit condition: Python no longer owns orchestration logic; it calls or bridges to core services.

## Stage 5 - Native Helper Expansion

Purpose: move OS-heavy work to native/core modules where it improves speed and clarity.

- [ ] Review process/window detection ownership.
- [ ] Review file watching, hashing, workspace scanning, and diff/hunk helper ownership.
- [ ] Move suitable work behind native/helper APIs.
- [ ] Keep fallback behavior for unsupported Windows environments.
- [ ] Add focused performance checks before and after migration.

Exit condition: native/helper boundaries own the practical OS-heavy work and expose stable APIs.

## Stage 6 - Runtime Provider Boundary Hardening

Purpose: make Codex and future Claude/runtime integrations replaceable.

- [ ] Keep credentials outside Talos.
- [ ] Treat Codex runtime as a provider with discovery, health, account metadata, runtime version, and safe reconnect status.
- [ ] Keep manual context package fallback.
- [ ] Define provider methods that future Claude or other runtimes can implement.

Exit condition: runtime behavior is provider-owned, explicit, and not tied to VS Code UI behavior.

## Stage 7 - Target Adapter Host Contract

Purpose: make new targets possible without touching the app core.

- [ ] Define adapter lifecycle: detect, map workspace, describe active document, package context, stage changes, verify/simulate/build, rollback, diagnostics.
- [ ] Require adapter-level permissions and selected-workspace scoping.
- [ ] Keep Arduino as the reference adapter.
- [ ] Add a skeleton adapter template for future targets without implementing those targets.

Exit condition: a future MATLAB/STM32CubeIDE/KiCad/SolidWorks adapter can start from a stable host contract.

## Stage 8 - Arduino Parity Through Core Complete Boundary

Purpose: prove the new structure did not break the product users already have.

- [ ] Run Arduino detection, workspace mapping, source file list, board/profile, verify, context package, Codex review, save, and rollback through the new boundaries.
- [ ] Compare results against 0.7.5 evidence.
- [ ] Record regressions and fix or explicitly block them.

Exit condition: Arduino is still usable as the reference target on the new core-complete structure.

## Stage 9 - Release Evidence And 0.9.0 Handoff

Purpose: prove 0.8.0 is a real architecture release and prepare runtime/product trust hardening.

- [ ] Update `dev_notes/evidence/TALOS_080_EVIDENCE.md`.
- [ ] Update the roadmap status for 0.8.0.
- [ ] Create or update the 0.9.0 pipeline from the real 0.8.0 state.
- [ ] List runtime independence, consent, diagnostics, recovery, installer, and update gaps for 0.9.x.

Exit condition: new target work can begin after 0.9.x trust/runtime gates, without another architecture rewrite.
