# Talos UI/UX Smoke Checklist

Use this checklist before treating a Talos 0.4.0 UI change as ready for broader testers.

## Window Sizes

Capture or manually inspect these sizes:

- Normal desktop window.
- Maximized desktop window.
- Narrow desktop window near the supported minimum.
- Codex panel visible.
- Codex panel hidden.
- Explorer, editor, verify output, and Codex splitters adjusted.

Pass criteria:

- No action bar overflow hides critical commands.
- Text remains readable and does not overlap.
- The selected file remains visible in Files instead of relying on a large editor tab.
- Verify output and Codex composer remain reachable.
- Scrollbars appear inside the relevant panel, not across the entire app.

## Main Arduino States

Inspect these workspace states:

- No open Arduino sketches.
- One selected `.ino` sketch.
- Multi-file sketch with `.ino`, `.h`, and `.cpp` files.
- Board detected.
- Board missing or ambiguous.
- Environment profile collapsed and expanded.

Pass criteria:

- Open sketches are selectable without layout jump.
- Files highlight the active file.
- Board/profile readiness is understandable.
- No information panel is empty or redundant.

## Editor And Review States

Inspect these editor states:

- Review mode.
- Edit in Talos mode.
- Dirty editor before save.
- Saved file.
- Codex staged change.
- Codex conflict recovery.
- Rollback available and unavailable.

Pass criteria:

- Primary action is visually clear.
- Dangerous or unavailable actions are disabled.
- Review/diff colors are readable in light, dark, and neutral themes.
- Save File remains the only action that writes Talos editor content back to Arduino files.

## Verify And History States

Inspect:

- Verify not run.
- Verify pending/cancellable.
- Verify passed.
- Verify failed.
- History filtered by all, verify, Codex, saved, conflict, rollback, and release evidence.
- Copy Issues, Copy All, Copy Support, and Record Evidence.

Pass criteria:

- Current verify result resets cleanly.
- History filters do not hide the active result unexpectedly.
- Copy buttons are grouped with the data they copy.

## Codex Panel States

Inspect:

- Codex disconnected.
- Codex connecting/reconnecting.
- Empty task history.
- Existing task history.
- New thread.
- Active thread with user and Codex messages.
- Context preview open and closed.

Pass criteria:

- History list fills the panel without fixed-width gaps.
- New chat and close controls remain reachable.
- Composer stays docked and usable when the panel is resized.

## Settings And Appearance

Inspect:

- Light, dark, and neutral themes.
- System-sync preview option.
- High contrast option.
- Editor font size and density preferences.
- Diagnostics disabled.
- Diagnostics enabled with preview export.

Pass criteria:

- Settings feels like a product surface, not a debug form.
- Appearance changes are understandable before saving.
- Diagnostics copy clearly states local-only behavior and redaction boundaries.
