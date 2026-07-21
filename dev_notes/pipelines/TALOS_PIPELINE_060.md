# Talos Pipeline - Version 0.6.0 Beta

Purpose: begin the real long-term rebuild of Talos while keeping the working Arduino source/debug app usable. This release must land implementation boundaries, not only documents, so future app targets can be added through adapters instead of forcing another rewrite.

```text
0.6.0 Beta = shell boundary + core runtime boundary + versioned local API/IPC + target host skeleton + runtime provider boundary + Python compatibility bridge.
```

Release evidence: `dev_notes/evidence/TALOS_060_EVIDENCE.md`

## Exit Condition

0.6.0 is complete when Talos still launches from `desktop_app.py`, but UI/core/runtime/target operations are routed through explicit boundaries that a future non-Python shell can reuse. Arduino must remain usable through a compatibility adapter, and Python must be documented in code as bridge/fallback/migration code rather than the permanent owner of the product architecture.

Stage completion rule: documentation alone cannot complete a stage unless the stage says it is documentation-only. Each implementation stage must leave code, config, tests, or a measurable validation artifact.

## Stage 0 - Baseline And Version Open

Purpose: open the rebuild safely from the 0.5.5 architecture-pivot baseline.

- [x] Confirm the 0.5.5 compatibility baseline, current branch, and dirty worktree state.
- [x] Set app identity, release notes, and evidence references to 0.6.0 Beta only when work on this version actually starts.
- [x] Keep `desktop_app.py` as the source/debug launcher.
- [x] Confirm no commit/tag/push happens unless explicitly requested by the user.
- [x] Record starting risk: this is a rebuild foundation, so later target work is blocked until this architecture is real.

Exit condition: 0.6.0 starts from a known baseline and has a clear no-silent-push/no-new-target rule.

## Stage 1 - Shell Boundary Scaffold

Purpose: stop binding the app directly to pywebview details.

- [x] Add a shell boundary module or package that owns launch profile, window creation, app identity, icon lookup, port selection, close handling, and static UI hosting.
- [x] Keep pywebview as the debug/source shell provider.
- [x] Define future provider slots for Tauri/Rust and Electron without implementing a fake production shell.
- [x] Move shell-specific constants out of mixed server/UI logic.
- [x] Add launch-parity tests or a validation script for source/debug startup, shutdown, resize/minimize/maximize behavior where practical.

Exit condition: the current app still runs, but shell concerns are isolated behind a provider boundary.

## Stage 2 - Core Runtime Boundary

Purpose: create the real backend owner of app state and orchestration.

- [x] Add a core runtime module/package that owns workspace state, selected target, selected file, verify state, runtime state, diagnostics state, and task history coordination.
- [x] Route HTTP/local API endpoints through the core runtime instead of directly reading/writing scattered module globals.
- [x] Move task queue and cancellation state behind the core boundary.
- [x] Add tests proving existing `/api/state`, Arduino workspace, verify, Codex package, and settings behavior still work through the new boundary.
- [x] Keep Python implementation acceptable for this stage only because the boundary, not the language, is the product contract.

Exit condition: server endpoints depend on a core runtime boundary, not on direct helper-module shortcuts.

## Stage 3 - Versioned Local API And IPC Contract

Purpose: make frontend, runtime providers, target adapters, and shell communicate through stable payloads.

- [x] Define versioned contract serializers for app state, target state, workspace map, source file, verify result, runtime status, diagnostics, command palette, settings, and evidence.
- [x] Add compatibility/version fields to UI-facing responses.
- [x] Validate outbound payloads in tests so internal Python object shapes do not leak into the local API.
- [x] Keep old Arduino API endpoints as compatibility wrappers only.
- [x] Document breaking-change rules for later Tauri/Rust IPC migration.

Exit condition: UI/runtime-facing data has explicit contracts and tests.

Stage 3 implementation note:

- Added explicit local API metadata with `api_version` and compatibility mode on UI/runtime-facing payloads.
- Expanded contract serializers for workspace maps, source files, verify results, runtime status, settings, command palette, diagnostics, evidence, state, targets, target context, and Codex context packages.
- Routed source file reads/writes, Arduino verify, Codex patch verify, runtime status, settings save, and command palette data through versioned contract surfaces while keeping existing Arduino endpoint paths stable.
- Breaking changes require a new local API version; additive fields remain allowed under `talos.local-api.v1`.

## Stage 4 - Target Host Skeleton

Purpose: create the shared place where Arduino, MATLAB, STM32CubeIDE, KiCad, and SolidWorks will eventually plug in.

- [x] Implement target registry, target capabilities, target workspace identity, source/design artifact identity, profile, context package, verify/check action, write/apply action, rollback action, and diagnostics hooks.
- [x] Wrap the existing Arduino behavior as the first compatibility target adapter.
- [x] Expose generic target metadata through `/api/targets` while preserving Arduino-specific endpoints.
- [x] Add tests that assert Arduino can be represented through the generic target contract.
- [x] Block non-Arduino target stubs from claiming support before they implement real workflows.

