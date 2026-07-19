# Talos Roadmap

## Purpose

This roadmap tracks Talos by product version. A roadmap entry describes why a version exists and what maturity gate it should reach. A pipeline file describes the concrete stage-by-stage implementation plan for one specific version.

```text
Roadmap = version map.
Pipeline = stage plan for one version.
```

## Product Direction

Talos is a local AI control layer between Codex and external IDEs/apps. Arduino IDE is the first reference target:

- Arduino IDE remains the primary coding, upload, board, and serial environment.
- Codex provides reasoning and code-change proposals.
- Talos detects the live Arduino context, stages Codex changes safely, verifies in a sandbox, and lets the user decide when to save changes into the real sketch folder.

The long-term product is broader than Arduino. Talos should become a controlled local bridge that gives AI runtimes, such as Codex, Claude, or compatible future agents, safe access to selected external software and project workspaces:

- **AI runtime layer:** Codex first, with Claude or other runtimes added only through explicit provider adapters.
- **Talos control layer:** permissions, context preview, workspace mapping, staging, review, verify, rollback, diagnostics, consent, and product telemetry policy.
- **Connector layer:** Arduino first, then MATLAB, KiCad, SolidWorks, and other target-specific connectors.
- **Target app layer:** the real IDE/design app remains the source of truth for editing, upload, simulation, design, and domain-specific operations.

Talos must not become a replacement IDE, firmware uploader, CAD system, or model host. Its job is to provide AI with controlled "eyes and hands" for the software the user chooses.

Arduino is the reference target. Future targets must not be placeholders or generic "prepared architecture" work. When Talos adds MATLAB, STM32CubeIDE, KiCad, SolidWorks, or another application, that target should be implemented as a real target product with its own detection, workspace mapping, context packaging, staged write/review path, verification/simulation/build path where available, rollback evidence, support evidence, and UX.

The first official `1.0.0 Alpha` should come only after the planned target blocks are complete enough to demonstrate Talos as a broader local AI control layer, not just an Arduino-specific helper. A target block may span multiple `0.x` versions because each external application needs discovery, workflow integration, safety hardening, UX polish, and real user validation.

## Long-Term Product Principles

- **User-scoped access:** Talos can read or modify only the selected project/workspace, never the whole machine by default.
- **Target app ownership:** Arduino IDE, MATLAB, KiCad, SolidWorks, and similar apps remain the authoritative tools for their domain.
- **Preview before transfer:** users should know what context is being sent to an AI runtime before it is used.
- **Review before write:** AI changes should pass through staging, diff/review, verify/simulation where possible, and explicit user apply/save.
- **Rollback always:** every write into a real workspace should have a recoverable checkpoint.
- **Connector-specific safety:** code connectors use patch/verify; design connectors should use native APIs, file formats, previews, and design-rule checks instead of blind UI automation whenever possible.
- **Consent-based product data:** the founder/owner may receive product analytics, reliability diagnostics, and compatibility data only under clear user consent and policy. Raw source code, CAD files, chat content, serial output, and sensitive local paths are excluded unless the user explicitly previews and submits them.

## Long-Term Architecture Direction

Talos should start the professional architecture migration before adding new target apps. The goal is not a big-bang rewrite; the goal is to make each layer replaceable while the working Arduino path remains usable.

Target architecture:

- **Desktop shell:** a native-quality app host with proper window behavior, app identity, packaging, and theme-aware chrome. Tauri/Rust is the first long-term candidate because it can keep the current web UI while reducing runtime weight; Electron is a fallback only if Tauri blocks required desktop behavior.
- **Web workbench:** static, modular HTML/CSS/JS remains the product UI until a proven shell migration requires a different frontend build path.
- **Local API/IPC contract:** all UI/runtime/target communication should go through stable local endpoints or IPC contracts, not direct cross-module shortcuts.
- **Native helper layer:** measurable hot paths such as process/window detection, hashing, scan summaries, diff helpers, and cache-key generation move to C/Rust/C++ only when benchmarks show user-facing value.
- **Python compatibility bridge:** Python stays as the debug launcher, orchestration fallback, and migration safety net, but it should not remain the permanent owner of performance-sensitive app logic.
- **Runtime manager:** Codex/Claude-compatible runtimes are providers behind a manager; VS Code extension-adjacent paths are legacy providers, not the product foundation.
- **Target adapters:** Arduino, MATLAB, STM32CubeIDE, KiCad, SolidWorks, and later targets must implement the same adapter contract: detect, map workspace, package context, stage/review, verify/simulate/build where possible, write safely, rollback, and produce support evidence.

