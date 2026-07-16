# Talos Pipeline - Version 0.5.5 Beta

Purpose: slim the project architecture after the Codex Runtime Manager and before new target apps. This release should make Talos easier to maintain, faster to run, and clearer to document without breaking the working Arduino/Codex path.

```text
0.5.5 Beta = documentation taxonomy + Python boundary cleanup + frontend module split + native-helper performance plan.
```

## Exit Condition

Talos 0.5.5 is complete when the repo has a clear documentation taxonomy, the largest Python/frontend modules have explicit ownership boundaries, performance-sensitive work has native-helper candidates with benchmark evidence, and the existing Arduino/Codex workflow still passes regression and manual smoke checks.

## Stage 0 - Baseline And Safety

Purpose: measure before changing structure.

- [ ] Create a 0.5.5 baseline note that records file sizes, module responsibilities, test count, startup path, verify path, and known slow paths.
- [ ] Run the full regression suite from a clean working tree.
- [ ] Record the current Arduino/Codex smoke path as the no-regression reference.
- [ ] Confirm all release scripts, installer scripts, and in-app links that reference `docs/` files.
- [ ] Define rollback instructions for documentation moves and module splits.

Exit condition: the team knows what must not regress before slimming starts.

## Stage 1 - Documentation Taxonomy

Purpose: reduce documentation sprawl without breaking packaged builds.

- [ ] Keep user-facing and release/legal docs at stable paths until scripts/tests are updated.
- [ ] Use `docs/DOCS_INDEX.md` as the source of truth for active, release/legal, validation/evidence, and pipeline docs.
- [ ] Add a docs-link checker for README, in-app help links, release packaging, and installer packaging.
- [ ] Move validation artifacts to `docs/evidence/` only after scripts/tests/in-app links support the new paths.
- [ ] Move stale planning notes to `docs/archive/` only when they are not referenced by runtime, packaging, or tests.
- [ ] Update release packaging to include only required user/release docs plus explicit evidence docs.

Exit condition: documentation is navigable and no packaged/in-app doc links are broken.

## Stage 2 - Python Boundary Cleanup

Purpose: reduce Python from broad app logic toward bridge/orchestration layers.

- [ ] Split `talos/arduino.py` into smaller ownership units: discovery, workspace mapping, board/profile parsing, file operations, sandbox verify, and target-contract helpers.
- [ ] Split `talos/codex_bridge.py` into runtime/session, context packaging, message transport, review state, and patch/action handling.
- [ ] Split `talos/server.py` route handling from business logic so HTTP endpoints stay thin.
- [ ] Keep `desktop_app.py` as the lightweight debug launcher and desktop bootstrap only.
- [ ] Add focused tests for each extracted module before deleting old inline logic.

Exit condition: Python modules have clear boundaries and no single module owns unrelated mechanics.

## Stage 3 - Frontend Module Split

Purpose: keep the web frontend maintainable before adding more target UIs.

- [ ] Split `ui/web_frontend/app.js` into modules for state/api, layout, editor/review, command palette/menu, Codex panel, Arduino explorer, diagnostics/history, and settings.
- [ ] Split large CSS sections into theme tokens, layout, workbench panes, editor, Codex, forms/buttons, menus, and utilities.
- [ ] Keep `index.html` as structure only where practical, with templates/components moved into JS modules if that reduces repetition.
- [ ] Preserve the current VS Code-style workflow and keyboard behavior.
- [ ] Add tests or smoke checks for module loading and core UI actions.

Exit condition: UI behavior is unchanged, but frontend responsibilities are easier to extend per target.

## Stage 4 - Native Helper Candidate Plan

Purpose: move only measurable hot paths out of Python.

- [ ] Benchmark detection refresh, workspace scanning, hashing/cache-key generation, diff/hunk parsing, and process/window queries.
- [ ] Identify which hot paths should move to `native/talos_native.c` or a future Rust/C++ helper.
- [ ] Define native API boundaries that are stable across Arduino, MATLAB, STM32CubeIDE, KiCad, and SolidWorks.
- [ ] Keep Python fallbacks for every native helper path.
- [ ] Add build/fallback verification so missing native binaries degrade gracefully.

Exit condition: native work is justified by measurements and has safe fallbacks.

## Stage 5 - Performance And Size Guardrails

Purpose: stop the app from growing back into a slow monolith.

- [ ] Add module-size and responsibility checks for the largest Python and frontend files.
- [ ] Add timing guardrails for startup, state refresh, Arduino detection, verify cache lookup, support bundle generation, and diagnostics export.
- [ ] Add a developer command or script that reports architecture health before release.
- [ ] Record acceptable thresholds and blocked-case handling in release evidence.

Exit condition: future versions can detect architecture drift before it hurts users.

## Stage 6 - Regression And Release Notes

Purpose: finish slimming without destabilizing the product.

- [ ] Run full automated checks.
- [ ] Run manual Arduino/Codex smoke checks.
- [ ] Verify installed-app packaging still includes required docs and native binaries.
- [ ] Update README, roadmap, release notes, and support docs with the new architecture boundaries.
- [ ] Record known limitations and any postponed cleanup.

Exit condition: Talos is cleaner internally, still usable externally, and ready for 0.6.0 Arduino reference-target hardening.
