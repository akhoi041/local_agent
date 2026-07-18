# Talos Pipeline - Version 0.5.5 Beta

Purpose: slim the project architecture after the Codex Runtime Manager and before new target apps. This release should make Talos easier to maintain, faster to run, and clearer to document without breaking the working Arduino/Codex path.

```text
0.5.5 Beta = documentation taxonomy + Python boundary cleanup + frontend module split + native-helper performance plan.
```

Current release evidence: `dev_notes/evidence/TALOS_055_EVIDENCE.md`

## Exit Condition

Talos 0.5.5 is complete when the repo has a clear documentation taxonomy, the largest Python/frontend modules have explicit ownership boundaries, performance-sensitive work has native-helper candidates with benchmark evidence, and the existing Arduino/Codex workflow still passes regression and manual smoke checks.

## Stage 0 - Baseline And Safety

Purpose: measure before changing structure.

- [x] Create a 0.5.5 baseline note that records file sizes, module responsibilities, test count, startup path, verify path, and known slow paths.
- [x] Record a pre-0.5.5 UI consistency audit inside `dev_notes/evidence/TALOS_055_EVIDENCE.md` so visual drift is tracked before frontend splitting starts.
- [x] Run the full regression suite and record the active working-tree state. Clean-tree rerun remains the Stage 6 release gate.
- [x] Record the current Arduino/Codex smoke path as the no-regression reference.
- [x] Confirm all release scripts, installer scripts, and in-app links that reference `docs/` files.
- [x] Define rollback instructions for documentation moves and module splits.

Stage 0 result: complete. The baseline, UI audit, regression output, docs-link baseline, and rollback instructions are recorded in the single 0.5.5 evidence file.

Exit condition: the team knows what must not regress before slimming starts.

## Stage 1 - Documentation Taxonomy

Purpose: reduce documentation sprawl without breaking packaged builds.

- [x] Keep user-facing and release/legal docs at stable paths until scripts/tests are updated.
- [x] Use `docs/DOCS_INDEX.md` as the source of truth for user-facing, release, legal, support, and packaged docs.
- [x] Use `dev_notes/README.md` as the source of truth for internal roadmap, pipeline, and evidence docs.
- [x] Add a docs-link checker for README, in-app help links, release packaging, and installer packaging.
- [x] Keep version evidence in `dev_notes/evidence/` because it is internal release proof, not user-facing documentation.
- [x] Move stale planning notes to `dev_notes/archive/` only when they are not referenced by runtime, packaging, tests, or active pipelines.
- [x] Validate release packaging includes only required user/release docs while internal evidence stays under `dev_notes/evidence/`.

Stage 1 result: complete. `docs/DOCS_INDEX.md` now identifies 0.5.5 as the active pipeline, `dev_notes/README.md` owns internal planning taxonomy, `scripts/check_docs_links.ps1` verifies docs/dev-note references, and `scripts/check.ps1` runs the checker before pipeline status.

Exit condition: documentation is navigable and no packaged/in-app doc links are broken.

## Stage 2 - Python Boundary Cleanup

Purpose: reduce Python from broad app logic toward bridge/orchestration layers.

- [x] Thin `talos/server.py` by moving event bus state, runtime readiness/gates, and `/api/state` composition into focused service modules while keeping route handlers small.
- [x] Define the Arduino boundary through `talos/state_service.py`: discovery snapshots, workspace map/profile state, native process reads, and summary payloads are composed outside the HTTP handler.
- [x] Define the Codex boundary through `talos/runtime_service.py`: runtime/session readiness, blocked-send semantics, reconnect gating, and runtime diagnostics are composed outside the HTTP handler.
- [x] Keep `talos/event_bus.py` as the only owner of transient server event and Arduino watcher state.
- [x] Keep `desktop_app.py` as the lightweight debug launcher and desktop bootstrap only.
- [x] Add focused tests that lock the new service boundaries and preserve compatibility exports for existing routes/UI code.
- [x] Avoid broad rewrites: `talos/arduino.py` and `talos/codex_bridge.py` remain behavior-compatible public owners until deeper native extraction stages.