Migration rules:

- Do not replace a working Python path until the new layer has parity tests and a fallback.
- Do not add a second target until the Arduino reference target proves the adapter contract under the new boundaries.
- Do not introduce a bundled frontend build stack unless it is required by the chosen shell and packaging path.
- Before `1.0.0 Alpha`, runtime independence and shell/runtime boundaries must be proven enough that Talos is not merely a VS Code extension companion.
- Treat `0.6.0` as the architecture cutoff: after this release, target connectors must extend the shared adapter contract instead of forcing another app-wide rewrite.
- Treat `0.7.0` as the Arduino proof release: no MATLAB, STM32CubeIDE, KiCad, or SolidWorks pipeline should start until Arduino has passed on the finalized contract.

## Approximate Capability Bands

These are direction bands, not strict release promises. A pipeline file becomes authoritative only when it is created for a specific version.

| Version band | Product capability target |
| --- | --- |
| 0.1.x - 0.3.x | Arduino proof-of-concept, packaging, Codex workflow maturity, sandbox verify, staged apply/save. |
| 0.4.x | Product-readiness Beta: UI/UX, docs, diagnostics, consent groundwork, broader tester readiness. |
| 0.5.x | Runtime and architecture Beta: Codex Runtime Manager, runtime discovery, pinning, health checks, sign-in readiness, VS Code extension fallback treated as one provider rather than the product dependency, documentation slimming, Python boundary cleanup, and long-term shell/native/API boundary planning. |
| 0.6.x | Architecture foundation Beta: freeze the target-adapter contract, local API/IPC boundary, native-helper boundary, Python fallback boundary, and shell migration decision before adding non-Arduino targets. |
| 0.7.x | Arduino reference-target Beta: refit Arduino onto the finalized adapter contract and prove that the new architecture can support a real target without breaking the existing workflow. |
| 0.8.x - 0.9.x | MATLAB target block: first implement live MATLAB/project workflow on the shared adapter contract, then harden run/check, staged edits, UX, recovery, and support evidence. |
| 0.10.x - 0.11.x | STM32CubeIDE target block: first implement workspace/project detection and build-log flow on the shared adapter contract, then harden generated-code safety, review, UX, and recovery. |
| 0.12.x - 0.13.x | KiCad target block: first implement `.kicad_pro` context and design diagnostics on the shared adapter contract, then harden ERC/DRC, preview, write safety, UX, and evidence. |
| 0.14.x - 0.15.x | SolidWorks target block: first validate official API/metadata access on the shared adapter contract, then harden staged design proposals, rollback, safety confirmation, and support evidence. |
| 0.16.x | Cross-target hardening Beta: unify target UX, support evidence, safety gates, rollback, diagnostics, and runtime behavior across all implemented targets. |
| 0.17.x+ | Alpha-candidate stabilization: final runtime-independence verification, full smoke matrix, installer/update readiness, recovery, policy completeness, investor/user demo polish, and confirmation that the long-term architecture chosen in 0.6.x did not create release blockers. |
| 1.0.0 Alpha | First official multi-target Alpha. Arduino remains the reference target, with other planned targets implemented as real product workflows before this gate. |
| 1.1.x | Post-Alpha native-shell polish if the pre-1.0 migration already proves the shell/runtime boundary; not the first time shell quality is considered. |
| 1.2.x+ | Hosted opt-in product analytics if policy/server work is ready, advanced runtime-provider updates, and post-1.0 architecture upgrades. |

