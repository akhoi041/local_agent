# Talos Recovery Guide

Use this guide when Arduino IDE and Talos/Codex may have edited the same sketch at the same time.

## Safety Rules

- Arduino IDE owns the real saved sketch.
- Codex changes stay in Talos review/editor state until you explicitly save them.
- Talos must not overwrite a file that changed outside Talos after a checkpoint or pending Codex review was created.

## If Talos Restarts With An Unfinished Codex Review

1. Choose `Restore Reviews` if you want to continue inspecting the pending Codex changes.
2. Choose `Discard Reviews` if Arduino IDE has the version you want to keep.
3. After restoring, verify the selected file before saving it back to Arduino IDE.

Discarding a review does not edit the Arduino sketch folder.

## If Arduino IDE Changed A File During Codex Review

1. Stop saving from Talos until the conflict is resolved.
2. Use `Keep Arduino Version` when the Arduino IDE file is the source of truth.
3. Use `Draft Merge` only when you need to manually combine the Arduino version and the Codex proposal.
4. Review the merged text in Talos, then verify before `Save File`.

Talos keeps the external Arduino content visible in the conflict panel so the decision is explicit.

## If Rollback Is Needed

1. Roll back only after checking that Arduino IDE has not changed the file since the last Talos save.
2. If Talos refuses rollback, keep the Arduino file and manually copy any needed text from Talos history or Codex review.
3. Run sandbox verify after any recovery save.

Rollback refusal is intentional: it means Talos detected that restoring the checkpoint could overwrite newer external work.

## Safest Manual Path

When unsure, use this order:

1. Copy the current Arduino IDE file to a temporary backup.
2. In Talos, discard or keep external changes instead of applying Codex blindly.
3. Ask Codex to review the current workspace again.
4. Apply only the reviewed changes, verify, then save.
