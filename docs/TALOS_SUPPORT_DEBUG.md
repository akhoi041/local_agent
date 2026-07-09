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

Paths are redacted by default as `<workspace>`, `<app-root>`, `<bundle-root>`, `<app-data>`, and `<python-executable>`. Use the non-redacted API form only when exact local paths are needed for private debugging:

```text
GET /api/support_bundle?redact=0
```

## Release Evidence

Use `Record Evidence` after a successful manual workflow check. For 0.3.0 Beta, release evidence should cover:

- simple `.ino` sketch
- multi-file `.h/.cpp` sketch
- AVR board verify
- ESP32 board verify
- conflict recovery
- reconnect/cancel behavior

The recorded evidence appears in the History panel under the `Release evidence` filter.