## Versioned Pipeline Files

| Version | Pipeline | Role |
| --- | --- | --- |
| 0.1.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_010.md` | Completed first-version technical MVP and packaging foundation. |
| 0.2.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_020.md` | Completed packaged Arduino reliability and daily-use readiness release. |
| 0.3.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_030.md` | Completed Codex-Arduino workflow maturity release. |
| 0.4.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_040.md` | Completed product-readiness, opt-in feedback, UI/UX polish, and broader tester preparation pipeline. |
| 0.4.5 Beta | `dev_notes/pipelines/TALOS_PIPELINE_045.md` | Planned policy, consent, privacy wording, and user-trust gate before any hosted telemetry. |
| 0.5.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_050.md` | Completed Codex Runtime Manager release to make Talos depend on a verified Codex runtime, not the VS Code extension UI. |
| 0.5.5 Beta | `dev_notes/pipelines/TALOS_PIPELINE_055.md` | Completed architecture slimming release for docs taxonomy, Python boundary cleanup, frontend module split, native-helper planning, and long-term app-shell migration boundaries before new target work. |
| 0.6.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_060.md` | Planned architecture foundation release for adapter contract, local API/IPC, native-helper boundary, Python fallback boundary, and shell migration decision. |
| 0.7.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_070.md` | Planned Arduino reference-target hardening release on the finalized architecture. |
| 0.8.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_080.md` | Planned MATLAB foundation release. |
| 0.9.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_090.md` | Planned MATLAB hardening and daily-use readiness release. |
| 0.10.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0100.md` | Planned STM32CubeIDE foundation release. |
| 0.11.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0110.md` | Planned STM32CubeIDE hardening and generated-code safety release. |
| 0.12.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0120.md` | Planned KiCad foundation release. |
| 0.13.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0130.md` | Planned KiCad hardening and ERC/DRC readiness release. |
| 0.14.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0140.md` | Planned SolidWorks API/metadata foundation release. |
| 0.15.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0150.md` | Planned SolidWorks safety hardening and staged-design review release. |
| 0.16.0 Beta | `dev_notes/pipelines/TALOS_PIPELINE_0160.md` | Planned cross-target hardening release. |
| 0.17.0 Alpha Candidate | `dev_notes/pipelines/TALOS_PIPELINE_0170.md` | Planned full multi-target Alpha-candidate stabilization and final runtime/shell readiness gate. |
| 1.0.0 Alpha | `dev_notes/pipelines/TALOS_PIPELINE_100.md` | Planned first official multi-target Alpha. |
| 1.1.0 Alpha | `dev_notes/pipelines/TALOS_PIPELINE_110.md` | Planned post-Alpha shell polish if the pre-1.0 shell/runtime migration path is already validated. |

Future version pipelines should follow the same naming rule:

```text
0.3.0 -> dev_notes/pipelines/TALOS_PIPELINE_030.md
0.4.0 -> dev_notes/pipelines/TALOS_PIPELINE_040.md
0.4.5 -> dev_notes/pipelines/TALOS_PIPELINE_045.md
0.5.0 -> dev_notes/pipelines/TALOS_PIPELINE_050.md
0.5.5 -> dev_notes/pipelines/TALOS_PIPELINE_055.md
0.6.0 -> dev_notes/pipelines/TALOS_PIPELINE_060.md
0.7.0 -> dev_notes/pipelines/TALOS_PIPELINE_070.md
0.8.0 -> dev_notes/pipelines/TALOS_PIPELINE_080.md
0.9.0 -> dev_notes/pipelines/TALOS_PIPELINE_090.md
0.10.0 -> dev_notes/pipelines/TALOS_PIPELINE_0100.md
0.11.0 -> dev_notes/pipelines/TALOS_PIPELINE_0110.md
0.12.0 -> dev_notes/pipelines/TALOS_PIPELINE_0120.md
0.13.0 -> dev_notes/pipelines/TALOS_PIPELINE_0130.md
0.14.0 -> dev_notes/pipelines/TALOS_PIPELINE_0140.md
0.15.0 -> dev_notes/pipelines/TALOS_PIPELINE_0150.md
0.16.0 -> dev_notes/pipelines/TALOS_PIPELINE_0160.md
0.17.0 -> dev_notes/pipelines/TALOS_PIPELINE_0170.md
1.0.0 -> dev_notes/pipelines/TALOS_PIPELINE_100.md
1.1.0 -> dev_notes/pipelines/TALOS_PIPELINE_110.md
```

## Version Roadmap

### 0.1.0 Beta - Technical MVP And Packaging Foundation

Status: complete.

Purpose:

- Prove Talos can connect Codex to Arduino IDE safely.
- Complete Arduino sketch/board detection, file access, staged Codex changes, sandbox verify, native Windows detection, release packaging scripts, installer smoke tooling, and distribution checklist tooling.

Primary evidence:

- `dev_notes/pipelines/TALOS_PIPELINE_010.md`
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

- `dev_notes/pipelines/TALOS_PIPELINE_020.md`
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

- `dev_notes/pipelines/TALOS_PIPELINE_030.md`

### 0.4.0 Beta - Product Readiness

Status: complete.

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

- `dev_notes/pipelines/TALOS_PIPELINE_040.md`

### 0.4.5 Beta - Policy, Consent, And Trust Gate

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

- `dev_notes/pipelines/TALOS_PIPELINE_045.md`

### 0.5.0 Beta - Codex Runtime Manager

Status: complete.

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

- `dev_notes/pipelines/TALOS_PIPELINE_050.md`

### 0.5.5 Beta - Architecture Slimming

Status: complete.

Purpose:

- Reduce Talos from a Python-heavy app toward a thinner bridge plus stronger native/frontend boundaries before adding more target products.
- Begin the long-term professional app migration by defining replaceable shell, web UI, local API/IPC, native helper, Python fallback, runtime manager, and target-adapter boundaries.
- Create a documentation taxonomy so release/user docs, version pipelines, evidence, and archived notes are easy to navigate without breaking packaged release paths.
- Split large frontend files into maintainable modules while preserving the current UI behavior.
- Split large Python modules into clearer layers: bridge/API orchestration, target adapters, runtime management, checkpoints/history, diagnostics, and support evidence.
- Move or prepare to move performance-sensitive primitives into the native helper where it is measurably useful, especially scanning, hashing, diff/hunk parsing, process/window detection, and cache-key generation.
- Evaluate the first shell-migration candidate in writing, with Tauri/Rust as the preferred lightweight direction and Electron only as a fallback if required desktop behavior blocks Tauri.
- Add lightweight size/performance guardrails so future versions cannot silently grow back into a slow monolith.

Non-goals:

- No new external target app.
- No risky rewrite of the working Arduino/Codex path.
- No broad documentation deletion until release packaging and tests are updated to the new taxonomy.
- No native rewrite unless benchmarks show a clear user-facing benefit.
- No immediate shell migration unless the spike can preserve source/debug launch, static UI serving, packaging, and Arduino workflow parity.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_055.md`

