# Talos Roadmap

## Purpose

This roadmap tracks Talos by product version. A roadmap entry explains why a version exists and what maturity gate it must reach. A pipeline file contains the concrete implementation stages for one version.

```text
Roadmap = version map.
Pipeline = stage plan for one version.
```

## Product Direction

Talos is a local AI control layer between AI runtimes and external engineering tools. Arduino IDE is the first reference target, but Talos is not meant to become an Arduino-only helper, a replacement IDE, a firmware uploader, a CAD system, or a model host.

The long-term product is:

- **AI runtime layer:** Codex first, Claude or other runtimes later through provider adapters.
- **Talos control layer:** permissions, context preview, workspace mapping, staging, review, verify/simulation/build, rollback, diagnostics, consent, and support evidence.
- **Target adapter layer:** Arduino first, then MATLAB, STM32CubeIDE, KiCad, SolidWorks, and other target-specific products.
- **Target app layer:** the real IDE/design app remains the source of truth for editing, upload, simulation, design, and domain-specific operations.

Talos gives AI controlled "eyes and hands" for the selected workspace or external app. It must not silently access the whole machine.

## Architecture Pivot

The early Talos versions proved the workflow quickly with a Python-heavy shell/server. That was useful for discovery, but it is not the professional long-term structure. Before adding more target apps, Talos must be rebuilt around a replaceable desktop shell, stable local API/IPC contracts, native helper boundaries, and target adapters.

Target architecture:

```text
Talos Desktop
|-- Desktop Shell
|   |-- native window behavior
|   |-- app identity, installer, updater path
|   `-- hosts the web workbench
|-- Web Workbench
|   |-- activity bar / explorer / editor-review surface
|   |-- Codex/runtime panel
|   |-- logs / diagnostics / settings
|   `-- command palette / status bar
|-- Local API Or IPC Contract
|   |-- versioned payloads
|   |-- target state
|   |-- runtime state
|   `-- support evidence
|-- Core Backend
|   |-- workspace state
|   |-- task queue
|   |-- policy and permissions
|   `-- adapter orchestration
|-- Native Helper Layer
|   |-- process/window detection
|   |-- file watching
|   |-- hashing/cache keys
|   |-- diff/hunk helpers
|   `-- OS integration
|-- Runtime Providers
|   |-- Codex runtime provider
|   |-- Claude runtime provider
|   `-- legacy/fallback providers
`-- Target Adapters
    |-- Arduino
    |-- MATLAB
    |-- STM32CubeIDE
    |-- KiCad
    `-- SolidWorks
```

Preferred long-term shell direction:

- **Tauri + Rust + current web workbench** is the preferred direction because it keeps the current UI investment while reducing Python/runtime weight.
- **Electron + TypeScript** remains a fallback if Tauri blocks required desktop behavior.
- **Python remains only a compatibility/debug bridge**, not the permanent owner of hot-path app logic.

Migration rules:

- Do not add a second target until the architecture rewrite has a real Arduino port.
- Do not remove a working Python path until the replacement has parity tests and fallback behavior.
- Do not call a stage complete if it only writes notes unless that stage is explicitly documentation-only.
- Do not treat VS Code extension behavior as the product foundation. Runtime providers must be explicit and replaceable.

## Long-Term Principles

- **User-scoped access:** Talos reads/modifies only the selected workspace.
- **Target app ownership:** Arduino IDE, MATLAB, KiCad, SolidWorks, and similar apps remain authoritative.
- **Preview before transfer:** users can see what context is sent to a runtime.
- **Review before write:** AI changes pass through staging/review/verify or equivalent safety gates.
- **Rollback always:** every real workspace write has a recoverable checkpoint.
- **Connector-specific safety:** code connectors use patch/verify; design connectors use native APIs, file formats, previews, and design-rule checks.
- **Consent-based data:** product analytics and diagnostics require explicit consent. Raw source code, CAD files, chat content, serial output, credentials, and sensitive local paths remain local unless explicitly previewed and submitted.

## Capability Bands

