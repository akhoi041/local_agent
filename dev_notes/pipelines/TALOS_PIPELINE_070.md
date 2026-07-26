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

- [ ] Define adapter methods for discovery, workspace resolution, file metadata, active file, profile, verify plan, context packaging, apply/save, and rollback.
- [ ] Route Arduino state through the adapter without changing visible UI behavior.
- [ ] Keep existing Python bridge paths as fallback during the port.
- [ ] Add contract tests for required adapter methods and payload shape.

Exit condition: Arduino has a documented and tested adapter contract.

## Stage 2 - Discovery And Workspace Mapping Port

Purpose: move Arduino IDE detection and sketch-folder mapping under the adapter.

- [ ] Route open-sketch discovery through the Arduino adapter.
- [ ] Preserve multi-window and multi-sketch selection behavior.
- [ ] Preserve unsaved sketch and folder-not-found handling.
- [ ] Add parity tests for `.ino`, `.h`, `.cpp`, and duplicate-folder cases.

Exit condition: adapter discovery produces the same selectable sketches as the current workflow.

## Stage 3 - Board/Profile And Environment Port

Purpose: move board/profile/environment readiness under the adapter.

- [ ] Route board/FQBN display, profile readiness, build flags, serial metadata, and library metadata through the adapter.
- [ ] Preserve board display-name behavior and detailed metadata only where useful.
- [ ] Keep profile validation explicit before verify.
- [ ] Add tests for board changes, profile changes, and missing profile data.

Exit condition: board/profile behavior is adapter-owned and verify-ready state is clear.

## Stage 4 - Verify And Cache Parity

Purpose: keep sandbox verify fast and deterministic through the adapter.

- [ ] Route verify plan generation through the adapter.
- [ ] Reuse the 0.6.5 cache-key boundary.
- [ ] Preserve cancellation, clear-cache, timing telemetry, and output parsing.
- [ ] Add tests for cache hit/miss, source change, board change, cancel, and verify output summary.

Exit condition: verify behavior is adapter-owned and remains cache-safe.

## Stage 5 - Codex Context And Change Review Port

Purpose: make Codex receive Arduino context through adapter-owned payloads.

- [ ] Route workspace map, active file, verify output, profile, and edit permission through the adapter context package.
- [ ] Reuse the 0.6.5 diff/hunk boundary.
- [ ] Preserve apply/reject/save/rollback semantics.
- [ ] Add tests for context package contents, partial hunk apply, apply-all, reject, save, and rollback.

Exit condition: Codex can work with Arduino through adapter payloads without knowing legacy glue details.

## Stage 6 - UI Parity And Usability Smoke

Purpose: keep the product experience stable while internals move.

- [ ] Confirm Explorer, Files, editor/review mode, verify/history, Codex column, command palette, menu bar, status bar, and settings still behave as expected.
- [ ] Confirm resize/split layout remains usable across normal and maximized windows.
- [ ] Confirm missing runtime state remains informational, not an Arduino failure.
- [ ] Record manual smoke notes in evidence.

Exit condition: the adapter port does not regress the current Arduino user experience.

## Stage 7 - Regression Gate

Purpose: prove the adapter port is complete enough for hardening.

- [ ] Run automated regression.
- [ ] Run Arduino adapter parity tests.
- [ ] Run sandbox verify smoke.
- [ ] Run Codex context package smoke without requiring credential capture.
- [ ] Record final evidence in `dev_notes/evidence/TALOS_070_EVIDENCE.md`.

Exit condition: Arduino adapter migration is validated and ready for explicit handoff.

## Stage 8 - 0.7.5 Handoff

Purpose: hand the Arduino adapter port to the daily-use hardening release.

- [ ] Update roadmap status for 0.7.0 completion.
- [ ] Create or update `dev_notes/pipelines/TALOS_PIPELINE_075.md` based on the real Arduino adapter state.
- [ ] List any remaining compatibility paths, fallbacks, or blocked items that 0.7.5 is allowed to carry.
- [ ] Record final evidence in `dev_notes/evidence/TALOS_070_EVIDENCE.md`.
- [ ] Confirm no new target product work starts before Arduino hardening has a clear 0.7.5 plan.

Exit condition: 0.7.5 can focus on daily-use Arduino hardening rather than adapter migration or architecture cleanup.