### 0.6.0 Beta - Architecture Foundation

Status: planned.

Purpose:

- Freeze the long-term architecture before adding non-Arduino targets.
- Define and test the target-adapter contract for detect, map workspace, package context, stage/review, verify/simulate/build, safe write, rollback, diagnostics, and evidence.
- Define the local API/IPC contract so the UI, runtime manager, and target adapters do not depend on Python module shortcuts.
- Decide the desktop shell migration path early enough that MATLAB, STM32CubeIDE, KiCad, and SolidWorks do not need to be refit later.
- Keep `desktop_app.py` as the debug/source launcher until a replacement shell proves parity.
- Identify which current Python responsibilities stay as bridge/fallback and which move to native helper, runtime manager, or target adapters.

Non-goals:

- No new external target app.
- No risky rewrite of the working Arduino workflow.
- No shell replacement unless it passes source/debug, packaged-app, Arduino detection, verify, Codex runtime, settings, and recovery parity.
- No replacement of Codex with a Talos-hosted model.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_060.md`

### 0.7.0 Beta - Arduino Reference Target Hardening

Status: planned.

Purpose:

- Treat Arduino IDE as the reference target implementation for every later connector.
- Refit Arduino onto the finalized target-adapter contract from `0.6.0`.
- Harden Arduino detection, board/profile mapping, source-file mapping, staged Codex changes, sandbox verify, checkpoint/rollback, support evidence, and UI affordances.
- Prove that the architecture can support one complete real target without leaking Arduino-specific assumptions into shared code.
- Keep runtime-provider behavior from `0.5.0` stable while the target-contract layer is extracted from Arduino-specific assumptions.

Non-goals:

- No hosted telemetry backend.
- No new target connector in `0.7.0`; this release makes Arduino the reference target before the next target-product versions.
- No replacement of Codex with a Talos-hosted model.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_070.md`

