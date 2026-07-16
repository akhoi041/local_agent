# Talos

Talos is a local Windows control layer for Codex and Arduino IDE.

It does not replace Codex, Arduino IDE, or VS Code. Codex remains the reasoning layer through the locally authenticated Codex app-server, Arduino IDE remains the hardware/source owner, and Talos provides the bridge: sketch discovery, scoped file access, staged change review, sandbox verification, checkpoints, rollback, and packaging support.

## Current Scope

- Native Windows desktop shell via pywebview.
- Local HTTP API on `127.0.0.1`.
- Native C assisted Arduino IDE process/window discovery with Python fallback.
- Multiple open Arduino sketch detection with per-sketch board/profile state.
- Source discovery for `.ino`, `.h`, `.hpp`, `.c`, `.cpp`, `.S`, `.txt`, and `.md`.
- Scoped file read/write/delete constrained to the selected sketch folder.
- Codex app-server panel with thread history, context preview, staged changes, hunk review, conflict handling, and cancellation/reconnect controls.
- Sandbox compile using `arduino-cli compile --fqbn ...`, with cancellation, cache controls, structured diagnostics, and timing output.
- Checkpoints, guarded rollback, release evidence, installer smoke tests, and per-user runtime data under `%LOCALAPPDATA%\T-Engine\Talos`.

## Tool API

Default source run URL:

```text
http://127.0.0.1:8787
```

Important endpoints:

```text
GET  /api/health
GET  /api/state
GET  /api/arduino_context
GET  /api/arduino_events?since=...
GET  /api/arduino_profile
GET  /api/arduino_projects
GET  /api/arduino_file?path=Blink.ino
GET  /api/arduino_checkpoint?path=Blink.ino
POST /api/arduino_workspace
POST /api/arduino_file
POST /api/arduino_rollback
POST /api/arduino_delete
POST /api/arduino_verify
POST /api/arduino_verify_cancel
POST /api/arduino_verify_cache_clear
POST /api/arduino_profile
POST /api/release_evidence
GET  /api/codex_status
GET  /api/run_history
GET  /api/support_bundle?redact=1
POST /api/codex_message
POST /api/codex_reconnect
POST /api/codex_cancel
POST /api/codex_restore_reviews
POST /api/codex_discard_reviews
POST /api/codex_review_patch
POST /api/codex_apply_patch
POST /api/codex_apply_hunk
POST /api/codex_reject_hunk
POST /api/codex_apply_all
POST /api/codex_reject_all
POST /api/codex_keep_external
POST /api/codex_merge_draft
POST /api/codex_verify_patch
POST /api/codex_save_patch
POST /api/codex_reject_patch
POST /api/codex_thread
POST /api/codex_conversation
```

`/api/state` and `/api/health` expose both `app` identity and `build` metadata. `app` contains the product identity from `config/app_identity.json`; `build` reports source vs packaged mode, version/channel, release manifest data when installed, Python/platform details, app root, bundle root, and per-user app-data path.

Example write request:

```json
{
  "path": "Blink.ino",
  "content": "void setup() {}\nvoid loop() {}\n"
}
```

Example verify request:

```json
{
  "path": "C:\\Users\\You\\Documents\\Arduino\\Blink",
  "fqbn": "arduino:avr:uno"
}
```

## Project Files

