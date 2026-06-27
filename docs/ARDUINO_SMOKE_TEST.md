# Arduino Smoke Test

This smoke test closes the Arduino MVP loop. Run it before treating Talos as ready for daily Arduino work or before starting another app integration.

## Prerequisites

- Arduino IDE is installed.
- At least one saved Arduino sketch folder exists. The folder must contain a main `.ino` file with the same name as the folder.
- `arduino-cli` is available either from PATH or from the bundled Arduino IDE location.
- Talos project verification passes:

```powershell
.\scripts\check.ps1
```

## Test Sketch

Use a small saved sketch first:

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  delay(1000);
}
```

Optional second-pass test: add a `.h` or `.cpp` tab in the same sketch folder and include it from the `.ino` file.

## Setup

1. Create two saved sketches with different folder names. Use different boards when available.
2. Keep one sketch small and add a `.h` or `.cpp` tab to the other.
3. Open both sketches in separate Arduino IDE windows.
4. Select a real board in each Arduino IDE window.
5. Start Talos:

```powershell
.\scripts\launch_desktop.ps1
```

6. In Talos, open the Arduino workspace view and leave the Codex panel visible.

## MVP Smoke-Test Matrix

Mark every row `PASS`, `FAIL`, or `BLOCKED`; record the evidence in the result log. Stop before any save that would overwrite code you do not intend to change.

| ID | Scenario | Steps | Expected result and evidence |
| --- | --- | --- | --- |
| D1 | Multiple Arduino windows | Refresh Explorer with both IDE windows open, then select each sketch in turn. | Both sketches appear as separate candidates. Sketch folder and board switch with the selection; no selection reverts during refresh. Screenshot or note both names and boards. |
| D2 | Source-tab discovery | Select the sketch containing `.ino`, `.h`, and `.cpp` files. | Files list contains every source tab and opens the selected file in Change Workspace. Note the source-tab count. |
| P1 | Environment profile | Expand **Environment profile**, set serial port, baud rate, a harmless build flag such as `-DTEST_SMOKE`, and library metadata; save. Select the other sketch, then return. | Values are restored only for the original sketch. Its FQBN is used for verify and Codex context. Record the profile values. |
| V1 | Sandbox verify | Click **Verify Sandbox**. | Output resets to one current result, command compiles beneath the Talos per-user app-data sandbox, and does not compile the real sketch folder. Copy the result or record status/timings. |
| C1 | Staged Codex change | Ask Codex for a small change with edits enabled. Open the resulting Change Review. | The real Arduino file remains unchanged. The review identifies changed file(s) and displays a colored diff. Record patch ID or timeline entry. |
| C2 | Hunk decision | For a multi-hunk patch, apply one hunk and reject another. | Only accepted hunk content reaches the Talos editor; rejected content does not. Save is still required before Arduino IDE changes. Record selected hunk outcomes. |
| C3 | Staged verification | Before saving a pending change, click **Verify Change**. | Talos compiles a merged sandbox copy of the staged change. The real Arduino file timestamp/content remains unchanged. Record pass/fail. |
| S1 | Save and verify | Apply a reviewed change to the Talos editor, then use **Save & Verify**. | Talos creates a checkpoint, writes only the chosen source file to the real sketch, then runs a new sandbox verify. Timeline shows save and verify events. |
| R1 | Rollback | After a successful Talos save, click **Rollback** for that file. | The file returns to its pre-save checkpoint only when it has not been changed externally. Record the restored content marker. |
| X1 | External-change conflict | Keep a Codex patch staged. Edit the same file in Arduino IDE or another editor and save, then refresh Talos. | Talos shows the three-way conflict view and does not overwrite the external change. **Keep Arduino Version** preserves disk content and rejects the conflicting patch. |
| O1 | Output and history | Run another verify after the above cases, then open **History**. | Verify Output contains only the latest run; History contains prior events. Copy Issues and Copy All are selectable and copyable. |

## Pass Criteria

- Every matrix row D1 through O1 is `PASS`, or any `BLOCKED` row has a documented hardware/tooling reason.
- Arduino IDE is detected without manually typing the sketch path.
- The selected sketch does not jump back to another sketch during refresh.
- File edits stay scoped inside the selected sketch folder.
- Verify Sandbox compiles a copied sandbox folder, not the original folder.
- Codex changes remain staged until an explicit review/apply/save decision.
- Conflict and rollback paths refuse to silently overwrite external work.

## Fail Conditions

- Talos shows a closed or stale sketch after Arduino IDE has closed it.
- Talos picks the wrong board for the selected sketch.
- Verify Sandbox compiles the original sketch folder.
- Verify Output mixes old history cards into the current result.
- Codex can edit outside the selected sketch folder.
- Talos UI becomes unresponsive during detection, verify, or Codex polling.

## Result Log

Record the latest manual run here:

```text
Date:
Arduino IDE version:
Sketches and boards:
Talos native available:
Profile values:
Matrix results (D1, D2, P1, V1, C1, C2, C3, S1, R1, X1, O1):
Verify result and timings:
Codex patch / hunk result:
Conflict / rollback result:
Evidence location (screenshots or copied output):
Notes and blocked cases:
```