Stage 4 implementation note:

- `talos/targets.py` now defines target actions, implemented/placeholder status, registry metadata, and a guard that prevents unimplemented adapters from being registered as supported targets by default.
- `talos/arduino_adapter.py` exposes Arduino as the first real target adapter with workspace identity, artifact identity, profile identity, context package, verify, write, rollback, and diagnostics hooks.
- `/api/targets` continues to expose generic metadata through `RUNTIME_CORE.targets_payload()` while Arduino-specific endpoints remain compatibility surfaces.
- Regression tests verify Arduino's generic target contract and confirm non-Arduino placeholders cannot claim support without an explicit placeholder opt-in.

Exit condition: Arduino is the first real adapter on a shared target host, and future target apps have a real integration shape.

## Stage 5 - Runtime Provider Boundary

Purpose: make Codex/Claude/runtime integration replaceable and explicit.

- [x] Implement a runtime provider registry for Codex first and placeholders only for future providers.
- [x] Route discovery, health, pinning, app-server status, context package, message sending, patch/review actions, and safe metadata display through the provider boundary.
- [x] Enforce a metadata allowlist: source, path, version, hash, auth readiness, app-server readiness, safe account/plan fields only if the runtime exposes them.
- [x] Prove Talos does not store OpenAI credentials, session tokens, cookies, or inferred subscription data.
- [x] Treat VS Code extension-adjacent runtime paths as fallback candidates, not the product foundation.

Stage 5 implementation note:

- Added `talos/runtime_provider.py` with a Codex provider, provider registry, placeholder runtime providers, and a safe runtime metadata sanitizer.
- `TalosRuntimeCore` now routes Codex state, runtime discovery/health, pinning, app-server status, message sending, reconnect/cancel/conversation, review restore/discard, and shutdown through the Codex provider boundary.
- Runtime metadata is allowlisted to source/path/version/hash/readiness plus safe account/plan fields only; token, cookie, session, password, authorization, API key, bearer, refresh, and secret fields are dropped.
- VS Code extension-adjacent runtime paths remain a fallback-candidate policy, not the product foundation.

Exit condition: runtime behavior is provider-owned, credential-safe, and not hardwired to VS Code UI behavior.

## Stage 6 - Python Compatibility Bridge

Purpose: keep the current app working while preparing Python reduction.

- [ ] Add an ownership map in code or config for Python modules: launcher, shell provider, core implementation, target adapter, runtime provider, diagnostics, native fallback, or migration candidate.
- [ ] Mark hot paths that must move in 0.6.5: process/window discovery, file watching, hashing/cache keys, diff/hunk parsing, task orchestration, and heavy workspace scans.
- [ ] Add a boundary check that flags new direct frontend/server access to internal helper modules.
- [ ] Remove or archive stale Python paths that no longer support the current architecture.
- [ ] Keep fallback behavior for machines without native helper support.

Exit condition: Python is explicitly a bridge/fallback/migration layer, and 0.6.5 can reduce it without guessing.

## Stage 7 - Native Helper Boundary

Purpose: make native acceleration a controlled interface, not scattered C calls.

- [ ] Expose native helper capabilities through one adapter.
- [ ] Report which operations are native-backed and which are fallback-backed.
- [ ] Add timing hooks for detection, scan, hash, diff, and verify preparation candidates.
- [ ] Keep missing-native behavior non-fatal.
- [ ] Record migration gates for primitives not ready to move yet.

Exit condition: native acceleration has a single boundary and measurable fallback behavior.

## Stage 8 - Arduino Compatibility Smoke

Purpose: prove the rebuild did not break the first product workflow.

- [ ] Detect open Arduino sketches and source tabs.
- [ ] Select a sketch and inspect `.ino`, `.h`, and `.cpp` files.
- [ ] Verify sandbox compile with the selected board/profile.
- [ ] Send a Codex turn with context package preview.
- [ ] Apply/reject/save remains safe and recoverable.
- [ ] Record the smoke result in `dev_notes/evidence/TALOS_060_EVIDENCE.md`.

Exit condition: Arduino remains usable on top of the new boundaries.

## Stage 9 - 0.6.5 Handoff

Purpose: prepare the Python-decomposition patch release.

- [ ] Summarize completed boundaries and remaining Python migration candidates.
- [ ] Update roadmap status for 0.6.0.
- [ ] Confirm `dev_notes/pipelines/TALOS_PIPELINE_065.md` matches the actual 0.6.0 result.
- [ ] Record final evidence in `dev_notes/evidence/TALOS_060_EVIDENCE.md`.

Exit condition: 0.6.5 can start reducing Python hot paths without changing product behavior.
