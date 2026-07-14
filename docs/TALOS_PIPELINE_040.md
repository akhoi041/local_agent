# Talos Pipeline - Version 0.4.0 Pre-Alpha

## Final Goal For 0.4.0

Talos 0.4.0 Pre-Alpha should turn the completed 0.3.0 Codex-Arduino workflow into a product-ready package that a broader tester can install, understand, troubleshoot, and report issues from.

This version is still Arduino-first. It is not the 1.0.0 Alpha and does not add MATLAB or another app target.

```text
0.4.0 Pre-Alpha = product readiness, documentation, supportability, opt-in feedback, UI polish, clean install confidence.
```

## Baseline

```text
Roadmap: docs/TALOS_ROADMAP.md
Previous completed pipeline: docs/TALOS_PIPELINE_030.md
Current active pipeline: docs/TALOS_PIPELINE_040.md
Target version: 0.4.0 Pre-Alpha
Starting branch: develop/0.4.0
```

Talos 0.3.0 Beta already completed the mature Codex-Arduino loop: context preview, task state, staged change review, verify-before-save, support bundle, run-history filters, release artifacts, installer smoke, installed-app smoke, and manual Arduino smoke confirmation. Version 0.4.0 should preserve those guarantees while improving product readiness and external tester experience.

### 0.4.0 Baseline Note

Carry-over guarantees from 0.3.0:

- Arduino-first workflow remains the only product target.
- Codex remains the external reasoning layer; Talos remains the local bridge and safety layer.
- Sketch detection, board/profile context, staged change review, verify-before-save, rollback, run history, support bundle, installer smoke, and installed-app smoke remain protected behavior.
- Release history files for 0.1.0, 0.2.0, and 0.3.0 are frozen references and should not be edited for new 0.4.0 implementation work.

0.4.0 release-readiness risks:

- External testers need clearer docs, first-run guidance, troubleshooting, and recovery instructions.
- Support data must be useful without silently collecting sketch source, Codex chat content, or sensitive local identifiers.
- UI/UX needs a more polished VS Code-inspired workbench appearance and workflow structure. GitHub-style polish is now limited to quiet settings/help documentation surfaces, not the main coding workspace.
- Clean install, upgrade, uninstall, signing status, and distribution wording must be explicit before public handoff.

## 0.4.0 Release Criteria

Talos 0.4.0 Pre-Alpha is ready only when these are true:

- A new tester can install Talos, understand what it does, and run the Arduino workflow without reading the source code.
- User-facing docs explain install, first run, Arduino workflow, Codex workflow, support bundle, recovery, uninstall, and known limitations.
- Troubleshooting guidance covers common failures: Arduino IDE not detected, board/FQBN missing, `arduino-cli` missing, Codex disconnected, verify failed, installer blocked, and unsigned Beta warnings.
- Product feedback is privacy-aware: diagnostics are opt-in, redacted, previewable by the user, and useful for development without collecting sketch source, Codex chat content, account identifiers, or full local paths by default.
- UI/UX is polished enough for broader testers: VS Code-inspired workbench structure and color hierarchy, clear active states, better theme/appearance controls, responsive layouts, a compact activity-bar navigation model, and tool actions grouped by workflow instead of scattered by implementation detail.
- Release artifacts include current 0.4.0 identity, release notes, legal/support docs, installer evidence, installed-app evidence, and distribution checklist.
- Clean install/uninstall validation works on a fresh Windows profile, VM, or documented equivalent clean app-data scenario.
- Code-signing state is either fully configured or explicitly documented as unsigned Pre-Alpha/Beta with user-facing warnings.
- 0.3.0 functionality remains intact: Arduino detection, file scoping, Codex staged review, verify-before-save, rollback, history, and support bundle.

## Non-Goals For 0.4.0

- No MATLAB or second-app integration.
- No hardware upload or serial-monitor commercial guarantee.
- No auto-update infrastructure.
- No public plugin SDK or marketplace.
- No AI model hosting inside Talos; Codex remains the external reasoning layer.
- No hidden telemetry or remote analytics by default.
- No raw sketch source, Codex chat content, account identifier, or unredacted local path collection unless the user explicitly previews and exports it for support.
- No large architectural UI rewrite; UI changes should polish the existing Arduino-first workspace instead of replacing the product model.

## Progress Rules

