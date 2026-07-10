# Talos User Guide

Talos is a local Windows control layer between Codex and Arduino IDE. Arduino IDE remains the owner of your real sketch files, board selection, upload flow, and serial monitor. Codex remains the reasoning layer. Talos connects the two by detecting the open Arduino sketch, showing the selected workspace, staging Codex changes, compiling sandbox copies, and saving changes only when you choose to write them.

## Before You Start

- Install Arduino IDE 2.x.
- Open at least one Arduino sketch in Arduino IDE.
- Select the intended board in Arduino IDE.
- Make sure the sketch has a real sketch folder when you want Talos to read source tabs.
- Install the board package and libraries required by the sketch before running Verify Sandbox.

Talos can inspect `.ino`, `.h`, `.hpp`, `.c`, `.cpp`, `.S`, `.txt`, and `.md` files inside the selected sketch folder.

## Launch Talos

Run Talos from the installed shortcut or from source with:

```powershell
python -B desktop_app.py
```

The Arduino workspace opens from the `Arduino` navigation item. Use `Refresh` if Arduino IDE was opened after Talos.

## Select An Arduino Sketch

1. Open your sketch in Arduino IDE.
2. In Talos, go to `Arduino`.
3. Choose the sketch from `Open sketches`.
4. Confirm the `Sketch folder` and `Board` fields.
5. Use `Save Workspace` if you adjusted the detected folder, board, or profile.

If no sketch appears, keep Arduino IDE open, make sure the sketch is saved to a folder, and press `Refresh`.

## Board And Profile

Talos reads the visible Arduino IDE board when possible. The `Board` field shows the board name or FQBN used for sandbox compile. Use `Environment profile` for optional per-sketch details:

- Serial port.
- Baud rate.
- Build flags.
- Build properties.
- Library notes.

The profile is stored per sketch so switching sketches does not mix board/profile data.

## Inspect Files

The `Files` section lists the source files in the sketch folder. Select a file to inspect it in the central pane.

By default, Talos is in review mode. Arduino IDE owns the saved sketch. Talos only writes to the real sketch folder when you explicitly use `Save` or `Save + Verify`.

## Edit In Talos

Use `Edit` when you want to edit the selected file in Talos.

- `Save` writes the Talos editor draft to the real Arduino sketch file.
- `Save + Verify` writes the draft, then runs sandbox verify.
- `Undo` rolls back the most recent Talos save when the checkpoint is still valid.

If Arduino IDE or another editor changes the same file after Talos opened it, Talos should warn or block unsafe overwrite paths.

## Verify Sandbox

`Verify Sandbox` compiles a copied sketch folder, not the real sketch folder. This protects your working sketch from generated build files or failed experiments.

Use it when:

- You selected a new sketch.
- Codex proposed a change.
- You edited a file in Talos.
- Arduino IDE board/profile changed.

The current output appears in `Verify output`. Previous runs are available in `History`.

## Use Codex

Open the Codex panel and choose a suggested prompt or write your own. Talos sends Codex a scoped context package:

- Selected workspace.
- Workspace file map.
- Active file.
- Latest verify summary.
- Profile readiness.

Codex changes are staged for review. They do not write directly to Arduino IDE. Review the proposed diff, apply it to the Talos editor if it is acceptable, then use `Save` or `Save + Verify` when you want to write it to the real sketch folder.

## Recovery And Conflicts

If Arduino IDE and Talos both changed the same file, keep the Arduino version unless you are sure the Talos draft is newer. Use:

- `Keep Arduino Version` to preserve the real file.
- `Draft Merge` when you want a manual merge draft.
- `Reject Codex` when the proposed change is no longer relevant.

See `docs/TALOS_RECOVERY_GUIDE.md` for the safest conflict and rollback workflow.

## Support Bundle

If something fails, use `Copy Support` from the output/history area. Talos creates a redacted support bundle for debugging. Review it before sending it to another person.

Do not send full source code, full Codex chat content, account details, or unredacted local paths unless you intentionally choose to share them.

## Local Diagnostics

Diagnostics are disabled by default. If you enable local product diagnostics in Settings, Talos stores redacted product-health events on your machine only. Version 0.4.0 does not upload diagnostics to a server.

Use `Preview Export` before sharing diagnostics. The export is designed to avoid sketch source code, Codex chat content, account identifiers, and raw absolute local paths.

## Common Next Steps

- For a first test, use `docs/TALOS_FIRST_RUN_CHECKLIST.md`.
- For Arduino smoke testing, use `docs/ARDUINO_SMOKE_TEST.md`.
- For recovery, use `docs/TALOS_RECOVERY_GUIDE.md`.
- For support/debug reports, use `docs/TALOS_SUPPORT_DEBUG.md`.
- For local diagnostics, use `docs/TALOS_DIAGNOSTICS.md`.
- For release notes and known limitations, use `docs/RELEASE_NOTES.md`.
