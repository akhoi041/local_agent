# Talos 0.7.0 Evidence

## Scope

0.7.0 ports the existing Arduino workflow onto the target-adapter/core contracts created in 0.6.0 and decomposed in 0.6.5. Arduino is the only active target in this release.

No MATLAB, STM32CubeIDE, KiCad, SolidWorks, or unrelated target work should start in 0.7.0.

## Stage 0 - Adapter Baseline And Scope Lock

Status: complete.

Stage 0 freezes the current Arduino parity target before adapter migration starts.

### 0.6.5 handoff confirmation

- `dev_notes/pipelines/TALOS_PIPELINE_065.md` Stage 8 is marked complete.
- `dev_notes/evidence/TALOS_065_EVIDENCE.md` records 0.6.5 as handed off to 0.7.0.
- Accepted Python compatibility paths for 0.7.0 remain:
  - `desktop_app.py`: source/debug launcher and WebView host.
  - `talos/server.py`: local HTTP compatibility bridge.
  - `talos/arduino.py`: legacy Arduino workflow owner until adapter parity lands.
  - `talos/codex_bridge.py`: Codex workflow bridge until adapter-owned payloads land.
  - `talos/native_bridge.py` and `talos/runtime_discovery.py`: compatibility glue while the long-term split matures.

### Current Arduino behavior surfaces to preserve

- Detection: Arduino IDE/open sketch detection remains the source of selectable Arduino workspaces.
- Sketch folder mapping: selected `.ino` sketch resolves to the sketch folder; companion `.h` and `.cpp` tabs stay part of the same workspace.
- Board/profile: board display name, FQBN/profile data, build flags, serial metadata, and library metadata stay visible where useful.
- File list: source files preserve Arduino tab behavior and show line/byte metadata.
- Active file: selected file drives the editor/review surface and Codex active-file context.
- Verify: sandbox verify uses the selected sketch folder, board/profile, cache key, cancellation, clear-cache behavior, timing telemetry, and parsed output summary.
- Apply/save: Codex-staged changes stay reviewable before editor/save transfer; Save File remains the explicit write path back to the Arduino workspace.
- Rollback: checkpoint/rollback behavior remains available before/after real workspace writes.
- Codex context: workspace map, active file, verify output, profile readiness, and edit permission remain explicitly packaged and previewable.
- Runtime state: missing Codex runtime is informational and must not mark Arduino workspace readiness as failed.

### Validation

- Documentation-only stage; no network, app launch, or full regression required.
- Local source of truth checked from 0.6.5 pipeline/evidence and 0.7.0 pipeline.
- `git diff --check` should be enough for this stage unless code changes are added later.

Conclusion: 0.7.0 starts from a known Arduino parity surface and can begin adapter migration without expanding scope.

## Stage 1 - Arduino Adapter Contract

Status: complete.

Stage 1 makes Arduino a first-class target adapter with a documented and enforced contract before deeper behavior is moved out of legacy glue.

### Contract surface

- `talos/targets.py` defines `TARGET_ADAPTER_REQUIRED_METHODS`, `target_adapter_contract`, and registry validation for implemented adapters.
- Required adapter methods cover discovery, workspace summary/identity, file metadata, active file, profile, verify plan, context packaging, read/write, rollback, and generic context.
- `ArduinoTargetAdapter` now exposes `file_metadata`, `active_file`, and `verify_plan` in addition to the existing discovery, workspace, profile, context, verify, write, and rollback paths.
- Existing Python Arduino bridge calls remain the fallback implementation during the port; Stage 1 does not change visible UI behavior or compile behavior.

### Validation

- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_satisfies_contract tests.test_desktop_app.TalosArduinoTests.test_target_registry_rejects_incomplete_implemented_adapter tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_contract_payload_shape`
- Result: 3 tests passed.

Conclusion: Arduino now has a tested adapter contract and can move discovery/workspace behavior under the adapter in Stage 2.

## Stage 2 - Discovery And Workspace Mapping Port

Status: complete.

Stage 2 moves the selectable Arduino sketch and workspace-mapping entry points under `ArduinoTargetAdapter` while keeping the existing scanner as the compatibility implementation.

### Adapter-owned entry points

- `ArduinoTargetAdapter.open_sketches(...)` is now the adapter-owned discovery entry point for open Arduino sketches.
- `ArduinoTargetAdapter.resolve_workspace(...)` maps a selected project back to a workspace summary without changing the proven folder scanner.
- `ArduinoTargetAdapter.source_inventory(...)` exposes the selected workspace source list as target files.
- `TalosRuntimeCore.arduino_projects_payload()` now routes project discovery through the adapter.

### Validation

- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_routes_open_sketch_discovery tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_workspace_mapping_source_inventory tests.test_desktop_app.TalosArduinoTests.test_state_payload_exposes_generic_target_context`
- Result: 3 tests passed.

Conclusion: discovery and sketch-folder mapping now enter through the Arduino adapter, preserving multi-sketch selection, folder-not-found handling, and `.ino/.h/.cpp` source inventory behavior.

## Stage 3 - Board/Profile And Environment Port

Status: complete.

Stage 3 moves Arduino board/profile/environment readiness under the adapter while preserving the existing API shape for the UI.

### Adapter-owned profile behavior

- `ArduinoTargetAdapter.profile_payload(...)` now owns board display/FQBN metadata, environment profile data, profile readiness, workspace map, and verify-ready profile fields.
- `TalosRuntimeCore.arduino_context_payload()` and `arduino_profile_payload()` consume the adapter profile payload instead of rebuilding board/profile state independently.
- Verify plans now expose explicit `profile_ready`, serial port, baud rate, build flags, build properties, and library metadata for downstream verify/Codex context.
- The profile endpoint keeps the legacy `profile` field as the environment profile and adds `target_profile` for board/FQBN identity.

### Validation

- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_satisfies_contract tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_contract_payload_shape tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_tracks_board_and_environment_metadata tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_updates_when_board_profile_changes tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_reports_missing_profile_data tests.test_desktop_app.TalosArduinoTests.test_state_payload_exposes_generic_target_context`
- Result: 6 tests passed.
- `git diff --check`
- Result: no patch errors; only existing LF/CRLF normalization warnings.

Conclusion: board/profile behavior is adapter-owned and verify-ready state is explicit.

## Stage 4 - Verify And Cache Parity

Status: complete.

Stage 4 routes Arduino verify behavior through the adapter without replacing the proven compile implementation.

### Adapter-owned verify behavior

- `TARGET_ADAPTER_REQUIRED_METHODS` now requires `verify`, `cancel_verify`, and `clear_verify_cache`.
- `ArduinoTargetAdapter.verify(...)` attaches the adapter verify plan, profile readiness, cache/timing defaults, and a compact summary to compile results.
- The existing 0.6.5 compile implementation remains the execution boundary, preserving cache keys, cancellation, clear-cache, timing telemetry, issue parsing, and output parsing.

### Validation

- `python -B -m unittest tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_satisfies_contract tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_attaches_plan_summary_and_preserves_output tests.test_desktop_app.TalosArduinoTests.test_stage_070_compile_cache_hit_miss_and_key_boundaries tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_cancel_and_clear_cache_are_owned`
- Result: 4 tests passed.

Conclusion: verify behavior is adapter-owned at the contract/API boundary and remains cache-safe.

## Stage 5 - Codex Context And Change Review Port

Status: complete.

Stage 5 makes the Codex payload adapter-owned while preserving the proven 0.6.5 change-review mechanics.

### Adapter-owned Codex context

- `ArduinoTargetAdapter.context_package(...)` now exposes `version: 0.7.0`, adapter ownership metadata, workspace map, active file, target profile, profile readiness, latest verify output, and edit permission payload.
- Legacy-compatible fields remain present during the migration so the current UI and Codex bridge do not need to know the new adapter internals.
- Edit permission is represented both as the existing string contract and as a structured adapter payload with `allow_edits`, `mode`, `save_required`, and sketch-folder scope.

### Change-review boundary

- The existing 0.6.5 `CodexBridge` hunk model remains the boundary for partial apply, reject, apply-all, save acknowledgement, and rollback.
- Tests cover adapter context package contents and hunk review behavior without requiring network, GitHub, or a real Codex runtime.

### Validation

- `python -B -m unittest tests.test_desktop_app.TalosArduinoTests.test_stage_070_context_package_routes_adapter_payloads tests.test_desktop_app.TalosArduinoTests.test_stage_070_change_review_boundary_preserves_apply_reject_save_rollback`
- Result: 2 tests passed.

Conclusion: Codex can receive Arduino workspace/profile/verify/edit context through adapter payloads, and change review remains compatible with the current editor flow.

## Stage 6 - UI Parity And Usability Smoke

Status: complete.

Stage 6 used low-resource UI contract checks rather than opening the GUI, keeping the smoke pass cheap and repeatable.

### Covered

- Explorer, Files, editor/review mode, verify/history, Codex column, command palette, menu bar, status bar, and settings markers are present and wired.
- Responsive split/grid layout markers remain present for normal and maximized window behavior.
- Missing Codex runtime remains a Codex gate (`runtime_missing`) and does not mark Arduino workspace/verify as failed.

### Validation

- `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_ui_parity_surfaces_stay_connected tests.test_desktop_app.TalosArduinoTests.test_stage_070_missing_runtime_remains_codex_status_not_arduino_failure`
- Result: 2 tests passed.

Conclusion: the adapter port keeps the current Arduino UI surfaces connected without requiring GUI launch, network access, or Codex credentials.

## Stage 7 - Regression Gate

Status: complete.

Stage 7 closes the Arduino adapter port with low-resource validation and no network dependency.

### Validation

- Focused Stage 070 adapter parity, verify, context, change-review, and UI smoke command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_satisfies_contract tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_contract_payload_shape tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_tracks_board_and_environment_metadata tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_updates_when_board_profile_changes tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_reports_missing_profile_data tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_attaches_plan_summary_and_preserves_output tests.test_desktop_app.TalosArduinoTests.test_stage_070_compile_cache_hit_miss_and_key_boundaries tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_cancel_and_clear_cache_are_owned tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_routes_open_sketch_discovery tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_workspace_mapping_source_inventory tests.test_desktop_app.TalosArduinoTests.test_stage_070_context_package_routes_adapter_payloads tests.test_desktop_app.TalosArduinoTests.test_stage_070_change_review_boundary_preserves_apply_reject_save_rollback tests.test_desktop_app.TalosArduinoTests.test_stage_070_ui_parity_surfaces_stay_connected tests.test_desktop_app.TalosArduinoTests.test_stage_070_missing_runtime_remains_codex_status_not_arduino_failure`
- Focused result: 14 tests passed.
- Automated regression command: `python -B -m unittest -q tests.test_desktop_app`
- Regression result: 173 tests passed.

### Coverage

- Arduino adapter contract, discovery, workspace map, profile payload, verify plan/cache/cancel/clear-cache, context package, change-review boundary, and UI continuity were covered.
- Sandbox verify smoke is covered through adapter verify and compile cache/timing tests without launching Arduino IDE or requiring `arduino-cli`.
- Codex context package smoke is covered without credential capture; missing runtime remains an informational Codex gate.

Conclusion: Arduino adapter migration is validated and ready for explicit 0.7.5 handoff.

## Stage 8 - 0.7.5 Handoff

Status: complete.

0.7.0 is closed at the adapter-port level and hands daily-use Arduino hardening to `dev_notes/pipelines/TALOS_PIPELINE_075.md`.

### Handoff Scope

- 0.7.5 may carry compatibility/debug Python where it preserves the existing Arduino workflow.
- 0.7.5 may harden Arduino detection, file sync, verify cache/cancel/readability, Codex runtime status, change review, recovery, and UI daily-use polish.
- 0.7.5 must not add MATLAB, STM32CubeIDE, KiCad, SolidWorks, or runtime-independence scope.

### Validation

- Stage 7 focused adapter smoke: 14 tests passed.
- Stage 7 full regression: 173 tests passed.
- Handoff artifacts updated: roadmap, 0.7.0 pipeline, 0.7.0 evidence, and new 0.7.5 pipeline.

Conclusion: 0.7.5 can focus on daily-use Arduino hardening rather than adapter migration or architecture cleanup.
