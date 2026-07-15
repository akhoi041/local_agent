# Talos Roadmap

## Purpose

This roadmap tracks Talos by product version. A roadmap entry describes why a version exists and what maturity gate it should reach. A pipeline file describes the concrete stage-by-stage implementation plan for one specific version.

```text
Roadmap = version map.
Pipeline = stage plan for one version.
```

## Product Direction

Talos is a local AI control layer between Codex and external IDEs/apps. The first official product line is Arduino-first:

- Arduino IDE remains the primary coding, upload, board, and serial environment.
- Codex provides reasoning and code-change proposals.
- Talos detects the live Arduino context, stages Codex changes safely, verifies in a sandbox, and lets the user decide when to save changes into the real sketch folder.

The long-term product is broader than Arduino. Talos should become a controlled local bridge that gives AI runtimes, such as Codex, Claude, or compatible future agents, safe access to selected external software and project workspaces:

- **AI runtime layer:** Codex first, with Claude or other runtimes added only through explicit provider adapters.
- **Talos control layer:** permissions, context preview, workspace mapping, staging, review, verify, rollback, diagnostics, consent, and product telemetry policy.
- **Connector layer:** Arduino first, then MATLAB, KiCad, SolidWorks, and other target-specific connectors.
- **Target app layer:** the real IDE/design app remains the source of truth for editing, upload, simulation, design, and domain-specific operations.

Talos must not become a replacement IDE, firmware uploader, CAD system, or model host. Its job is to provide AI with controlled "eyes and hands" for the software the user chooses.

MATLAB, KiCad, SolidWorks, and other targets are intentionally deferred until the Arduino product line and runtime-provider foundation are reliable.

## Long-Term Product Principles

- **User-scoped access:** Talos can read or modify only the selected project/workspace, never the whole machine by default.
- **Target app ownership:** Arduino IDE, MATLAB, KiCad, SolidWorks, and similar apps remain the authoritative tools for their domain.
- **Preview before transfer:** users should know what context is being sent to an AI runtime before it is used.
- **Review before write:** AI changes should pass through staging, diff/review, verify/simulation where possible, and explicit user apply/save.
- **Rollback always:** every write into a real workspace should have a recoverable checkpoint.
- **Connector-specific safety:** code connectors use patch/verify; design connectors should use native APIs, file formats, previews, and design-rule checks instead of blind UI automation whenever possible.
- **Consent-based product data:** the founder/owner may receive product analytics, reliability diagnostics, and compatibility data only under clear user consent and policy. Raw source code, CAD files, chat content, serial output, and sensitive local paths are excluded unless the user explicitly previews and submits them.

## Approximate Capability Bands

These are direction bands, not strict release promises. A pipeline file becomes authoritative only when it is created for a specific version.

| Version band | Product capability target |
| --- | --- |
| 0.1.x - 0.3.x | Arduino proof-of-concept, packaging, Codex workflow maturity, sandbox verify, staged apply/save. |
| 0.4.x | Product-readiness polish: UI/UX, docs, diagnostics, consent groundwork, broader tester readiness. |
| 0.5.x | Codex Runtime Manager: runtime discovery, pinning, health checks, sign-in readiness, VS Code extension fallback treated as one provider rather than the product dependency. |
| 0.6.x - 0.8.x | Runtime-independent hardening, connector abstraction, stronger context contracts, reliability gates, and first multi-runtime/provider experiments if practical. |
| 0.9.x | Arduino release-candidate stabilization: full smoke matrix, installer/update readiness, recovery, support workflow, policy completeness. |
| 1.0.0 Alpha | First official Arduino-first release. Stable local AI control layer for Arduino workflows. |
| 1.1.x+ | Native-quality shell, deeper runtime independence, and post-1.0 architecture upgrades. |
| 1.x later | New target connectors such as MATLAB, KiCad, or SolidWorks after Arduino foundations are proven. |
| 2.x later | Multi-target connector ecosystem, hosted opt-in product analytics, team/admin controls, and commercial-scale distribution if policy and infrastructure are ready. |

## Versioned Pipeline Files

| Version | Pipeline | Role |
| --- | --- | --- |
| 0.1.0 Beta | `docs/TALOS_PIPELINE_010.md` | Completed first-version technical MVP and packaging foundation. |
| 0.2.0 Beta | `docs/TALOS_PIPELINE_020.md` | Completed packaged Arduino reliability and daily-use readiness release. |
| 0.3.0 Beta | `docs/TALOS_PIPELINE_030.md` | Completed Codex-Arduino workflow maturity release. |
| 0.4.0 Pre-Alpha | `docs/TALOS_PIPELINE_040.md` | Active pipeline for product readiness, opt-in feedback, UI/UX polish, and broader tester preparation. |
| 0.4.5 Pre-Alpha | `docs/TALOS_PIPELINE_045.md` | Planned policy, consent, privacy wording, and user-trust gate before any hosted telemetry. |
| 0.5.0 Pre-Alpha | `docs/TALOS_PIPELINE_050.md` | Planned Codex Runtime Manager release to make Talos depend on a verified Codex runtime, not the VS Code extension UI. |
| 0.6.0 Pre-Alpha | `docs/TALOS_PIPELINE_060.md` | Planned runtime-independent release hardening before the first official Arduino Alpha. |
| 1.1.0 Alpha | `docs/TALOS_PIPELINE_110.md` | Planned native-quality desktop shell/chrome upgrade after the first official Arduino release. |

