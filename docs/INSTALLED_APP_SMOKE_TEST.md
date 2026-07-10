# Installed App Smoke Test

This smoke test validates the packaged Talos Beta outside the source tree. It is the final functional check before the distribution checklist is produced.

## Automated Harness

Run from the source checkout after building the installer:

```powershell
.\scripts\smoke_installed_app.ps1 -AllowDirty
```

The script installs Talos into a temporary directory, launches the installed executable, waits for `/api/health`, confirms packaged build metadata, and writes `installed_app_smoke.json` into the release folder.

For the complete Arduino/Codex release gate, run the same script after performing the manual checks below:

```powershell
.\scripts\smoke_installed_app.ps1 -SkipBuild -ManualArduinoConfirmed
```

To run the installed-app Arduino/Codex gate without manual confirmation, use the automated harness:

```powershell
.\scripts\smoke_installed_app.ps1 -SkipBuild -AutoArduinoHarness
```

The harness creates a temporary Arduino sketch, launches the installed Talos app with isolated app data, configures the sketch through Talos APIs, saves a Talos editor change, stages a controlled Codex smoke patch, applies it into the Talos editor, confirms the Arduino workspace is not written before `Save File`, saves the applied change to the Arduino workspace, and runs sandbox verify before and after the patch. Set `TALOS_SMOKE_FQBN` before running the command if the default `arduino:avr:uno` profile is not installed locally.

For install/upgrade/uninstall lifecycle evidence, also run:

```powershell
.\scripts\smoke_app_lifecycle.ps1
```

This writes `app_lifecycle_smoke.json` and verifies isolated app-data preservation rules.

## Manual Arduino/Codex Checks

Use a saved Arduino sketch and keep Arduino IDE open during the test.

1. Launch the installed Talos app, not `desktop_app.py`.
2. Confirm Talos detects the open Arduino IDE sketch.
3. Select the sketch and confirm the board/profile are shown.
4. Open a source file from the Files list.
5. Use `Edit in Talos`, make a small safe change, then `Save File`.
6. Run `Verify Sandbox` and confirm the result is structured and copyable.
7. Ask Codex to make a small safe change.
8. Review the staged Codex diff, apply at least one file or hunk to the Talos editor, then save to Arduino IDE.
9. Run `Verify Sandbox` again and confirm it passes or reports expected diagnostics.
10. Confirm the source file in Arduino IDE reflects only the changes explicitly saved from Talos.

## Pass Criteria

- Talos was launched from the installed executable outside the repository.
- `/api/health` reported packaged mode and the expected app identity.
- Runtime state was written outside the install directory.
- Arduino IDE sketch detection worked.
- File edit, Save File, Verify Sandbox, Codex staged change, apply/save, and second verify were completed.
- `installed_app_smoke.json` records `status: passed`.

## Fail Conditions

- Talos only works when launched from the source checkout.
- The installed app writes user config into the install directory.
- Arduino IDE is not detected while a saved sketch is open.
- Codex can write directly to the Arduino sketch without Change Review and Save File.
- Verify runs against the original sketch folder instead of a sandbox copy.
