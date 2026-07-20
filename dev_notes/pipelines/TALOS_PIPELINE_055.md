# Talos Pipeline - Version 0.5.5 Beta

Purpose: make the architecture pivot explicit before the long-term rewrite starts. This version stops treating the Python-heavy prototype as the permanent structure and prepares Talos for a real shell/core/API migration without breaking the working Arduino path.

```text
0.5.5 Beta = architecture pivot + compatibility baseline + ownership audit + rewrite boundary.
```

Current release evidence: `dev_notes/evidence/TALOS_055_EVIDENCE.md`

## Exit Condition

0.5.5 is complete when Talos has a clear compatibility baseline, a documented ownership map, a no-new-target rule before Core Complete, a concrete migration boundary for 0.6.0/0.6.5, and roadmap/pipeline files that no longer imply MATLAB, STM32CubeIDE, KiCad, or SolidWorks can start before the platform rewrite is proven.

## Stage 0 - Baseline And Safety

Purpose: preserve the working product before changing the foundation.

- [x] Record the current Arduino/Codex workflow as the compatibility baseline.
- [x] Record current release/version state and active branch expectations.
- [x] Run regression checks and record known limitations.
- [x] Confirm `desktop_app.py` remains the debug/source launcher until shell parity is proven.
- [x] Confirm no commit/tag/push happens unless the user explicitly asks.

Exit condition: there is a known-good baseline that later rewrite work must preserve.

## Stage 1 - Documentation And Roadmap Taxonomy

Purpose: keep user-facing docs separate from internal planning before the rewrite generates more architecture notes.

- [x] Move roadmap, pipelines, and evidence into `dev_notes/`.
- [x] Keep release/legal/user docs under `docs/`.
- [x] Add or update index files so packaged docs and internal notes have clear owners.
- [x] Remove references that still treat roadmap/pipeline files as shipped user documentation.
- [x] Keep one evidence file per version unless a later release explicitly needs deeper audit artifacts.

Exit condition: docs are classified by audience and future architecture notes will not pollute release docs.

## Stage 2 - Python Ownership Audit

Purpose: identify what Python currently owns and what must move.

- [x] Classify Python modules as launcher, HTTP/local API bridge, target adapter, runtime manager, diagnostics, fallback, or migration candidate.
- [x] Identify hot paths currently owned by Python: process/window detection, workspace scans, hashing/cache keys, diff/hunk parsing, task orchestration, and file sync.
- [x] Identify mixed-ownership modules that should be split before or during 0.6.0.
- [x] Record which paths must keep Python fallback behavior during migration.

Exit condition: Python reduction is measurable and staged, not ad hoc.

## Stage 3 - Frontend Ownership Audit

Purpose: prevent the web UI from becoming another monolith during the shell rewrite.

- [x] Classify frontend code by workbench state, target explorer, editor/review surface, runtime/Codex panel, command palette, settings, diagnostics, and shared UI primitives.
- [x] Keep the frontend static/no-build until the new shell requires a build step.
- [x] Record UI areas that must survive shell migration: activity bar, explorer toggle, editor/review, verify/history, Codex panel, command palette, status bar, settings, and theme behavior.
- [x] Treat VS Code-style UI patterns as the long-term visual direction for engineering workflows.

Exit condition: 0.6.0 can migrate shell/core boundaries without redesigning the UI blindly.

## Stage 4 - Rewrite Boundary Decision

Purpose: decide what will actually be rebuilt.

- [x] Set Tauri + Rust + current web workbench as the preferred long-term shell direction.
- [x] Keep Electron as fallback only if Tauri blocks required windowing, packaging, or WebView behavior.
- [x] Define the first rewrite boundary: shell abstraction, local API/IPC contract, core backend boundary, target adapter host, native helper adapter, runtime provider boundary, and Python compatibility bridge.
- [x] Move new target work out of 0.8.x/0.9.x until after Core Complete.
- [x] Add `0.6.5` as the explicit Python decomposition release.

Exit condition: the roadmap has a real rewrite sequence instead of feature expansion on the prototype foundation.

## Stage 5 - Pipeline Realignment

Purpose: make the next pipelines executable.

- [x] Rewrite `dev_notes/roadmap/TALOS_ROADMAP.md` around the architecture pivot.
- [x] Rewrite `dev_notes/pipelines/TALOS_PIPELINE_055.md` as the pivot patch.
- [x] Rewrite `dev_notes/pipelines/TALOS_PIPELINE_060.md` as the core runtime rewrite foundation.
- [x] Add `dev_notes/pipelines/TALOS_PIPELINE_065.md` for Python decomposition.
- [x] Create later pipelines only when their version starts; do not create placeholder target pipelines before Core Complete.

Exit condition: 0.6.0 and 0.6.5 describe real implementation work and target expansion is gated behind Core Complete.

## Stage 6 - Regression And Handoff

Purpose: close the pivot without destabilizing the app.

- [x] Run full automated regression.
- [x] Run architecture health checks.
- [x] Run a lightweight source/debug launch check.
- [x] Record final pivot evidence in `dev_notes/evidence/TALOS_055_EVIDENCE.md`.
- [x] Confirm release notes/README do not need user-facing wording changes for this internal architecture pivot patch.

Exit condition: 0.5.5 can hand off to 0.6.0 with a stable baseline and a corrected architecture roadmap.
