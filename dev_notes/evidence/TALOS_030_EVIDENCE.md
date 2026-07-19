# Talos 0.3.0 Baseline

Date: 2026-07-08

## Starting Point

Talos 0.3.0 starts from the completed 0.2.0 Beta foundation.

Frozen comparison records:

- `dev_notes/pipelines/TALOS_PIPELINE_010.md`
- `dev_notes/pipelines/TALOS_PIPELINE_020.md`

Active development record:

- `dev_notes/pipelines/TALOS_PIPELINE_030.md`

## Carry-Over Guarantees

- Arduino remains the only active target.
- Installed-app and installer smoke tooling from 0.2.0 must continue to pass.
- Codex changes must remain staged or editor-applied until the user explicitly saves.
- External Arduino edits must not be silently overwritten.
- PowerShell/CMD fallback subprocesses should remain hidden and throttled during normal app use.

## Known Carry-Over Risk

- 0.3.0 focuses on Codex workflow maturity, so the highest risk is UI/state complexity around context preview, pending turns, reconnect/cancel, staged changes, and verify-before-save.
- Packaging metadata should not be bumped from 0.2.0 to 0.3.0 until the final 0.3.0 release gate.
