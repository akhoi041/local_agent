# Talos 0.5.5 Evidence

Date: 2026-07-18
Status: Stage 1 documentation taxonomy complete

## Evidence Policy

This is the single evidence file for Talos 0.5.5 Beta. Stage-level implementation details stay in `dev_notes/pipelines/TALOS_PIPELINE_055.md`; this file records only version-level proof that matters for release review.

## Stage 0 - Baseline And Safety

Result: complete.

### Baseline File Sizes

| File | Lines | Bytes | Baseline role |
| --- | ---: | ---: | --- |
| `ui/web_frontend/app.js` | 4017 | 168264 | Frontend state, API calls, workbench UI, editor/review/find, Arduino explorer, Codex panel, settings, menu/command wiring. |
| `talos/codex_bridge.py` | 1681 | 78184 | Codex runtime/session bridge, context package, message transport, review state, patch/action handling. |
| `ui/web_frontend/styles.css` | 4139 | 75777 | Theme tokens, workbench layout, editor, Codex panel, settings, menu, dialogs, buttons, scrollbars. |
| `talos/arduino.py` | 1492 | 61483 | Arduino discovery, workspace mapping, board/profile parsing, file operations, sandbox verify, target-contract helpers. |
| `talos/server.py` | 1029 | 48532 | Local HTTP routes, state payloads, request/response glue, endpoint orchestration. |
| `ui/web_frontend/index.html` | 764 | 45507 | Static app shell, workbench structure, help links, templates that have not yet moved to JS modules. |
| `talos/native_bridge.py` | 617 | 23414 | Python bridge and fallback boundary for native detection helpers. |
| `talos/codex_runtime.py` | 444 | 16826 | Runtime discovery, pinning, health checks, safe runtime metadata. |
| `talos/run_history.py` | 373 | 14394 | Run/event history persistence and filtering. |
| `talos/core.py` | 248 | 9788 | Shared config, paths, migration, app identity helpers. |
| `talos/checkpoints.py` | 152 | 6219 | Checkpoint and rollback support. |
| `desktop_app.py` | 170 | 6205 | Source/debug launcher and desktop bootstrap. |
| `talos/diagnostics.py` | 174 | 5935 | Diagnostics/support bundle data collection. |
| `talos/arduino_events.py` | 126 | 4322 | Arduino event watcher and change/event stream support. |
| `talos/client.py` | 101 | 3907 | Local client helpers. |
| `talos/performance.py` | 41 | 1409 | Timing/measurement helpers. |
| `talos/__init__.py` | 0 | 0 | Package marker. |

### Startup Path

- Source/debug startup remains `python desktop_app.py`.
- `desktop_app.py` loads app identity, sets Windows AppUserModelID on Windows, starts `ThreadingHTTPServer` on `127.0.0.1`, starts the Arduino event watcher, and opens the static frontend through pywebview.
- Packaged startup remains owned by the existing PyInstaller and installer scripts. Stage 0 did not rebuild installer artifacts.

### Verify Path

- User selects an Arduino sketch and active file in Talos.
- Talos resolves workspace/profile/FQBN, creates or reuses a sandbox copy, and runs `arduino-cli compile --fqbn ...`.
- The result is surfaced in Verify output, run history, context preview, and support evidence without making Arduino IDE the editor owner unless the user saves back.

### Known Slow Paths

- Large frontend files, especially `app.js` and `styles.css`, make UI changes risky and slow to reason about.
- `talos/arduino.py`, `talos/codex_bridge.py`, and `talos/server.py` still mix multiple responsibilities.
- Arduino/window/process detection is fast through native helpers but slower through PowerShell/WMIC fallbacks.
- Workspace scanning, hashing/cache-key generation, diff/hunk parsing, diagnostics export, support bundle generation, and `arduino-cli compile` remain measurable hot paths.
- Editor find/review behavior is still custom frontend logic and should be isolated before deeper feature work.

