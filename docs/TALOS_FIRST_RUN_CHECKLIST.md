# Talos First-Run Checklist

Use this checklist when a new tester opens Talos for the first time.

## A. Simple `.ino` Sketch

- [ ] Open Arduino IDE.
- [ ] Create or open a simple sketch such as `Blink.ino`.
- [ ] Save the sketch so it has a real sketch folder.
- [ ] Select an Arduino board in Arduino IDE.
- [ ] Open Talos and go to `Arduino`.
- [ ] Press `Refresh`.
- [ ] Confirm the sketch appears in `Open sketches`.
- [ ] Select the sketch.
- [ ] Confirm `Sketch folder` points to the expected folder.
- [ ] Confirm `Board` is detected or manually saved.
- [ ] Select the `.ino` file from `Files`.
- [ ] Run `Verify Sandbox`.
- [ ] Confirm the result is either `PASSED` or a clear Arduino CLI error.
- [ ] Open `History` and confirm the verify run is listed.

Pass condition: Talos can detect, inspect, and sandbox-verify the saved `.ino` sketch without writing unexpected changes to the real sketch folder.

## B. Multi-File Sketch

- [ ] Open a sketch with one `.ino` file and at least one `.h` or `.cpp` tab.
- [ ] Confirm Arduino IDE shows those tabs.
- [ ] In Talos, press `Refresh`.
- [ ] Select the sketch.
- [ ] Confirm the `Files` list includes the `.ino`, `.h`, and `.cpp` files.
- [ ] Select each source file and confirm its content appears in review mode.
- [ ] Run `Verify Sandbox`.
- [ ] Confirm missing libraries, board errors, or compile failures are shown clearly if the sketch does not pass.

Pass condition: Talos scopes the workspace to the selected sketch folder and sees all source tabs used by Arduino IDE.

## C. Codex Review Flow

- [ ] Select a source file.
- [ ] Open the Codex panel.
- [ ] Ask Codex for a small safe change, such as adding a comment or improving a constant name.
- [ ] Confirm the proposed change appears as a staged review.
- [ ] Confirm the real Arduino sketch file has not changed yet.
- [ ] Apply the change to the Talos editor only if it is correct.
- [ ] Run `Verify Change` or `Verify Sandbox`.
- [ ] Use `Save` or `Save + Verify` only when you want to write the Talos draft to the real Arduino file.

Pass condition: Codex changes remain staged until the user reviews and saves them.

## D. Recovery Sanity Check

- [ ] Start a Talos edit or staged Codex review.
- [ ] Change the same file in Arduino IDE and save it.
- [ ] Return to Talos and refresh.
- [ ] Confirm Talos does not silently overwrite the Arduino IDE version.
- [ ] Use `Keep Arduino Version` or reject the staged change.

Pass condition: external Arduino edits are protected from silent overwrite.

## E. Support Report

- [ ] Run one verify.
- [ ] Open `History`.
- [ ] Use `Copy Support`.
- [ ] Confirm the copied support text avoids unnecessary source code, account details, and raw local paths.

Pass condition: a tester can collect useful debug evidence without copying scattered panels by hand.
