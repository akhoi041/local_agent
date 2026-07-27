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