- Keep `docs/TALOS_PIPELINE_010.md`, `docs/TALOS_PIPELINE_020.md`, and `docs/TALOS_PIPELINE_030.md` as frozen history records.
- Track all 0.4.0 work in this file. During 0.4.0 development, project planning and helper checks should default to `docs/TALOS_PIPELINE_040.md`.
- Every completed 0.4.0 task must update this file.
- Do not add MATLAB or unrelated app targets to this pipeline.
- Use the pipeline status checker with this file:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pipeline_status.ps1 -Path docs\TALOS_PIPELINE_040.md
```

## Stage 0 - 0.4.0 Pipeline Setup

Purpose: establish 0.4.0 as the active product-readiness pipeline.

- [x] Preserve the completed 0.3.0 Beta pipeline as `docs/TALOS_PIPELINE_030.md`.
- [x] Create a dedicated 0.4.0 Pre-Alpha pipeline as `docs/TALOS_PIPELINE_040.md`.
- [x] Update `docs/TALOS_ROADMAP.md` so 0.3.0 is complete and 0.4.0 is active.
- [x] Decide whether project docs and helper scripts should default to pipeline 0.4.0 during development.
- [x] Add a short 0.4.0 baseline note listing carry-over guarantees and release-readiness risks.

Exit condition: 0.4.0 has its own active pipeline, roadmap state is current, and no 0.3.0 release-history file needs to be edited for new implementation work.

## Stage 1 - 0.3.0 Baseline Lock

Purpose: make sure 0.4.0 starts from the completed 0.3.0 release instead of regressing Codex-Arduino workflow maturity.

- [x] Run `scripts/check.ps1` and record the result.
- [x] Run pipeline status for `docs/TALOS_PIPELINE_040.md`.
- [x] Confirm 0.3.0 release artifacts remain available for comparison: executable, installer, signing status, installer smoke, installed-app smoke, and distribution checklist.
- [x] Confirm `develop/0.4.0` starts from GitHub `main` after the 0.3.0 merge.
- [x] Review dirty/uncommitted files and separate 0.4.0 work from release artifacts or local build output.

Stage 1 validation notes:

- `scripts/check.ps1` passed on 2026-07-09: native DLL built, native exports loaded, native detection benchmark passed, recovery smoke passed, and 94 unit tests passed.
- `scripts/check.ps1` still reports the completed 0.3.0 pipeline by default; the dedicated 0.4.0 status check below is the active 0.4.0 planning source.
- `docs/TALOS_PIPELINE_040.md` status after Stage 0: Stage 0 is 5/5 and overall progress was 5/58 before this Stage 1 update.
- 0.3.0 comparison artifacts are present under `releases/Talos-0.3.0-beta`, including `Talos-0.3.0-beta.exe`, `Talos-0.3.0-beta-setup.exe`, `DISTRIBUTION_CHECKLIST.md`, `installer_smoke.json`, `installed_app_smoke.json`, `signing_policy.json`, and `signing_status.json`.
- Git baseline is aligned: `develop/0.4.0`, `origin/develop/0.4.0`, and `origin/main` all point to `f145421`, the merge commit for 0.3.0 release PR #6.
- Dirty-state review: current 0.4.0 planning changes are `docs/TALOS_ROADMAP.md` and `docs/TALOS_PIPELINE_040.md`; `native/bin/talos_native.dll` is build output regenerated by the Stage 1 check and should be treated separately from source edits.

Exit condition: automated checks pass, 0.3.0 artifacts are available, and the repository has a clean 0.4.0 starting point.

## Stage 2 - User Guide And First-Run Experience

Purpose: make Talos understandable to a new Arduino tester without source-code knowledge.

- [x] Add a user guide covering install, launch, Arduino IDE prerequisites, sketch selection, board/profile, Verify Sandbox, Codex panel, Save & Verify, rollback, and support bundle.
- [x] Add a first-run checklist for a new tester using one simple `.ino` sketch and one multi-file `.h/.cpp` sketch.
- [x] Add in-app links or references to user guide, support debug workflow, release notes, and recovery guide where practical.
- [x] Clarify wording in the UI around Arduino IDE ownership, Talos review mode, and when files are actually written.
- [x] Add regression/marker coverage for new docs or UI references so product help does not silently disappear.

Stage 2 implementation notes:

- Added `docs/TALOS_USER_GUIDE.md` as the user-facing guide for launch, Arduino prerequisites, sketch selection, board/profile, file inspection, Edit in Talos, Verify Sandbox, Codex staged review, recovery, and support bundle.
- Added `docs/TALOS_FIRST_RUN_CHECKLIST.md` for first-time tester validation across simple `.ino`, multi-file `.h/.cpp`, Codex review, recovery, and support-report flows.
- Added a `Help` panel in Settings that points to the user guide, first-run checklist, recovery guide, support debug guide, and release notes.
- Packaged the new user-facing docs through `scripts/build_release.ps1`, `scripts/install_app.ps1`, and installer smoke verification.
- Added regression markers in `tests/test_desktop_app.py` so the new docs, Settings references, and packaging paths cannot disappear silently.

Exit condition: a new tester can run the expected Arduino/Codex workflow from documentation alone.

## Stage 3 - Troubleshooting And Support Readiness

Purpose: reduce support friction for the most common failure paths.

- [x] Add a troubleshooting guide for Arduino IDE detection, missing sketch folder, stale board/FQBN, missing `arduino-cli`, verify failures, Codex disconnected, and installer/unsigned warnings.
- [x] Add a support bundle review checklist explaining what to redact, what to keep, and how to attach it to an issue/report.
- [x] Improve support bundle metadata if needed: app identity, build mode, OS/platform, install mode, active workspace, profile readiness, latest verify summary, and recent history filters.
- [x] Add one-click or documented copy paths for release evidence, verify output, and support bundle.
- [x] Add tests for support bundle schema stability and redaction safety.

Stage 3 implementation notes:

- Added `docs/TALOS_TROUBLESHOOTING.md` for Arduino IDE detection, missing sketch folders, stale board/FQBN, missing `arduino-cli`, verify failures, Codex disconnected, unsigned installer warnings, installed-app differences, and useful bug-report contents.
- Expanded `docs/TALOS_SUPPORT_DEBUG.md` with a review-before-sharing checklist, what to keep, what to redact, related guide links, and the documented support-bundle API path.
- Added `support_scope` and `included_history_filters` to support bundles so reports state their privacy/default scope, history limit, and whether source/chat content is intentionally included. The 0.4.0 default remains redacted and source/chat-free.
- Added the troubleshooting guide to Settings Help, README, release packaging, local install packaging, and installer smoke verification.
- Added regression markers for the troubleshooting guide, support metadata, redaction behavior, Help links, and packaged-doc paths in `tests/test_desktop_app.py`.

Exit condition: a tester can produce a useful issue report without manually collecting scattered logs or leaking unnecessary local paths.

## Stage 4 - Opt-In Diagnostics And Product Feedback

Purpose: let Talos learn from broader testers without silently collecting sensitive project data.

- [x] Define the 0.4.0 diagnostics taxonomy: app version, install mode, Windows version, Arduino detection state, board/profile readiness, verify timing/status, Codex connection state, support bundle status, crash/restart markers, and installer/uninstaller outcomes.
- [x] Define explicit data minimization rules: no sketch source, no Codex chat content, no account/email, no project names, no raw absolute paths, and no full command output unless the user previews and exports it.
- [x] Add an opt-in settings flow and privacy copy for diagnostics/product feedback, with collection disabled until the user chooses it.
- [x] Add a local diagnostics/export shape that redacts sensitive values and lets the user preview the payload before attaching it to a report.
- [x] Add tests or schema checks for consent state, redaction behavior, diagnostics schema stability, and disabled-by-default behavior.

Stage 4 implementation notes:

- Added `talos/diagnostics.py` with schema v1, allowed product-health event taxonomy, local JSON storage, sensitive-key filtering, workspace hashing, sketch-extension reduction, and redacted export generation.
- Added disabled-by-default diagnostics settings to default config and runtime config normalization; 0.4.0 keeps remote upload unavailable.
- Added `/api/diagnostics_event` and `/api/diagnostics_export`, plus safe verify/support-event recording only when diagnostics are enabled.
- Added Settings UI for local diagnostics consent, privacy copy, preview, and copy-export actions.
- Added `docs/TALOS_DIAGNOSTICS.md` and linked it from README, Privacy, User Guide, Help UI, release packaging, installer copy, and installer smoke checks.
- Added regression coverage for default-off behavior, consent state, redaction behavior, export policy, UI markers, and packaged diagnostics documentation.

Exit condition: Talos can produce useful product-development evidence from testers through explicit consent, while preserving the local/private nature of Arduino sketches and Codex conversations.

## Stage 5 - Clean Install, Upgrade, And Uninstall Validation

Purpose: validate that Talos behaves like a real app outside the development checkout.

- [x] Define a clean-profile validation procedure using a fresh Windows profile, VM, or isolated `TALOS_APP_DATA_DIR` substitute.
- [x] Validate first install, launch, health check, packaged metadata, Start Menu shortcut, optional Desktop shortcut, and clean uninstall.
- [x] Validate upgrade behavior from 0.3.0 app-data to 0.4.0 app-data without silently discarding settings, profiles, history, checkpoints, or pending review state.
- [x] Validate uninstall behavior: installer-owned files removed, user runtime data policy documented, no writable config left inside install directory.
- [x] Record install/upgrade/uninstall evidence in release docs or generated evidence files.

Stage 5 implementation notes:

- Added `docs/TALOS_INSTALL_LIFECYCLE.md` to define clean-profile, install, launch, upgrade, uninstall, and app-data evidence expectations.
- Added `scripts/smoke_app_lifecycle.ps1`, which uses isolated `TALOS_APP_DATA_DIR`, seeds 0.3.0-style user state, verifies Talos core can load/save it, confirms config/history/checkpoints/reviews/diagnostics/profiles/staging/sandbox data are preserved, and writes `app_lifecycle_smoke.json`.
- Updated `scripts/smoke_installer.ps1` to validate the optional Desktop shortcut with `/TASKS=desktopicon`, Start Menu shortcuts, installed docs, no writable runtime config inside the install directory, and silent uninstall cleanup.
- Updated release packaging, local install packaging, Settings Help, README, and installed-app smoke documentation so lifecycle validation is visible to testers.
- Updated `scripts/distribution_checklist.ps1` so `app_lifecycle_smoke.json` is part of the release-ready gate alongside manifest, signing, installer smoke, and installed-app smoke.
- Ran `scripts/smoke_app_lifecycle.ps1 -AllowDirty`; it passed and wrote evidence to the current identity release folder. App identity remains `0.3.0 Beta` until the Stage 9 release gate, where the pipeline explicitly bumps identity to `0.4.0 Pre-Alpha`.
- Added regression tests for lifecycle documentation, script evidence markers, packaged lifecycle docs, optional Desktop shortcut smoke coverage, and distribution checklist gating.

Exit condition: installed Talos can be trusted on a clean tester machine and the app-data lifecycle is explicit.

## Stage 6 - VS Code-Inspired UI/UX And Structural Tool Ergonomics

Purpose: make Talos feel like a polished developer product, not only a functional bridge, and keep the Arduino/Codex workspace structurally simple at real desktop sizes.

- [x] Define a VS Code-inspired visual refresh for Talos workbench panels: titlebar, activity bar, Explorer, editor, bottom output panel, and Codex column each get their own role-based surface, spacing, borders, selected states, focus states, contrast, and light/dark/neutral theme consistency.
- [x] Redesign Settings/Appearance into a richer product surface with theme previews, system-sync option, saved theme behavior, contrast preference, and editor display preferences where practical.
- [x] Rework workspace structure around three primary regions: navigation rail, Arduino context/files, and the main workbench; treat Codex as a real resizable workbench column when opened, not as a floating support overlay.
- [x] Keep the selected source file highlighted in Files instead of relying on a large editor tab, so toolbar space is reserved for actions.
- [x] Keep Verify/History as the bottom workbench panel, let the Arduino activity button toggle the Explorer/context panel, and reserve the right workbench column for Codex conversations only when the user opens Codex.
- [x] Convert the navigation rail from a pin/unpin sidebar into a compact VS Code-style activity bar with persistent icons and no expandable blank area.
- [x] Rework non-workspace screens into product surfaces: Server becomes a readiness dashboard with quick actions and collapsed developer details, Logs becomes a filtered event stream with empty states, and Settings uses grouped sections.
- [x] Optimize tool ergonomics for core workflows: Verify Sandbox, Save File, Save & Verify, Rollback, Codex context, support bundle, diagnostics export, history filters, and copy actions.
- [x] Review UI behavior at normal, maximized, and narrow desktop window sizes; keep splitters, panels, action bars, and Codex side panel responsive without overflow.
- [x] Add screenshot/manual checklist coverage for the main UI states: no sketch, selected sketch, review mode, edit mode, verify passed/failed, Codex connected/disconnected, diagnostics disabled/enabled, and settings appearance.
- [x] Split the color system by workbench role so titlebar, activity bar, Explorer, editor, output/terminal, and Codex side panel have distinct but harmonious VS Code-like surfaces.
- [x] Replace the crowded always-visible editor command row with a VS Code-style top menu bar for secondary actions, grouped by File, Edit, Selection, View, Go, Run, Codex, and Help.
- [x] Keep Codex as a real right-side workbench column with its own history, context preview, composer, and resize behavior instead of treating it as a small helper tab.
- [x] Add a compact Command Palette and titlebar command center so advanced actions are searchable, visible, and discoverable without adding more permanent toolbar buttons.
- [x] Add a bottom Status Bar for workspace, active file, board, verify, and Codex state so important context remains visible without opening extra panels.
- [x] Keep a VS Code-style custom frame that follows Talos themes, contains the menu bar, command center, and window controls, while avoiding the earlier custom Snap Layout flyout that made window behavior feel noisy.

Stage 6 implementation notes:

- Added a richer Settings/Appearance surface with theme preview cards, system theme sync, high-contrast toggle, editor font-size preference, and editor density preference.
- Added local UI preference persistence for system theme sync, high contrast, editor font size, and editor density without changing the 0.4.0 backend config contract.
- Refined CSS tokens for mono font, editor font size, editor line height, high contrast borders, selected states, and theme preview cards across light, dark, and neutral themes.
- Added VS Code-like workbench surface tokens so titlebar, activity bar, Explorer, toolbar, editor, output/terminal, and Codex panels no longer share one flat application background.
- Improved tool ergonomics by making editor action groups stay on one polished row with internal horizontal scrolling at constrained widths, preventing Verify, Save, Save & Verify, Rollback, Cancel, Clear, and Codex from wrapping into noisy multi-row layouts.
- Replaced the crowded editor toolbar with a workflow-first command model: the editor keeps only primary in-context actions, while `File`, `Edit`, `Selection`, `View`, `Go`, `Run`, `Codex`, and `Help` live in a VS Code-style top menu bar that closes after selection or outside click.
- Expanded the menu bar into a real Talos command surface rather than a decorative dropdown: line copy/cut/comment, line selection, move/duplicate line, verify/history navigation, support bundle, Codex context, reconnect, and workspace navigation now live in predictable groups.
- Strengthened active-file selection cues in the Files panel so the selected source file is visible without relying on a large editor tab.
- Simplified the workbench structure so Codex behaves as a resizeable right column when opened instead of a floating overlay, keeping the editor, verify output, and Codex conversation in predictable regions.
- Kept Explorer as the Arduino context/file surface, made it toggleable from the Arduino activity button, and kept Verify/History as the bottom workbench panel so the main workspace reads closer to VS Code.
- Removed the pin/unpin navigation mode and replaced the wide rail with a fixed icon activity bar, reducing dead space and making the app feel closer to VS Code.
- Restored the Talos custom chrome so the frame behaves like a VS Code-style workbench titlebar: theme-aware, compact, and able to host the menu bar, command center, and minimize/maximize/close controls in one product surface.
- Removed the Talos Snap Layout flyout from the custom frame; window controls remain in the themed frame, but snap layout simulation is intentionally deferred instead of being faked with an unreliable HTML flyout.
- Reworked Server, Logs, and Settings so they present tester-ready status, actions, filters, and grouped information instead of raw debug-only panels.
- Added a VS Code-style Command Palette (`Ctrl+Shift+P`) plus an always-visible titlebar command center for workspace, editor, view, run, Codex, and support commands, with keyboard navigation and disabled-state awareness.
- Added a bottom Status Bar with clickable workspace, active file, board, verify, and Codex state shortcuts so users can jump back to the right surface quickly.
- Added `docs/TALOS_UI_UX_CHECKLIST.md` for manual/screenshot coverage across window sizes, Arduino states, editor/review states, verify/history states, Codex states, and Settings/Appearance.
- Added the UI/UX checklist to Settings Help, release packaging, local install packaging, installer smoke coverage, README, and regression tests.

Exit condition: a tester can understand the available tools visually, use common actions with fewer clicks, and resize Talos without broken layout, cramped controls, or unnecessary permanent columns.

## Stage 7 - Signing, Security, Privacy, And Distribution Copy

Purpose: make the release posture honest and user-facing.

- [ ] Revisit `config/signing_policy.json` and decide whether 0.4.0 remains explicitly unsigned or moves to a signed artifact path.
- [ ] Update `docs/CODE_SIGNING.md` with 0.4.0 status, user verification steps, and expected Windows warning behavior.
- [ ] Review `docs/PRIVACY.md`, `docs/EULA.md`, and `docs/THIRD_PARTY_NOTICES.md` for 0.4.0 accuracy.
- [ ] Add privacy documentation for opt-in diagnostics, local support export, redaction guarantees, disabled-by-default behavior, and what data Talos never collects silently.
- [ ] Add distribution copy that clearly states Talos is Arduino-first, Codex-authenticated, local-bridge software, not an embedded AI model.
- [ ] Add a release-readiness check that refuses final checklist generation when signing/unsigned status is missing.

Exit condition: distribution materials clearly explain trust, privacy, limitations, and signing status.

## Stage 8 - Product Polish And Performance Guardrails

Purpose: remove rough edges before the broader Pre-Alpha release.

- [ ] Confirm detection, verify, Codex polling, and history refresh do not spawn disruptive PowerShell/CMD windows during normal use.
- [ ] Add or update timing thresholds for native detection, verify cache, support bundle generation, and installed-app health.
- [ ] Add or update timing thresholds for diagnostics export and UI refresh paths introduced in 0.4.0.
- [ ] Run folder/code cleanup to remove stale generated files, unused docs, dead code, and obsolete pipeline references.
- [ ] Optimize repeated tool actions so Verify Sandbox, Save & Verify, support export, and diagnostics preview report progress clearly and do not block the main UI.
- [ ] Add regression tests for any product-readiness polish fixes.

Exit condition: Talos feels stable enough for external testers and does not disrupt normal Windows desktop use.

## Stage 9 - 0.4.0 Release Gate

Purpose: package and validate the completed 0.4.0 Pre-Alpha.

- [ ] Run full automated checks.
- [ ] Run manual Arduino/Codex smoke matrix for simple `.ino`, multi-file `.h/.cpp`, AVR board, ESP32 board, conflict recovery, reconnect/cancel, support bundle, and troubleshooting docs.
- [ ] Run diagnostics/privacy smoke: disabled-by-default, opt-in enable/disable, redacted export preview, and support-report attachment path.
- [ ] Run UI/UX smoke across light, dark, neutral, normal window, maximized window, narrow window, and the main tool workflows.
- [ ] Build final 0.4.0 Pre-Alpha release artifacts.
- [ ] Sign artifacts or explicitly mark unsigned Pre-Alpha/Beta status.
- [ ] Run installer smoke and installed-app smoke.
- [ ] Run clean install/upgrade/uninstall validation and record evidence.
- [ ] Generate final 0.4.0 distribution checklist with `-RequireReady`.
- [ ] Bump app identity, release manifest naming, Inno fallback metadata, and release notes from 0.3.0 to 0.4.0 only at the final release gate.
- [ ] Update release notes with 0.4.0 product-readiness fixes, UI/UX refresh, opt-in diagnostics behavior, known limitations, upgrade notes, and support instructions.

Exit condition: Talos 0.4.0 Pre-Alpha can be installed by a broader tester, used for the Arduino/Codex workflow, debugged through support evidence, and distributed with honest release documentation.

## Deferred Until After 0.4.0

- MATLAB target integration.
- Hardware upload and serial-monitor guarantees.
- Auto-update infrastructure.
- Public plugin/target SDK.
- 1.0.0 Alpha release gate.

## Deferred Until After 1.0.0

These are valuable product upgrades, but they are not required to finish the Arduino-first path to 1.0.0:

- Full editor parity with VS Code, including customizable keybindings, multi-cursor editing, replace-in-file, find-in-files, minimap, and advanced selection commands.
- Marketplace-style theme/icon customization beyond the built-in light, dark, neutral, contrast, and density preferences.
- Full accessibility certification pass for screen readers, keyboard-only flows, high-contrast variants, and reduced-motion preferences.
- Remote telemetry ingestion, dashboards, and automated product analytics; 0.4.x only keeps local, explicit, opt-in diagnostics export until policy, consent, and server stages are complete.
- Plugin/target marketplace infrastructure for non-Arduino targets after the core Arduino workflow is stable.