Future version pipelines should follow the same naming rule:

```text
0.3.0 -> docs/TALOS_PIPELINE_030.md
0.4.0 -> docs/TALOS_PIPELINE_040.md
0.4.5 -> docs/TALOS_PIPELINE_045.md
0.5.0 -> docs/TALOS_PIPELINE_050.md
0.6.0 -> docs/TALOS_PIPELINE_060.md
1.0.0 -> docs/TALOS_PIPELINE_100.md
1.1.0 -> docs/TALOS_PIPELINE_110.md
```

## Version Roadmap

### 0.1.0 Beta - Technical MVP And Packaging Foundation

Status: complete.

Purpose:

- Prove Talos can connect Codex to Arduino IDE safely.
- Complete Arduino sketch/board detection, file access, staged Codex changes, sandbox verify, native Windows detection, release packaging scripts, installer smoke tooling, and distribution checklist tooling.

Primary evidence:

- `docs/TALOS_PIPELINE_010.md`
- Arduino smoke test documentation
- Stage 10 packaging and distribution checklist tooling

### 0.2.0 Beta - Packaged Arduino Reliability

Status: complete.

Purpose:

- Turn the completed MVP into a more reliable packaged Beta.
- Validate installed-app behavior outside the source tree.
- Harden Arduino detection, verify responsiveness, workbench UX, Codex context flow, and safety recovery.

Non-goals:

- No MATLAB.
- No plugin SDK.
- No auto-update infrastructure.
- No commercial-grade upload or serial-monitor guarantee.

Primary evidence:

- `docs/TALOS_PIPELINE_020.md`
- Clean release build
- Installer smoke result
- Installed-app smoke result
- Distribution checklist
- Manual Arduino reliability checks

### 0.3.0 Beta - Codex-Arduino Workflow Maturity

Status: complete.

Purpose:

- Make the Codex loop the clearest product value.
- Improve context preview, conversation/task states, staged change review, verify-before-save, and per-sketch Codex history.
- Reduce friction in applying, rejecting, verifying, and saving Codex-generated changes.

Expected pipeline:

- `docs/TALOS_PIPELINE_030.md`

### 0.4.0 Pre-Alpha - Product Readiness

Status: active.

Purpose:

- Prepare Talos for a broader user-facing Alpha.
- Complete or explicitly document code-signing status.
- Add user guide, troubleshooting guide, support bundle workflow, clean release notes, and clean install/uninstall validation on a fresh Windows profile or VM.
- Add privacy-aware opt-in diagnostics and product feedback so tester issues can guide development without silently collecting sketch source, Codex chat content, or sensitive local identifiers.
- Refresh UI/UX toward a polished GitHub-inspired developer-tool appearance with better theme/appearance controls, clearer action grouping, responsive layouts, and more convenient tool workflows.

Non-goals:

- No hidden telemetry.
- No raw code/chat collection by default.
- No MATLAB or second target yet.
- No full cloud analytics backend unless a later version explicitly scopes it.

Expected pipeline:

- `docs/TALOS_PIPELINE_040.md`

### 0.4.5 Pre-Alpha - Policy, Consent, And Trust Gate

Status: planned.

Purpose:

- Finalize the trust layer before Talos sends any product data to a hosted service.
- Turn 0.4.0 local diagnostics/export into a clear consent model that users can understand, enable, disable, preview, and audit.
- Define privacy policy wording, diagnostic data categories, retention intent, deletion path, user-facing consent copy, and support-report redaction rules.
- Validate that Talos never collects or transmits sketch source, Codex chat content, account identifiers, raw absolute paths, or serial output unless the user explicitly previews and exports that data.

Non-goals:

- No production telemetry backend yet.
- No automatic remote upload by default.
- No third-party analytics SDK.
- No commercial data monetization path.

Expected pipeline:

- `docs/TALOS_PIPELINE_045.md`

### 0.5.0 Pre-Alpha - Codex Runtime Manager

Status: planned.

Purpose:

