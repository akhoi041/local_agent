# Talos ChatGPT Handoff Note

Purpose: let ChatGPT continue Talos work while Codex context is low, then let Codex return later and quickly audit what changed.

## Current Project Direction

Talos is a local AI control layer between AI runtimes and external engineering tools.

The long-term architecture is:

```text
Talos Desktop Shell
-> Web Workbench
-> Local API/IPC Contract
-> Core Backend
-> Native Helper Layer
-> Runtime Providers
-> Target Adapters
```

Arduino IDE is the first reference target. Talos must not become an Arduino-only helper, a firmware uploader, a replacement IDE, or a model host. The real target app remains the owner of domain operations; Talos provides controlled context, review, verify, rollback, diagnostics, and runtime bridging.

## Current Branch And Version

- Current branch: `develop/0.7.0`
- Last closed version: `0.6.5 Beta`
- Active version to continue: `0.7.0 Beta`
- Active roadmap: `dev_notes/roadmap/TALOS_ROADMAP.md`
- Active completed pipeline: `dev_notes/pipelines/TALOS_PIPELINE_065.md`
- Active pipeline: `dev_notes/pipelines/TALOS_PIPELINE_070.md`
- Current evidence: `dev_notes/evidence/TALOS_065_EVIDENCE.md`
- Next evidence file to create/update: `dev_notes/evidence/TALOS_070_EVIDENCE.md`

## Git Handoff State

0.6.5 has been closed on GitHub:

- Commit: `c983ffc` (`Complete Talos 0.6.5 handoff`)
- Develop branch pushed: `origin/develop/0.6.5`
- Release branch pushed: `origin/release/0.6.5-beta`
- Tag pushed: `origin/v0.6.5-beta`

0.7.0 has been opened locally as `develop/0.7.0`. If this note is being read after the branch handoff commit, `origin/develop/0.7.0` should also exist.

## Important Working Rules

- Do not commit, push, tag, merge, or close branches unless the user explicitly asks.
- Keep `desktop_app.py` as the source/debug launcher.
- Keep Python as compatibility/debug bridge while moving product behavior behind core/native/adapter boundaries.
- Do not start MATLAB, STM32CubeIDE, KiCad, SolidWorks, or other target work before Arduino is ported and hardened on the new adapter architecture.
- Avoid large downloads or dependency installs unless the user explicitly approves.
- Prefer small targeted checks over heavy full regression when only docs changed.
- If code is edited manually, use small scoped patches and preserve existing style.
- Keep changes easy for Codex to audit later.

## 0.6.5 Status

0.6.5 is a Python-decomposition release. It reduced or contained Python-heavy ownership by introducing/reusing boundaries for:

- Detection: native-backed/fallback detection contract.
- Workspace scan: reusable metadata scanner.
- Cache keys: centralized deterministic cache-key helper.
- Diff/hunks: target-neutral helper.
- Task orchestration: centralized long-running task state.
- Runtime discovery: provider-configured discovery and pinned runtime behavior.

Stage 8 is complete and hands off to 0.7.0.

Latest validation:

- Stage 7 full regression passed before handoff: `158 tests`.
- Stage 8 only changed roadmap, pipeline, and evidence.
- `git diff --check` passed, with only expected CRLF warnings.

## Current Uncommitted Work

At the 0.6.5 handoff point, these paths were committed into `c983ffc`:

```text
M  config/default_config.json
M  dev_notes/evidence/TALOS_065_EVIDENCE.md
M  dev_notes/pipelines/TALOS_PIPELINE_065.md
M  dev_notes/roadmap/TALOS_ROADMAP.md
M  talos/codex_runtime.py
M  talos/core.py
M  talos/stage_baseline.py
M  tests/test_desktop_app.py
?? dev_notes/pipelines/TALOS_PIPELINE_070.md
?? talos/runtime_discovery.py
```

Before continuing 0.7.0, run:

```powershell
git status --short
git diff --stat
```

Do not assume this list is still current if the user or another assistant has changed files.

## 0.7.0 Intended Work

0.7.0 should port Arduino onto the new adapter/core contracts. It should not be another planning-only version.

Primary goal:

```text
Arduino adapter port + parity proof + adapter-owned workflow behavior.
```

Pipeline: `dev_notes/pipelines/TALOS_PIPELINE_070.md`

Expected stages:

1. Adapter baseline and scope lock.
2. Arduino adapter contract.
3. Discovery and workspace mapping port.
4. Board/profile/environment port.
5. Verify and cache parity.
6. Codex context and change review port.
7. UI parity and usability smoke.
8. Regression gate.

0.7.0 is complete only when Arduino behavior is adapter-owned, parity-tested, and ready for 0.7.5 daily-use hardening.

## Coding Style And Product Preferences

- UI direction: VS Code-like workbench behavior is preferred for coding surfaces, panels, command palette, status bar, keyboard shortcuts, and dark/light consistency.
- GitHub-style polish is acceptable for settings/help/product pages, but not at the cost of coding efficiency.
- Avoid decorative UI. Prioritize dense, clear, engineering-focused layouts.
- Keep user-visible failure states honest. Missing Codex runtime is informational and must not make Arduino workspace look broken.
- Keep runtime credentials outside Talos. Talos may display safe runtime metadata but must not persist tokens or credentials.
- Use explicit context preview and user-scoped access. Talos must not silently scan the whole machine.
- Review before write and rollback always.

## How ChatGPT Should Record Changes

If ChatGPT changes anything, append a section below using this format:

```markdown
## ChatGPT Change Log - YYYY-MM-DD HH:MM

Branch:

Goal:

Files changed:

- `path`: short reason.

Validation:

- Command/result or manual check.

Risks / follow-up for Codex:

- Short note for Codex to audit later.
```

Also update the relevant pipeline and evidence file when a stage is completed.

Do not silently mark a stage complete if the work was only planned. A stage may be documentation-only only when the pipeline explicitly says so.

## First Recommended Next Step

If the user asks ChatGPT to continue implementation, start with `dev_notes/pipelines/TALOS_PIPELINE_070.md` Stage 0.

Use lightweight checks first:

```powershell
git status --short
python -B -m unittest -q tests.test_desktop_app
```

Run full/manual app checks only when UI/runtime/Arduino behavior changes.