| Version band | Product capability target |
| --- | --- |
| 0.1.x - 0.4.x | Completed Arduino proof, packaging, Codex workflow maturity, UI/UX polish, diagnostics, and tester-readiness work. These versions remain historical proof, not the final architecture. |
| 0.5.0 | Codex Runtime Manager foundation. Runtime discovery/pinning/status is introduced, but full runtime independence is not complete. |
| 0.5.5 | Architecture Pivot Patch. Freeze the Python-heavy approach, audit ownership, define the rewrite boundary, and prepare migration without adding new targets. |
| 0.6.0 | Core Runtime Rewrite Foundation. Start the real shell/API/core split and land implementation artifacts, not just documents. |
| 0.6.5 | Python Decomposition. Move hot-path and mixed ownership logic behind native/core boundaries while preserving source/debug compatibility. |
| 0.7.0 | Arduino Adapter Port. Rebuild Arduino as the first real target on the new adapter/core contracts. |
| 0.7.5 | Arduino Workflow Hardening. Make Arduino stable for daily use on the new architecture. |
| 0.8.0 | Talos Core Complete. The platform itself is complete enough to support new target products without another rewrite. |
| 0.9.x | Runtime Independence And Product Trust. Harden runtime providers, consent, diagnostics, recovery, and installer/update posture before broad target expansion. |
| 0.10.x - 0.11.x | MATLAB target block: foundation, then hardening. |
| 0.12.x - 0.13.x | STM32CubeIDE target block: foundation, then hardening. |
| 0.14.x - 0.15.x | KiCad target block: foundation, then hardening. |
| 0.16.x - 0.17.x | SolidWorks target block: foundation, then hardening. |
| 0.18.x+ | Cross-target hardening, investor/demo readiness, final smoke matrix, and Alpha-candidate stabilization. |
| 1.0.0 Alpha | First official Alpha only after Talos Core is complete, Arduino is production-grade, runtime independence is clear, and planned target blocks have real workflows or explicit go/no-go decisions. |

## Versioned Pipeline Files

| Version | Pipeline | Role |
| --- | --- | --- |
| 0.1.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_010.md` | Completed first MVP and packaging foundation. |
| 0.2.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_020.md` | Completed packaged Arduino reliability release. |
| 0.3.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_030.md` | Completed Codex-Arduino workflow maturity release. |
| 0.4.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_040.md` | Completed product readiness, UI/UX, diagnostics, and tester preparation. |
| 0.5.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_050.md` | Completed Codex Runtime Manager foundation. |
| 0.5.5 Beta | `dev_notes/pipelines/TALOS_PIPELINE_055.md` | Active architecture pivot patch. |
| 0.6.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_060.md` | Planned core runtime rewrite foundation. |
| 0.6.5 Beta | `dev_notes/pipelines/TALOS_PIPELINE_065.md` | Planned Python decomposition and native/core extraction. |
| 0.7.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_070.md` when version starts. | Planned Arduino adapter port on the new architecture. |
| 0.7.5 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_075.md` when version starts. | Planned Arduino workflow hardening. |
| 0.8.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_080.md` when version starts. | Planned Talos Core Complete gate. |
| 0.9.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_090.md` when version starts. | Planned runtime independence and product trust hardening. |
| 0.10.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0100.md` when version starts. | Planned MATLAB foundation release. |
| 0.11.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0110.md` when version starts. | Planned MATLAB hardening release. |
| 0.12.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0120.md` when version starts. | Planned STM32CubeIDE foundation release. |
| 0.13.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0130.md` when version starts. | Planned STM32CubeIDE hardening release. |
| 0.14.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0140.md` when version starts. | Planned KiCad foundation release. |
| 0.15.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0150.md` when version starts. | Planned KiCad hardening release. |
| 0.16.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0160.md` when version starts. | Planned SolidWorks foundation release. |
| 0.17.0 Beta | Open as `dev_notes/pipelines/TALOS_PIPELINE_0170.md` when version starts. | Planned SolidWorks hardening release. |
| 0.18.0+ | Open versioned pipeline files when each version starts. | Planned cross-target hardening and Alpha-candidate stabilization. |
| 1.0.0 Alpha | Open as `dev_notes/pipelines/TALOS_PIPELINE_100.md` when Alpha preparation starts. | Planned first official Alpha. |

Naming rule:

The names below are conventions. Create a pipeline file only when that version starts, except for the active rewrite transition files that already exist.

```text
0.5.5 -> TALOS_PIPELINE_055.md
0.6.0 -> TALOS_PIPELINE_060.md
0.6.5 -> TALOS_PIPELINE_065.md
0.7.0 -> TALOS_PIPELINE_070.md
0.7.5 -> TALOS_PIPELINE_075.md
0.8.0 -> TALOS_PIPELINE_080.md
0.9.0 -> TALOS_PIPELINE_090.md
0.10.0 -> TALOS_PIPELINE_0100.md
1.0.0 -> TALOS_PIPELINE_100.md
```

## Version Roadmap

### 0.1.0 - 0.4.0 Beta History

Status: complete.

Purpose:

- Prove the Arduino/Codex bridge.
- Add packaging, installer, smoke tests, UI/UX polish, diagnostics, support bundle, and tester-readiness work.
- These versions remain valuable evidence, but they are not the final architecture.

Primary pipelines:

- `dev_notes/pipelines/TALOS_PIPELINE_010.md`
- `dev_notes/pipelines/TALOS_PIPELINE_020.md`
- `dev_notes/pipelines/TALOS_PIPELINE_030.md`
- `dev_notes/pipelines/TALOS_PIPELINE_040.md`

### 0.5.0 Beta - Runtime Manager Foundation

Status: complete.

Purpose:

- Discover, verify, pin, and health-check Codex runtimes.
- Treat VS Code extension-adjacent runtime paths as one provider, not the product foundation.
- Keep authentication owned by the runtime.

Pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_050.md`

