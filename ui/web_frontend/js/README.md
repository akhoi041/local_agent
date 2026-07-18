# Talos Frontend Modules

Talos keeps the web frontend static and no-build. Use browser-native ES modules only; do not add Node, bundlers, transpilers, or generated frontend artifacts for this layer.

## Current Modules

- `state.js`: shared mutable runtime state. Keep it data-only.
- `config.js`: constants, storage keys, command/menu definitions, timing values, and theme definitions.
- `dom.js`: DOM query helpers and local API fetch helper.
- `app.js`: current workbench orchestrator. It still owns feature wiring while the split is incremental.
- `styles/tokens.css`: theme, density, contrast, and scrollbar tokens.
- `styles.css`: layout, component, editor, menu, Codex, forms, and utility rules.

## Feature Owners To Split Next

- Layout/workbench: shell panes, splitters, responsive panel behavior, status bar.
- Arduino explorer: sketch selection, workspace profile, source file list.
- Editor/review: local editor, review mode, find, hunk actions, save/verify flow.
- Command palette/menu: app menu, command search, keyboard dispatch.
- Codex panel: context preview, chat shell, runtime gate, review activity.
- Diagnostics/history: verify output, run history, evidence, support bundle.
- Settings: appearance, runtime selection, privacy/diagnostics controls.

## Guardrails

- Keep `index.html` mostly structural.
- Keep shared UI primitives centralized before feature-specific CSS splitting.
- Preserve VS Code-style workflow and keyboard behavior during each split.
- Add a smoke or unit test whenever module ownership changes.
