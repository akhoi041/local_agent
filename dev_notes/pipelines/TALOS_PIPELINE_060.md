# Talos Pipeline - Version 0.6.0 Beta

Purpose: freeze Talos' long-term architecture before adding non-Arduino targets. This release defines the contracts later connectors must implement instead of letting MATLAB, STM32CubeIDE, KiCad, or SolidWorks force another app-wide rewrite.

0.6.0 Beta = target-adapter contract + local API/IPC contract + Python boundary freeze + native-helper boundary + Codex runtime boundary + shell migration decision.

Release evidence: `dev_notes/evidence/TALOS_060_EVIDENCE.md`

## Exit Condition

0.6.0 is complete when the shared contracts are documented and tested, the existing Arduino path still works unchanged, shell/native/Python responsibilities are explicit, and 0.7.0 can harden Arduino as the reference target without another architecture reset.

## Stage 0 - Baseline And Version Open

Purpose: open 0.6.0 from the completed 0.5.5 release.

- [x] Close 0.5.5 with commit `ddf0744`, release branch `release/0.5.5-beta`, and tag `v0.5.5-beta`.
- [x] Open local branch `develop/0.6.0` from the completed 0.5.5 baseline.
- [x] Set app identity and release notes to 0.6.0 Beta.
- [x] Create 0.6.0 evidence and pipeline files.
- [x] Push `develop/0.6.0` to GitHub.

Exit condition: 0.6.0 has a clean branch, version metadata, release notes, evidence file, and pipeline.

## Stage 1 - Target Adapter Contract

Purpose: define what every supported external app must expose to Talos.

- [ ] Document the target-adapter interface: detect, enumerate workspaces, map source files, read context, stage changes, apply/save, verify/build/simulate, rollback, diagnostics, and evidence.
- [ ] Map the current Arduino implementation onto the adapter contract without changing behavior.
- [ ] Add compatibility tests proving Arduino data can be represented through the generic target contract.
- [ ] Define target capability flags so non-code tools can expose design/review/build actions without pretending to be Arduino sketches.

Exit condition: the target-adapter contract exists, Arduino fits it, and tests protect the contract.

## Stage 2 - Local API And IPC Contract

Purpose: make UI, runtime manager, target adapters, and native helpers communicate through stable contracts instead of Python module shortcuts.

- [ ] Document stable local API routes/events and their versioning rules.
- [ ] Add schema validation for state, target context, Codex context package, verify result, diagnostics, and evidence payloads.
- [ ] Separate internal Python helper calls from public local API behavior.
- [ ] Add regression tests for backward-compatible API responses used by the frontend.

Exit condition: UI-facing and runtime-facing contracts are documented, validated, and test-covered.

## Stage 3 - Python Boundary Freeze

Purpose: decide what Python keeps and what must migrate.

- [ ] Classify each Python module as debug launcher, bridge/orchestration, target adapter, fallback, or migration candidate.
- [ ] Create a migration checklist for replacing Python-heavy hot paths with native/runtime services.
- [ ] Keep `desktop_app.py` as a required debug/source launcher until shell parity is proven.
- [ ] Remove or archive stale Python paths that no longer support the current architecture.

Exit condition: Python ownership is explicit and future reductions are measurable instead of ad hoc.

## Stage 4 - Native Helper Boundary

Purpose: keep native code useful, narrow, and benchmark-driven.

- [ ] Define which primitives belong in native code: scanning, hashing, cache-key generation, diff/hunk parsing, and process/window discovery.
- [ ] Add or update benchmarks for every native candidate before migration.
- [ ] Keep Python fallback paths for unsupported Windows environments.
- [ ] Document build/fallback behavior for packaged and source/debug runs.

Exit condition: native work has clear performance gates and fallback guarantees.

## Stage 5 - Codex Runtime Boundary

Purpose: keep Talos independent from the VS Code UI while respecting the user's authenticated Codex runtime.

- [ ] Ensure runtime discovery/pinning remains provider-neutral.
- [ ] Document which metadata Talos may display: source, version, hash, auth readiness, app-server readiness, and safe account/plan fields only if exposed by the runtime.
- [ ] Confirm Talos never stores OpenAI credentials, session tokens, or inferred plan data.
- [ ] Keep VS Code extension-adjacent runtimes as explicit fallback candidates, not the normal product dependency.

Exit condition: Codex runtime behavior is clear, safe, and independent from VS Code UI assumptions.

## Stage 6 - Desktop Shell Migration Decision

Purpose: choose the long-term shell path before adding more targets.

- [ ] Compare current pywebview shell, Tauri/Rust, and Electron against native frame behavior, Windows snap layout, packaging, app-data paths, static UI serving, local API access, and installer complexity.
- [ ] Define parity tests required before replacing the current shell.
- [ ] Record the shell decision and the earliest version where migration may start.
- [ ] Keep source/debug launch available even if the production shell changes later.

Exit condition: the shell direction is chosen in writing, and no later target connector depends on a temporary shell detail.

## Stage 7 - Arduino Compatibility Smoke

Purpose: prove architecture work did not damage the working Arduino path.

- [ ] Detect open Arduino sketches and source tabs.
- [ ] Select a sketch and inspect `.ino`, `.h`, and `.cpp` files.
- [ ] Verify sandbox compile with the current board profile.
- [ ] Send a Codex turn with context package preview.
- [ ] Apply/reject/save flow remains safe and recoverable.

Exit condition: Arduino remains usable while the architecture is being formalized.

## Stage 8 - 0.7.0 Handoff

Purpose: hand the finalized architecture to the Arduino reference-target hardening release.

- [ ] Summarize completed contracts and unresolved risks in this pipeline.
- [ ] Update roadmap status for 0.6.0 completion and 0.7.0 readiness.
- [ ] Create or prepare `dev_notes/pipelines/TALOS_PIPELINE_070.md`.
- [ ] Record final evidence in `dev_notes/evidence/TALOS_060_EVIDENCE.md`.

Exit condition: 0.7.0 can begin with stable contracts and clear Arduino hardening scope.