- Add a Codex Runtime Manager so Talos can discover, verify, pin, and health-check the Codex runtime it uses.
- Treat VS Code's bundled Codex executable only as one runtime provider, not as the product dependency.
- Prefer a standalone `codex` executable on `PATH` or a user-selected runtime path when available.
- Show runtime source, path, version, hash, sign-in readiness, app-server readiness, and last health-check result in Settings.
- Let users pin a known-good runtime and warn before silently switching to a different extension/runtime after updates.
- Keep Codex authentication owned by the Codex runtime. Talos should not store OpenAI credentials, account tokens, or plan claims unless the runtime exposes safe metadata.

Non-goals:

- No bundled or redistributed VS Code extension unless OpenAI provides a clear supported redistribution path.
- No fake Talos-side Codex login.
- No server-side telemetry or hosted feedback path in this version.
- No plan guessing from email, GitHub account, or local profile names.
- No MATLAB or second target.

Expected pipeline:

- `docs/TALOS_PIPELINE_050.md`

### 0.6.0 Pre-Alpha - Runtime-Independent Release Hardening

Status: planned.

Purpose:

- Harden the 0.5.0 runtime provider model for release candidates.
- Validate Talos across multiple Codex runtime sources: `PATH`, manual path, VS Code extension fallback, and no-runtime failure mode.
- Add runtime migration/rollback behavior, support-bundle evidence for runtime failures, and clear first-run guidance.
- Ensure Arduino-first workflows remain stable when Codex runtime changes or becomes temporarily unavailable.

Non-goals:

- No hosted telemetry backend.
- No second IDE target.
- No replacement of Codex with a Talos-hosted model.

Expected pipeline:

- `docs/TALOS_PIPELINE_060.md`

### 1.0.0 Alpha - Official Arduino-First Release

Status: planned.

Purpose:

- Ship the first official Arduino-focused Talos release.
- Freeze scope to the Arduino-first Codex control layer.
- Require Codex runtime selection, sign-in readiness, and app-server health checks to be visible and recoverable.
- Run full automated checks, manual Arduino smoke matrix, signed or explicitly unsigned release artifacts, installer smoke, installed-app smoke, and final distribution checklist.

Expected pipeline:

- `docs/TALOS_PIPELINE_100.md`

### 1.1.0 Alpha - Native-Quality Desktop Shell

Status: planned.

Purpose:

- Upgrade Talos from a pywebview-style custom chrome toward a VS Code-class desktop shell while preserving the Arduino-first product behavior.
- Keep the existing Python/Talos backend and web frontend as the product core, but evaluate or migrate the outer desktop shell to a framework with stronger native window integration, such as Electron, Tauri, WinUI/WebView2, or a small native Windows host.
- Provide a theme-aware custom title bar with menu bar, command center, window controls, drag-to-restore, resize hit-testing, and Windows Snap Layout behavior that feels native rather than simulated.
- Preserve `desktop_app.py` or an equivalent lightweight debug launcher so development remains fast even if the commercial shell changes.

Non-goals:

- No rewrite of Arduino detection, sandbox verify, Codex context, or staged save logic unless the shell boundary requires a small adapter.
- No second IDE target.
- No UI novelty that weakens the VS Code-style developer workflow.

Expected pipeline:

- `docs/TALOS_PIPELINE_110.md`

## Post-1.0 Expansion Notes

These directions should not dilute the Arduino-first 1.0.0 Alpha. They become active only after the core connector/runtime architecture is stable.

### MATLAB Connector Direction

- Detect MATLAB sessions and selected project folders.
- Read `.m`, `.mlx` metadata where practical, project files, run/test output, and simulation logs under user consent.
- Prefer MATLAB Engine/API or project-file integration over UI scraping.
- Support AI review, refactor suggestions, test execution guidance, and controlled file writes.

### KiCad Connector Direction

- Detect `.kicad_pro` projects and map schematic, PCB, footprint, symbol, and ERC/DRC output files.
- Prefer KiCad project files, CLI tools, Python scripting, and native automation APIs where available.
- Let AI review schematics/layout constraints and propose changes through previewable diffs or generated design notes before any project write.

### SolidWorks Connector Direction

- Treat SolidWorks as a high-risk design target because direct changes can affect mechanical constraints, assemblies, and manufacturing intent.
- Prefer official COM/API automation, exported neutral formats, design tables, metadata, and generated change proposals.
- Require explicit preview, checkpoint, and user confirmation before changing a part, assembly, drawing, or parameter.

### Commercial Data Direction

- Hosted feedback/diagnostics should start only after policy, consent, schema, retention, deletion/export, abuse handling, and admin review paths are ready.
- Product data should focus on reliability and usage signals: feature usage, crash/error category, app/runtime versions, connector versions, verify/simulation status, and performance timings.
- Sensitive artifacts such as source code, CAD files, chat content, serial output, raw absolute paths, credentials, and account tokens stay local unless the user explicitly previews and submits them.

### Platform And Distribution Direction

- Auto-update infrastructure.
- Public plugin/target SDK.
- Multi-OS packaging.
- Team/admin controls.
- Marketplace or connector ecosystem only after connector safety contracts are mature.
