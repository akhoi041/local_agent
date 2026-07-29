# Talos Pipeline - Version 0.7.0 Beta

Purpose: port Arduino onto the new target-adapter/core contracts proven in 0.6.0 and decomposed in 0.6.5. This is the first real target-product release on the long-term architecture.

```text
0.7.0 Beta = Arduino adapter port + parity proof + adapter-owned workflow behavior.
```

Release evidence: `dev_notes/evidence/TALOS_070_EVIDENCE.md`

## 0.6.5 Handoff Baseline

0.6.5 completed the decomposition work that 0.7.0 depends on:

- `desktop_app.py` remains the source/debug launcher.
- Python is allowed as compatibility/debug bridge, but product behavior should enter through core boundaries and target adapters.
- Detection, workspace scanning, cache keys, diff/hunk behavior, task orchestration, and runtime discovery now have explicit boundaries.
- Arduino remains the only active target for 0.7.0.
- Missing Codex runtime is informational and must not block Arduino workspace readiness.

## Exit Condition

0.7.0 is complete when Arduino behavior is adapter-owned, parity-tested against the current working workflow, and explicitly handed off to 0.7.5 daily-use hardening without another architecture cleanup stage.

Stage completion rule: every stage must include an adapter contract, parity test, or evidence note. Do not add MATLAB, STM32CubeIDE, KiCad, SolidWorks, or unrelated target work in this release.

Version handoff rule: every Talos version pipeline must end with a handoff stage for the next planned version. The handoff stage is mandatory before opening the next branch.

## Stage 0 - Adapter Baseline And Scope Lock

Purpose: freeze the Arduino parity target before moving behavior.

- [x] Confirm 0.6.5 Stage 8 handoff is complete.
- [x] Record current Arduino behavior surfaces: detection, sketch folder mapping, board/profile, file list, active file, verify, apply/save, rollback, and Codex context.
- [x] Confirm no new target products start in this release.
- [x] Create or update `dev_notes/evidence/TALOS_070_EVIDENCE.md`.

Exit condition: 0.7.0 starts from a known Arduino parity surface.

Stage 0 implementation note: recorded the 0.6.5 handoff, accepted compatibility paths, Arduino parity surfaces, and no-new-target scope lock in `dev_notes/evidence/TALOS_070_EVIDENCE.md`. This stage is documentation-only by design to avoid unnecessary app launches, network use, and full regression before code migration begins.

## Stage 1 - Arduino Adapter Contract

Purpose: make Arduino a first-class target adapter rather than app-specific glue.

- [x] Define adapter methods for discovery, workspace resolution, file metadata, active file, profile, verify plan, context packaging, apply/save, and rollback.
- [x] Route Arduino state through the adapter without changing visible UI behavior.
- [x] Keep existing Python bridge paths as fallback during the port.
- [x] Add contract tests for required adapter methods and payload shape.

Exit condition: Arduino has a documented and tested adapter contract.

Stage 1 implementation note: added the required target-adapter contract in `talos/targets.py`, made registry validation reject incomplete implemented adapters, and extended `ArduinoTargetAdapter` with file metadata, active-file, and verify-plan methods while keeping the existing Python Arduino bridge as the compatibility fallback. Added focused Stage 070 tests for contract compliance and payload shape.

## Stage 2 - Discovery And Workspace Mapping Port

Purpose: move Arduino IDE detection and sketch-folder mapping under the adapter.

- [x] Route open-sketch discovery through the Arduino adapter.
- [x] Preserve multi-window and multi-sketch selection behavior.
- [x] Preserve unsaved sketch and folder-not-found handling.
- [x] Add parity tests for `.ino`, `.h`, `.cpp`, and duplicate-folder cases.

Exit condition: adapter discovery produces the same selectable sketches as the current workflow.

Stage 2 implementation note: `ArduinoTargetAdapter` now owns `open_sketches`, `resolve_workspace`, and `source_inventory` entry points while reusing the proven Arduino compatibility scanner. Runtime project payloads route through `open_sketches`, and focused parity tests cover multi-sketch discovery, missing-folder/unsaved-style entries, and `.ino/.h/.cpp` source inventory without launching Arduino IDE or using network.

## Stage 3 - Board/Profile And Environment Port

Purpose: move board/profile/environment readiness under the adapter.

- [x] Route board/FQBN display, profile readiness, build flags, serial metadata, and library metadata through the adapter.
- [x] Preserve board display-name behavior and detailed metadata only where useful.
- [x] Keep profile validation explicit before verify.
- [x] Add tests for board changes, profile changes, and missing profile data.

