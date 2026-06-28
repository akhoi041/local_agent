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
| 0.2.0 Beta | `docs/TALOS_PIPELINE_020.md` | Active pipeline for packaged Arduino reliability and daily-use readiness. |

Future version pipelines should follow the same naming rule:

```text
0.3.0 -> docs/TALOS_PIPELINE_030.md
0.4.0 -> docs/TALOS_PIPELINE_040.md
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

Status: active.

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

Status: planned.

Purpose:

- Make the Codex loop the clearest product value.
- Improve context preview, conversation/task states, staged change review, verify-before-save, and per-sketch Codex history.
- Reduce friction in applying, rejecting, verifying, and saving Codex-generated changes.

Expected pipeline:

- `docs/TALOS_PIPELINE_030.md`

### 0.4.0 Pre-Alpha - Product Readiness

Status: planned.

Purpose:

- Prepare Talos for a broader user-facing Alpha.
- Complete or explicitly document code-signing status.
- Add user guide, troubleshooting guide, support bundle workflow, clean release notes, and clean install/uninstall validation on a fresh Windows profile or VM.

Expected pipeline:

- `docs/TALOS_PIPELINE_040.md`

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
