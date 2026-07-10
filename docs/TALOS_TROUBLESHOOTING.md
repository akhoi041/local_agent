# Talos Troubleshooting Guide

Use this guide when Talos does not detect Arduino IDE, cannot verify a sketch, loses Codex connection, or the installed app behaves differently from the source checkout.

## Arduino IDE Is Not Detected

Check:

- Arduino IDE 2.x is open.
- The sketch is saved to a real folder.
- The Arduino window title includes the sketch name.
- Talos is on the `Arduino` workspace and `Refresh` was pressed after Arduino IDE opened.

Try:

1. Click `Refresh`.
2. Focus Arduino IDE, then return to Talos.
3. Save the sketch in Arduino IDE.
4. Restart Talos.
5. If the problem remains, copy a support bundle from Talos after selecting any available workspace.

## Sketch Folder Is Missing

Talos can only inspect a sketch that has a folder on disk. New unsaved Arduino IDE sketches may not have a stable folder yet.

Try:

1. In Arduino IDE, use `File > Save`.
2. Confirm the folder contains the main `.ino` file.
3. Return to Talos and press `Refresh`.

## Board Or FQBN Is Missing Or Stale

Talos uses the selected board/profile for sandbox compile. If the board is missing or stale:

1. Select the correct board in Arduino IDE.
2. Return to Talos and press `Refresh`.
3. Confirm the `Board` field.
4. Use `Environment profile` if you need to save a specific board/profile for the sketch.
5. Run `Verify Sandbox` again.

## `arduino-cli` Was Not Found

Talos first tries to use Arduino IDE's bundled `arduino-cli`, then available CLI paths. If it cannot find one:

1. Confirm Arduino IDE is installed.
2. Launch Arduino IDE once so its backend resources are available.
3. Restart Talos.
4. If using a portable/custom Arduino install, install `arduino-cli` and add it to `PATH`.

## Verify Sandbox Failed

Verify Sandbox compiles a copied sketch folder. It does not upload to hardware and does not write build files into the real sketch folder.

Common causes:

- Wrong board/FQBN.
- Missing Arduino board package.
- Missing library.
- Build property typo.
- Code compile error.

What to copy:

- `Verify output > Copy Issues` for short issue text.
- `Verify output > Copy All` for full compile output.
- `History > Copy Support` for a redacted support bundle.

## Codex Is Disconnected

Codex remains the external reasoning layer. Talos only connects to the local Codex app-server.

Try:

1. Make sure Codex is authenticated in the environment where Talos is running.
2. Use `Reconnect` if Talos shows a reconnect option.
3. Start a new Codex thread if the old turn was interrupted.
4. Do not resend the same prompt repeatedly while a previous turn is still marked busy.

If a Codex turn was interrupted, Talos should not replay it automatically. Review the status text, then decide whether to send a new prompt.

## Installer Is Blocked Or Windows Shows An Unsigned Warning

Talos Pre-Alpha/Beta builds may be unsigned unless `docs/CODE_SIGNING.md` says otherwise.

Check:

- The release folder contains `signing_status.json`.
- The installer and executable hashes match `release_manifest.json`.
- The warning matches the documented unsigned Pre-Alpha/Beta state.

Do not bypass a warning if the file came from an unknown source or the hash does not match the release manifest.

## Installed App Differs From Source Run

The installed app runs from its install folder and uses per-user runtime data under `%LOCALAPPDATA%\T-Engine\Talos`.

Try:

1. Close all Talos windows.
2. Launch Talos from the installed shortcut.
3. Open Settings and verify the release/version/app-data details.
4. Use `scripts\smoke_installed_app.ps1` only from a development checkout.

## What To Send With A Bug Report

Prefer:

- Talos version and channel.
- Windows version.
- Arduino IDE version.
- Board name/FQBN family.
- Whether the sketch is simple `.ino` or multi-file `.h/.cpp`.
- `Copy Issues` or redacted `Copy Support`.
- The exact step where the failure happened.

Avoid sending:

- Full source code.
- Full Codex chat content.
- Account names, emails, or tokens.
- Unredacted local paths unless private debugging requires them.
