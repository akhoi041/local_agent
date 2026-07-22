# Talos 0.6.5 Evidence

Version: 0.6.5 Beta

Scope: Python decomposition, native/core extraction, performance parity, and compatibility fallback.

## Stage 0 - Baseline And Measurement Setup

Status: complete.

Stage 0 establishes the measured baseline before any Python hot-path reduction. The baseline uses a synthetic Arduino sketch workspace so it can run quickly and without touching the user's real Arduino projects or requiring `arduino-cli`.

### Boundary Confirmation

- 0.6.0 boundary implementation confirmed through `talos.python_ownership.boundary_check`.
- Boundary status: complete.
- No new target work starts in 0.6.5; Arduino remains the only active target.
- `desktop_app.py` remains the source/debug launcher.

### Timing Baseline

- `arduino_detection`: `0.009 ms`
- `workspace_scan`: `6.546 ms`
- `file_list_generation`: `0.002 ms`
- `hash_cache_key_generation`: `0.357 ms`
- `verify_preparation`: `0.002 ms`
- `diff_hunk_parsing`: `0.073 ms`
- `codex_context_packaging`: `0.001 ms`

Baseline sample:

- Main sketch: `talos_test.ino`
- Source files: `4`
- Context package size: `501 bytes`
- Detection sample: no real process touched; synthetic boundary measurement only.

### Python Hot-Path Ownership

Current hot paths recorded from the 0.6.0 ownership map:

- `talos.runtime_core` -> `native core`
- `talos.state_service` -> `native core`
- `talos.arduino` -> `target host`
- `talos.arduino_events` -> `target host`
- `talos.codex_runtime` -> `runtime host`
- `talos.codex_bridge` -> `runtime host`
- `talos.native_bridge` -> `native helper`
- `talos.native_boundary` -> `native helper`
- `talos.run_history` -> `storage`
- `talos.event_bus` -> `event bus`

### Validation

- `python -B -m py_compile talos\stage_baseline.py tests\test_desktop_app.py`: passed.
- `python -B -c "from talos.stage_baseline import run_stage_065_baseline; ..."`: passed.

Conclusion: Python reduction starts from measured behavior, not guesswork.
