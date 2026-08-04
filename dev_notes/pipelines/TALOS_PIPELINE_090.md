# Talos Pipeline - Version 0.9.0 Beta

Purpose: harden runtime independence and product trust after 0.8.0 made Rust/Cargo the product-logic owner.

```text
0.9.0 Beta = runtime independence + consent/policy + diagnostics/recovery gates before new target products.
```

Release evidence: `dev_notes/evidence/TALOS_090_EVIDENCE.md`

Python guardrail: Python remains debug/compatibility glue only. Any Python module in normal execution must have a named Rust owner, removal target, and explicit exception.

## Stage 0 - 0.8.0 Handoff Intake

- [ ] Import the 0.8.0 release handoff report from `talos-core-audit release-handoff`.
- [ ] Confirm every open Python purge item has an owner and target removal version.
- [ ] Confirm Arduino reference target still passes focused smoke before runtime changes.

Exit condition: 0.9.0 starts from measured 0.8.0 state, not a planning-only reset.

## Stage 1 - Runtime Independence Gate

- [ ] Replace extension-dependent runtime assumptions with explicit runtime provider selection.
- [ ] Expose runtime health, auth status, version, account, and plan only when the runtime reports them.
- [ ] Keep credentials outside Talos storage.

Exit condition: Talos can distinguish missing, pinned, healthy, unauthenticated, and incompatible runtimes without VS Code assumptions.

## Stage 2 - Consent And Policy Gate

- [ ] Add consent wording for local diagnostics, support bundle, and optional product telemetry.
- [ ] Keep data collection opt-in and off by default until server policy exists.
- [ ] Add visible export/delete controls for local diagnostic data.

Exit condition: a tester can understand and control what Talos stores or exports.

## Stage 3 - Diagnostics And Support Gate

- [ ] Move diagnostic summaries to Rust-owned service boundaries where practical.
- [ ] Generate a compact support bundle without source code unless the user explicitly includes it.
- [ ] Redact account, path, and environment details by default.

Exit condition: support evidence is useful, small, and privacy-aware.

## Stage 4 - Recovery And Checkpoint Gate

- [ ] Harden checkpoint restore/discard after crash or restart.
- [ ] Keep Arduino IDE as the saved-file source of truth unless the user explicitly saves Talos edits.
- [ ] Confirm no external Arduino change is overwritten silently.

Exit condition: recovery protects user code during runtime crashes, app restarts, and pending reviews.

## Stage 5 - Installer And Update Trust Gate

- [ ] Align installer, app identity, shortcut, uninstall, and update-channel metadata.
- [ ] Add update/fallback behavior for missing or incompatible runtime managers.
- [ ] Keep release artifacts reproducible from documented commands.

Exit condition: beta builds are installable, uninstallable, and explain their update/runtime state.

## Stage 6 - Python Purge Closure

- [ ] Use the 0.8.0 Python purge ledger to remove or justify remaining normal-execution Python.
- [ ] Move hot-path detection, verify preparation, cache, and event logic toward Rust owners.
- [ ] Keep Python only as launcher/debug/test/temporary compatibility bridge.

Exit condition: every remaining Python file is either outside normal execution or has a dated removal target.

## Stage 7 - Release Candidate Validation

- [ ] Run focused Rust core tests.
- [ ] Run focused Python bridge tests.
- [ ] Run manual Arduino smoke with runtime missing and runtime selected states.

Exit condition: 0.9.0 can ship without regressing Arduino reference behavior.

## Stage 8 - Next Target Handoff

- [ ] Freeze the target adapter template for post-Arduino products.
- [ ] Document which runtime/trust gates must pass before MATLAB, STM32CubeIDE, KiCad, or SolidWorks implementation begins.

Exit condition: new product targets start only after runtime independence and trust gates are stable.