```text
desktop_app.py          Desktop pywebview shell
talos/server.py         Local HTTP API server
talos/client.py         CLI bridge for terminal/debug use
talos/core.py           Thin Python bridge config and path utilities
talos/arduino.py        Arduino workspace and sandbox runner
talos/arduino_events.py Event-assisted Arduino window refresh
talos/checkpoints.py    Save checkpoints and guarded rollback
talos/codex_bridge.py   Codex staging, change review, and patch lifecycle bridge
talos/native_bridge.py  ctypes bridge to the native library
talos/run_history.py    Local verify and change activity history
native/talos_native.c   Native Windows app-discovery logic
ui/web_frontend/        Desktop UI assets
assets/icons/           Generated Talos Windows icon set
config/default_config.json Clean packaged configuration defaults
config/app_identity.json Product identity and packaging metadata
config/signing_policy.json Code-signing policy and unsigned-Beta rules
config/requirements.txt Build/runtime Python dependencies
scripts/build_app.ps1   Build one-file Windows executable
scripts/build_icons.py  Generate PNG and ICO app icons from talos_icon.png
scripts/build_native.ps1 Build the native Windows helper
scripts/benchmark_native.py Measure native detection and fallback availability
scripts/check.ps1       Rebuild and run the normal verification flow
scripts/clean_runtime.ps1 Remove disposable sandbox, staging, and test cache data
scripts/install_app.ps1 Install built app to LocalAppData and create desktop shortcut
scripts/launch_desktop.ps1 Open source app or installed app
scripts/pipeline_status.ps1 Show pipeline progress
scripts/build_release.ps1 Build a versioned release folder
scripts/build_installer.ps1 Build the Windows installer with Inno Setup
scripts/sign_release.ps1 Sign release artifacts or record an explicit unsigned Pre-Alpha/Beta
scripts/smoke_installer.ps1 Build, silently install, verify shortcuts, and uninstall the installer
scripts/smoke_installed_app.ps1 Launch installed Talos outside the repo and record smoke evidence
scripts/smoke_app_lifecycle.ps1 Validate isolated app-data upgrade/uninstall lifecycle evidence
scripts/distribution_checklist.ps1 Generate the final release distribution checklist
installer/talos.iss     Inno Setup installer definition
scripts/smoke_release_recovery.py Validate restart/recovery safety for pending Codex reviews
tests/                  Regression tests
docs/                   User, release, legal, support, and trust docs
dev_notes/              Internal roadmap, version pipelines, and stage evidence
```

Documentation inventory:

```text
docs/LICENSE                 Project license
docs/EULA.md                 Pre-Alpha/Beta packaged-app terms
docs/PRIVACY.md              Local data and Codex data-flow notes
docs/RELEASE_NOTES.md        Current release highlights and known limitations
docs/THIRD_PARTY_NOTICES.md  Dependency and tooling notices
docs/CODE_SIGNING.md         Signing policy, unsigned Pre-Alpha/Beta path, and verification commands
docs/DISTRIBUTION_COPY.md    Release copy explaining Talos as an Arduino-first Codex local bridge
docs/DOCS_INDEX.md           Navigation index and cleanup taxonomy for active, release, evidence, and version docs
docs/INSTALLED_APP_SMOKE_TEST.md Installed-app Arduino/Codex smoke-test checklist
docs/TALOS_USER_GUIDE.md     User-facing install, first-run, Arduino, Codex, verify, save, and recovery guide
docs/TALOS_FIRST_RUN_CHECKLIST.md New-tester checklist for simple `.ino`, multi-file sketches, Codex review, recovery, and support
docs/TALOS_TROUBLESHOOTING.md Common failure paths for Arduino detection, board/FQBN, `arduino-cli`, verify, Codex, installer, and installed-app issues
docs/TALOS_DIAGNOSTICS.md Local-only diagnostics, consent, redaction, event taxonomy, and export shape
docs/TALOS_INSTALL_LIFECYCLE.md Clean install, upgrade, uninstall, and app-data lifecycle validation
docs/TALOS_UI_UX_CHECKLIST.md UI/UX smoke checklist for window sizes, tools, Codex, verify, and settings states
docs/TALOS_RECOVERY_GUIDE.md Safe recovery path for Codex review, Arduino external edits, and rollback conflicts
docs/TALOS_SUPPORT_DEBUG.md Support bundle, run-history filters, and release-evidence workflow
```

Internal developer planning notes:

```text
dev_notes/roadmap/TALOS_ROADMAP.md              Version-level roadmap across Talos releases
dev_notes/pipelines/TALOS_PIPELINE_010.md       Completed 0.1.0 Beta first-version pipeline
dev_notes/pipelines/TALOS_PIPELINE_020.md       Completed 0.2.0 Beta pipeline
dev_notes/pipelines/TALOS_PIPELINE_030.md       Completed 0.3.0 Beta pipeline
dev_notes/pipelines/TALOS_PIPELINE_040.md       Active 0.4.0 Beta pipeline
dev_notes/pipelines/TALOS_PIPELINE_055.md       Planned 0.5.5 Beta architecture-slimming pipeline
dev_notes/evidence/TALOS_020_STAGE1_VALIDATION.md 0.2.0 Stage 1 validation evidence
dev_notes/evidence/TALOS_030_BASELINE.md       0.3.0 starting baseline and carry-over guarantees
```