### UI Consistency Audit

The pre-0.5.5 visual baseline is usable, but it still mixes VS Code-style workbench patterns, GitHub-style dashboard/settings cards, and remnants of custom desktop chrome/menu behavior.

0.5.5 should not introduce a new look. It should normalize the current direction through shared primitives:

- button variants and icon buttons
- panel/card surfaces
- status badges and empty states
- toolbar/menu controls
- runtime/readiness states
- scrollbars
- editor/review/find patterns

Deferred beyond 0.5.5:

- true VS Code-grade custom titlebar and native snap parity
- full editor replacement
- deep product polish for additional target apps

### Regression Baseline

Full regression command:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check.ps1
```

Result:

```text
Native DLL build/export: OK
Native benchmark: OK
Unit tests: Ran 113 tests, OK
Release recovery smoke: OK
```

Native benchmark:

```text
native_window_rows: count=11 min=0.154ms median=0.25ms max=0.929ms
native_arduino_process_rows: count=10 min=6.141ms median=6.156ms max=6.426ms
fallback available: window/process/tool PowerShell and WMIC fallbacks
```

Release recovery smoke:

```text
scenario: restart-pending-review-external-change-guard
restored: 1
resolution: kept-external
workspace_content: external arduino edit
```

Known Stage 0 caveat: the regression suite was run from the active 0.5.5 working tree, not from a pristine release tree, because active architecture/UI changes were already present. A clean-tree rerun remains a Stage 6 release gate.

### Arduino/Codex No-Regression Reference

The no-regression workflow is:

1. Arduino IDE or Arduino workspace is available.
2. Talos detects or opens the selected sketch folder.
3. Talos resolves source files, board/profile, and active file.
4. Codex receives only the selected workspace/context package.
5. Codex changes are staged/reviewed in Talos.
6. User applies accepted changes, verifies sandbox, and saves back intentionally.
7. Rollback/recovery protects external Arduino edits and unfinished reviews.

Stage 0 used the automated recovery smoke as the safety proxy. Manual Arduino/Codex smoke remains required at release gate.

### Docs And Link Baseline

Runtime/in-app help links currently point at:

- `docs/TALOS_USER_GUIDE.md`
- `docs/TALOS_FIRST_RUN_CHECKLIST.md`
- `docs/TALOS_TROUBLESHOOTING.md`
- `docs/TALOS_DIAGNOSTICS.md`
- `docs/TALOS_INSTALL_LIFECYCLE.md`
- `docs/TALOS_UI_UX_CHECKLIST.md`
- `docs/TALOS_RECOVERY_GUIDE.md`
- `docs/TALOS_SUPPORT_DEBUG.md`
- `docs/RELEASE_NOTES.md`

Packaging and installer scripts still package or reference user/release docs such as `LICENSE`, `RELEASE_NOTES.md`, `EULA.md`, `PRIVACY.md`, `THIRD_PARTY_NOTICES.md`, `CODE_SIGNING.md`, `DISTRIBUTION_COPY.md`, `INSTALLED_APP_SMOKE_TEST.md`, and the Talos user/support guides.

Guardrail issue for later 0.5.5 stages: `scripts/pipeline_status.ps1` still defaults to `dev_notes/pipelines/TALOS_PIPELINE_050.md`. Stage 5 or Stage 6 should point active helper checks at the 0.5.5 pipeline before release.

### Rollback Instructions

- Documentation moves: restore old paths and update `docs/DOCS_INDEX.md`, `dev_notes/README.md`, `scripts/build_release.ps1`, `scripts/install_app.ps1`, `installer/talos.iss`, `ui/web_frontend/index.html`, and tests together.
- Python module splits: keep compatibility wrappers until tests pass; rollback by restoring the extracted logic and imports for the affected module only.
- Frontend split: keep the no-build static frontend; rollback by restoring `app.js`, `styles.css`, and `index.html` without adding a bundler requirement.
- Native-helper changes: keep Python fallback enabled; disable the native path if benchmark, export check, or regression fails.
- Release safety: do not commit, tag, push, or delete archived docs unless the user explicitly asks.

## Stage 1 - Documentation Taxonomy

Result: complete.

- User-facing, release, legal, support, and trust docs remain at stable `docs/` paths.
- `docs/DOCS_INDEX.md` is the packaged/user docs inventory and now marks 0.5.5 as the active pipeline.
- `dev_notes/README.md` is the internal planning source of truth for roadmap, pipelines, version evidence, and archive policy.
- Version evidence remains internal under `dev_notes/evidence/`, with one evidence file per release track.
- No stale planning note was moved to `dev_notes/archive/` in Stage 1 because the current planning files are still referenced by docs, tests, active pipelines, or release history.
- Release and install packaging continue to copy only required user/release docs from `docs/`; internal evidence is not packaged unless a future release explicitly opts in.
- `scripts/check_docs_links.ps1` verifies required docs plus discovered `docs/` and `dev_notes/` references in README, in-app help, scripts, installer files, tests, and planning notes.
- `scripts/check.ps1` now runs the docs-link checker before printing pipeline status.
- `scripts/pipeline_status.ps1` now defaults to `dev_notes/pipelines/TALOS_PIPELINE_055.md`.

Validation commands:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_docs_links.ps1
python -B -m unittest tests.test_desktop_app
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1
```

