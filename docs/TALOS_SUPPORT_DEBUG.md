# Talos Support Debug Workflow

This note explains how to collect enough local evidence to debug a Codex-Arduino issue without copying scattered panels by hand.

## Quick Flow

1. Select the Arduino sketch in Talos.
2. Open `Verify output` and run `Verify Sandbox`.
3. Open `History`.
4. Use the filter to narrow the view to `Verify`, `Codex turns`, `Saved changes`, `Conflicts`, `Rollbacks`, or release evidence.
5. Use `Copy Support` to copy a redacted support bundle.

## Support Bundle

`Copy Support` calls:

```text
GET /api/support_bundle?redact=1
```

The bundle includes:

- app and build metadata
- selected workspace summary
- Arduino environment profile and readiness
- latest verify result
- recent run history for the selected workspace
- included history filters and support scope metadata

Paths are redacted by default as `<workspace>`, `<app-root>`, `<bundle-root>`, `<app-data>`, and `<python-executable>`. Use the non-redacted API form only when exact local paths are needed for private debugging:

```text
GET /api/support_bundle?redact=0
```

## Review Before Sharing

Before sending a support bundle, check:

- [ ] The bundle says `"redacted": true`.
- [ ] Workspace paths appear as `<workspace>` or another redacted token.
- [ ] The latest verify result does not include private serial output or secrets.
- [ ] Recent history describes actions and statuses without unnecessary source code.
- [ ] You are comfortable sharing board/profile details such as FQBN, build flags, and library names.

Keep:

- App version/channel.
- Source vs packaged mode.
- Windows/Python platform details.
- Board/FQBN family.
- Verify status, timing, cache, memory, library, platform, and issue summary.
- Codex connection outcome and staged-review status when relevant.

Redact or remove:

- Full sketch source unless the bug is impossible to reproduce without it.
- Full Codex conversation content.
- Emails, tokens, serial numbers, network credentials, and private folder names.
- Absolute local paths when public issue reports are enough.

## Release Evidence

Use `Record Evidence` after a successful manual workflow check. For 0.5.5 Beta, release evidence should cover:

- simple `.ino` sketch
- multi-file `.h/.cpp` sketch
- AVR board verify
- ESP32 board verify
- conflict recovery
- reconnect/cancel behavior
- Codex runtime manager state
- architecture-health check result

The recorded evidence appears in the History panel under the `Release evidence` filter.

## 0.5.5 Architecture Notes For Support

When debugging a 0.5.5 issue, classify the owner before changing code:

- Arduino adapter: sketch discovery, source files, profile/FQBN, sandbox verify, and safe writes.
- Codex runtime manager: runtime discovery, pinning, health, app-server readiness, and blocked-send reasons.
- Local bridge/API: request routing, app state composition, support bundles, diagnostics, and run history.
- Native helper: Windows process/window discovery and other measured OS hot paths.
- Frontend workbench: command palette, status bar, editor/review UI, Codex panel, and settings.
- Packaging: bundled docs, native DLL, icons, installer, and app-data lifecycle.

0.5.5 is not a full rewrite away from Python. It documents and enforces the boundaries needed for the 0.6.x adapter contract and later shell/runtime migration.

## Related Guides

- `docs/TALOS_TROUBLESHOOTING.md`
- `docs/TALOS_USER_GUIDE.md`
- `docs/TALOS_FIRST_RUN_CHECKLIST.md`
- `docs/TALOS_RECOVERY_GUIDE.md`
