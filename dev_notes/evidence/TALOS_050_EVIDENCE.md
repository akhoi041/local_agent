# Talos 0.5.0 Evidence

Date: 2026-07-16
Status: in progress

## Evidence Policy

This is the single evidence file for Talos 0.5.0 Beta. Stage-level implementation details stay in `dev_notes/pipelines/TALOS_PIPELINE_050.md`; this file records only version-level proof that matters for release review.

## Stage 0 - Pipeline Setup

Result: complete.

- 0.4.0 was closed as the previous completed release track.
- `develop/0.5.0` is the active development branch.
- `dev_notes/pipelines/TALOS_PIPELINE_050.md` is the active 0.5.0 pipeline.
- `dev_notes/pipelines/TALOS_PIPELINE_055.md` remains reserved for Python/native boundary slimming.

## Stage 1 - Runtime Contract And Provider Inventory

Result: complete.

- Defined supported runtime providers:
  - standalone `codex` on `PATH`
  - user-selected runtime path
  - VS Code extension-adjacent fallback
  - no-runtime state
- Defined canonical runtime metadata: provider, path/display path, version, hash, health, app-server readiness, auth readiness, optional safe account/plan labels, warnings, and limitations.
- Defined safety rules:
  - Talos must not store OpenAI credentials, OAuth tokens, browser cookies, VS Code secrets, GitHub tokens, ChatGPT session data, or raw account identifiers.
  - Talos must not infer subscription tier from email, GitHub username, file path, window title, or local profile name.
  - Talos may display only runtime-provided non-secret account/plan/readiness labels.
- Defined unsupported runtime states and user-facing recovery copy for missing runtime, changed runtime, unknown signature, unauthenticated runtime, incompatible runtime, timeout, and fallback use.

## Stage 2 - Runtime Discovery And Pinning Backend

Result: complete.

- Added `talos/codex_runtime.py` as the runtime manager backend.
- Added `codex_runtime` config defaults and migration normalization.
- Added deterministic discovery order:
  1. standalone `codex` from `PATH`
  2. user-selected runtime path
  3. VS Code extension-adjacent fallback path when allowed
  4. no-runtime state
- Added runtime selection, pin mismatch warnings, hidden `codex --version` health checks, pre-launch cancellation, timeout handling, and in-memory health cache.
- Added redacted runtime evidence to diagnostics/support bundle output.
- Added tests for discovery order, migration defaults, pinning, missing runtime, changed runtime, health cache, cancellation, timeout, and redaction.

Validation:

```text
python -B -m unittest tests.test_desktop_app
Ran 103 tests
OK
```

Known boundary: Stage 2 validates process/version readiness only. Runtime API, settings UI, bridge routing, and sign-in guidance belong to later 0.5.0 stages.

## Stage 3 - Runtime Status API

Result: complete.

- Added `GET /api/codex_runtime` as the canonical local runtime status endpoint for candidates, active runtime, health, pin state, and warnings.
- Added `POST /api/codex_runtime_pin` for explicit runtime pin and clear actions.
- Added `POST /api/codex_runtime_health` for user-triggered health refresh.
- Added compact runtime status to `/api/state` so normal refreshes do not carry full candidate/config payloads.
- Added structured runtime pin errors with stable codes safe for UI logs and support review.
- Added tests for summary redaction/size, pin/clear behavior, unknown candidate handling, and `/api/state` endpoint exposure.

Validation:

```text
python -B -m unittest tests.test_desktop_app
Ran 106 tests
OK
```

Known boundary: Stage 3 exposes the runtime API only. Settings UI, runtime actions in the visible interface, and bridge routing belong to later 0.5.0 stages.

## Stage 4 - Settings And Server UI

Result: complete.

- Added a Codex Runtime section in Settings showing provider, path, version/hash, health, auth readiness, app-server readiness, pin state, candidates, safe account metadata, warnings, and limitations.
- Added visible runtime actions: Refresh Health, Pin Runtime, Clear Pin, and Select Path.
- Added Codex runtime readiness to the Server overview so runtime selection is not hidden inside the Codex chat panel.
- Added explicit copy for VS Code extension-adjacent fallback ownership.
- Added frontend regression coverage for the runtime UI, actions, server card, fallback copy, and safe metadata boundary.

Validation:

```text
python -B -m unittest tests.test_desktop_app
Ran 107 tests
OK
```

Known boundary: Stage 4 makes runtime ownership visible. Stage 5 is still responsible for routing Codex bridge startup/reconnect behavior through the selected runtime boundary.

## Stage 5 - Codex Bridge Integration

Result: complete.

- Codex bridge startup now receives the selected runtime executable from the runtime manager instead of relying only on `codex` from `PATH`.
- `/api/codex_status` now includes runtime-gate metadata and does not start Codex when the selected runtime is missing, changed, or unhealthy.
- `/api/codex_message` and `/api/codex_reconnect` now block safely on runtime readiness failures and record the block without replaying a user prompt.
- Runtime failure copy is distinct from Codex conversation failure copy in the Codex panel.
- `/api/codex_context_package` remains unchanged so Arduino context packaging still works independently of runtime readiness.
- Runtime health refresh remains probe-only and does not call message or reconnect flows.

Validation:

```text
python -B -m unittest tests.test_desktop_app
Ran 111 tests
OK
```
