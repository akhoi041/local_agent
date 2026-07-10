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

MATLAB and other targets are intentionally deferred until the Arduino product line is reliable.

## Versioned Pipeline Files

| Version | Pipeline | Role |
| --- | --- | --- |
| 0.1.0 Beta | `docs/TALOS_PIPELINE_010.md` | Completed first-version technical MVP and packaging foundation. |
| 0.2.0 Beta | `docs/TALOS_PIPELINE_020.md` | Completed packaged Arduino reliability and daily-use readiness release. |
| 0.3.0 Beta | `docs/TALOS_PIPELINE_030.md` | Completed Codex-Arduino workflow maturity release. |
| 0.4.0 Pre-Alpha | `docs/TALOS_PIPELINE_040.md` | Active pipeline for product readiness, opt-in feedback, UI/UX polish, and broader tester preparation. |
| 0.4.5 Pre-Alpha | `docs/TALOS_PIPELINE_045.md` | Planned policy, consent, privacy wording, and user-trust gate before any hosted telemetry. |
| 0.5.0 Pre-Alpha | `docs/TALOS_PIPELINE_050.md` | Planned opt-in server-side feedback/telemetry foundation after policy and consent are ready. |

Future version pipelines should follow the same naming rule:

```text
0.3.0 -> docs/TALOS_PIPELINE_030.md
0.4.0 -> docs/TALOS_PIPELINE_040.md
0.4.5 -> docs/TALOS_PIPELINE_045.md
0.5.0 -> docs/TALOS_PIPELINE_050.md
1.0.0 -> docs/TALOS_PIPELINE_100.md
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

### 0.5.0 Pre-Alpha - Opt-In Feedback Server

Status: planned.

Purpose:

- Add the first hosted feedback/diagnostics receiving path after the 0.4.5 policy and consent gate is complete.
- Build a minimal server endpoint for opt-in diagnostics, issue reports, install/verify failure summaries, and anonymized product-health events.
- Add server-side storage, retention rules, admin review workflow, abuse protection, deletion/export request handling, and clear versioned schema.
- Keep local support export as the fallback path for users who do not opt into remote diagnostics.

Non-goals:

- No raw code/chat telemetry.
- No telemetry without explicit opt-in.
- No broad analytics dashboard before the schema, consent, and retention model are stable.
- No MATLAB or second target.

Expected pipeline:

- `docs/TALOS_PIPELINE_050.md`

### 1.0.0 Alpha - Official Arduino-First Release

Status: planned.

Purpose:

- Ship the first official Arduino-focused Talos release.
- Freeze scope to the Arduino-first Codex control layer.
- Run full automated checks, manual Arduino smoke matrix, signed or explicitly unsigned release artifacts, installer smoke, installed-app smoke, and final distribution checklist.

Expected pipeline:

- `docs/TALOS_PIPELINE_100.md`

## Deferred Until After 1.0.0 Alpha

- MATLAB target integration.
- Hardware upload and serial-monitor guarantees as commercial-grade features.
- Auto-update infrastructure.
- Public plugin/target SDK.
- Multi-OS packaging.