Validation result:

```text
Documentation link check OK: 32 repo doc references verified.
Unit tests: Ran 113 tests, OK.
Pipeline status: Stage 0 6/6, Stage 1 7/7, overall 13/46.
```

## Stage 2 - Python Boundary Cleanup

Result: complete.

- Added `talos/event_bus.py`, `talos/runtime_service.py`, and `talos/state_service.py` as focused service boundaries.
- `talos/server.py` now delegates transient events, Codex runtime readiness/status, and `/api/state` payload composition instead of owning those mechanics inline.
- Existing route/UI compatibility is preserved through server-level imports for callers that still reference old symbols.
- `talos/arduino.py` and `talos/codex_bridge.py` remain behavior-compatible public owners until deeper extraction stages, avoiding a risky broad rewrite.
- Added a Stage 0.5.5 boundary regression test covering service exports and absence of inline server definitions.

Validation commands:

```text
python -B -m unittest tests.test_desktop_app
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_docs_links.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1
```

Validation result:

```text
Unit tests: Ran 115 tests, OK.
Documentation link check OK: 32 repo doc references verified.
Pipeline status: Stage 0 6/6, Stage 1 7/7, Stage 2 7/7, Stage 3 9/9, overall 29/47.
git diff --check: no whitespace errors; Windows CRLF warnings only.
```

Validation result:

```text
Unit tests: Ran 114 tests, OK.
Documentation link check OK: 32 repo doc references verified.
Pipeline status: Stage 0 6/6, Stage 1 7/7, Stage 2 7/7, overall 20/47.
```

## Stage 3 - Frontend Module Split

Result: complete.

- `ui/web_frontend/app.js` now loads as a browser-native ES module.
- Shared frontend state, constants/config, and DOM/API helpers moved to `ui/web_frontend/js/state.js`, `ui/web_frontend/js/config.js`, and `ui/web_frontend/js/dom.js`.
- Theme, density, contrast, and scrollbar tokens moved to `ui/web_frontend/styles/tokens.css`; `styles.css` now imports token definitions before component/layout rules.
- `ui/web_frontend/js/README.md` records module ownership, future feature split targets, and no-build frontend guardrails.
- `index.html` remains structural and has no inline event-handler dependency that would break module scoping.
- The split is intentionally foundational rather than a full feature rewrite, keeping current UI behavior stable while making later Arduino/Codex/runtime panels easier to isolate.

Validation commands:

```text
python -B -m unittest tests.test_desktop_app
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_docs_links.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1
```