Stage 2 result: complete. `server.py` now delegates state/runtime/event mechanics to `state_service.py`, `runtime_service.py`, and `event_bus.py`; the public behavior remains covered by regression tests.

Exit condition: Python modules have clear boundaries and no single module owns unrelated mechanics.

## Stage 3 - Frontend Module Split

Purpose: keep the web frontend maintainable before adding more target UIs.

- [x] Split `ui/web_frontend/app.js` foundation into `state`, `config`, and `dom/api` ES modules, and document owners for later feature-level splits.
- [x] Split large CSS foundations by moving theme, density, contrast, and scrollbar tokens into `ui/web_frontend/styles/tokens.css`.
- [x] Keep shared UI primitives centralized before deeper feature-level CSS splitting: button variants, icon buttons, panel/card surfaces, status badges, empty states, toolbar/menu controls, runtime/readiness states, and scrollbars.
- [x] Keep `index.html` as structure only where practical, with script loading moved to browser-native module mode.
- [x] Preserve the current VS Code-style workflow and keyboard behavior.
- [x] Treat custom window/menu remnants, duplicated command wiring, and editor-find complexity as explicit cleanup targets instead of hidden behavior.
- [x] Keep the frontend static and no-build: do not require Node, bundlers, transpilers, or a new packaging pipeline.
- [x] Use browser-native ES modules only where pywebview/source and packaged builds can load them through the existing static server.
- [x] Add tests or smoke checks for module loading and core UI actions.

Exit condition: UI behavior is unchanged, but frontend responsibilities are easier to extend per target.

## Stage 4 - Native Helper Candidate Plan

Purpose: move only measurable hot paths out of Python.

- [ ] Benchmark detection refresh, workspace scanning, hashing/cache-key generation, diff/hunk parsing, and process/window queries.
- [ ] Identify which hot paths should move to `native/talos_native.c` or a future Rust/C++ helper.
- [ ] Define native API boundaries that are stable across Arduino, MATLAB, STM32CubeIDE, KiCad, and SolidWorks.
- [ ] Keep Python fallbacks for every native helper path.
- [ ] Add build/fallback verification so missing native binaries degrade gracefully.
- [ ] Produce a native candidate report for 0.5.5; do not migrate a path to native unless the benchmark shows clear user-facing benefit and the fallback remains tested.

Exit condition: native work is justified by measurements and has safe fallbacks.

## Stage 5 - Performance And Size Guardrails

Purpose: stop the app from growing back into a slow monolith.

- [ ] Add module-size and responsibility checks for the largest Python and frontend files.
- [ ] Add timing guardrails for startup, state refresh, Arduino detection, verify cache lookup, support bundle generation, and diagnostics export.
- [ ] Add a developer command or script that reports architecture health before release.
- [ ] Record acceptable thresholds and blocked-case handling in release evidence.
- [ ] Set initial size thresholds from the 0.5.5 baseline: no extracted Python module should grow back into a multi-domain file, and frontend modules should stay grouped by ownership rather than by incidental UI order.
- [ ] Record baseline timings and compare against them instead of inventing arbitrary performance targets.

Exit condition: future versions can detect architecture drift before it hurts users.

## Stage 6 - Regression And Release Notes

Purpose: finish slimming without destabilizing the product.

- [ ] Run full automated checks.
- [ ] Run manual Arduino/Codex smoke checks.
- [ ] Verify installed-app packaging still includes required docs and native binaries.
- [ ] Update README, roadmap, release notes, and support docs with the new architecture boundaries.
- [ ] Record known limitations and any postponed cleanup.
- [ ] Prepare release branch/tag instructions, but do not commit, tag, or push unless the user explicitly asks for it.

Exit condition: Talos is cleaner internally, still usable externally, and ready for 0.6.0 Arduino reference-target hardening.
