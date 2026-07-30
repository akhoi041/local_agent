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

## Stage 3 - Verify Workflow Hardening

Status: complete.

### Verify Behavior

- Verify timing payloads are normalized across early failures, cache hits, cache clears, and normal compile results.
- Cache hits remain explicitly labelled and cache clear responses include clear cache metadata.
- Cancel idle feedback remains explicit and does not pretend a compile was cancelled when none is active.
- Verify output stays concise in the UI while preserving copyable raw compiler output.

### Validation

- Focused command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_arduino_verify_requires_fqbn_before_compile tests.test_desktop_app.TalosArduinoTests.test_compile_cache_is_keyed_by_workspace_content_and_can_be_cleared tests.test_desktop_app.TalosArduinoTests.test_compile_cache_clear_result_and_cached_runtime_feedback tests.test_desktop_app.TalosArduinoTests.test_verify_runtime_status_flags_slow_compile_and_total tests.test_desktop_app.TalosArduinoTests.test_verify_cancel_feedback_reports_idle_state tests.test_desktop_app.TalosArduinoTests.test_verify_ui_resets_output_before_new_request`
- Focused result: 6 tests passed in 0.020 seconds.

Conclusion: Stage 3 exit condition is met for focused validation; verify is predictable across cache, cancel, early-failure, and normal UI summary paths.

## Stage 4 - Codex Runtime UX Hardening

Status: complete.

### Runtime UX Behavior

- Missing runtime states are scoped to Codex only and do not block Arduino workspace, file, or verify tools.
- Runtime status and blocked-gate payloads expose a manual replay guard so reconnect/status refreshes do not replay a user turn.
- Context package copy remains available as the manual fallback path when Codex cannot act directly.
- Runtime payloads report safe metadata only and explicitly keep credential handling outside Talos.

### Validation

- Focused command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_075_runtime_gate_is_codex_only_private_and_fallback_ready tests.test_desktop_app.TalosArduinoTests.test_stage_075_codex_status_reports_no_replay_privacy_policy tests.test_desktop_app.TalosArduinoTests.test_stage_075_codex_runtime_ui_keeps_manual_fallback_copy`
- Focused result: 4 tests passed in 0.039 seconds, including the Stage 0.7.0 missing-runtime regression guard.

Conclusion: Stage 4 exit condition is implemented; focused validation confirms whether users can distinguish Codex runtime readiness from Arduino tool readiness.

## Stage 5 - Change Review And Recovery Hardening

Status: complete.

### Review And Recovery Behavior

- Hunk apply/reject, apply-all, and reject-all are validated at the CodexBridge boundary.
- Save acknowledgement marks applied editor content as saved without writing workspace content by itself.
- Checkpoint rollback restores the previous Talos-saved file content through an explicit rollback action.
- Pending reviews still persist until the user restores or discards them.
- External file conflicts keep Arduino Version as the non-destructive default and do not overwrite Arduino-owned work.

### Validation

- Focused command: `python -B -m unittest -q tests.test_desktop_app.TalosArduinoTests.test_stage_075_change_review_recovery_keeps_arduino_as_default tests.test_desktop_app.TalosArduinoTests.test_codex_unfinished_reviews_persist_until_restored_or_discarded tests.test_desktop_app.TalosArduinoTests.test_release_recovery_keeps_external_arduino_change_after_restart tests.test_desktop_app.TalosArduinoTests.test_stage_070_change_review_boundary_preserves_apply_reject_save_rollback`
- Focused result: 4 tests passed in 0.231 seconds.

Conclusion: Stage 5 exit condition is met; Codex changes do not silently overwrite Arduino-owned work.

## Stage 6 - UI Daily-Use Polish

Status: complete.

### Focused UI Result

- Command palette, menu bar, status bar, keyboard shortcuts, and find behavior are treated as the canonical quick-command surfaces for the Arduino workbench.
- Explorer remains the Arduino context surface; Codex remains a separate right-column runtime surface; Verify/History remains the bottom workbench output surface.
- Toolbar actions remain grouped around immediate workflow actions so verify/Codex activity does not add another long-term UI architecture layer.
- Deferred UI architecture items are explicitly moved beyond 0.7.5: native frame parity, toolkit replacement, runtime independence, and shell rewrite.

### Architecture Guardrail

- 0.7.5 now records that Python must not keep expanding as the product logic owner.
- 0.8.0 receives the structural work: shell/core/API/runtime/native/adapter boundaries and Python reduction.

### Validation

- Evidence type: focused design/behavior review with no new app-code expansion in this pass.
- Automated validation is intentionally not rerun for Stage 6 because this pass only updates release notes, guardrails, and pipeline state.

Conclusion: Stage 6 exit condition is met for focused release evidence; daily Arduino use has a stable UI contract and remaining structural work is assigned to 0.8.0.

## Stage 7 - Support Evidence And Release Gate

Status: complete.

### Release Gate Result

- Support/evidence is consolidated in this version evidence file rather than scattered into per-stage files.
- Daily-use smoke coverage is represented by the completed Stage 1-6 evidence: detection, file ownership, verify behavior, Codex runtime UX, change review/recovery, and UI daily-use polish.
- Manual Arduino smoke is recorded as ready for tester execution with a real Arduino IDE session and board; no new hardware/GUI action is claimed in this focused pass.
- Python expansion remains blocked: this stage records readiness only and adds no Python-owned product logic.

### Validation

- Regression command: `python -B -m unittest -q tests.test_desktop_app`
- Regression result: 183 tests passed in 33.321 seconds.
- Diff hygiene command: `git diff --check -- dev_notes\roadmap\TALOS_ROADMAP.md dev_notes\pipelines\TALOS_PIPELINE_075.md dev_notes\pipelines\TALOS_PIPELINE_080.md dev_notes\evidence\TALOS_075_EVIDENCE.md`
- Diff hygiene result: no whitespace errors; Git reported expected LF-to-CRLF working-copy warnings for edited markdown files.

Conclusion: Stage 7 exit condition is met for focused 0.7.5 release gating. The Arduino daily-use hardening path is validated by regression and consolidated evidence, while real-device smoke remains an explicit tester action instead of hidden automation.

## Stage 8 - 0.8.0 Handoff

Status: complete.

### Handoff Result

- Roadmap status updated: 0.7.5 is complete and 0.8.0 remains the next Talos Core Complete implementation gate.
- `dev_notes/pipelines/TALOS_PIPELINE_080.md` already contains implementation stages, not only planning notes or interface contracts.
- No new target product work should start before 0.8.0 closes the core gate.

### 0.8.0 Core Gaps

- Move Python-owned orchestration out of the durable product path; keep Python only as launcher, compatibility/debug bridge, temporary migration shim, or test harness.
- Implement clear shell/core/API/runtime/native/adapter boundaries before MATLAB, STM32CubeIDE, KiCad, SolidWorks, or other targets.
- Make runtime provider behavior explicit and replaceable instead of coupling Talos to VS Code UI behavior.
- Preserve Arduino as the reference adapter while validating the new core-complete structure.

### Toolchain Readiness

- `rustc --version`: not found in PATH.
- `cargo --version`: not found in PATH.
- `node --version`: not found in PATH.
- `npm --version`: not found in PATH.

0.8.0 Stage 0 must request approval before installing Rust/Cargo or Node/NPM. No downloads were performed during this handoff.

Conclusion: Stage 8 exit condition is met. 0.8.0 can focus on core completeness rather than Arduino daily-use bugs, with missing toolchains and Python ownership debt recorded up front.
