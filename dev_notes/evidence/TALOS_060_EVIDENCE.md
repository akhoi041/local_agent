# Talos 0.6.0 Evidence

## Baseline

- Source branch: `develop/0.6.0`
- Baseline commit: `ddf0744` (`Complete Talos 0.5.5 architecture slimming`)
- Closed prior release markers:
  - `develop/0.5.5`
  - `release/0.5.5-beta`
  - `v0.5.5-beta`

## Scope

0.6.0 is the architecture foundation release. It should define and validate the long-term contracts before new target products are added.

Stage completion rule:

- A stage is not complete with documentation alone unless the stage is explicitly a release-document task.
- Each architecture stage must record implementation artifacts, validation, and a conclusion.
- Evidence should name the changed modules/config/scripts, the tests or measurable checks run, and the remaining risk.

Required evidence for completion:

- Target-adapter contract implemented and covered by tests.
- Local API/IPC contract implemented, versioned, and covered by compatibility tests.
- Python responsibilities classified into bridge, fallback, or legacy-removal paths, with at least one boundary cleanup landed.
- Native-helper boundary exposed through code with benchmark/timing gates recorded.
- Desktop shell boundary and migration decision recorded with parity checks.
- Existing Arduino workflow passes smoke/regression checks after boundary work.

## Stage 1 - Target Adapter Foundation

Status: complete.

Implementation:

- Added `talos/targets.py` with generic target workspace, source file, profile, context, adapter, and registry types.
- Added `talos/arduino_adapter.py` so Arduino IDE is now the first concrete target adapter instead of the permanent hard-coded app model.
- Updated `talos/server.py` to register the Arduino adapter and expose `GET /api/targets`.
- Updated `talos/state_service.py` so `/api/state` includes generic target metadata/context and lists `GET /api/targets`.
- Preserved the existing Arduino endpoints for backward compatibility while routing shared behavior through the adapter boundary.

Validation:

- `python -B -m py_compile talos\targets.py talos\arduino_adapter.py talos\server.py talos\state_service.py`
- `python -B -m unittest tests.test_desktop_app`
- Result: 121 tests passed.

Conclusion: Stage 1 is implemented in code, not only documented. Future targets can now begin from the `TargetAdapter` boundary instead of copying Arduino-specific server logic.

## Stage 2 - Local API And IPC Contract

Status: complete.

Implementation:

- Added `talos/contracts.py` with `talos.local-api.v1` metadata helpers and named contracts for state, targets, target context, Codex context packages, verify results, diagnostics, and evidence payloads.
- Added `require_contract()` compatibility guards so tests and future bridge code can reject missing, mismatched, or unsupported local API contracts.
- Routed `/api/state`, `/api/targets`, `/api/arduino_context`, `/api/codex_context_package`, `/api/arduino_verify`, `/api/diagnostics_export`, and `/api/release_evidence` through contract serializers.
- Updated `ArduinoTargetAdapter.context()` to accept precomputed summary/profile/readiness/workspace-map snapshots, preventing internal helper calls from leaking or repeating at the public API boundary.
- Preserved existing Arduino payload fields while adding top-level contract metadata for forward-compatible UI/runtime consumption.

Versioning rules:

- Additive fields may remain on `talos.local-api.v1`.
- Removing or renaming UI/runtime-facing fields requires a new local API version.
- Internal helper dictionaries must cross HTTP/local IPC through a serializer in `talos/contracts.py`.

Validation:

- `python -B -m py_compile talos\contracts.py talos\targets.py talos\arduino_adapter.py talos\state_service.py talos\server.py tests\test_desktop_app.py`
- `python -B -m unittest tests.test_desktop_app`
- `python -B scripts\architecture_health.py --json --iterations 1`
- Result: 123 tests passed; architecture health passed with no failures.
- Timing note: `state_refresh` averaged `1069.872 ms`, under the `2000 ms` guardrail, after reusing one Arduino process/window snapshot for contract serialization.

Conclusion: Stage 2 now has a real versioned local contract layer. The frontend and future runtime/target adapters can consume stable payloads without depending on raw Python helper shapes.
