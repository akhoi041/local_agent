# Talos 0.4.0 Release Evidence

Date: 2026-07-16

## Release State

Talos 0.4.0 is closed as the completed product-readiness Beta/Pre-Alpha milestone.

GitHub state:

- `origin/main`: `e6ac01c` (`Merge pull request #13 from akhoi041/develop/0.4.0`)
- Release branch: `release/0.4.0-beta`
- Release tag: `v0.4.0-beta`
- Completed pipeline: `dev_notes/pipelines/TALOS_PIPELINE_040.md`
- Next active pipeline: `dev_notes/pipelines/TALOS_PIPELINE_050.md`

## Completed Scope

0.4.0 finished the broader tester-readiness pass:

- Product-facing UI/UX refresh.
- Arduino workflow polish.
- Codex activity/history/context preview polish.
- Diagnostics export and support bundle flow.
- Privacy and local diagnostics posture.
- Distribution copy and release documentation.
- Installer and installed-app smoke evidence.
- Runtime limitation documented honestly: Talos can use an available Codex runtime and may fall back to the VS Code extension runtime, but first-class runtime discovery/pinning is deferred to 0.5.0.

## Validation Evidence

Primary 0.4.0 release-gate evidence is recorded in:

- `dev_notes/pipelines/TALOS_PIPELINE_040.md`
- `releases/Talos-0.4.0-pre-alpha/release_manifest.json`
- `releases/Talos-0.4.0-pre-alpha/DISTRIBUTION_CHECKLIST.md`
- `releases/Talos-0.4.0-pre-alpha/installer_smoke.json`
- `releases/Talos-0.4.0-pre-alpha/installed_app_smoke.json`
- `releases/Talos-0.4.0-pre-alpha/app_lifecycle_smoke.json`
- `docs/RELEASE_NOTES.md`

Release-gate checks recorded by the completed 0.4.0 pipeline:

- Full regression test pass.
- `git diff --check` with only known CRLF warnings.
- `scripts/check.ps1` pass.
- Distribution checklist generated with `-RequireReady`.
- Installer smoke pass.
- Installed-app smoke pass.
- Clean install/upgrade/uninstall validation pass.
- Explicit unsigned Beta/Pre-Alpha signing status.

## Known Limits Carried Forward

The following are intentionally not solved in 0.4.0:

- Codex Runtime Manager.
- Python/native architecture slimming.
- Non-Arduino target connectors.
- Hosted telemetry/server ingestion.
- Auto-update infrastructure.
- Full VS Code-quality shell frame.

## Exit Summary

0.4.0 is safe to treat as a frozen release baseline for future comparisons. Version 0.5.0 starts from this state and focuses specifically on making the Codex runtime boundary explicit, discoverable, pinnable, and supportable.