### 0.8.0 Beta - MATLAB Foundation

Status: planned.

Purpose:

- Implement the first real MATLAB target workflow, not a placeholder connector.
- Detect live MATLAB/project context, selected project folders, `.m` files, and practical project metadata through the shared target-adapter contract.
- Package MATLAB context for Codex/AI with clear preview and user-scoped access.
- Support basic staged edits, review, save, rollback, and script/test/run-output capture where MATLAB integration allows.
- Record initial support evidence and troubleshooting docs specific to MATLAB.

Non-goals:

- No blind whole-machine MATLAB file indexing.
- No hidden upload of `.m` source, output logs, or workspace data.
- No replacement for MATLAB's own editor, runner, or Simulink environment.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_080.md`

### 0.9.0 Beta - MATLAB Hardening And Daily-Use Readiness

Status: planned.

Purpose:

- Harden MATLAB detection, project mapping, staged edits, run/check flows, review UX, rollback, support evidence, and documentation after real use.
- Improve MATLAB-specific context packaging so Codex can distinguish active file, project files, scripts, output, and user-selected data safely.
- Validate MATLAB target behavior through manual smoke tests and blocked-case notes.

Non-goals:

- No new target connector in this release unless MATLAB is stable enough to serve as the second reference implementation.
- No hidden collection of `.m` source, workspace variables, or output logs.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_090.md`

### 0.10.0 Beta - STM32CubeIDE Foundation

Status: planned.

Purpose:

- Implement STM32CubeIDE as a real firmware target workflow.
- Detect workspace/project, `.ioc`, `Core/Inc`, `Core/Src`, generated files, user files, and build configuration where practical through the shared target-adapter contract.
- Package context for Codex/AI while respecting generated-code boundaries.
- Support staged edits, review, save, rollback, build invocation or build-log parsing, and troubleshooting evidence.

Non-goals:

- No replacement programmer/debugger.
- No unsafe overwrite of generated CubeMX sections without explicit review.
- No hardware flashing guarantee in the first STM32CubeIDE target release.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0100.md`

### 0.11.0 Beta - STM32CubeIDE Hardening And Generated-Code Safety

Status: planned.

Purpose:

- Harden STM32CubeIDE generated-code boundaries, build parsing, staged review, rollback, and support evidence.
- Add clearer safety UX for user-code sections versus generated sections.
- Validate firmware-project smoke tests across at least one simple project and one generated CubeMX-style project.

Non-goals:

