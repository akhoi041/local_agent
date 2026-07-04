# Talos 0.2.0 Stage 1 Validation

Checked: 2026-06-30

## Summary

Stage 1 release-candidate validation is complete. The build, installer, signing-status, installer smoke, installed-app Arduino/Codex auto harness, source-debug launch check, and `-RequireReady` distribution checklist passed.

## Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Active branch | Passed | `develop/0.2.0` |
| Clean release build without `-AllowDirty` | Passed | `releases/Talos-0.1.0-beta/release_manifest.json` |
| Windows installer build | Passed | `releases/Talos-0.1.0-beta/Talos-0.1.0-beta-setup.exe` |
| Signing status | Passed as explicit unsigned Beta | `releases/Talos-0.1.0-beta/signing_status.json` |
| Installer install/uninstall smoke | Passed | `releases/Talos-0.1.0-beta/installer_smoke.json` |
| Installed-app automated smoke | Passed automated launch/health/packaged-mode checks and Arduino/Codex auto harness | `releases/Talos-0.1.0-beta/installed_app_smoke.json` |
| Source-debug launch | Passed | `desktop_app.py` responded through `/api/health` on port 8787 |
| Distribution checklist generation | Passed with `-RequireReady` | `releases/Talos-0.1.0-beta/DISTRIBUTION_CHECKLIST.md` |

## Release Gate

The installed-app Arduino/Codex gate is automated:

```powershell
.\scripts\smoke_installed_app.ps1 -SkipBuild -AutoArduinoHarness
.\scripts\distribution_checklist.ps1 -RequireReady
```

Manual confirmation remains available as a fallback. Required manual steps are listed in `docs/INSTALLED_APP_SMOKE_TEST.md` and mirrored inside `installed_app_smoke.json`:

- launch installed Talos;
- detect an open Arduino sketch;
- select sketch and board;
- open a source file;
- edit in Talos and save file;
- verify sandbox;
- ask Codex for a safe change;
- review, apply, and save Codex change;
- verify sandbox again;
- confirm Arduino IDE reflects the saved change.

After those manual checks pass, rerun:

```powershell
.\scripts\smoke_installed_app.ps1 -SkipBuild -ManualArduinoConfirmed
.\scripts\distribution_checklist.ps1 -RequireReady
```

## Issue Found And Fixed

- The first installed-app smoke run left the packaged `Talos.exe` process alive long enough for cleanup to fail when deleting the temp install folder. `scripts/smoke_installed_app.ps1` was hardened to stop the launched app, stop matching installed Talos processes, wait briefly, and retry temp-folder cleanup.
- The distribution checklist initially treated `status: unsigned-beta` as missing signing evidence. `scripts/distribution_checklist.ps1` now recognizes signed releases and explicit unsigned-Beta status.
- `scripts/smoke_installed_app.ps1` now supports `-AutoArduinoHarness`, which creates a temporary sketch, drives the installed app through Talos APIs, stages a controlled Codex smoke patch, confirms no pre-save workspace write occurs, saves the applied patch, and records installed-app smoke as `passed`.
