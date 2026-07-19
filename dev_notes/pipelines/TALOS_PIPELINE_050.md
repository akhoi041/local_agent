# Talos Pipeline - Version 0.5.0 Beta

Purpose: add a Codex Runtime Manager so Talos can use a verified local Codex runtime without treating the VS Code extension UI as the product dependency.

```text
0.5.0 Beta = Codex runtime discovery + runtime pinning + health checks + sign-in readiness + honest fallback behavior.
```

## Baseline

```text
Previous completed pipeline: dev_notes/pipelines/TALOS_PIPELINE_040.md
Previous release evidence: dev_notes/evidence/TALOS_040_EVIDENCE.md
Current active pipeline: dev_notes/pipelines/TALOS_PIPELINE_050.md
Current release evidence: dev_notes/evidence/TALOS_050_EVIDENCE.md
Next planned pipeline: dev_notes/pipelines/TALOS_PIPELINE_055.md
Target version: 0.5.0 Beta
Starting branch: develop/0.5.0
```

Talos 0.4.0 completed the broader tester-readiness pass: docs, support bundle, diagnostics export, UI/UX polish, release evidence, installer smoke, and honest runtime limitation notes. Version 0.5.0 should turn that limitation into a managed runtime boundary.

## Release Criteria

Talos 0.5.0 Beta is ready only when these are true:

- Talos can discover available Codex runtime candidates from supported local sources.
- Users can see which runtime Talos is using, where it came from, its version/hash when available, and whether it is healthy.
- Users can pin a known-good runtime and clear that pin intentionally.
- Talos warns clearly when the selected runtime is missing, changed, unsigned/unknown, not authenticated, or cannot provide the app-server/session surface.
- Codex authentication remains owned by the Codex runtime. Talos does not store OpenAI credentials, account tokens, or guessed plan data.
- The existing Arduino/Codex workflow remains usable with the selected runtime.

## Non-Goals

- No bundled or redistributed VS Code extension unless OpenAI provides a clear supported redistribution path.
- No fake Talos-side Codex login.
- No server-side telemetry or hosted feedback path.
- No plan guessing from email, GitHub account, local profile names, or window titles.
- No Python slimming or broad native rewrite; that belongs to `dev_notes/pipelines/TALOS_PIPELINE_055.md`.
- No MATLAB, STM32CubeIDE, KiCad, SolidWorks, or second target connector.

## Progress Rules