- No hardware flashing as a required gate.
- No automatic regeneration of CubeMX output unless the user explicitly requests it.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0110.md`

### 0.12.0 Beta - KiCad Foundation

Status: planned.

Purpose:

- Implement KiCad as a real electronics-design target workflow.
- Detect `.kicad_pro` projects and map schematic, PCB, footprint, symbol, netlist/ERC/DRC outputs, and relevant project metadata through the shared target-adapter contract.
- Prefer KiCad files, CLI, Python scripting, and official automation paths over fragile UI scraping.
- Let AI review designs, explain issues, propose changes, and stage previewable edits or design notes before any write.

Non-goals:

- No silent PCB/schematic write.
- No manufacturing-output generation without explicit user review.
- No claim of electrical correctness without ERC/DRC or user validation.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0120.md`

### 0.13.0 Beta - KiCad Hardening And ERC/DRC Readiness

Status: planned.

Purpose:

- Harden KiCad project parsing, ERC/DRC collection, design preview, staged design notes/edits, rollback evidence, and troubleshooting documentation.
- Validate KiCad with at least one schematic-only and one PCB project smoke path.
- Make KiCad's safety boundaries explicit so Talos does not blur review notes, generated artifacts, and actual design writes.

Non-goals:

- No SolidWorks connector yet.
- No manufacturing-ready output claim.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0130.md`

### 0.14.0 Beta - SolidWorks API And Metadata Foundation

Status: planned.

Purpose:

- Implement SolidWorks as a high-safety mechanical-design target workflow.
- Explore and use official SolidWorks COM/API automation, metadata export, design tables, parameters, sketches/features, parts, assemblies, and drawing metadata where possible through the shared target-adapter contract.
- Package read-only model context for AI review with clear consent and no blind whole-disk indexing.
- Stage AI-generated design proposals or macro/API action plans without destructive writes by default.

Non-goals:

- No blind UI automation as the primary control path.
- No destructive part/assembly edits.
- No manufacturing-readiness claim without user review.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0140.md`

### 0.15.0 Beta - SolidWorks Safety Hardening And Staged Design Review

Status: planned.

Purpose:

- Harden SolidWorks checkpoints, staged parameter/design proposals, preview, explicit confirmation, rollback evidence, and support bundles.
- Validate a limited set of safe model-review and parameter-proposal workflows before any write-capable path is considered.
- Separate read-only review, staged proposal, and explicit apply actions with strong visual warnings.

Non-goals:

- No autonomous mechanical redesign.
- No silent part, assembly, or drawing write.
- No CAM/manufacturing handoff automation.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0150.md`

### 0.16.0 Beta - Cross-Target Hardening

Status: planned.

Purpose:

- Make Arduino, MATLAB, STM32CubeIDE, KiCad, and SolidWorks feel like one Talos product rather than separate experiments.
- Unify target selection, context preview, staged changes, review, rollback, support evidence, diagnostics, and runtime status.
- Add target-specific safety levels so code, firmware, electronics design, and mechanical design have appropriate write/verify rules.
- Prepare investor/user demos that show Talos moving across several external apps with consistent controls.

Non-goals:

- No new target app in this release unless the existing target matrix is stable.
- No hosted product-data backend unless the 0.4.5 policy/consent and later server work are complete.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0160.md`

### 0.17.0 Alpha Candidate - Multi-Target Stabilization

Status: planned.

Purpose:

- Freeze major feature work before `1.0.0 Alpha`.
- Run full smoke/regression matrices across implemented target products.
- Stabilize installer/update/signing posture, documentation, support evidence, onboarding, known limitations, and investor/demo materials.
- Verify Codex runtime independence as a pre-Alpha gate: the implementation work should already be completed before this stage, and Talos must prefer an official standalone Codex runtime, CLI, or supported runtime-manager path that can authenticate outside VS Code.
- Treat the VS Code extension-adjacent Codex runtime only as an explicit legacy fallback if licensing and support rules allow it, not as the normal product dependency.
- Display runtime source, version, update channel, auth readiness, and account/plan metadata only when the runtime exposes those fields safely.
- Confirm the long-term shell/runtime architecture chosen in `0.6.0` is either already in use or has no blocker to `1.0.0 Alpha` reliability.
- Decide whether another `0.x` release is needed or whether Talos is ready for `1.0.0 Alpha`.

