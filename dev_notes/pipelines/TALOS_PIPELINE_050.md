# Talos Pipeline - Version 0.5.0 Beta

Purpose: add a Codex Runtime Manager so Talos can use a verified local Codex runtime without treating the VS Code extension UI as the product dependency.

```text
0.5.0 Beta = Codex runtime discovery + runtime pinning + health checks + sign-in readiness + honest fallback behavior.
```

## Baseline

```text
Previous completed pipeline: dev_notes/pipelines/TALOS_PIPELINE_040.md
Current active pipeline: dev_notes/pipelines/TALOS_PIPELINE_050.md
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

- [ ] Document supported runtime providers: standalone `codex` on `PATH`, user-selected executable path, and existing VS Code extension-adjacent fallback if available.
- [ ] Define runtime metadata fields: provider, path, version, hash, last health check, app-server readiness, auth readiness, and limitation notes.
- [ ] Define safe account metadata rules: display only runtime-provided non-secret identity/plan fields, never infer or store credentials.
- [ ] Define unsupported states and user-facing copy for missing runtime, changed runtime, not signed/unknown, not authenticated, and incompatible runtime.
- [ ] Add a baseline note with current local runtime behavior and any blocked cases.

Exit condition: runtime behavior is specified before code changes, including what Talos must not collect or guess.

## Stage 2 - Runtime Discovery And Pinning Backend

Purpose: make runtime selection deterministic and auditable.

- [ ] Add a runtime manager module that discovers runtime candidates without launching disruptive consoles.
- [ ] Add config fields for selected runtime path, pinned runtime hash/version where available, and fallback policy.
- [ ] Add migration defaults so existing users keep working without losing Codex state.
- [ ] Add runtime health checks with timeout, cancellation, and cached status.
- [ ] Add support-bundle/runtime evidence that redacts secrets and raw tokens.
- [ ] Add tests for discovery order, pinning, missing runtime, changed runtime, and redaction.

Exit condition: Talos can choose a runtime predictably and explain that choice to the user.

## Stage 3 - Runtime Status API

Purpose: expose runtime state through thin APIs instead of UI guessing.

- [ ] Add `GET /api/codex_runtime` for candidates, active runtime, health, pin state, and warnings.
- [ ] Add `POST /api/codex_runtime_pin` to pin or clear a runtime explicitly.
- [ ] Add `POST /api/codex_runtime_health` to rerun health checks on demand.
- [ ] Include runtime status in `/api/state` without bloating normal refresh payloads.
- [ ] Ensure API errors are structured and safe for logs/support bundles.

Exit condition: frontend, support bundle, and tests consume one canonical runtime status surface.

## Stage 4 - Settings And Server UI

Purpose: make runtime ownership visible without turning Talos into a login provider.

- [ ] Add a Codex Runtime section in Settings showing active provider, path, version/hash, health, auth readiness, and warnings.
- [ ] Add actions for refresh health, pin runtime, clear pin, and select runtime path.
- [ ] Add a Server overview card summarizing runtime readiness.
- [ ] Show clear copy when Talos is using a VS Code extension-adjacent fallback.
- [ ] Keep account/plan display limited to safe metadata the runtime itself exposes.

Exit condition: a tester can understand whether Codex is ready and how Talos selected the runtime.

## Stage 5 - Codex Bridge Integration

Purpose: route Codex work through the selected runtime boundary.

- [ ] Update Codex bridge startup/reconnect logic to use the selected runtime status.
- [ ] Prevent user turns from being sent when runtime health/auth readiness is blocked.
- [ ] Add retry and reconnect copy that distinguishes runtime failure from Codex conversation failure.
- [ ] Keep existing Arduino context package behavior unchanged.
- [ ] Verify that a runtime refresh does not replay an old user prompt.

Exit condition: Codex messaging is safer and clearer, while the Arduino workflow remains unchanged.

## Stage 6 - Runtime Evidence And Recovery

Purpose: make runtime problems debuggable without leaking user secrets.

- [ ] Add runtime diagnostics to support bundle with redacted path/hash policy.
- [ ] Add run-history events for runtime changed, health check failed, pin changed, and fallback used.
- [ ] Add recovery instructions to troubleshooting docs.
- [ ] Add a manual smoke path for missing runtime, fallback runtime, pinned runtime, and changed runtime.
- [ ] Confirm app startup remains usable when no Codex runtime is available.

Exit condition: runtime failures are recoverable and supportable without requiring source-code inspection.

## Stage 7 - Regression And Release Gate

Purpose: close 0.5.0 without weakening 0.4.0 product-readiness guarantees.

- [ ] Run full automated checks.
- [ ] Run runtime-manager smoke checks from source.
- [ ] Run packaged/installed smoke checks if release artifacts are built.
- [ ] Confirm Arduino detection, context package, staged review, verify, save, rollback, diagnostics, and support bundle still work.
- [ ] Update release notes and roadmap status.
- [ ] Create and push the 0.5.0 release branch/tag only after validation.

Exit condition: Talos can use and explain a selected Codex runtime reliably, 0.4.0 behavior remains intact, and 0.5.5 can begin architecture slimming from a stable runtime boundary.
