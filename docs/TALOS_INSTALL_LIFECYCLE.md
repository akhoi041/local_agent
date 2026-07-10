# Talos Install Lifecycle Validation

This document defines the 0.4.0 clean install, upgrade, and uninstall validation path.

## Scope

Stage 5 validates Talos as an installed Windows app, not only as a source checkout:

- First install into a clean install directory.
- Launch from the installed executable with isolated app data.
- Health check and packaged build metadata.
- Start Menu shortcut and optional Desktop shortcut.
- Upgrade preservation for existing app-data files.
- Clean uninstall of installer-owned files.
- Explicit user-runtime-data policy.

## Clean Profile Method

Use a fresh Windows profile, VM, or an isolated app-data substitute:

```powershell
$env:TALOS_APP_DATA_DIR = "$env:TEMP\TalosLifecycleSmoke\app-data"
```

The isolated app-data path must be outside the install directory and outside the repository.

## Required Smoke Scripts

Run the installer smoke:

```powershell
.\scripts\smoke_installer.ps1 -AllowDirty
```

This validates silent install, packaged files, Start Menu shortcut, optional Desktop shortcut, no writable runtime config in the install directory, silent uninstall, and installer-owned cleanup.

Run the installed-app smoke:

```powershell
.\scripts\smoke_installed_app.ps1 -AllowDirty -AutoArduinoHarness
```

This validates installed launch, `/api/health`, packaged metadata, isolated app-data usage, Talos file operations, Codex staged change behavior, and sandbox verify.

Run the lifecycle smoke:

```powershell
.\scripts\smoke_app_lifecycle.ps1
```

This validates the app-data lifecycle without touching the real user profile.

## Upgrade Preservation

When upgrading from 0.3.0 to 0.4.0, Talos must not silently discard these user-owned files:

- `config.json`
- `run_history.json`
- `checkpoints.json`
- `codex_reviews.json`
- `diagnostics.json`
- `profiles\`
- `staging\`
- `sandbox\`

If a future migration changes schema, it must write a backup before replacing user state.

## Uninstall Policy

The uninstaller removes installer-owned files and shortcuts. It does not automatically delete user runtime data under `%LOCALAPPDATA%\T-Engine\Talos`.

Users who want a full data removal can delete that folder manually, or developers can use isolated `TALOS_APP_DATA_DIR` during validation.

## Evidence Files

The release folder should contain:

- `installer_smoke.json`
- `installed_app_smoke.json`
- `app_lifecycle_smoke.json`

The final distribution checklist should summarize all three before public handoff.