Exit condition: board/profile behavior is adapter-owned and verify-ready state is clear.

Stage 3 implementation note: `ArduinoTargetAdapter.profile_payload` now owns board/FQBN display, profile readiness, build flags, serial metadata, library metadata, workspace map, and verify-plan profile data. Runtime context/profile endpoints consume that adapter-owned payload while preserving the legacy profile response for UI/API compatibility.

## Stage 4 - Verify And Cache Parity

Purpose: keep sandbox verify fast and deterministic through the adapter.

- [x] Route verify plan generation through the adapter.
- [x] Reuse the 0.6.5 cache-key boundary.
- [x] Preserve cancellation, clear-cache, timing telemetry, and output parsing.
- [x] Add tests for cache hit/miss, source change, board change, cancel, and verify output summary.

Exit condition: verify behavior is adapter-owned and remains cache-safe.

Stage 4 implementation note: `ArduinoTargetAdapter.verify` now attaches the adapter-owned verify plan, profile readiness, timing/cache defaults, and compact verify summary while preserving the 0.6.5 compile/cache/output implementation. The adapter contract now requires verify, cancel, and clear-cache methods, with focused tests covering cache hit/miss, source/board/override cache-key changes, cancel, clear-cache, and parsed output summary preservation.

## Stage 5 - Codex Context And Change Review Port

Purpose: make Codex receive Arduino context through adapter-owned payloads.

- [x] Route workspace map, active file, verify output, profile, and edit permission through the adapter context package.
- [x] Reuse the 0.6.5 diff/hunk boundary.
- [x] Preserve apply/reject/save/rollback semantics.
- [x] Add tests for context package contents, partial hunk apply, apply-all, reject, save, and rollback.

Exit condition: Codex can work with Arduino through adapter payloads without knowing legacy glue details.

Stage 5 implementation note: `ArduinoTargetAdapter.context_package()` now owns the Codex payload for workspace map, active file, profile, latest verify output, and edit permission while keeping legacy-compatible fields during the migration. Change review still uses the 0.6.5 `CodexBridge` hunk boundary for apply, reject, apply-all, save acknowledgement, and rollback.

## Stage 6 - UI Parity And Usability Smoke

Purpose: keep the product experience stable while internals move.

- [x] Confirm Explorer, Files, editor/review mode, verify/history, Codex column, command palette, menu bar, status bar, and settings still behave as expected.
- [x] Confirm resize/split layout remains usable across normal and maximized windows.
- [x] Confirm missing runtime state remains informational, not an Arduino failure.
- [x] Record manual smoke notes in evidence.

Exit condition: the adapter port does not regress the current Arduino user experience.

Stage 6 implementation note: UI parity is covered with lightweight contract tests instead of launching the desktop shell. The smoke checks Explorer, Files, editor/review mode, verify/history, Codex column, command palette, menu bar, status bar, settings, responsive split/grid markers, and the missing-runtime gate remaining a Codex status rather than an Arduino failure.

## Stage 7 - Regression Gate

Purpose: prove the adapter port is complete enough for hardening.

- [x] Run automated regression.
- [x] Run Arduino adapter parity tests.
- [x] Run sandbox verify smoke.
- [x] Run Codex context package smoke without requiring credential capture.
- [x] Record final evidence in `dev_notes/evidence/TALOS_070_EVIDENCE.md`.

Exit condition: Arduino adapter migration is validated and ready for explicit handoff.

Stage 7 implementation note: validated with local-only focused Stage 070 adapter smokes plus full regression. No GUI launch, credential capture, downloads, or network calls were required.

## Stage 8 - 0.7.5 Handoff

Purpose: hand the Arduino adapter port to the daily-use hardening release.

- [x] Update roadmap status for 0.7.0 completion.
- [x] Create or update `dev_notes/pipelines/TALOS_PIPELINE_075.md` based on the real Arduino adapter state.
- [x] List any remaining compatibility paths, fallbacks, or blocked items that 0.7.5 is allowed to carry.
- [x] Record final evidence in `dev_notes/evidence/TALOS_070_EVIDENCE.md`.
- [x] Confirm no new target product work starts before Arduino hardening has a clear 0.7.5 plan.

Exit condition: 0.7.5 can focus on daily-use Arduino hardening rather than adapter migration or architecture cleanup.

Stage 8 implementation note: 0.7.0 is closed at the planning/evidence level and hands Arduino daily-use hardening to 0.7.5. The next release must harden the existing Arduino adapter instead of adding MATLAB, STM32CubeIDE, KiCad, SolidWorks, or runtime-independence work.