User-writable runtime data is stored under `%LOCALAPPDATA%\T-Engine\Talos` by default. `config.json`, `run_history.json`, `checkpoints.json`, and `codex_reviews.json` live there, while disposable compile and Codex staging copies live under `sandbox\` and `staging\`. Set `TALOS_APP_DATA_DIR` only for tests or isolated debug runs.

Legacy source-tree runtime folders such as `.talos_sandbox/` and `.talos_staging/` are still cleaned if present, but Talos no longer relies on them for normal source or packaged runs.

Clean disposable runtime data when Talos is not running:

```powershell
.\scripts\clean_runtime.ps1
```

Use `-KeepStaging` only when you need to preserve an in-progress Codex change review.

## Codex Bridge CLI

Codex can call Talos from a VS Code terminal through `talos.client`.

```powershell
python -B -m talos.client state
python -B -m talos.client projects
python -B -m talos.client workspace "C:\Users\You\Documents\Arduino\Blink" --fqbn arduino:avr:uno
python -B -m talos.client context
python -B -m talos.client read Blink.ino
python -B -m talos.client write Blink.ino --from-file edited\Blink.ino
python -B -m talos.client verify
```

## Run From Source

Install runtime/build dependencies first if this checkout has no `.venv`:

```powershell
python -m pip install -r config\requirements.txt
```

```powershell
python -B desktop_app.py
```

Or:

```powershell
.\scripts\launch_desktop.ps1
```

To run only the HTTP server:

```powershell
python -B -m talos.server --port 8787
```

## Build And Install

Install dependencies:

```powershell
python -m pip install -r config\requirements.txt
```

Build the native C helper when a C compiler is available:

```powershell
.\scripts\build_native.ps1
```

Regenerate app icons after changing `talos_icon.png`:

```powershell
python -B scripts\build_icons.py
```

Run the normal project verification flow:

```powershell
.\scripts\check.ps1
```

This rebuilds the native DLL, checks that the current Python bridge can load the expected native exports, benchmarks native detection, runs the regression tests, validates restart/recovery safety for pending Codex reviews, and prints the pipeline status.

Run the manual Arduino MVP smoke test before treating Arduino support as ready:

```text
docs\ARDUINO_SMOKE_TEST.md
```

Build:

```powershell
.\scripts\build_app.ps1
```

Build a versioned release folder from a clean tree:

```powershell
.\scripts\build_release.ps1
```

For local validation before committing, use `-AllowDirty`; do not use that flag for distribution builds.

Build the Windows installer:

```powershell
.\scripts\build_installer.ps1
```

The installer is written into the same versioned release folder and creates a Start Menu shortcut by default. Desktop shortcut creation is optional in the installer wizard.
Installed builds include `release_manifest.json` beside `Talos.exe` so the UI and API can show release/build metadata.

Record the current Pre-Alpha/Beta as deliberately unsigned while the publisher certificate is not configured:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\<versioned-release-folder> -AllowUnsignedBeta
```

Sign release artifacts after a certificate is available:

```powershell
.\scripts\sign_release.ps1 -ReleaseDir releases\<versioned-release-folder> -CertificateThumbprint "<thumbprint>"
```

Smoke-test the installer install/uninstall behavior:

```powershell
.\scripts\smoke_installer.ps1
```

Validate isolated app-data lifecycle behavior:

```powershell
.\scripts\smoke_app_lifecycle.ps1
```

Smoke-test the installed app outside the source checkout:

```powershell
.\scripts\smoke_installed_app.ps1 -AllowDirty
```

After completing the Arduino/Codex manual checks in `docs\INSTALLED_APP_SMOKE_TEST.md`, record the full pass:

```powershell
.\scripts\smoke_installed_app.ps1 -SkipBuild -ManualArduinoConfirmed
```

Generate the final distribution checklist:

```powershell
.\scripts\distribution_checklist.ps1 -RequireReady
```

The checklist is written to the versioned release folder and summarizes artifact names, SHA-256 hashes, signing status, installer install/uninstall evidence, installed-app smoke evidence, app-data lifecycle evidence, rollback/recovery coverage, and known limitations.

Install locally:

```powershell
.\scripts\install_app.ps1
```

## Arduino Requirements

For sandbox verify, install `arduino-cli` and make sure it is available in `PATH`.

Talos does not compile in your real sketch folder. It copies the sketch into `%LOCALAPPDATA%\T-Engine\Talos\sandbox\arduino\...` and compiles the copy.