### 0.5.5 Beta - Architecture Pivot Patch

Status: active.

Purpose:

- Stop treating the Python-heavy prototype architecture as the long-term product.
- Freeze the working Arduino/Codex path as a compatibility baseline.
- Audit Python/frontend/native/runtime ownership.
- Decide the rewrite boundary and prepare the 0.6.0 shell/core/API migration.
- Remove or archive planning that still assumes new targets can start before the architecture pivot is complete.

Exit gate:

- Talos has a documented and testable migration boundary.
- 0.6.0 can start real implementation work, not another planning-only cycle.

Pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_055.md`

### 0.6.0 Beta - Core Runtime Rewrite Foundation

Status: planned.

Purpose:

- Begin the real long-term rewrite while preserving the debug/source launcher.
- Introduce the production shell abstraction, core backend boundary, local IPC/API contract, target adapter host, and migration bridge.
- Prove that the app can run through the new structure while Python remains a fallback.

Non-goals:

- No new external target app.
- No removal of the working Arduino path until parity exists.
- No all-at-once rewrite without regression gates.

Pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_060.md`

### 0.6.5 Beta - Python Decomposition

Status: planned.

Purpose:

- Move performance-sensitive and mixed-ownership logic out of Python hot paths.
- Put scanning, hashing, process/window detection, diff helpers, task orchestration, and runtime discovery behind native/core boundaries where practical.
- Keep Python as compatibility/debug bridge only.

Pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_065.md`

### 0.7.0 Beta - Arduino Adapter Port

Status: planned.

Purpose:

- Port Arduino onto the new core/adapter contracts.
- Preserve detection, sketch mapping, board/profile, multi-file context, sandbox verify, staged apply/save, rollback, and Codex context behavior.
- Prove the new architecture with the first real target.

Pipeline:

- Open `dev_notes/pipelines/TALOS_PIPELINE_070.md` when 0.7.0 starts.

### 0.7.5 Beta - Arduino Workflow Hardening

Status: planned.

Purpose:

- Make Arduino stable enough for daily use on the new architecture.
- Harden verify speed, file sync, review/apply/save, runtime errors, support evidence, and UI workflow.

Pipeline:

- Open `dev_notes/pipelines/TALOS_PIPELINE_075.md` when 0.7.5 starts.

### 0.8.0 Beta - Talos Core Complete

Status: planned.

Purpose:

- Declare the Talos platform complete enough to add new target products without another app-wide rewrite.
- Require shell/core/API/runtime/native/adapter boundaries to be implemented, tested, and documented.
- Require Arduino to remain functional as the reference target.

Exit gate:

- New target products can start by implementing adapters, not by rewriting the app.

Pipeline:

- Open `dev_notes/pipelines/TALOS_PIPELINE_080.md` when 0.8.0 starts.

### 0.9.0 Beta - Runtime Independence And Product Trust

Status: planned.

Purpose:

- Harden runtime-provider independence, sign-in readiness, safe account/plan metadata display, consent, diagnostics, recovery, and installer/update posture.
- Ensure Talos is not merely a VS Code extension companion before target expansion.

Pipeline:

- Open `dev_notes/pipelines/TALOS_PIPELINE_090.md` when 0.9.0 starts.

### 0.10.x And Later - Target Product Blocks

Status: planned.

Purpose:

- Add new external tools only after Talos Core Complete.
- Each target needs at least a foundation release and a hardening release.

Initial target order:

1. MATLAB
2. STM32CubeIDE
3. KiCad
4. SolidWorks

Each target must implement:

- detection
- workspace mapping
- context packaging
- staged review/write
- verify/simulate/build/check where possible
- rollback
- support evidence
- target-specific safety UX

### 1.0.0 Alpha - First Official Alpha

Status: planned.

Purpose:

- Ship only after Talos Core is complete, Arduino is production-grade, runtime independence is clear, and planned target blocks have either real workflows or explicit go/no-go decisions.

Non-goals:

- No Alpha label for a Python-heavy prototype.
- No hidden telemetry.
- No claim of multi-target support from placeholder connectors.
