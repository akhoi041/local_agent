# Talos 0.7.5 Evidence

Purpose: record concise validation evidence for the Arduino workflow hardening release.

## Stage 0 - Baseline Refresh

Status: complete.

### Baseline

- Branch: `develop/0.7.5`
- Version metadata: `config/app_identity.json` reports `0.7.5 Beta`.
- Source/debug launcher: `desktop_app.py` remains the app entry point.
- 0.7.0 handoff source: `dev_notes/evidence/TALOS_070_EVIDENCE.md`

### 0.7.0 Adapter State

- Arduino discovery, workspace mapping, board/profile payloads, verify plans, Codex context packaging, and change-review boundaries are adapter-owned.
- Missing Codex runtime is informational and does not block Arduino workspace readiness.
- Compatibility/debug Python remains allowed where it preserves the current Arduino workflow.
- 0.7.5 must harden Arduino daily use only; no MATLAB, STM32CubeIDE, KiCad, SolidWorks, or runtime-independence work is in scope.

### Blocked Items

- None for Stage 0.

### Validation

- Command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_satisfies_contract tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_contract_payload_shape tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_tracks_board_and_environment_metadata tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_updates_when_board_profile_changes tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_profile_payload_reports_missing_profile_data tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_attaches_plan_summary_and_preserves_output tests.test_desktop_app.TalosArduinoTests.test_stage_070_compile_cache_hit_miss_and_key_boundaries tests.test_desktop_app.TalosArduinoTests.test_stage_070_adapter_verify_cancel_and_clear_cache_are_owned tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_routes_open_sketch_discovery tests.test_desktop_app.TalosArduinoTests.test_stage_070_arduino_adapter_workspace_mapping_source_inventory tests.test_desktop_app.TalosArduinoTests.test_stage_070_context_package_routes_adapter_payloads tests.test_desktop_app.TalosArduinoTests.test_stage_070_change_review_boundary_preserves_apply_reject_save_rollback tests.test_desktop_app.TalosArduinoTests.test_stage_070_ui_parity_surfaces_stay_connected tests.test_desktop_app.TalosArduinoTests.test_stage_070_missing_runtime_remains_codex_status_not_arduino_failure`
- Result: 14 tests passed in 0.243 seconds.

Conclusion: 0.7.5 starts from a known Arduino adapter state and can proceed to daily-use hardening.

## Stage 1 - Daily Arduino Detection Hardening

Status: complete.

### Detection Behavior

- Reopen flow: stale process-sourced `.ino` paths are ignored when the current live Arduino window title resolves to a different saved sketch folder.
- Multi-sketch flow: source-tab titles from distinct parent folders resolve independently and keep source inventory counts.
- Refresh model: event-assisted window updates remain debounced, with polling fallback still available through the existing Arduino state refresh path.
- Timing: synthetic three-sketch discovery is guarded under 250 ms.

### Validation

- Focused command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_arduino_discovery_ignores_persisted_workspace_after_ide_closes tests.test_desktop_app.TalosArduinoTests.test_arduino_discovery_lists_multiple_open_ino_paths tests.test_desktop_app.TalosArduinoTests.test_arduino_discovery_keeps_sketch_folder_when_active_title_is_cpp_or_header_tab tests.test_desktop_app.TalosArduinoTests.test_stage_075_discovery_reopen_replaces_stale_process_path tests.test_desktop_app.TalosArduinoTests.test_stage_075_discovery_resolves_source_tabs_from_distinct_roots tests.test_desktop_app.TalosArduinoTests.test_stage_075_event_watcher_keeps_debounced_event_assist tests.test_desktop_app.TalosArduinoTests.test_stage_075_detection_timing_stays_within_local_refresh_budget`
- Focused result: 7 tests passed in 0.088 seconds.
- Regression command: `python -B -m unittest -q tests.test_desktop_app`
- Regression result: 177 tests passed in 9.583 seconds.

Conclusion: Stage 1 exit condition is met for automated coverage; manual Arduino IDE smoke can still be used as a user-facing confirmation pass.

## Stage 2 - Workspace And File Sync Hardening

Status: complete.

### File Sync Behavior

- Arduino workspace file reads now return a stable SHA-256 content hash.
- Save File sends the loaded hash plus mtime to the backend, keeping saves explicit.
- Backend stale-write protection rejects saves when Arduino IDE or another process changed the file after Talos loaded it.
- Atomic write behavior is retained; rejected stale saves leave the Arduino-owned file untouched.
- The UI marks conflicted files and keeps Talos in review/local-edit mode instead of silently becoming the source of truth.

### Validation

- Focused command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_075_workspace_save_returns_content_hash tests.test_desktop_app.TalosArduinoTests.test_stage_075_workspace_save_rejects_external_edit_with_loaded_hash`
- Focused result: 2 tests passed in 0.033 seconds.
- Atomic-write guard command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_arduino_workspace_file_write_is_atomic`
- Atomic-write guard result: 1 test passed in 0.009 seconds.

Conclusion: Stage 2 exit condition is met for focused validation; Talos can detect external file changes without overwriting Arduino-owned edits.