Non-goals:

- No broad new connector work.
- No risky UI shell rewrite; shell architecture work should have been validated before target expansion.
- No copying, bundling, or redistributing VS Code extension binaries without clear license and support guarantees.
- No storing OpenAI credentials, session tokens, or inferred plan data.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_0170.md`

### 1.0.0 Alpha - Official Multi-Target Release

Status: planned.

Purpose:

- Ship the first official Talos Alpha only after the planned target products are complete enough to demonstrate the real product direction.
- Keep Arduino IDE as the reference target, but require MATLAB, STM32CubeIDE, KiCad, and SolidWorks lines to have real workflows or explicit go/no-go decisions before release.
- Require Codex runtime selection, sign-in readiness, runtime independence, and app-server health checks to be visible and recoverable.
- Run full automated checks, manual target smoke matrices, signed or explicitly unsigned release artifacts, installer smoke, installed-app smoke, and final distribution checklist.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_100.md`

### 1.1.0 Alpha - Post-Alpha Shell Polish

Status: planned.

Purpose:

- Continue the shell work started before 1.0 after the first official Alpha has proven the target workflows.
- Polish or complete the migration from a pywebview-style custom chrome toward a VS Code-class desktop shell while preserving the established target workflows.
- Keep the existing Talos backend contracts and web frontend behavior stable, but allow the outer shell to move to the validated long-term host if the pre-1.0 migration chose one.
- Provide a theme-aware custom title bar with menu bar, command center, window controls, drag-to-restore, resize hit-testing, and Windows Snap Layout behavior that feels native rather than simulated.
- Preserve `desktop_app.py` or an equivalent lightweight debug launcher so development remains fast even if the commercial shell changes.

Non-goals:

- No rewrite of target detection, sandbox/build/verify, Codex context, or staged save logic unless the shell boundary requires a small adapter.
- No new target connector in this shell-focused release unless required to validate shell extensibility.
- No UI novelty that weakens the VS Code-style developer workflow.

Expected pipeline:

- `dev_notes/pipelines/TALOS_PIPELINE_110.md`

## Pre-1.0 Target Product Notes

These directions are not generic future placeholders. Each target becomes active only when its version pipeline is created, and each target must reach a real product workflow before Talos is considered ready for `1.0.0 Alpha`.

### MATLAB Connector Direction

- Detect MATLAB sessions and selected project folders.
- Read `.m`, `.mlx` metadata where practical, project files, run/test output, and simulation logs under user consent.
- Prefer MATLAB Engine/API or project-file integration over UI scraping.
- Support AI review, refactor suggestions, test execution guidance, and controlled file writes.

### STM32CubeIDE Connector Direction

- Detect STM32CubeIDE workspaces and selected projects.
- Map `.ioc`, generated code boundaries, `Core/Inc`, `Core/Src`, build configuration, and relevant logs.
- Prefer Eclipse workspace/project metadata and CLI/build logs over brittle UI scraping.
- Support AI review, staged code edits, generated-code warnings, build-log parsing, rollback, and support evidence.

### KiCad Connector Direction

- Detect `.kicad_pro` projects and map schematic, PCB, footprint, symbol, and ERC/DRC output files.
- Prefer KiCad project files, CLI tools, Python scripting, and native automation APIs where available.
- Let AI review schematics/layout constraints and propose changes through previewable diffs or generated design notes before any project write.

### SolidWorks Connector Direction

- Treat SolidWorks as a high-risk design target because direct changes can affect mechanical constraints, assemblies, and manufacturing intent.
- Prefer official COM/API automation, exported neutral formats, design tables, metadata, and generated change proposals.
- Require explicit preview, checkpoint, and user confirmation before changing a part, assembly, drawing, or parameter.

## Post-1.0 Platform And Commercial Notes

These directions should not block the pre-1.0 target-product work unless they are required for trust, support, or investor-facing demos.

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