- Keep `dev_notes/pipelines/TALOS_PIPELINE_040.md` as the completed 0.4.0 release record.
- Track all 0.5.0 runtime-manager work in this file.
- Keep evidence version-level only: 0.5.0 release proof lives in `dev_notes/evidence/TALOS_050_EVIDENCE.md`, not in per-stage evidence files.
- Every completed 0.5.0 task must update this file.
- Use the pipeline status checker with this file:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/pipeline_status.ps1 -Path dev_notes\pipelines\TALOS_PIPELINE_050.md
```

## Stage 0 - 0.5.0 Pipeline Setup

Purpose: open 0.5.0 cleanly from the completed 0.4.0 release.

- [x] Confirm 0.4.0 is merged to GitHub `main`.
- [x] Create and push `release/0.4.0-beta`.
- [x] Create and push `v0.4.0-beta`.
- [x] Create `develop/0.5.0` from the 0.4.0 release state.
- [x] Create this dedicated 0.5.0 Beta pipeline.
- [x] Update roadmap, docs index, README, and pipeline status default so 0.5.0 is active.

Exit condition: 0.4.0 is closed on GitHub, 0.5.0 has its own branch and active pipeline, and 0.5.5 remains reserved for architecture/Python slimming.

## Stage 1 - Runtime Contract And Provider Inventory

Purpose: define what Talos is allowed to know and do with Codex runtimes.

- [x] Document supported runtime providers: standalone `codex` on `PATH`, user-selected executable path, and existing VS Code extension-adjacent fallback if available.
- [x] Define runtime metadata fields: provider, path, version, hash, last health check, app-server readiness, auth readiness, and limitation notes.
- [x] Define safe account metadata rules: display only runtime-provided non-secret identity/plan fields, never infer or store credentials.
- [x] Define unsupported states and user-facing copy for missing runtime, changed runtime, not signed/unknown, not authenticated, and incompatible runtime.
- [x] Add a baseline note with current local runtime behavior and any blocked cases.

Stage 1 implementation notes:

- Recorded Stage 1 release proof in `dev_notes/evidence/TALOS_050_EVIDENCE.md`; detailed runtime contract notes remain in this pipeline.
- Runtime provider order is now defined as standalone `codex` on `PATH`, user-selected executable path, VS Code extension-adjacent fallback, then no-runtime state.
- Canonical runtime metadata fields now cover provider, path/display path, version, hash, health, app-server readiness, auth readiness, optional safe account/plan labels, warnings, and limitations.
- Account rules are explicit: Talos may display only runtime-provided non-secret metadata and must not store credentials, infer plan status, or provide a fake Talos-side Codex login.
- Unsupported states and recovery copy are defined for missing runtime, changed runtime, unknown signature, unauthenticated runtime, incompatible runtime, timeout, and fallback use.
- Stage 2 backend proof is consolidated in `dev_notes/evidence/TALOS_050_EVIDENCE.md`.

Exit condition: runtime behavior is specified before code changes, including what Talos must not collect or guess.

## Stage 2 - Runtime Discovery And Pinning Backend

Purpose: make runtime selection deterministic and auditable.

- [x] Add a runtime manager module that discovers runtime candidates without launching disruptive consoles.
- [x] Add config fields for selected runtime path, pinned runtime hash/version where available, and fallback policy.
- [x] Add migration defaults so existing users keep working without losing Codex state.
- [x] Add runtime health checks with timeout, cancellation, and cached status.
- [x] Add support-bundle/runtime evidence that redacts secrets and raw tokens.
- [x] Add tests for discovery order, pinning, missing runtime, changed runtime, and redaction.

Stage 2 implementation notes:

- Added `talos/codex_runtime.py` with deterministic provider discovery, runtime choice, pin mismatch detection, hidden `codex --version` health checks, pre-launch cancellation, timeout handling, and cached status.
- Added `codex_runtime` defaults to packaged config and config migration so existing users keep Arduino/Codex state while gaining runtime-manager settings.
- Added redacted runtime evidence to diagnostics/support bundle output; raw paths, full hashes, credentials, account identifiers, and tokens are not included.
- Added tests for discovery order, migration defaults, pinning, missing runtime, changed runtime, health cache, cancellation, timeout, and redaction.
- Validation: `python -B -m unittest tests.test_desktop_app` passed 103/103.
- Updated `dev_notes/evidence/TALOS_050_EVIDENCE.md` as the single 0.5.0 evidence record.

Exit condition: Talos can choose a runtime predictably and explain that choice to the user.

## Stage 3 - Runtime Status API

Purpose: expose runtime state through thin APIs instead of UI guessing.

- [x] Add `GET /api/codex_runtime` for candidates, active runtime, health, pin state, and warnings.
- [x] Add `POST /api/codex_runtime_pin` to pin or clear a runtime explicitly.
- [x] Add `POST /api/codex_runtime_health` to rerun health checks on demand.
- [x] Include runtime status in `/api/state` without bloating normal refresh payloads.
- [x] Ensure API errors are structured and safe for logs/support bundles.

Stage 3 implementation notes:

- Added a canonical runtime status surface: `GET /api/codex_runtime` returns the full local runtime payload for Settings/Server UI and support workflows.
- Added explicit runtime actions: `POST /api/codex_runtime_pin` pins or clears a discovered runtime, and `POST /api/codex_runtime_health` reruns health checks on demand.
- Added `runtime_state_summary()` so `/api/state` carries only compact provider, display path, version/hash short, pin state, health summary, warning, limitation, and candidate count fields.
- Added structured runtime pin errors with stable codes such as `runtime_pin_missing_target` and `runtime_pin_unknown_candidate`.
- Added runtime API tests for compact summaries, pin/clear behavior, unknown candidate errors, and `/api/state` tool exposure.
- Validation: `python -B -m unittest tests.test_desktop_app` passed 106/106.

Exit condition: frontend, support bundle, and tests consume one canonical runtime status surface.

## Stage 4 - Settings And Server UI

Purpose: make runtime ownership visible without turning Talos into a login provider.

- [x] Add a Codex Runtime section in Settings showing active provider, path, version/hash, health, auth readiness, and warnings.
- [x] Add actions for refresh health, pin runtime, clear pin, and select runtime path.
- [x] Add a Server overview card summarizing runtime readiness.
- [x] Show clear copy when Talos is using a VS Code extension-adjacent fallback.
- [x] Keep account/plan display limited to safe metadata the runtime itself exposes.

Stage 4 implementation notes:

- Settings now has a Codex Runtime panel backed by `/api/codex_runtime_health` and `/api/codex_runtime_pin`.
- Server overview now includes Codex runtime readiness as a first-class card, separate from the Codex bridge conversation state.
- Runtime warnings and fallback notes are visible in the app, including the VS Code extension-adjacent fallback boundary.
- Account/plan display remains limited to runtime-exposed non-secret labels; Talos still does not collect or infer credentials.

Exit condition: a tester can understand whether Codex is ready and how Talos selected the runtime.

## Stage 5 - Codex Bridge Integration

Purpose: route Codex work through the selected runtime boundary.

- [x] Update Codex bridge startup/reconnect logic to use the selected runtime status.
- [x] Prevent user turns from being sent when runtime health/auth readiness is blocked.
- [x] Add retry and reconnect copy that distinguishes runtime failure from Codex conversation failure.
- [x] Keep existing Arduino context package behavior unchanged.
- [x] Verify that a runtime refresh does not replay an old user prompt.

Stage 5 implementation notes:

- Added a server-side runtime gate that blocks Codex user turns and reconnect attempts when the selected runtime is missing, changed, or unhealthy.
- Routed Codex bridge startup through the selected runtime executable path instead of relying only on `codex` from `PATH`.
- Added runtime-gate metadata to `/api/codex_status` so the Codex panel can distinguish runtime readiness failures from conversation/auth/app-server failures.
- Updated the Codex panel to disable prompt input and send/reconnect controls when runtime readiness is blocked.
- Kept `/api/codex_context_package` unchanged so Arduino context packaging remains available and testable even when runtime setup is incomplete.
- Verified runtime health refresh only reruns the runtime probe and does not call Codex message/reconnect paths.

Exit condition: Codex messaging is safer and clearer, while the Arduino workflow remains unchanged.

## Stage 6 - Runtime Evidence And Recovery

Purpose: make runtime problems debuggable without leaking user secrets.

- [x] Add runtime diagnostics to support bundle with redacted path/hash policy.
- [x] Add run-history events for runtime changed, health check failed, pin changed, and fallback used.
- [x] Add recovery instructions to troubleshooting docs.
- [x] Add a manual smoke path for missing runtime, fallback runtime, pinned runtime, and changed runtime.
- [x] Confirm app startup remains usable when no Codex runtime is available.

Stage 6 implementation note: runtime evidence now stays redacted in support bundles, runtime lifecycle events are filterable in run history, and troubleshooting documents the manual recovery paths for no-runtime, fallback, pinned/changed, and failed-health states.

Exit condition: runtime failures are recoverable and supportable without requiring source-code inspection.

## Stage 7 - Regression And Release Gate

Purpose: close 0.5.0 without weakening 0.4.0 product-readiness guarantees.

- [x] Run full automated checks.
- [x] Run runtime-manager smoke checks from source.
- [x] Run packaged/installed smoke checks if release artifacts are built.
- [x] Confirm Arduino detection, context package, staged review, verify, save, rollback, diagnostics, and support bundle still work.
- [x] Update release notes and roadmap status.
- [x] Create and push the 0.5.0 release branch/tag only after validation.

Stage 7 implementation notes:

- Full `scripts/check.ps1` gate passed with native DLL build/export, native benchmark, 113/113 unit tests, and release recovery smoke.
- Runtime-manager source smoke found a ready standalone Codex runtime: `codex-cli 0.144.5`.
- 0.5.0 app-data lifecycle smoke passed and wrote `releases/Talos-0.5.0-beta/app_lifecycle_smoke.json`.
- No full 0.5.0 executable/installer artifact was built during this source gate, so packaged/installed smoke is not applicable for this closure.
- Release metadata, release notes, roadmap status, and 0.5.0 evidence were updated.
- `release/0.5.0-beta` and `v0.5.0-beta` are created from this validated release-gate commit.

Exit condition: Talos can use and explain a selected Codex runtime reliably, 0.4.0 behavior remains intact, and 0.5.5 can begin architecture slimming from a stable runtime boundary.
