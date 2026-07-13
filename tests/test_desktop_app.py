import json
import re
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from talos import arduino as arduino_module
from talos import checkpoints as checkpoint_store
from talos import core, native_bridge
from talos import run_history as run_history_store
from talos.arduino_events import ArduinoEventWatcher, is_arduino_window_title
from talos.arduino import (
    cached_compile_result,
    clear_arduino_compile_cache,
    clear_arduino_compile_cache_result,
    compile_cache_key,
    boards_by_window_title,
    codex_context_package,
    copy_workspace_to_sandbox,
    delete_workspace_file,
    discover_arduino_projects,
    environment_profile,
    extract_ino_names,
    format_compile_issue_context,
    parse_compile_output,
    profile_readiness,
    read_workspace_file,
    run_arduino_compile,
    save_environment_profile,
    verify_runtime_status,
    workspace_context,
    workspace_map,
    workspace_summary,
    write_workspace_file,
)
from talos.native_bridge import (
    extract_board_name,
    extract_fqbn,
    native_available,
    parse_process_rows_payload,
    parse_window_rows_payload,
)
from talos.codex_bridge import (
    CODEX_TURN_TIMEOUT_SECONDS,
    CodexBridge,
    THREAD_SANDBOX_MODE,
    build_patch_hunks,
    build_codex_prompt,
    diff_workspace_snapshots,
    messages_from_codex_thread,
    normalize_codex_thread,
    snapshot_workspace,
    staged_patch_files,
)
from talos.checkpoints import (
    create_before_save_checkpoint,
    latest_saved_checkpoint,
    mark_checkpoint_saved,
    rollback_last_checkpoint,
)
from talos.run_history import (
    filtered_run_history,
    record_codex_turn,
    record_patch,
    record_patch_transition,
    record_release_evidence,
    record_verify,
    run_history,
    support_bundle,
)
from talos.diagnostics import diagnostics_export, diagnostics_settings, record_diagnostic, sanitize_payload
from talos.server import state_payload

class TalosArduinoTests(unittest.TestCase):
    def test_codex_prompt_contains_selected_arduino_context(self) -> None:
        prompt = build_codex_prompt(
            "Fix the compile error.",
            {
                "path": r"C:\Sketch\Blink",
                "main_sketch": "Blink.ino",
                "fqbn": "arduino:avr:uno",
                "map": {
                    "source_tab_count": 2,
                    "source_tabs": [{"path": "Blink.ino"}, {"path": "motor.cpp"}],
                    "diagnostics": {
                        "status": "passed",
                        "libraries": [{"name": "Wire", "version": "1.0.0"}],
                        "platforms": [{"name": "arduino:avr", "version": "1.8.6"}],
                    },
                },
            },
            {"path": "Blink.ino", "content": "void setup() {}\n"},
            "ERROR Blink.ino:2:1 - expected declaration",
        )

        self.assertIn("Fix the compile error.", prompt)
        self.assertIn(r"C:\Sketch\Blink", prompt)
        self.assertIn("arduino:avr:uno", prompt)
        self.assertIn("void setup()", prompt)
        self.assertIn("ERROR Blink.ino:2:1", prompt)
        self.assertIn("Talos staging copy", prompt)
        self.assertIn("Source tabs (2): Blink.ino, motor.cpp", prompt)
        self.assertIn("Verified libraries: Wire 1.0.0", prompt)

    def test_arduino_event_filter_and_debounce_only_signal_arduino_windows(self) -> None:
        signals: list[str] = []
        watcher = ArduinoEventWatcher(signals.append, debounce_seconds=60)

        watcher._signal("Untitled - Notepad")
        watcher._signal("Blink.ino | Arduino IDE 2.3.4")
        watcher._signal("Blink.ino | Arduino IDE 2.3.4")

        self.assertFalse(is_arduino_window_title("Untitled - Notepad"))
        self.assertTrue(is_arduino_window_title("Blink.ino | Arduino IDE 2.3.4"))
        self.assertEqual(signals, ["window"])

    def test_codex_prompt_includes_per_sketch_environment_profile(self) -> None:
        prompt = build_codex_prompt(
            "Review this sketch.",
            {
                "path": r"C:\Sketch\Blink",
                "map": {
                    "environment_profile": {
                        "serial_port": "COM7",
                        "baud_rate": 115200,
                        "build_flags": ["-DDEBUG"],
                        "libraries": ["Wire", "ArduinoJson"],
                    },
                },
            },
        )

        self.assertIn("Serial profile: COM7 @ 115200 baud", prompt)
        self.assertIn("Build flags: -DDEBUG", prompt)
        self.assertIn("Profile libraries: Wire, ArduinoJson", prompt)

    def test_codex_context_package_is_scoped_and_classified(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Robot"
            root.mkdir()
            (root / "Robot.ino").write_text("void setup() {}\n", encoding="utf-8")
            (root / "motor.cpp").write_text("void motor() {}\n", encoding="utf-8")
            (root / "motor.h").write_text("#pragma once\n", encoding="utf-8")
            (root / "README.md").write_text("notes\n", encoding="utf-8")
            (root / "secret.bin").write_text("do not send\n", encoding="utf-8")
            (root / ".git").mkdir()
            (root / ".git" / "config").write_text("private\n", encoding="utf-8")

            package = codex_context_package(
                {"arduino_workspace_path": str(root), "arduino_fqbn": "arduino:avr:uno"},
                {"path": "../outside.ino", "content": "outside secret"},
                "Status: passed",
                True,
                "Review.",
            )

            inventory = package["workspace_map"]["file_inventory"]
            self.assertEqual(package["workspace"]["main_sketch"], "Robot.ino")
            self.assertEqual(inventory["categories"]["main_sketch"], ["Robot.ino"])
            self.assertIn("motor.cpp", inventory["categories"]["sources"])
            self.assertIn("motor.h", inventory["categories"]["headers"])
            self.assertIn("README.md", inventory["categories"]["docs"])
            self.assertGreaterEqual(inventory["ignored_count"], 2)
            self.assertFalse(package["active_file"]["included"])
            self.assertTrue(package["scope"]["active_file_rejected"])
            self.assertNotIn("outside secret", json.dumps(package))

    def test_codex_prompt_can_be_read_only(self) -> None:
        prompt = build_codex_prompt("Review only.", allow_edits=False)

        self.assertIn("This turn is read-only.", prompt)

    def test_codex_protocol_uses_legacy_thread_sandbox_enum(self) -> None:
        self.assertEqual(THREAD_SANDBOX_MODE, "workspace-write")
        self.assertEqual(CODEX_TURN_TIMEOUT_SECONDS, 300)

    def test_codex_workspace_snapshot_reports_added_updated_and_deleted_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "update.cpp").write_text("old\n", encoding="utf-8")
            (root / "delete.h").write_text("remove\n", encoding="utf-8")
            before = snapshot_workspace(root)
            (root / "update.cpp").write_text("new\n", encoding="utf-8")
            (root / "delete.h").unlink()
            (root / "add.ino").write_text("void setup() {}\n", encoding="utf-8")

            changes = diff_workspace_snapshots(before, snapshot_workspace(root))

            self.assertEqual(
                [(change["path"], change["kind"]) for change in changes],
                [("add.ino", "add"), ("delete.h", "delete"), ("update.cpp", "update")],
            )

    def test_codex_patch_tracking_supports_an_initially_empty_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            staging = Path(tmp) / "staging"
            root.mkdir()
            staging.mkdir()
            bridge = CodexBridge(persist_reviews=False)
            bridge._turn_workspace = str(root)
            bridge._turn_staging_workspace = str(staging)
            bridge._turn_track_changes = True
            bridge._turn_snapshot = snapshot_workspace(staging)
            (staging / "created.ino").write_text("void setup() {}\n", encoding="utf-8")

            bridge._finalize_turn_patch()
            status = bridge.status(start=False)

            self.assertEqual(status["patch_revision"], 1)
            self.assertEqual(status["patch_event_revision"], 1)
            self.assertEqual(status["patches"][0]["files"][0]["path"], "created.ino")
            self.assertEqual(status["patches"][0]["files"][0]["kind"], "add")
            self.assertEqual(status["patches"][0]["files"][0]["review_status"], "staged")
            self.assertEqual(status["patches"][0]["review_status"], "staged")
            self.assertFalse((root / "created.ino").exists())

    def test_codex_thread_changes_do_not_emit_patch_events(self) -> None:
        bridge = CodexBridge(persist_reviews=False)
        bridge.new_thread()

        status = bridge.status(start=False)
        self.assertEqual(status["patch_event_revision"], 0)

    def test_codex_review_patch_moves_one_file_to_editor_without_writing_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "Sketch.ino"
            target.write_text("old\n", encoding="utf-8")
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append(
                {
                    "id": "patch-1",
                    "workspace": str(root),
                    "review_status": "staged",
                    "files": [{"path": "Sketch.ino", "kind": "update", "content": "new\n", "review_status": "staged"}],
                }
            )

            reviewed = bridge.review_patch("patch-1", str(root), "Sketch.ino")
            self.assertTrue(reviewed["ok"])
            self.assertEqual(bridge._patches[0]["files"][0]["review_status"], "reviewing")

            result = bridge.apply_patch("patch-1", str(root), "Sketch.ino")

            self.assertTrue(result["ok"])
            self.assertEqual(target.read_text(encoding="utf-8"), "old\n")
            self.assertEqual(result["file"]["content"], "new\n")
            self.assertEqual(bridge._patches[0]["files"][0]["review_status"], "applied-to-editor")
            self.assertEqual(bridge._patches[0]["review_status"], "applied-to-editor")

            saved = bridge.mark_patch_saved(str(root), "Sketch.ino")

            self.assertTrue(saved["ok"])
            self.assertTrue(saved["saved"])
            self.assertEqual(bridge._patches[0]["files"][0]["review_status"], "saved")
            self.assertEqual(bridge._patches[0]["review_status"], "saved")

    def test_codex_hunk_review_applies_only_the_selected_hunk(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = "first\nkeep\nsecond\n"
            after = "FIRST\nkeep\nSECOND\n"
            hunks = build_patch_hunks(before, after)
            self.assertEqual(len(hunks), 2)
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append(
                {
                    "id": "patch-hunks",
                    "workspace": str(root),
                    "review_status": "staged",
                    "files": [{
                        "path": "Sketch.ino",
                        "kind": "update",
                        "base_content": before,
                        "content": after,
                        "review_status": "staged",
                        "hunks": hunks,
                    }],
                }
            )

            result = bridge.apply_hunk("patch-hunks", str(root), "Sketch.ino", hunks[0]["id"])

            self.assertTrue(result["ok"])
            statuses = [hunk["review_status"] for hunk in bridge._patches[0]["files"][0]["hunks"]]
            self.assertEqual(statuses, ["applied-to-editor", "staged"])
            self.assertEqual(bridge._patches[0]["files"][0]["review_status"], "reviewing")

            applied = bridge.apply_all("patch-hunks", str(root))

            self.assertTrue(applied["ok"])
            self.assertEqual(applied["changed"], 1)
            file = bridge._patches[0]["files"][0]
            self.assertEqual(file["review_status"], "applied-to-editor")
            self.assertEqual(file["editor_content"], after)

    def test_codex_hunk_builder_fast_paths_add_delete_and_equal_files(self) -> None:
        self.assertEqual(build_patch_hunks("same\n", "same\n"), [])
        added = build_patch_hunks("", "one\ntwo\n")
        deleted = build_patch_hunks("one\ntwo\n", "")

        self.assertEqual(added[0]["kind"], "insert")
        self.assertEqual(added[0]["new_lines"], ["one", "two"])
        self.assertEqual(deleted[0]["kind"], "delete")
        self.assertEqual(deleted[0]["old_lines"], ["one", "two"])

    def test_codex_unfinished_reviews_persist_until_restored_or_discarded(self) -> None:
        with TemporaryDirectory() as tmp:
            review_path = Path(tmp) / "codex_reviews.json"
            workspace = Path(tmp) / "Sketch"
            workspace.mkdir()
            patch_item = {
                "id": "patch-restore",
                "workspace": str(workspace),
                "review_status": "reviewing",
                "files": [{"path": "Sketch.ino", "kind": "update", "review_status": "reviewing"}],
            }

            with patch("talos.codex_bridge.REVIEW_STATE_PATH", review_path):
                bridge = CodexBridge()
                bridge._patches.append(patch_item)
                bridge._persist_reviews_locked()

                restored_bridge = CodexBridge()
                status = restored_bridge.status(start=False)
                self.assertTrue(status["review_recovery"]["pending"])
                self.assertEqual(status["review_recovery"]["count"], 1)

                restored = restored_bridge.restore_reviews()
                self.assertTrue(restored["ok"])
                self.assertEqual(restored["restored"], 1)
                self.assertFalse(restored_bridge.status(start=False)["review_recovery"]["pending"])

                discarded = restored_bridge.discard_reviews()
                self.assertTrue(discarded["ok"])
                self.assertEqual(discarded["discarded"], 1)
                self.assertEqual(restored_bridge.status(start=False)["patches"], [])

    def test_release_recovery_keeps_external_arduino_change_after_restart(self) -> None:
        with TemporaryDirectory() as tmp:
            review_path = Path(tmp) / "codex_reviews.json"
            workspace = Path(tmp) / "RecoverySketch"
            staging = Path(tmp) / "RecoverySketch_staging"
            workspace.mkdir()
            staging.mkdir()
            source_file = workspace / "RecoverySketch.ino"
            source_file.write_text("before\n", encoding="utf-8")
            (staging / "RecoverySketch.ino").write_text("codex change\n", encoding="utf-8")
            files = staged_patch_files(workspace, staging, [{"path": "RecoverySketch.ino", "kind": "update"}])

            with patch("talos.codex_bridge.REVIEW_STATE_PATH", review_path):
                bridge = CodexBridge()
                bridge._patches.append({
                    "id": "patch-recovery-smoke",
                    "workspace": str(workspace),
                    "staging_workspace": str(staging),
                    "review_status": "staged",
                    "files": files,
                })
                bridge._persist_reviews_locked()

                restarted_bridge = CodexBridge()
                recovery = restarted_bridge.status(start=False)["review_recovery"]
                self.assertTrue(recovery["pending"])
                self.assertEqual(recovery["count"], 1)

                restored = restarted_bridge.restore_reviews()
                self.assertEqual(restored["restored"], 1)
                source_file.write_text("external arduino edit\n", encoding="utf-8")

                conflict_status = restarted_bridge.status(start=False)
                self.assertEqual(conflict_status["patches"][0]["files"][0]["review_status"], "conflict")
                kept = restarted_bridge.keep_external_conflict(
                    "patch-recovery-smoke",
                    str(workspace),
                    "RecoverySketch.ino",
                )

            self.assertTrue(kept["ok"])
            self.assertEqual(kept["file"]["conflict_resolution"], "kept-external")
            self.assertEqual(source_file.read_text(encoding="utf-8"), "external arduino edit\n")

    def test_external_workspace_change_marks_staged_codex_file_as_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            staging = Path(tmp) / "staging"
            root.mkdir()
            staging.mkdir()
            (root / "Sketch.ino").write_text("before\n", encoding="utf-8")
            (staging / "Sketch.ino").write_text("codex change\n", encoding="utf-8")
            files = staged_patch_files(root, staging, [{"path": "Sketch.ino", "kind": "update"}])
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-conflict",
                "workspace": str(root),
                "review_status": "staged",
                "files": files,
            })
            (root / "Sketch.ino").write_text("external edit\n", encoding="utf-8")

            status = bridge.status(start=False)

            self.assertEqual(status["patches"][0]["files"][0]["review_status"], "conflict")
            self.assertEqual(status["patches"][0]["review_status"], "conflict")
            self.assertEqual(status["patches"][0]["files"][0]["conflict_current_content"], "external edit\n")

            resolved = bridge.keep_external_conflict("patch-conflict", str(root), "Sketch.ino")

            self.assertTrue(resolved["ok"])
            self.assertEqual(resolved["file"]["review_status"], "rejected")
            self.assertEqual(resolved["file"]["conflict_resolution"], "kept-external")
            self.assertEqual((root / "Sketch.ino").read_text(encoding="utf-8"), "external edit\n")

    def test_external_workspace_change_marks_editor_applied_codex_file_as_conflict(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            staging = Path(tmp) / "staging"
            root.mkdir()
            staging.mkdir()
            (root / "Sketch.ino").write_text("before\n", encoding="utf-8")
            (staging / "Sketch.ino").write_text("codex change\n", encoding="utf-8")
            files = staged_patch_files(root, staging, [{"path": "Sketch.ino", "kind": "update"}])
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-editor-conflict",
                "workspace": str(root),
                "review_status": "staged",
                "files": files,
            })

            applied = bridge.apply_patch("patch-editor-conflict", str(root), "Sketch.ino")
            self.assertTrue(applied["ok"])
            self.assertEqual(applied["file"]["review_status"], "applied-to-editor")
            (root / "Sketch.ino").write_text("external after editor apply\n", encoding="utf-8")

            status = bridge.status(start=False)

            self.assertEqual(status["patches"][0]["files"][0]["review_status"], "conflict")
            self.assertEqual(status["patches"][0]["review_status"], "conflict")
            self.assertEqual(
                status["patches"][0]["files"][0]["conflict_current_content"],
                "external after editor apply\n",
            )
            self.assertNotIn("editor_content", status["patches"][0]["files"][0])

    def test_conflict_can_create_editor_only_three_way_merge_draft(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            staging = Path(tmp) / "staging"
            root.mkdir()
            staging.mkdir()
            (root / "Sketch.ino").write_text("base\n", encoding="utf-8")
            (staging / "Sketch.ino").write_text("codex\n", encoding="utf-8")
            files = staged_patch_files(root, staging, [{"path": "Sketch.ino", "kind": "update"}])
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-merge",
                "workspace": str(root),
                "review_status": "staged",
                "files": files,
            })
            (root / "Sketch.ino").write_text("arduino\n", encoding="utf-8")
            bridge.status(start=False)

            result = bridge.draft_conflict_merge("patch-merge", str(root), "Sketch.ino")

            self.assertTrue(result["ok"])
            self.assertEqual((root / "Sketch.ino").read_text(encoding="utf-8"), "arduino\n")
            self.assertEqual(result["file"]["review_status"], "applied-to-editor")
            self.assertEqual(result["file"]["conflict_resolution"], "merge-draft")
            self.assertIn("<<<<<<< Arduino current", result["file"]["editor_content"])
            self.assertIn("arduino", result["file"]["editor_content"])
            self.assertIn("codex", result["file"]["editor_content"])

    def test_conflict_can_apply_codex_to_editor_without_writing_arduino_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            staging = Path(tmp) / "staging"
            root.mkdir()
            staging.mkdir()
            (root / "Sketch.ino").write_text("base\n", encoding="utf-8")
            (staging / "Sketch.ino").write_text("codex\n", encoding="utf-8")
            files = staged_patch_files(root, staging, [{"path": "Sketch.ino", "kind": "update"}])
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-apply-conflict",
                "workspace": str(root),
                "review_status": "staged",
                "files": files,
            })
            (root / "Sketch.ino").write_text("arduino\n", encoding="utf-8")
            bridge.status(start=False)

            result = bridge.apply_conflict_to_editor("patch-apply-conflict", str(root), "Sketch.ino")

            self.assertTrue(result["ok"])
            self.assertEqual((root / "Sketch.ino").read_text(encoding="utf-8"), "arduino\n")
            self.assertEqual(result["file"]["review_status"], "applied-to-editor")
            self.assertEqual(result["file"]["conflict_resolution"], "codex-to-editor")
            self.assertEqual(result["file"]["editor_content"], "codex\n")
            self.assertEqual(result["file"]["review_summary"]["applied_to_editor"], 1)

    def test_review_summary_tracks_hunk_state_transitions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = "first\nkeep\nsecond\n"
            after = "FIRST\nkeep\nSECOND\n"
            hunks = build_patch_hunks(before, after)
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-summary",
                "workspace": str(root),
                "review_status": "staged",
                "files": [{
                    "path": "Sketch.ino",
                    "kind": "update",
                    "base_content": before,
                    "content": after,
                    "review_status": "staged",
                    "hunks": hunks,
                }],
            })

            applied = bridge.apply_hunk("patch-summary", str(root), "Sketch.ino", hunks[0]["id"])
            rejected = bridge.reject_hunk("patch-summary", str(root), "Sketch.ino", hunks[1]["id"])

            self.assertTrue(applied["ok"])
            self.assertTrue(rejected["ok"])
            summary = rejected["file"]["review_summary"]
            self.assertEqual(summary["applied_to_editor"], 1)
            self.assertEqual(summary["rejected"], 1)
            self.assertEqual(summary["total"], 2)

    def test_multifile_review_state_survives_active_file_switching(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-multi-review",
                "workspace": str(root),
                "review_status": "staged",
                "files": [
                    {"path": "Main.ino", "kind": "update", "content": "main codex\n", "review_status": "staged"},
                    {"path": "Motor.cpp", "kind": "update", "content": "motor codex\n", "review_status": "staged"},
                ],
            })

            main = bridge.apply_patch("patch-multi-review", str(root), "Main.ino")
            motor = bridge.reject_patch("patch-multi-review", "Motor.cpp")
            status = bridge.status(start=False)

            self.assertTrue(main["ok"])
            self.assertTrue(motor["ok"])
            files = {file["path"]: file for file in status["patches"][0]["files"]}
            self.assertEqual(files["Main.ino"]["review_status"], "applied-to-editor")
            self.assertEqual(files["Motor.cpp"]["review_status"], "rejected")
            self.assertEqual(status["patches"][0]["review_summary"]["applied_to_editor"], 1)
            self.assertEqual(status["patches"][0]["review_summary"]["rejected"], 1)

    def test_staged_patch_sandbox_overrides_use_pending_codex_content_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Sketch"
            root.mkdir()
            bridge = CodexBridge(persist_reviews=False)
            bridge._patches.append({
                "id": "patch-verify",
                "workspace": str(root),
                "review_status": "reviewing",
                "files": [
                    {"path": "Sketch.ino", "kind": "update", "content": "proposed\n", "review_status": "reviewing"},
                    {"path": "ignored.cpp", "kind": "update", "content": "ignored\n", "review_status": "rejected"},
                ],
            })

            result = bridge.staged_sandbox_overrides("patch-verify", str(root))

            self.assertTrue(result["ok"])
            self.assertEqual(result["overrides"], {"Sketch.ino": "proposed\n"})

    def test_frontend_contains_codex_workbench_panel(self) -> None:
        html = (Path(__file__).parents[1] / "ui" / "web_frontend" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="codexPanel"', html)
        self.assertIn('id="codexComposer"', html)
        self.assertIn('id="toggleCodexBtn"', html)
        self.assertIn('id="editInTalosBtn"', html)
        self.assertIn('id="editorModeBadge"', html)
        self.assertIn('id="boardInfoBtn"', html)
        self.assertIn('id="boardInfoPanel"', html)
        self.assertIn('id="environmentProfile"', html)
        self.assertIn('id="saveEnvironmentProfileBtn"', html)
        self.assertIn('id="editorLineNumbers"', html)
        self.assertIn("data-codex-prompt", html)
        self.assertIn('id="codexAllowEdits"', html)
        self.assertIn('id="cancelCodexBtn"', html)
        self.assertNotIn('id="virtualPatchToggleBtn"', html)
        self.assertIn('id="codexDiffPreview"', html)
        self.assertIn('id="codexContextPreview"', html)
        self.assertIn('id="codexContextPreviewText"', html)
        self.assertIn('id="codexReviewRecovery"', html)
        self.assertIn('id="codexReviewRecoveryHint"', html)
        self.assertIn('id="restoreCodexReviewsBtn"', html)
        self.assertIn('id="discardCodexReviewsBtn"', html)
        self.assertIn("Discard Reviews", html)
        self.assertIn("Restore Reviews", html)
        self.assertIn("keep the current Arduino workspace unchanged", html)
        self.assertIn('id="draftConflictMergeBtn"', html)
        self.assertIn('id="applyConflictToEditorBtn"', html)
        self.assertIn('id="rejectConflictCodexBtn"', html)
        self.assertIn('id="codexReviewScope"', html)
        self.assertIn("Apply To Talos Editor", html)
        self.assertIn("Reject Codex", html)
        self.assertNotIn('id="codexHistoryBtn"', html)
        self.assertIn('id="codexBackBtn"', html)
        self.assertIn('id="codexHistoryCount"', html)
        self.assertIn('id="runHistoryTab"', html)
        self.assertIn('id="profileBuildPropertyInput"', html)
        self.assertIn('id="profileReadinessStatus"', html)
        self.assertIn('id="recordEvidenceBtn"', html)
        self.assertIn("docs/TALOS_USER_GUIDE.md", html)
        self.assertIn("docs/TALOS_FIRST_RUN_CHECKLIST.md", html)
        self.assertIn("docs/TALOS_TROUBLESHOOTING.md", html)
        self.assertIn("docs/TALOS_DIAGNOSTICS.md", html)
        self.assertIn("docs/TALOS_INSTALL_LIFECYCLE.md", html)
        self.assertIn("docs/TALOS_UI_UX_CHECKLIST.md", html)
        self.assertIn('id="diagnosticsEnabledInput"', html)
        self.assertIn('id="diagnosticsPreview"', html)
        self.assertIn('id="previewDiagnosticsBtn"', html)
        self.assertIn("docs/TALOS_RECOVERY_GUIDE.md", html)
        self.assertIn("docs/TALOS_SUPPORT_DEBUG.md", html)
        self.assertIn("docs/RELEASE_NOTES.md", html)
        self.assertIn('id="runHistoryFilter"', html)
        self.assertIn('id="runHistorySketchOnly"', html)
        self.assertIn('id="copySupportBundleBtn"', html)
        self.assertIn('id="explorerSplitter"', html)
        self.assertIn('id="codexSplitter"', html)
        self.assertIn('id="verifySplitter"', html)
        self.assertIn('Save + Verify', html)
        self.assertIn('title="Compile the selected sketch in the Talos sandbox"', html)
        self.assertIn("Arduino IDE owns the saved sketch; Save writes Talos edits back.", html)

        script = (Path(__file__).parents[1] / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        self.assertIn("patch_event_revision", script)
        self.assertIn("Codex patch is ready for review.", script)
        self.assertIn("formatDuration", script)
        self.assertIn("timings.compile", script)
        self.assertIn("ACTIVE_FILE_POLL_MS", script)
        self.assertIn("checkActiveFileOnDisk", script)
        self.assertIn("pending_patch", script)
        self.assertIn("previewPendingCodexPatch", script)
        self.assertIn("applyUnifiedDiff", script)
        self.assertIn("Codex change review", script)
        self.assertIn("transientWorkspaceLoss", script)
        self.assertIn("activeFileByWorkspace", script)
        self.assertIn("applyCodexPatch", script)
        self.assertIn("rejectCodexPatch", script)
        self.assertIn("reviewCodexHunk", script)
        self.assertIn("contentWithAppliedHunks", script)
        self.assertIn("reviewStatusLabel", script)
        self.assertIn("reviewSummaryText", script)
        self.assertIn("/api/codex_apply_hunk", script)
        self.assertIn("/api/codex_apply_conflict", script)
        self.assertIn("applyConflictToEditor", script)
        self.assertIn("Reject this hunk", script)
        self.assertIn("Apply this hunk", script)
        self.assertIn("resolveCodexTurn", script)
        self.assertIn("/api/codex_apply_all", script)
        self.assertIn("Codex change conflict detected", script)
        self.assertIn("Save blocked: this file changed outside Talos", script)
        self.assertIn("setCodexConflictMode", script)
        self.assertIn("rollbackWorkspaceFile", script)
        self.assertIn("/api/arduino_rollback", script)
        self.assertIn("saveAndVerifyWorkspace", script)
        self.assertIn("verifySource", script)
        self.assertIn("currentVerifyIsFresh", script)
        self.assertIn("shouldWarnUnverifiedCodexSave", script)
        self.assertIn("editor_override", script)
        self.assertIn("Save + Verify runs sandbox compile before saving", script)
        self.assertIn("patch-timeline", script)
        self.assertIn("verifyCodexPatch", script)
        self.assertIn("/api/codex_verify_patch", script)
        self.assertIn("keepExternalConflict", script)
        self.assertIn("buildCodexContextPreview", script)
        self.assertIn("Profile readiness:", script)
        self.assertIn("Edit permission:", script)
        self.assertIn("Coverage:", script)
        self.assertIn("Scope: selected Arduino sketch folder only", script)
        self.assertIn("copyCodexContextPackage", script)
        self.assertIn("/api/codex_context_package", script)
        self.assertIn("codexPatchFileLabel", script)
        self.assertIn("Verify the staged change before saving", script)
        self.assertIn("verify before saving to Arduino IDE", script)
        self.assertIn('$("#codexContextPreview").open = true', script)
        self.assertIn("renderCodexContextPreview", script)
        self.assertIn("renderCodexReviewRecovery", script)
        self.assertIn("/api/codex_restore_reviews", script)
        self.assertIn("/api/codex_discard_reviews", script)
        self.assertIn("/api/codex_merge_draft", script)
        self.assertIn("/api/codex_keep_external", script)
        self.assertIn('id="codexConflictView"', html)
        self.assertIn('id="keepExternalConflictBtn"', html)
        self.assertIn('id="rollbackFileBtn"', html)
        self.assertIn('id="saveAndVerifyBtn"', html)
        self.assertIn('class="app-menu-bar"', html)
        self.assertIn('data-menu-button="file"', html)
        self.assertIn('data-menu-button="edit"', html)
        self.assertIn('data-menu-button="selection"', html)
        self.assertIn('data-menu-button="view"', html)
        self.assertIn('data-menu-button="go"', html)
        self.assertIn('data-menu-button="run"', html)
        self.assertIn('data-menu-button="codex"', html)
        self.assertIn('class="app-menu-separator"', html)
        self.assertIn('data-command="find"', html)
        self.assertIn('data-command="copy-line"', html)
        self.assertIn('data-command="comment-line"', html)
        self.assertIn('data-command="run-history"', html)
        self.assertIn('data-command="support-bundle"', html)
        self.assertIn('data-command="toggle-explorer"', html)
        self.assertIn('data-command="copy-context"', html)
        self.assertIn('aria-expanded="false"', html)
        self.assertIn("Clear Verify Cache", html)
        self.assertIn('id="editorFileName" class="sr-only"', html)
        self.assertNotIn('id="editorMoreBtn"', html)
        self.assertNotIn('id="editorActionsMenuBtn"', html)
        self.assertNotIn('id="editorActionsMenuPanel"', html)
        self.assertIn('id="verifyCodexPatchBtn"', html)
        self.assertIn('id="applyCodexTurnBtn"', html)
        self.assertIn('id="copyCodexContextBtn"', html)
        self.assertIn("localEditMode", script)
        self.assertIn("setLocalEditMode", script)
        self.assertIn("updateEditorAccess", script)
        self.assertIn("boardInfoText", script)
        self.assertIn("Arduino IDE owns the saved sketch", script)
        self.assertIn("codexDiffPreview", html)
        self.assertNotIn("virtualPatchEnabled", script)
        self.assertNotIn("toggleVirtualPatchMode", script)
        self.assertNotIn("virtualPatchStatus", script)
        self.assertIn("Codex change applied to Talos editor", script)
        self.assertIn('"Apply To Editor"', script)
        self.assertIn('addEventListener("click", () => applyCodexPatch())', script)
        self.assertIn("selectEditorLine", script)
        self.assertIn("lineFromGutterEvent", script)
        self.assertIn("handleEditorShortcut", script)
        self.assertIn("replaceEditorRangeNative", script)
        self.assertIn("copyCurrentEditorLine", script)
        self.assertIn("copyRawText", script)
        self.assertIn("toggleEditorLineComment", script)
        self.assertIn("moveEditorLine", script)
        self.assertIn("duplicateEditorLine", script)
        self.assertIn("showEditorFind", script)
        self.assertIn("runEditorFind", script)
        self.assertIn("scrollEditorToPosition", script)
        self.assertIn("renderEditorFindLayer", script)
        self.assertIn("syncEditorFindRenderScroll", script)
        self.assertIn("updateEditorCursorLine", script)
        self.assertIn("editorCursorLineIndex", script)
        self.assertIn("editor-find-match", script)
        self.assertIn("editor-find-line", script)
        self.assertIn("cursor-line", script)
        self.assertIn("redirectEditorFindKeystroke", script)
        self.assertIn('editor.focus({ preventScroll: true })', script)
        self.assertIn("editorFindBar", html)
        self.assertIn("editorFindRender", html)
        self.assertNotIn("editorFindHighlights", html)
        self.assertIn('wrap="off"', html)
        self.assertIn("runEditorFind(1, Boolean(selected))", script)
        self.assertIn('document.execCommand?.("insertText"', script)
        self.assertIn('event.key.toLowerCase() === "b"', script)
        self.assertIn('event.key.toLowerCase() === "s"', script)
        self.assertIn("setInterval(checkActiveFileOnDisk", script)
        self.assertIn("View all (", script)
        self.assertIn("relativeTimeLabel", script)
        self.assertIn("showCodexTasks(true)", script)
        self.assertNotIn("toggleCodexHistory", script)
        self.assertIn("codexTaskViewModel", script)
        self.assertIn("renderCodexTaskBanner", script)
        self.assertIn("manual_send_required", script)
        self.assertIn("The interrupted user turn was not replayed", script)
        self.assertIn("codex-history-context", script)
        self.assertIn("bindExplorerSplitter", script)
        self.assertIn("bindCodexSplitter", script)
        self.assertIn("bindVerifySplitter", script)
        self.assertIn("VERIFY_HEIGHT_KEY", script)
        self.assertIn("resetVerifyHeight", script)
        self.assertIn("saveEnvironmentProfile", script)
        self.assertIn("/api/arduino_profile", script)
        self.assertIn("renderProfileReadiness", script)
        self.assertIn("recordReleaseEvidence", script)
        self.assertIn("/api/release_evidence", script)
        self.assertIn("copySupportBundle", script)
        self.assertIn("/api/support_bundle?redact=1", script)
        self.assertIn("runHistoryFilter", script)
        self.assertIn("runHistorySketchOnly", script)
        self.assertIn("watchArduinoEvents", script)
        self.assertIn("/api/arduino_events", script)
        self.assertIn("renderActiveFileRow", script)
        self.assertIn("APP_MENU_COMMANDS", script)
        self.assertIn("toggleAppMenu", script)
        self.assertIn("closeAppMenus", script)
        self.assertIn("runAppMenuCommand", script)
        self.assertIn('copyCurrentEditorLine(false)', script)
        self.assertIn('toggleEditorLineComment()', script)
        self.assertIn('selectEditorLine(editorCursorLineIndex() + 1)', script)
        self.assertIn('setOutputView("history")', script)
        self.assertIn('$$("[data-menu-button]")', script)
        self.assertIn('!event.target.closest(".app-menu")', script)
        self.assertNotIn("setEditorActionsMenu", script)
        self.assertNotIn("editorActionsMenuBtn", script)
        self.assertIn("CODEX_WIDTH_KEY", script)
        self.assertIn("EXPLORER_PANEL_KEY", script)
        self.assertIn("applyExplorerPanel", script)
        style = (Path(__file__).parents[1] / "ui" / "web_frontend" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".editor-find-bar", style)
        self.assertIn(".editor-find-render", style)
        self.assertIn("z-index: 1", style)
        self.assertIn("position: absolute", style)
        self.assertIn("inset: 0 0 0 48px", style)
        self.assertIn(".editor-canvas.finding #sourceEditor:disabled", style)
        self.assertIn(".editor-find-match.current", style)
        self.assertIn("color: transparent", style)
        self.assertIn(".editor-find-line.cursor-line", style)
        self.assertIn(".editor-canvas.has-cursor-line::after", style)
        self.assertIn("--cursor-line-bg", style)
        self.assertNotIn(".editor-find-highlights", style)
        self.assertIn("--editor-bg", style)
        self.assertIn("--gutter-bg", style)
        self.assertIn("--selection-bg", style)
        self.assertIn("--active-item-bg", style)
        self.assertIn("--titlebar-bg", style)
        self.assertIn("--activity-bg", style)
        self.assertIn("--sidebar-bg", style)
        self.assertIn("--toolbar-bg", style)
        self.assertIn("--terminal-bg", style)
        self.assertIn("--assistant-bg", style)
        self.assertIn("background: var(--activity-bg)", style)
        self.assertIn("background: var(--sidebar-bg)", style)
        self.assertIn("background: var(--toolbar-bg)", style)
        self.assertIn("background: var(--terminal-bg)", style)
        self.assertIn("background: var(--assistant-bg)", style)
        self.assertIn(".app-menu-bar", style)
        self.assertIn(".app-menu-panel", style)
        self.assertIn(".app-menu-panel[hidden]", style)
        self.assertIn(".app-menu-separator", style)
        self.assertIn(".app-menu-action", style)
        self.assertIn("-webkit-app-region: no-drag", style)
        self.assertNotIn(".editor-command-menu-panel", style)
        self.assertNotIn(".menu-action", style)
        self.assertIn("overflow: visible", style)
        self.assertIn("Simplified", (Path(__file__).parents[1] / "docs" / "TALOS_PIPELINE_040.md").read_text(encoding="utf-8"))
        self.assertIn("VS Code-style top menu bar", (Path(__file__).parents[1] / "docs" / "TALOS_PIPELINE_040.md").read_text(encoding="utf-8"))
        self.assertIn("explorer-hidden", style)
        self.assertIn("minmax(300px, var(--codex-pane-width))", style)
        self.assertNotIn("translateX(100%)", style)
        self.assertNotIn("right: min(var(--codex-pane-width)", style)
        self.assertNotIn("applyWindowMetrics", script)
        self.assertNotIn("--native-window-width", script)

        server = (Path(__file__).parents[1] / "talos" / "server.py").read_text(encoding="utf-8")
        self.assertIn("/api/codex_restore_reviews", server)
        self.assertIn("/api/codex_discard_reviews", server)
        self.assertIn("/api/codex_merge_draft", server)
        self.assertIn("/api/codex_apply_conflict", server)
        self.assertIn("editor_override", server)
        self.assertIn("/api/release_evidence", server)
        self.assertIn("/api/support_bundle", server)
        self.assertIn("support_bundle", server)
        self.assertIn("filtered_run_history", server)
        self.assertIn("record_codex_turn", server)
        self.assertIn("conversation_loaded", server)
        self.assertIn("context_replay_guard", server)

        styles = (Path(__file__).parents[1] / "ui" / "web_frontend" / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn("width: 100vw;", styles)
        self.assertIn("max-width: none;", styles)
        self.assertIn("justify-self: stretch;", styles)
        self.assertIn("inset: 0;", styles)
        self.assertIn("border-left: 1px solid var(--line);", styles)
        self.assertIn("inline-size: 100%;", styles)
        self.assertIn(".ide-workbench.explorer-hidden", styles)
        self.assertIn("minmax(300px, var(--codex-pane-width))", styles)
        self.assertNotIn("right: min(var(--codex-pane-width)", styles)
        self.assertNotIn("box-shadow: -18px 0 32px", styles)
        self.assertIn("@media (max-width: 1240px)", styles)
        self.assertIn("minmax(280px, var(--codex-pane-width))", styles)
        self.assertNotIn("minmax(260px, var(--codex-pane-width))", styles)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", styles)
        self.assertIn("grid-template-areas:", styles)
        self.assertIn("grid-column: 1 / -1;", styles)
        self.assertNotIn("body.native-window .app-chrome", styles)
        self.assertNotIn(".editor-tabbar::before", styles)
        self.assertIn(".workspace-file-list tbody tr.active td", styles)
        self.assertIn(".review-status-chip", styles)
        self.assertIn(".codex-review-scope", styles)
        self.assertIn(".history-filter", styles)
        self.assertIn(".history-sketch-filter", styles)
        self.assertIn(".sr-only", styles)
        self.assertIn('src="/assets/talos_icon.png"', html)
        self.assertIn('class="chrome-mark app-logo-mark"', html)
        self.assertIn('class="rail-icon brand-icon app-logo-mark"', html)
        self.assertIn(".app-logo-mark img", styles)
        self.assertIn('class="rail-icon nav-glyph"', html)
        self.assertIn('class="arduino-logo"', html)
        self.assertIn('<rect x="2" y="2" width="20" height="20" rx="5"', html)
        self.assertIn("fill: currentColor;", styles)
        self.assertNotIn("#008184", styles)
        self.assertIn("viewBox=\"0 0 24 24\"", html)
        self.assertIn('id="windowMenu"', html)
        self.assertIn('data-resize-edge="nw"', html)
        self.assertIn('data-resize-edge="se"', html)
        self.assertNotIn("pinRailBtn", html)
        self.assertNotIn("applyRailPinned", script)
        self.assertNotIn("RAIL_PIN_KEY", script)

        desktop = (Path(__file__).parents[1] / "desktop_app.py").read_text(encoding="utf-8")
        self.assertIn("frameless=True", desktop)
        self.assertIn("def get_window_bounds", desktop)
        self.assertIn("def set_window_bounds", desktop)
        self.assertIn("def restore", desktop)
        self.assertIn("bindWindowResizeHandles", script)
        self.assertIn("resizeBoundsFromEdge", script)
        self.assertIn("showWindowMenu", script)
        self.assertIn('event.altKey && event.code === "Space"', script)
        self.assertIn(".window-resize-handle", styles)
        self.assertIn(".window-menu", styles)
        self.assertIn("--scrollbar-track", styles)
        self.assertIn("scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);", styles)
        self.assertIn("background: var(--scrollbar-track);", styles)
        self.assertIn("background: var(--scrollbar-thumb);", styles)
        self.assertNotIn("scrollbar-color: #8c959f #f6f8fa", styles)
        self.assertIn('class="verify-raw"', script)
        self.assertIn("max-height: min(220px, 32vh);", styles)
        self.assertIn(".verify-output > *", styles)
        self.assertIn(".verify-raw", styles)
        self.assertIn("display: none;", styles)
        self.assertIn("[hidden]", styles)
        self.assertIn("display: none !important;", styles)
        self.assertIn("cursor: pointer;", styles)
        self.assertIn("--codex-pane-width", styles)
        self.assertIn("--verify-pane-height", styles)
        self.assertIn(".row-splitter", styles)
        self.assertIn("grid-template-rows: auto minmax(220px, 1fr) var(--pane-splitter-width) minmax(140px, var(--verify-pane-height));", styles)
        self.assertIn("flex-wrap: wrap;", styles)
        self.assertIn(".codex-patch-file-copy", styles)
        self.assertIn(".run-history-item.codex-turn", styles)

        check_script = (Path(__file__).parents[1] / "scripts" / "check.ps1").read_text(encoding="utf-8")
        self.assertIn("build_native.ps1", check_script)
        self.assertIn("_HAS_NATIVE_WINDOW_ROWS", check_script)
        self.assertIn("_HAS_NATIVE_PROCESS_ROWS", check_script)
        self.assertIn("benchmark_native.py", check_script)
        self.assertIn("unittest tests.test_desktop_app", check_script)
        self.assertIn("smoke_release_recovery.py", check_script)

        benchmark_script = (Path(__file__).parents[1] / "scripts" / "benchmark_native.py").read_text(encoding="utf-8")
        self.assertIn("list_window_rows", benchmark_script)
        self.assertIn("list_arduino_process_rows_native", benchmark_script)
        self.assertIn("fallback_status", benchmark_script)
        self.assertIn("list_arduino_tool_processes_wmic", benchmark_script)

        native_source = (Path(__file__).parents[1] / "talos" / "native_bridge.py").read_text(encoding="utf-8")
        arduino_source = (Path(__file__).parents[1] / "talos" / "arduino.py").read_text(encoding="utf-8")
        self.assertIn("CREATE_NO_WINDOW", native_source)
        self.assertIn("run_hidden_capture", native_source)
        self.assertIn("_PROCESS_FALLBACK_CACHE_TTL_SECONDS", native_source)
        self.assertIn("_COMMAND_LINE_CACHE_TTL_SECONDS = 20.0", native_source)
        self.assertIn("CREATE_NO_WINDOW", arduino_source)
        self.assertIn("creationflags=CREATE_NO_WINDOW", arduino_source)

        recovery_script = (Path(__file__).parents[1] / "scripts" / "smoke_release_recovery.py").read_text(encoding="utf-8")
        self.assertIn("restart-pending-review-external-change-guard", recovery_script)
        self.assertIn("keep_external_conflict", recovery_script)

        smoke_test = (Path(__file__).parents[1] / "docs" / "ARDUINO_SMOKE_TEST.md").read_text(encoding="utf-8")
        self.assertIn("Verify Sandbox", smoke_test)
        self.assertIn("Codex", smoke_test)
        self.assertIn("Pass Criteria", smoke_test)
        self.assertIn("Fail Conditions", smoke_test)
        self.assertIn("MVP Smoke-Test Matrix", smoke_test)
        self.assertIn("Hunk decision", smoke_test)
        self.assertIn("External-change conflict", smoke_test)
        self.assertIn("Save and verify", smoke_test)

    def test_desktop_entrypoint_remains_source_debuggable(self) -> None:
        root = Path(__file__).parents[1]
        desktop_shell = (root / "desktop_app.py").read_text(encoding="utf-8")
        launcher = (root / "scripts" / "launch_desktop.ps1").read_text(encoding="utf-8")

        self.assertIn('import webview  # type: ignore[import-not-found]', desktop_shell)
        self.assertIn('Join-Path $root "desktop_app.py"', launcher)
        self.assertIn(".venv\\Scripts\\python.exe", launcher)
        self.assertIn("import webview", launcher)
        self.assertIn("python -m pip install -r config\\requirements.txt", launcher)
        self.assertIn("Start-Process -FilePath $python", launcher)

    def test_stage_10_icon_is_wired_into_desktop_build_and_shortcut(self) -> None:
        root = Path(__file__).parents[1]
        desktop_shell = (root / "desktop_app.py").read_text(encoding="utf-8")
        build_script = (root / "scripts" / "build_app.ps1").read_text(encoding="utf-8")
        install_script = (root / "scripts" / "install_app.ps1").read_text(encoding="utf-8")

        self.assertIn("_set_windows_app_id(app_identity)", desktop_shell)
        self.assertIn("webview.start(debug=\"--debug-webview\" in sys.argv, icon=icon_path)", desktop_shell)
        self.assertIn("--icon", build_script)
        self.assertIn("assets\\icons;assets\\icons", build_script)
        self.assertIn("config\\app_identity.json;config", build_script)
        self.assertIn("config\\default_config.json;config", build_script)
        self.assertIn("docs;docs", build_script)
        self.assertIn(".venv\\Scripts\\python.exe", build_script)
        self.assertIn("IconLocation", install_script)
        self.assertIn("config\\app_identity.json", install_script)
        self.assertIn("config\\default_config.json", install_script)
        self.assertNotIn("config\\config.json\") -Destination", install_script)

    def test_stage_10_release_build_command_is_versioned_and_clean_tree_gated(self) -> None:
        root = Path(__file__).parents[1]
        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        gitignore = (root / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("param(", release_script)
        self.assertIn("[switch]$AllowDirty", release_script)
        self.assertIn("git status --porcelain", release_script)
        self.assertIn("Release build requires a clean git tree", release_script)
        self.assertIn("releases", release_script)
        self.assertIn("$appName-$version-$channel", release_script)
        self.assertIn("Get-FileHash", release_script)
        self.assertIn("release_manifest.json", release_script)
        self.assertIn("scripts\\build_app.ps1", release_script)
        self.assertIn("releases/", gitignore)

    def test_stage_10_installer_build_has_shortcuts_and_uninstall_cleanup(self) -> None:
        root = Path(__file__).parents[1]
        installer_script = (root / "scripts" / "build_installer.ps1").read_text(encoding="utf-8")
        installer_smoke = (root / "scripts" / "smoke_installer.ps1").read_text(encoding="utf-8")
        inno_script = (root / "installer" / "talos.iss").read_text(encoding="utf-8")

        self.assertIn("Find-InnoCompiler", installer_script)
        self.assertIn("scripts\\build_release.ps1", installer_script)
        self.assertIn("-AllowDirty:$AllowDirty", installer_script)
        self.assertIn("release_manifest.json", installer_script)
        self.assertIn("windows-installer", installer_script)
        self.assertIn("$releaseName-setup.exe", installer_script)
        self.assertIn("Where-Object { $_.file -ne $installerFile }", installer_script)

        self.assertIn("PrivilegesRequired=lowest", inno_script)
        self.assertIn("DefaultDirName={localappdata}\\Programs\\{#MyAppName}", inno_script)
        self.assertIn("Name: \"desktopicon\"", inno_script)
        self.assertIn("{userprograms}\\{#MyAppName}\\{#MyAppName}", inno_script)
        self.assertIn("{userdesktop}\\{#MyAppName}", inno_script)
        self.assertIn("Tasks: desktopicon", inno_script)
        self.assertIn("[UninstallDelete]", inno_script)
        self.assertIn("Type: dirifempty; Name: \"{app}\\config\"", inno_script)
        self.assertIn("release_manifest.json", inno_script)
        self.assertIn("{#ReleaseDir}\\docs\\*", inno_script)
        self.assertIn("Release Notes", inno_script)
        self.assertIn("Privacy Notes", inno_script)
        self.assertIn("default_config.json", inno_script)
        self.assertNotIn("DestName: \"config.json\"", inno_script)
        self.assertIn("#ifndef MyAppName", inno_script)
        self.assertIn("TalosInstallerSmoke", installer_smoke)
        self.assertIn("scripts\\build_installer.ps1", installer_smoke)
        self.assertIn("/VERYSILENT", installer_smoke)
        self.assertIn("config\\default_config.json", installer_smoke)
        self.assertIn("release_manifest.json", installer_smoke)
        self.assertIn("docs\\RELEASE_NOTES.md", installer_smoke)
        self.assertIn("docs\\EULA.md", installer_smoke)
        self.assertIn("docs\\PRIVACY.md", installer_smoke)
        self.assertIn("docs\\THIRD_PARTY_NOTICES.md", installer_smoke)
        self.assertIn("docs\\CODE_SIGNING.md", installer_smoke)
        self.assertIn("docs\\INSTALLED_APP_SMOKE_TEST.md", installer_smoke)
        self.assertIn("docs\\TALOS_USER_GUIDE.md", installer_smoke)
        self.assertIn("docs\\TALOS_FIRST_RUN_CHECKLIST.md", installer_smoke)
        self.assertIn("docs\\TALOS_TROUBLESHOOTING.md", installer_smoke)
        self.assertIn("docs\\TALOS_DIAGNOSTICS.md", installer_smoke)
        self.assertIn("docs\\TALOS_INSTALL_LIFECYCLE.md", installer_smoke)
        self.assertIn("docs\\TALOS_UI_UX_CHECKLIST.md", installer_smoke)
        self.assertIn("/TASKS=desktopicon", installer_smoke)
        self.assertIn("optional_desktop_shortcut", installer_smoke)
        self.assertIn("writable runtime config inside the install directory", installer_smoke)
        self.assertIn("Silent uninstall", installer_smoke)
        self.assertIn("Installer smoke test passed", installer_smoke)

    def test_stage_10_runtime_state_uses_per_user_app_data(self) -> None:
        root = Path(__file__).parents[1]
        core_source = (root / "talos" / "core.py").read_text(encoding="utf-8")
        arduino_source = (root / "talos" / "arduino.py").read_text(encoding="utf-8")
        codex_source = (root / "talos" / "codex_bridge.py").read_text(encoding="utf-8")
        history_source = (root / "talos" / "run_history.py").read_text(encoding="utf-8")
        checkpoint_source = (root / "talos" / "checkpoints.py").read_text(encoding="utf-8")
        server_source = (root / "talos" / "server.py").read_text(encoding="utf-8")
        cleaner = (root / "scripts" / "clean_runtime.ps1").read_text(encoding="utf-8")
        gitignore = (root / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("APP_DATA_ENV = \"TALOS_APP_DATA_DIR\"", core_source)
        self.assertIn("APP_DATA_ROOT = _default_app_data_root()", core_source)
        self.assertIn("CONFIG_PATH = APP_DATA_ROOT / \"config.json\"", core_source)
        self.assertIn("LEGACY_CONFIG_PATH = ROOT / \"config\" / \"config.json\"", core_source)
        self.assertIn("source_path = LEGACY_CONFIG_PATH", core_source)

        self.assertIn("SANDBOX_ROOT = APP_DATA_ROOT / \"sandbox\" / \"arduino\"", arduino_source)
        self.assertIn("STAGING_ROOT = APP_DATA_ROOT / \"staging\"", codex_source)
        self.assertIn("REVIEW_STATE_PATH = APP_DATA_ROOT / \"codex_reviews.json\"", codex_source)
        self.assertIn("RUN_HISTORY_PATH = APP_DATA_ROOT / \"run_history.json\"", history_source)
        self.assertIn("CHECKPOINT_PATH = APP_DATA_ROOT / \"checkpoints.json\"", checkpoint_source)
        self.assertIn("\"app_data\": str(APP_DATA_ROOT)", server_source)

        self.assertIn("T-Engine\\Talos", cleaner)
        self.assertIn("insideAppData", cleaner)
        self.assertIn("config/config.json", gitignore)
        self.assertIn("config/codex_reviews.json", gitignore)

    def test_stage_10_version_and_build_metadata_are_visible(self) -> None:
        root = Path(__file__).parents[1]
        core_source = (root / "talos" / "core.py").read_text(encoding="utf-8")
        server_source = (root / "talos" / "server.py").read_text(encoding="utf-8")
        html = (root / "ui" / "web_frontend" / "index.html").read_text(encoding="utf-8")
        script = (root / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        styles = (root / "ui" / "web_frontend" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("RELEASE_MANIFEST_PATH = ROOT / \"release_manifest.json\"", core_source)
        self.assertIn("def load_build_metadata", core_source)
        self.assertIn("\"mode\": \"packaged\" if getattr(sys, \"frozen\", False) else \"source\"", core_source)
        self.assertIn("\"artifacts\": artifacts", core_source)
        self.assertIn("load_build_metadata(app_identity)", server_source)
        self.assertIn("\"build\": build_metadata", server_source)

        self.assertIn('id="chromeVersion"', html)
        self.assertIn('id="dashboardReleaseDetails"', html)
        self.assertIn('id="releaseDetails"', html)
        self.assertIn("function versionLabel", script)
        self.assertIn("function renderReleaseDetails", script)
        self.assertIn("hydrateAppIdentity(payload.app || {}, payload.build || {})", script)
        self.assertIn(".release-details", styles)

    def test_stage_10_release_legal_and_third_party_docs_are_packaged(self) -> None:
        root = Path(__file__).parents[1]
        required_docs = {
            "LICENSE": ["MIT License", "Copyright"],
            "RELEASE_NOTES.md": ["0.1.0 Beta", "Known Limitations"],
            "EULA.md": ["End User License Agreement", "Beta Status"],
            "PRIVACY.md": ["Privacy Notes", "Codex"],
            "THIRD_PARTY_NOTICES.md": ["Third-Party Notices", "pywebview", "PyInstaller", "Pillow"],
            "CODE_SIGNING.md": ["Code Signing", "signtool.exe", "Get-AuthenticodeSignature", "unsigned-Beta"],
            "INSTALLED_APP_SMOKE_TEST.md": ["Installed App Smoke Test", "Manual Arduino/Codex Checks", "Pass Criteria"],
            "TALOS_USER_GUIDE.md": ["Talos User Guide", "Arduino IDE remains the owner", "Verify Sandbox", "Use Codex"],
            "TALOS_FIRST_RUN_CHECKLIST.md": ["Talos First-Run Checklist", "Simple `.ino` Sketch", "Multi-File Sketch", "Codex Review Flow"],
            "TALOS_TROUBLESHOOTING.md": ["Talos Troubleshooting Guide", "Arduino IDE Is Not Detected", "`arduino-cli` Was Not Found", "Codex Is Disconnected"],
            "TALOS_DIAGNOSTICS.md": ["Talos Diagnostics And Product Feedback", "Consent Model", "Event Taxonomy", "does not upload"],
            "TALOS_INSTALL_LIFECYCLE.md": ["Talos Install Lifecycle Validation", "Clean Profile Method", "Upgrade Preservation", "Uninstall Policy"],
            "TALOS_UI_UX_CHECKLIST.md": ["Talos UI/UX Smoke Checklist", "Window Sizes", "Editor And Review States", "Settings And Appearance"],
        }
        for doc_name, required_terms in required_docs.items():
            content = (root / "docs" / doc_name).read_text(encoding="utf-8")
            for term in required_terms:
                self.assertIn(term, content, doc_name)

        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        installer_script = (root / "installer" / "talos.iss").read_text(encoding="utf-8")
        local_install = (root / "scripts" / "install_app.ps1").read_text(encoding="utf-8")
        readme = (root / "docs" / "README.md").read_text(encoding="utf-8")
        pipeline = (root / "docs" / "TALOS_PIPELINE_010.md").read_text(encoding="utf-8")

        for doc_name in required_docs:
            self.assertIn(doc_name, release_script)
            self.assertIn(doc_name, local_install)
            self.assertIn(doc_name, readme)
        self.assertIn("Source: \"{#ReleaseDir}\\docs\\*\"", installer_script)
        self.assertIn("Start Menu includes Release Notes and Privacy shortcuts", pipeline)

    def test_stage_10_code_signing_path_is_documented_and_scripted(self) -> None:
        root = Path(__file__).parents[1]
        policy = json.loads((root / "config" / "signing_policy.json").read_text(encoding="utf-8"))
        signing_doc = (root / "docs" / "CODE_SIGNING.md").read_text(encoding="utf-8")
        sign_script = (root / "scripts" / "sign_release.ps1").read_text(encoding="utf-8")
        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        readme = (root / "docs" / "README.md").read_text(encoding="utf-8")
        pipeline = (root / "docs" / "TALOS_PIPELINE_010.md").read_text(encoding="utf-8")

        self.assertEqual(policy["schema_version"], 1)
        self.assertEqual(policy["publisher"], "T-Engine")
        self.assertTrue(policy["unsigned_beta_allowed"])
        self.assertEqual(policy["digest_algorithm"], "SHA256")
        self.assertIn("windows-executable", policy["targets"])
        self.assertIn("windows-installer", policy["targets"])

        self.assertIn("config/signing_policy.json", signing_doc)
        self.assertIn("timestamp server", signing_doc)
        self.assertIn("signing_status.json", signing_doc)
        self.assertIn("-AllowUnsignedBeta", signing_doc)
        self.assertIn("-CertificateThumbprint", signing_doc)

        self.assertIn("param(", sign_script)
        self.assertIn("[switch]$AllowUnsignedBeta", sign_script)
        self.assertIn("signtool.exe", sign_script)
        self.assertIn("Get-AuthenticodeSignature", sign_script)
        self.assertIn("Get-FileHash", sign_script)
        self.assertIn("signing_status.json", sign_script)
        self.assertIn("unsigned-beta", sign_script)
        self.assertIn("Signing verification failed", sign_script)

        self.assertIn("signing_policy.json", release_script)
        self.assertIn("CODE_SIGNING.md", release_script)
        self.assertIn("scripts\\sign_release.ps1", readme)
        self.assertIn("[x] Define the code-signing path", pipeline)

    def test_stage_10_installed_app_smoke_is_scripted_and_documented(self) -> None:
        root = Path(__file__).parents[1]
        smoke_script = (root / "scripts" / "smoke_installed_app.ps1").read_text(encoding="utf-8")
        smoke_doc = (root / "docs" / "INSTALLED_APP_SMOKE_TEST.md").read_text(encoding="utf-8")
        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        readme = (root / "docs" / "README.md").read_text(encoding="utf-8")
        pipeline = (root / "docs" / "TALOS_PIPELINE_010.md").read_text(encoding="utf-8")

        self.assertIn("[switch]$ManualArduinoConfirmed", smoke_script)
        self.assertIn("[switch]$AutoArduinoHarness", smoke_script)
        self.assertIn("[switch]$SkipLaunch", smoke_script)
        self.assertIn("TalosInstalledAppSmoke", smoke_script)
        self.assertIn("Start-Process -FilePath $installedExe", smoke_script)
        self.assertIn("/api/health", smoke_script)
        self.assertIn("TALOS_SMOKE_HARNESS", smoke_script)
        self.assertIn("/api/smoke/codex_patch", smoke_script)
        self.assertIn("TALOS_APP_DATA_DIR", smoke_script)
        self.assertIn("installed_app_smoke.json", smoke_script)
        self.assertIn("packaged", smoke_script)
        self.assertIn("manual-confirmation-required", smoke_script)
        self.assertIn("detect-open-arduino-sketch", smoke_script)
        self.assertIn("review-apply-and-save-codex-change", smoke_script)

        self.assertIn("installed executable outside the repository", smoke_doc)
        self.assertIn("Verify Sandbox", smoke_doc)
        self.assertIn("-AutoArduinoHarness", smoke_doc)
        self.assertIn("Ask Codex", smoke_doc)
        self.assertIn("status: passed", smoke_doc)
        self.assertIn("INSTALLED_APP_SMOKE_TEST.md", release_script)
        self.assertIn("scripts\\smoke_installed_app.ps1", readme)
        self.assertIn("[x] Smoke-test the installed app outside the repository", pipeline)

    def test_stage_040_install_lifecycle_validation_is_scripted_and_packaged(self) -> None:
        root = Path(__file__).parents[1]
        lifecycle_script = (root / "scripts" / "smoke_app_lifecycle.ps1").read_text(encoding="utf-8")
        lifecycle_doc = (root / "docs" / "TALOS_INSTALL_LIFECYCLE.md").read_text(encoding="utf-8")
        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        local_install = (root / "scripts" / "install_app.ps1").read_text(encoding="utf-8")
        checklist_script = (root / "scripts" / "distribution_checklist.ps1").read_text(encoding="utf-8")
        readme = (root / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn("TALOS_APP_DATA_DIR", lifecycle_script)
        self.assertIn("app_lifecycle_smoke.json", lifecycle_script)
        self.assertIn("config.json", lifecycle_script)
        self.assertIn("run_history.json", lifecycle_script)
        self.assertIn("checkpoints.json", lifecycle_script)
        self.assertIn("codex_reviews.json", lifecycle_script)
        self.assertIn("diagnostics.json", lifecycle_script)
        self.assertIn("user_runtime_data_preserved", lifecycle_script)
        self.assertIn("installer_owned_files_removed", lifecycle_script)
        self.assertIn("writable_config_absent_from_install_dir", lifecycle_script)

        self.assertIn("Clean Profile Method", lifecycle_doc)
        self.assertIn("Upgrade Preservation", lifecycle_doc)
        self.assertIn("Uninstall Policy", lifecycle_doc)
        self.assertIn("app_lifecycle_smoke.json", lifecycle_doc)
        self.assertIn("TALOS_INSTALL_LIFECYCLE.md", release_script)
        self.assertIn("TALOS_INSTALL_LIFECYCLE.md", local_install)
        self.assertIn("app_lifecycle_smoke.json", checklist_script)
        self.assertIn("App-data lifecycle smoke", checklist_script)
        self.assertIn("app lifecycle smoke must all be present", checklist_script)
        self.assertIn("scripts/smoke_app_lifecycle.ps1", readme)

    def test_stage_040_ui_ux_appearance_and_responsive_markers_exist(self) -> None:
        root = Path(__file__).parents[1]
        html = (root / "ui" / "web_frontend" / "index.html").read_text(encoding="utf-8")
        script = (root / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        styles = (root / "ui" / "web_frontend" / "styles.css").read_text(encoding="utf-8")
        release_script = (root / "scripts" / "build_release.ps1").read_text(encoding="utf-8")
        local_install = (root / "scripts" / "install_app.ps1").read_text(encoding="utf-8")
        readme = (root / "docs" / "README.md").read_text(encoding="utf-8")

        self.assertIn('id="systemThemeInput"', html)
        self.assertIn('id="highContrastInput"', html)
        self.assertIn('id="editorFontSizeInput"', html)
        self.assertIn('id="editorDensityInput"', html)
        self.assertIn("theme-preview", html)
        self.assertIn("TALOS_UI_UX_CHECKLIST.md", html)

        self.assertIn("SYSTEM_THEME_KEY", script)
        self.assertIn("HIGH_CONTRAST_KEY", script)
        self.assertIn("EDITOR_FONT_SIZE_KEY", script)
        self.assertIn("EDITOR_DENSITY_KEY", script)
        self.assertIn("applyAppearancePreferences", script)
        self.assertIn("hydrateAppearance(payload.config || {})", script)

        self.assertIn("--editor-font-size", styles)
        self.assertIn("data-editor-density", styles)
        self.assertIn('data-contrast="high"', styles)
        self.assertIn(".theme-card", styles)
        self.assertIn(".appearance-grid", styles)
        self.assertIn(".editor-actions", styles)
        self.assertIn("overflow-x: auto", styles)
        self.assertIn("@media (max-width: 1240px)", styles)

        self.assertIn("TALOS_UI_UX_CHECKLIST.md", release_script)
        self.assertIn("TALOS_UI_UX_CHECKLIST.md", local_install)
        self.assertIn("TALOS_UI_UX_CHECKLIST.md", readme)

    def test_pipeline_defines_exit_condition_for_every_stage(self) -> None:
        pipeline = (Path(__file__).parents[1] / "docs" / "TALOS_PIPELINE_010.md").read_text(encoding="utf-8")
        stages = re.split(r"(?=^## Stage \d+ - )", pipeline, flags=re.MULTILINE)
        stage_sections = [section for section in stages if section.startswith("## Stage ")]

        self.assertEqual(len(stage_sections), 11)
        for section in stage_sections:
            self.assertIn("Exit condition:", section, section.splitlines()[0])

    def test_stage_10_icon_set_exists_for_windows_packaging(self) -> None:
        from PIL import Image

        root = Path(__file__).parents[1]
        identity = json.loads((root / "config" / "app_identity.json").read_text(encoding="utf-8"))
        icon_dir = root / identity["icon_png_dir"]

        self.assertEqual(identity["icon_ico"], "assets/icons/talos.ico")
        self.assertTrue((root / identity["icon_source"]).exists())
        self.assertTrue((root / identity["icon_ico"]).exists())

        for size in (16, 24, 32, 48, 64, 128, 256):
            with Image.open(icon_dir / f"talos_{size}.png") as icon:
                self.assertEqual(icon.size, (size, size))
                self.assertEqual(icon.mode, "RGBA")

    def test_stage_10_default_config_is_packaging_safe(self) -> None:
        root = Path(__file__).parents[1]
        default_config = json.loads((root / "config" / "default_config.json").read_text(encoding="utf-8"))

        self.assertFalse((root / "config" / "config.json").exists())
        self.assertEqual(default_config["schema_version"], 1)
        self.assertEqual(default_config["arduino_workspace_path"], "")
        self.assertEqual(default_config["arduino_fqbn"], "")
        self.assertEqual(default_config["arduino_profiles"], {})
        self.assertEqual(default_config["diagnostics"], {"enabled": False, "allow_remote_upload": False})

    def test_codex_thread_summary_prefers_name_and_supports_unix_time(self) -> None:
        summary = normalize_codex_thread(
            {
                "id": "thread-1",
                "name": "Arduino review",
                "preview": "Long injected prompt",
                "cwd": r"C:\Sketch",
                "updatedAt": 1781541452,
            },
            "thread-1",
        )

        self.assertEqual(summary["title"], "Arduino review")
        self.assertEqual(summary["updated_at"], 1781541452)
        self.assertTrue(summary["active"])

    def test_codex_thread_messages_restore_user_and_assistant_text(self) -> None:
        messages = messages_from_codex_thread(
            {
                "turns": [
                    {
                        "startedAt": 1781541452,
                        "items": [
                            {
                                "id": "user-1",
                                "type": "userMessage",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Review this sketch.\n\nTalos Arduino context:\n- Workspace: C:\\Sketch",
                                    }
                                ],
                            },
                            {
                                "id": "assistant-1",
                                "type": "agentMessage",
                                "text": "The sketch compiles.",
                            },
                        ],
                    }
                ]
            }
        )

        self.assertEqual(messages[0]["text"], "Review this sketch.")
        self.assertEqual(messages[1]["text"], "The sketch compiles.")

    def test_run_history_keeps_verify_and_patch_events(self) -> None:
        with TemporaryDirectory() as tmp:
            history_path = Path(tmp) / "run_history.json"
            with patch("talos.run_history.RUN_HISTORY_PATH", history_path):
                record_verify(
                    {
                        "ok": True,
                        "status": "passed",
                        "summary": {"path": r"C:\Sketch", "main_sketch": "Sketch.ino"},
                        "output": "Sketch uses 100 bytes.",
                    },
                    "codex_patch",
                )
                record_patch(
                    {
                        "id": "patch-1",
                        "turn_id": "turn-1",
                        "workspace": r"C:\Sketch",
                        "files": [{"path": "Sketch.ino", "kind": "update"}],
                    }
                )
                record_codex_turn(r"C:\Sketch", "Review this sketch.", "started", {"active_file": "Sketch.ino"})
                record_patch_transition(
                    {
                        "id": "patch-1",
                        "turn_id": "turn-1",
                        "workspace": r"C:\Sketch",
                        "review_status": "saved",
                        "files": [{"path": "Sketch.ino", "kind": "update", "review_status": "saved", "hunks": [{}, {}]}],
                    },
                    "saved",
                    "Sketch.ino",
                )
                events = run_history()

            self.assertEqual([event["type"] for event in events], ["codex_turn", "patch", "verify"])
            self.assertEqual(events[2]["source"], "codex_patch")
            self.assertEqual(events[1]["turn_id"], "turn-1")
            self.assertEqual(events[1]["files"][0]["hunks"], 2)
            self.assertEqual(events[1]["timeline"][-1]["action"], "saved")
            self.assertEqual(events[0]["status"], "started")
            self.assertEqual(events[0]["detail"]["active_file"], "Sketch.ino")

    def test_run_history_records_versioned_release_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            history_path = Path(tmp) / "run_history.json"
            with patch("talos.run_history.RUN_HISTORY_PATH", history_path):
                record_release_evidence(
                    {
                        "workspace": r"C:\Sketch",
                        "main_sketch": "Sketch.ino",
                        "source_tab_count": 2,
                    },
                    {"ready": True, "issues": [], "warnings": []},
                    {
                        "ok": True,
                        "status": "passed",
                        "summary": {"path": r"C:\Sketch", "main_sketch": "Sketch.ino"},
                        "memory": {"program": {"percent": 12}},
                        "timings": {"total": 1.25},
                    },
                    ["none"],
                )
                events = run_history()

            self.assertEqual(events[0]["type"], "release_evidence")
            self.assertEqual(events[0]["schema_version"], 1)
            self.assertEqual(events[0]["release"], "0.3.0-beta")
            self.assertTrue(events[0]["profile_ready"])
            self.assertEqual(events[0]["verify_summary"]["memory"]["program"]["percent"], 12)
            self.assertEqual(events[0]["blocked_cases"], ["none"])

    def test_run_history_filters_by_workspace_sketch_and_kind(self) -> None:
        with TemporaryDirectory() as tmp:
            history_path = Path(tmp) / "run_history.json"
            with patch("talos.run_history.RUN_HISTORY_PATH", history_path):
                record_verify(
                    {
                        "ok": True,
                        "status": "passed",
                        "summary": {"path": r"C:\SketchA", "main_sketch": "Main.ino"},
                    },
                    "manual",
                )
                record_codex_turn(r"C:\SketchA", "Review", "completed", {"active_file": "Motor.cpp"})
                record_patch_transition(
                    {
                        "id": "patch-save",
                        "workspace": r"C:\SketchA",
                        "review_status": "saved",
                        "files": [{"path": "Motor.cpp", "review_status": "saved"}],
                    },
                    "saved",
                    "Motor.cpp",
                )
                record_verify(
                    {
                        "ok": False,
                        "status": "failed",
                        "summary": {"path": r"C:\SketchB", "main_sketch": "Other.ino"},
                    },
                    "manual",
                )

                saved = filtered_run_history(workspace=r"C:\SketchA", sketch="Motor.cpp", kind="saved")
                verifies = filtered_run_history(workspace=r"C:\SketchA", kind="verify")

            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["type"], "patch")
            self.assertEqual(saved[0]["timeline"][-1]["action"], "saved")
            self.assertEqual(len(verifies), 1)
            self.assertEqual(verifies[0]["main_sketch"], "Main.ino")

    def test_support_bundle_redacts_shareable_paths(self) -> None:
        bundle = support_bundle(
            app={"display_name": "Talos", "version": "0.3.0"},
            build={
                "root": r"C:\University\Bao\local_agent",
                "bundle_root": r"C:\University\Bao\local_agent",
                "app_data": r"C:\Users\Admin\AppData\Local\T-Engine\Talos",
                "executable": r"C:\Python311\python.exe",
            },
            workspace_summary={"path": r"C:\Users\Admin\Desktop\Sketch", "main_sketch": "Sketch.ino"},
            profile={"fqbn": "arduino:avr:uno"},
            profile_readiness={"ready": True},
            latest_verify={"workspace": r"C:\Users\Admin\Desktop\Sketch"},
            history=[{"type": "verify", "workspace": r"C:\Users\Admin\Desktop\Sketch"}],
            redact=True,
        )

        body = json.dumps(bundle)
        self.assertIn("<workspace>", body)
        self.assertIn("<app-data>", body)
        self.assertNotIn(r"C:\Users\Admin\Desktop\Sketch", body)
        self.assertEqual(bundle["support_scope"]["privacy_default"], "redacted")
        self.assertFalse(bundle["support_scope"]["includes_source_code"])
        self.assertFalse(bundle["support_scope"]["includes_codex_chat"])
        self.assertIn("verify", bundle["included_history_filters"])

    def test_diagnostics_are_consent_based_redacted_and_exportable(self) -> None:
        config = {"diagnostics": {"enabled": False}}
        disabled = record_diagnostic(config, "verify_failed", {"workspace": r"C:\Private\Sketch", "content": "secret"})
        self.assertFalse(disabled["recorded"])

        sanitized = sanitize_payload({
            "workspace": r"C:\Private\Sketch",
            "content": "void loop() {}",
            "message": "full Codex chat",
            "main_sketch": "Blink.ino",
            "status": "failed",
        })
        self.assertIn("workspace_hash", sanitized)
        self.assertEqual(sanitized["sketch_ext"], ".ino")
        self.assertNotIn("content", sanitized)
        self.assertNotIn("message", sanitized)

        enabled_config = {"diagnostics": {"enabled": True}}
        self.assertTrue(diagnostics_settings(enabled_config)["enabled"])
        export = diagnostics_export(
            enabled_config,
            {"display_name": "Talos", "version": "0.4.0", "channel": "Pre-Alpha"},
            {"mode": "source", "version": "0.4.0", "channel": "Pre-Alpha", "python": "3.11"},
        )
        self.assertFalse(export["consent"]["remote_upload"])
        self.assertTrue(export["consent"]["user_preview_required"])
        self.assertFalse(export["data_policy"]["contains_source_code"])
        self.assertFalse(export["data_policy"]["contains_codex_chat"])

    def test_codex_status_starts_runtime_without_blocking_for_handshake(self) -> None:
        bridge = CodexBridge(persist_reviews=False)

        with patch.object(bridge, "start_async") as start_async:
            status = bridge.status()

        start_async.assert_called_once_with()
        self.assertFalse(status["connected"])
        self.assertFalse(status["ok"])

    def test_codex_start_respects_reconnect_cooldown(self) -> None:
        bridge = CodexBridge(persist_reviews=False)
        bridge._next_retry_at = time.monotonic() + 60

        with patch("talos.codex_bridge.threading.Thread") as thread:
            bridge.start_async()
            bridge.start_async(force=True)

        self.assertEqual(thread.call_count, 1)

    def test_codex_reconnect_does_not_replay_interrupted_turn(self) -> None:
        bridge = CodexBridge(persist_reviews=False)
        bridge._turn_running = True
        bridge._turn_id = "turn-1"
        bridge._turn_workspace = r"C:\Sketch"
        bridge._turn_protocol_changes = {"Sketch.ino": {"path": "Sketch.ino"}}

        with patch.object(bridge, "start_async") as start_async:
            result = bridge.reconnect()

        self.assertTrue(result["ok"])
        self.assertFalse(bridge._turn_running)
        self.assertEqual(bridge._turn_id, "")
        self.assertEqual(bridge._turn_protocol_changes, {})
        self.assertIn("not replayed", bridge._turn_error)
        status = bridge.status(start=False)
        self.assertEqual(status["task_state"]["state"], "retry_reconnect")
        self.assertEqual(status["task_state"]["replay_guard"], "manual_send_required")
        self.assertIn("not replayed", status["task_state"]["detail"])
        start_async.assert_called_once_with(force=True)

    def test_codex_cancel_reports_manual_replay_guard(self) -> None:
        bridge = CodexBridge(persist_reviews=False)
        bridge._turn_running = True
        bridge._turn_id = ""

        result = bridge.cancel_turn()
        status = bridge.status(start=False)

        self.assertTrue(result["ok"])
        self.assertEqual(status["task_state"]["state"], "cancelled_turn")
        self.assertEqual(status["task_state"]["last_turn_status"], "cancelled")
        self.assertEqual(status["task_state"]["replay_guard"], "manual_send_required")

    def test_board_mapping_uses_window_plugin_host_process_tree(self) -> None:
        windows = [
            {"pid": 101, "title": "first | Arduino IDE 2.3.4"},
            {"pid": 201, "title": "second | Arduino IDE 2.3.4"},
        ]
        processes = [
            {"name": "Arduino IDE.exe", "pid": 101, "created_at": 1000, "command_line": "--type=renderer"},
            {"name": "Arduino IDE.exe", "pid": 102, "created_at": 2000, "command_line": r"backend\plugin-host"},
            {"name": "arduino-language-server.exe", "pid": 103, "parent_pid": 102, "fqbn": "vendor:arch:first", "board_name": "First"},
            {"name": "Arduino IDE.exe", "pid": 201, "created_at": 20000, "command_line": "--type=renderer"},
            {"name": "Arduino IDE.exe", "pid": 202, "created_at": 21000, "command_line": r"backend\plugin-host"},
            {"name": "arduino-language-server.exe", "pid": 203, "parent_pid": 202, "fqbn": "vendor:arch:second", "board_name": "Second"},
        ]

        mapping = boards_by_window_title(windows, processes)

        self.assertEqual(mapping["first | Arduino IDE 2.3.4"]["board_name"], "First")
        self.assertEqual(mapping["second | Arduino IDE 2.3.4"]["board_name"], "Second")

    def test_board_mapping_rejects_shared_electron_window_pid(self) -> None:
        windows = [
            {"pid": 101, "title": "first | Arduino IDE 2.3.4"},
            {"pid": 101, "title": "second | Arduino IDE 2.3.4"},
        ]
        processes = [
            {"name": "Arduino IDE.exe", "pid": 101, "created_at": 1000, "command_line": ""},
            {"name": "Arduino IDE.exe", "pid": 102, "created_at": 2000, "command_line": r"backend\plugin-host"},
            {"name": "arduino-language-server.exe", "pid": 103, "parent_pid": 102, "fqbn": "vendor:arch:first", "board_name": "First"},
        ]

        self.assertEqual(boards_by_window_title(windows, processes), {})

    def test_arduino_workspace_summary_finds_main_sketch_and_tabs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            (root / "Blink.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (root / "helpers.cpp").write_text("int value() { return 1; }\n", encoding="utf-8")
            (root / "notes.tmp").write_text("ignored\n", encoding="utf-8")

            summary = workspace_summary({"arduino_workspace_path": str(root), "arduino_fqbn": "arduino:avr:uno"})

            self.assertTrue(summary["valid"])
            self.assertEqual(summary["main_sketch"], "Blink.ino")
            self.assertEqual([item["path"] for item in summary["files"]], ["Blink.ino", "helpers.cpp"])

    def test_arduino_workspace_summary_includes_header_and_cpp_tabs_case_insensitively(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Controller"
            root.mkdir()
            (root / "Controller.ino").write_text("void setup() {}\n", encoding="utf-8")
            (root / "motor.CPP").write_text("void motor_init() {}\n", encoding="utf-8")
            (root / "motor.H").write_text("void motor_init();\n", encoding="utf-8")

            summary = workspace_summary({"arduino_workspace_path": str(root), "arduino_fqbn": ""})

            self.assertEqual(
                [item["path"] for item in summary["files"]],
                ["Controller.ino", "motor.CPP", "motor.H"],
            )

    def test_native_bridge_extracts_multiple_open_sketch_titles(self) -> None:
        self.assertEqual(extract_ino_names("1.ino - Arduino IDE"), ["1.ino"])
        self.assertEqual(extract_ino_names("2.ino | Arduino IDE"), ["2.ino"])
        self.assertEqual(extract_ino_names("test | Arduino IDE 2.3.4"), ["test.ino"])
        self.assertEqual(
            extract_ino_names("LQR_pendulum - lqr_controller.cpp | Arduino IDE 2.3.4"),
            ["LQR_pendulum.ino"],
        )
        self.assertEqual(
            extract_ino_names("LQR_pendulum - config.h | Arduino IDE 2.3.4"),
            ["LQR_pendulum.ino"],
        )
        self.assertIsInstance(native_available(), bool)

    def test_native_bridge_extracts_board_from_language_server_command(self) -> None:
        command = (
            'arduino-language-server.exe -cli-daemon-addr localhost:51373 '
            '-fqbn esp32:esp32:esp32:UploadSpeed=921600,CPUFreq=240 '
            '-board-name "ESP32 Dev Module"'
        )

        self.assertEqual(extract_fqbn(command), "esp32:esp32:esp32:UploadSpeed=921600,CPUFreq=240")
        self.assertEqual(extract_board_name(command), "ESP32 Dev Module")

    def test_native_bridge_parses_native_window_rows(self) -> None:
        rows = parse_window_rows_payload("123\tBlink | Arduino IDE 2.3.4\nbad\tIgnored\n456\tTalos")

        self.assertEqual(rows[0], {"pid": 123, "title": "Blink | Arduino IDE 2.3.4"})
        self.assertEqual(rows[1], {"pid": 0, "title": "Ignored"})
        self.assertEqual(rows[2], {"pid": 456, "title": "Talos"})

    def test_native_bridge_parses_native_process_rows(self) -> None:
        rows = parse_process_rows_payload(
            "Arduino IDE.exe\t101\t1\t1781541452000\narduino-language-server.exe\t102\t101\tbad"
        )

        self.assertEqual(rows[0]["name"], "Arduino IDE.exe")
        self.assertEqual(rows[0]["pid"], 101)
        self.assertEqual(rows[0]["parent_pid"], 1)
        self.assertEqual(rows[0]["created_at"], 1781541452000)
        self.assertEqual(rows[1]["created_at"], 0)
        self.assertEqual(rows[1]["fqbn"], "")

    def test_native_tool_processes_merge_native_snapshot_with_cached_command_lines(self) -> None:
        native_bridge._CACHE.clear()
        native_rows = [
            {
                "name": "Arduino IDE.exe",
                "pid": 101,
                "parent_pid": 1,
                "created_at": 10,
                "title": "",
                "command_line": "",
                "ino_paths": [],
                "fqbn": "",
                "board_name": "",
            },
            {
                "name": "arduino-language-server.exe",
                "pid": 102,
                "parent_pid": 101,
                "created_at": 11,
                "title": "",
                "command_line": "",
                "ino_paths": [],
                "fqbn": "",
                "board_name": "",
            },
        ]
        command_rows = [
            {
                "name": "arduino-language-server.exe",
                "pid": 102,
                "parent_pid": 101,
                "created_at": 11,
                "title": "",
                "command_line": "-fqbn esp32:esp32:esp32 -board-name ESP32",
                "ino_paths": [],
                "fqbn": "esp32:esp32:esp32",
                "board_name": "ESP32",
            }
        ]

        with (
            patch("talos.native_bridge.list_arduino_process_rows_native", return_value=native_rows),
            patch("talos.native_bridge.list_arduino_tool_processes_commandline_uncached", return_value=command_rows) as command_scan,
        ):
            first = native_bridge.list_arduino_tool_processes_uncached()
            second = native_bridge.list_arduino_tool_processes_uncached()

        self.assertEqual(command_scan.call_count, 1)
        self.assertEqual(first[1]["fqbn"], "esp32:esp32:esp32")
        self.assertEqual(second[1]["board_name"], "ESP32")

    def test_arduino_discovery_maps_open_sketches_to_folders(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            one = root / "1"
            two = root / "2"
            one.mkdir(parents=True)
            two.mkdir()
            (one / "1.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (two / "2.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                titles=["1.ino - Arduino IDE", "2.ino - Arduino IDE"],
            )

            self.assertEqual([project["sketch"] for project in projects], ["1.ino", "2.ino"])
            self.assertEqual([Path(project["path"]).name for project in projects], ["1", "2"])
            self.assertTrue(all(project["valid"] for project in projects))
            self.assertTrue(all(project["source_count"] == 1 for project in projects))

    def test_arduino_discovery_maps_multiple_windows_with_distinct_board_process_trees(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            avr = root / "blink_uno"
            esp = root / "sensor_esp32"
            avr.mkdir(parents=True)
            esp.mkdir()
            (avr / "blink_uno.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (esp / "sensor_esp32.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                window_rows=[
                    {"pid": 101, "title": "blink_uno | Arduino IDE 2.3.4", "created_at": 1000},
                    {"pid": 202, "title": "sensor_esp32 | Arduino IDE 2.3.4", "created_at": 5000},
                ],
                ide_processes=[
                    {"pid": 101, "title": "blink_uno | Arduino IDE 2.3.4", "created_at": 1000, "ino_paths": []},
                    {"pid": 202, "title": "sensor_esp32 | Arduino IDE 2.3.4", "created_at": 5000, "ino_paths": []},
                ],
                tool_processes=[
                    {"pid": 301, "name": "arduino-cli.exe", "command_line": r"backend\plugin-host", "created_at": 1100},
                    {"pid": 302, "name": "arduino-language-server.exe", "parent_pid": 301, "fqbn": "arduino:avr:uno", "board_name": "Arduino Uno"},
                    {"pid": 401, "name": "arduino-cli.exe", "command_line": r"backend\plugin-host", "created_at": 5100},
                    {"pid": 402, "name": "arduino-language-server.exe", "parent_pid": 401, "fqbn": "esp32:esp32:esp32", "board_name": "ESP32 Dev Module"},
                ],
                open_workspaces=[],
                workspace_boards={},
            )

            self.assertEqual([project["sketch"] for project in projects], ["blink_uno.ino", "sensor_esp32.ino"])
            self.assertEqual([project["board_name"] for project in projects], ["Arduino Uno", "ESP32 Dev Module"])
            self.assertTrue(all(project["board_source"] == "process_tree" for project in projects))

    def test_arduino_discovery_maps_ide_2_titles_without_ino_extension(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            sketch = root / "test"
            sketch.mkdir(parents=True)
            (sketch / "test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                titles=["test | Arduino IDE 2.3.4"],
            )

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["sketch"], "test.ino")
            self.assertEqual(Path(projects[0]["path"]).name, "test")
            self.assertTrue(projects[0]["valid"])

    def test_arduino_discovery_uses_window_title_when_process_has_no_ino_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            sketch = root / "test"
            sketch.mkdir(parents=True)
            (sketch / "test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                titles=["test | Arduino IDE 2.3.4"],
                ino_paths=[],
            )

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["sketch"], "test.ino")
            self.assertEqual(projects[0]["source"], "window_title")

    def test_arduino_discovery_reuses_supplied_window_rows(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            sketch = root / "test"
            sketch.mkdir(parents=True)
            (sketch / "test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            with patch("talos.arduino.open_window_titles", side_effect=AssertionError("window titles should be reused")):
                projects = discover_arduino_projects(
                    {"arduino_search_roots": str(root)},
                    window_rows=[{"pid": 123, "title": "test | Arduino IDE 2.3.4"}],
                    tool_processes=[],
                    open_workspaces=[],
                    workspace_boards={},
                )

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["sketch"], "test.ino")

    def test_state_payload_reuses_one_detection_snapshot(self) -> None:
        config = {"theme": "light", "arduino_workspace_path": "", "arduino_fqbn": ""}
        with (
            patch("talos.server.load_config", return_value=config),
            patch("talos.server.list_arduino_ide_processes", return_value=[]) as ide_scan,
            patch("talos.server.list_arduino_tool_processes", return_value=[]) as tool_scan,
            patch("talos.server.list_window_rows", return_value=[{"pid": 0, "title": "test | Arduino IDE 2.3.4"}]) as window_scan,
            patch("talos.server.list_arduino_open_workspaces", return_value=[]),
            patch("talos.server.list_arduino_workspace_boards", return_value={}),
        ):
            payload = state_payload()

        self.assertEqual(ide_scan.call_count, 1)
        self.assertEqual(tool_scan.call_count, 1)
        self.assertEqual(window_scan.call_count, 1)
        self.assertEqual(payload["app"]["publisher"], "T-Engine")
        self.assertEqual(payload["app"]["version"], "0.3.0")
        self.assertEqual(payload["app"]["channel"], "Beta")
        self.assertEqual(payload["build"]["schema_version"], 1)
        self.assertEqual(payload["build"]["version"], "0.3.0")
        self.assertEqual(payload["build"]["channel"], "Beta")
        self.assertIn(payload["build"]["mode"], {"source", "packaged"})
        self.assertIn("python", payload["build"])
        self.assertTrue(payload["arduino_ide"]["running"])
        self.assertIn("arduino_profile_readiness", payload)
        self.assertIn("POST /api/release_evidence", payload["tools"])
        self.assertIn("GET /api/support_bundle", payload["tools"])

    def test_arduino_discovery_does_not_include_configured_folder_without_open_ide_signal(self) -> None:
        with TemporaryDirectory() as tmp:
            sketch = Path(tmp) / "test"
            sketch.mkdir()
            (sketch / "test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects({"arduino_workspace_path": str(sketch)}, titles=[])

            self.assertEqual(projects, [])

    def test_arduino_discovery_ignores_persisted_workspace_after_ide_closes(self) -> None:
        with TemporaryDirectory() as tmp:
            sketch = Path(tmp) / "closed_sketch"
            sketch.mkdir()
            (sketch / "closed_sketch.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            with (
                patch("talos.arduino.list_arduino_ide_processes", return_value=[]),
                patch("talos.arduino.list_arduino_tool_processes", return_value=[]),
                patch("talos.arduino.list_window_rows", return_value=[]),
                patch("talos.arduino.open_window_titles", return_value=["Talos", "desktop_app.py - Visual Studio Code"]),
                patch("talos.arduino.list_arduino_open_workspaces", return_value=[{"path": str(sketch), "time": 1}]),
                patch(
                    "talos.arduino.list_arduino_workspace_boards",
                    return_value={
                        str(sketch.resolve()).lower(): {
                            "fqbn": "esp32:esp32:esp32",
                            "name": "ESP32 Dev Module",
                        }
                    },
                ),
            ):
                projects = discover_arduino_projects({})

            self.assertEqual(projects, [])

    def test_arduino_discovery_maps_open_process_ino_path_to_folder(self) -> None:
        with TemporaryDirectory() as tmp:
            sketch = Path(tmp) / "test"
            sketch.mkdir()
            ino = sketch / "test.ino"
            ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects({}, titles=[], ino_paths=[str(ino)])

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["sketch"], "test.ino")
            self.assertEqual(Path(projects[0]["path"]).name, "test")
            self.assertTrue(projects[0]["valid"])

    def test_arduino_discovery_lists_multiple_open_ino_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            first = Path(tmp) / "one"
            second = Path(tmp) / "two"
            first.mkdir()
            second.mkdir()
            one = first / "one.ino"
            two = second / "two.ino"
            one.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            two.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects({}, titles=[], ino_paths=[str(one), str(two)])

            self.assertEqual([project["sketch"] for project in projects], ["one.ino", "two.ino"])

    def test_arduino_discovery_combines_process_paths_and_window_titles(self) -> None:
        with TemporaryDirectory() as tmp:
            desktop = Path(tmp) / "Desktop"
            parent = desktop / "test"
            title_sketch = parent
            process_sketch = parent / "mpu6050"
            configured_sketch = parent / "velo_test"
            title_sketch.mkdir(parents=True)
            process_sketch.mkdir()
            configured_sketch.mkdir()
            (title_sketch / "test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            process_ino = process_sketch / "mpu6050.ino"
            process_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (configured_sketch / "velo_test.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {"arduino_workspace_path": str(configured_sketch)},
                titles=["test | Arduino IDE 2.3.4"],
                ino_paths=[str(process_ino)],
            )

            self.assertEqual([project["sketch"] for project in projects], ["mpu6050.ino", "test.ino"])
            self.assertTrue(all(project["valid"] for project in projects))

    def test_arduino_discovery_ignores_stale_process_path_for_unsaved_current_sketch(self) -> None:
        with TemporaryDirectory() as tmp:
            old = Path(tmp) / "old"
            old.mkdir()
            old_ino = old / "old.ino"
            old_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {},
                titles=["sketch_jun11a | Arduino IDE 2.3.4"],
                ino_paths=[str(old_ino)],
            )

            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["sketch"], "sketch_jun11a.ino")
            self.assertEqual(projects[0]["path"], "")
            self.assertFalse(projects[0]["valid"])
            self.assertEqual(projects[0]["source"], "window_title")
            self.assertTrue(projects[0]["unsaved"])
            self.assertEqual(projects[0]["status"], "unsaved")

    def test_arduino_discovery_keeps_sketch_folder_when_active_title_is_cpp_or_header_tab(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            sketch = root / "LQR_pendulum"
            sketch.mkdir(parents=True)
            (sketch / "LQR_pendulum.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (sketch / "encoder.cpp").write_text("int ticks = 0;\n", encoding="utf-8")
            (sketch / "encoder.h").write_text("#pragma once\n", encoding="utf-8")

            cpp_projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                titles=["LQR_pendulum - encoder.cpp | Arduino IDE 2.3.4"],
            )
            header_projects = discover_arduino_projects(
                {"arduino_search_roots": str(root)},
                titles=["LQR_pendulum - encoder.h | Arduino IDE 2.3.4"],
            )

            self.assertEqual(cpp_projects[0]["sketch"], "LQR_pendulum.ino")
            self.assertEqual(header_projects[0]["sketch"], "LQR_pendulum.ino")
            self.assertEqual(cpp_projects[0]["source_count"], 3)

    def test_arduino_discovery_attaches_detected_board_to_open_project(self) -> None:
        with TemporaryDirectory() as tmp:
            sketch = Path(tmp) / "test"
            sketch.mkdir()
            ino = sketch / "test.ino"
            ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {},
                titles=[],
                ino_paths=[str(ino)],
                tool_processes=[
                    {
                        "fqbn": "esp32:esp32:esp32:UploadSpeed=921600",
                        "board_name": "ESP32 Dev Module",
                    }
                ],
            )

            self.assertEqual(projects[0]["fqbn"], "esp32:esp32:esp32:UploadSpeed=921600")
            self.assertEqual(projects[0]["board_name"], "ESP32 Dev Module")

    def test_arduino_discovery_matches_board_by_sketch_name_hint(self) -> None:
        with TemporaryDirectory() as tmp:
            first = Path(tmp) / "mpu6050"
            second = Path(tmp) / "mpu6050_esp32c3"
            first.mkdir()
            second.mkdir()
            first_ino = first / "mpu6050.ino"
            second_ino = second / "mpu6050_esp32c3.ino"
            first_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            second_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {},
                titles=[],
                ino_paths=[str(first_ino), str(second_ino)],
                tool_processes=[
                    {
                        "fqbn": "esp32:esp32:esp32:UploadSpeed=921600",
                        "board_name": "ESP32 Dev Module",
                    },
                    {
                        "fqbn": "esp32:esp32:esp32c3:UploadSpeed=921600",
                        "board_name": "ESP32C3 Dev Module",
                    },
                ],
            )

            self.assertEqual(projects[0]["board_name"], "ESP32 Dev Module")
            self.assertEqual(projects[1]["board_name"], "ESP32C3 Dev Module")

    def test_arduino_discovery_prefers_exact_workspace_board_state(self) -> None:
        with TemporaryDirectory() as tmp:
            first = Path(tmp) / "controller_a"
            second = Path(tmp) / "controller_b"
            first.mkdir()
            second.mkdir()
            first_ino = first / "controller_a.ino"
            second_ino = second / "controller_b.ino"
            first_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            second_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            projects = discover_arduino_projects(
                {},
                titles=[],
                ino_paths=[str(first_ino), str(second_ino)],
                tool_processes=[
                    {
                        "fqbn": "esp32:esp32:esp32:UploadSpeed=921600",
                        "board_name": "ESP32 Dev Module",
                    },
                    {
                        "fqbn": "esp32:esp32:esp32s3:USBMode=hwcdc",
                        "board_name": "ESP32S3 Dev Module",
                    },
                ],
                workspace_boards={
                    str(first.resolve()).lower(): {
                        "fqbn": "esp32:esp32:esp32s3",
                        "name": "ESP32S3 Dev Module",
                    },
                    str(second.resolve()).lower(): {
                        "fqbn": "esp32:esp32:esp32",
                        "name": "ESP32 Dev Module",
                    },
                },
            )

            self.assertEqual(projects[0]["board_name"], "ESP32S3 Dev Module")
            self.assertEqual(projects[0]["board_source"], "workspace_state")
            self.assertEqual(projects[1]["board_name"], "ESP32 Dev Module")

    def test_arduino_discovery_reports_missing_and_ambiguous_board_diagnostics(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Arduino"
            first = root / "plain"
            second = root / "controller"
            first.mkdir(parents=True)
            second.mkdir()
            first_ino = first / "plain.ino"
            second_ino = second / "controller.ino"
            first_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            second_ino.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            missing = discover_arduino_projects({}, titles=[], ino_paths=[str(first_ino)])
            ambiguous = discover_arduino_projects(
                {},
                titles=[],
                ino_paths=[str(second_ino)],
                tool_processes=[
                    {"fqbn": "arduino:avr:uno", "board_name": "Arduino Uno"},
                    {"fqbn": "esp32:esp32:esp32", "board_name": "ESP32 Dev Module"},
                ],
            )

            self.assertEqual(missing[0]["board_source"], "missing")
            self.assertEqual(missing[0]["diagnostics"][0]["code"], "missing_board")
            self.assertEqual(ambiguous[0]["board_source"], "ambiguous")
            self.assertEqual(ambiguous[0]["fqbn"], "")
            self.assertEqual(ambiguous[0]["diagnostics"][0]["code"], "ambiguous_board")

    def test_arduino_context_includes_sketch_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Sensor"
            root.mkdir()
            (root / "Sensor.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            context = workspace_context({"arduino_workspace_path": str(root), "arduino_fqbn": ""})

            self.assertIn("Arduino workspace context", context)
            self.assertIn("--- Sensor.ino ---", context)

    def test_workspace_map_includes_board_tabs_and_latest_diagnostics(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Sensor"
            root.mkdir()
            (root / "Sensor.ino").write_text("void setup() {}\n", encoding="utf-8")
            (root / "motor.cpp").write_text("void motor() {}\n", encoding="utf-8")

            result = workspace_map(
                {"arduino_workspace_path": str(root), "arduino_fqbn": "arduino:avr:uno"},
                {"status": "passed", "time": "2026-06-24", "result": {
                    "issues": [{"message": "warning"}],
                    "libraries": [{"name": "Wire", "version": "1.0.0"}],
                    "platforms": [{"name": "arduino:avr", "version": "1.8.6"}],
                }},
            )

            self.assertTrue(result["valid"])
            self.assertEqual(result["main_sketch"], "Sensor.ino")
            self.assertEqual(result["board"]["fqbn"], "arduino:avr:uno")
            self.assertEqual(result["source_tab_count"], 2)
            self.assertEqual(result["diagnostics"]["status"], "passed")
            self.assertEqual(result["diagnostics"]["libraries"][0]["name"], "Wire")

    def test_environment_profile_is_isolated_per_resolved_sketch_folder(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "First"
            second = root / "Second"
            first.mkdir()
            second.mkdir()
            config = {"arduino_profiles": {}, "arduino_workspace_path": str(first), "arduino_fqbn": "arduino:avr:uno"}

            saved = save_environment_profile(config, str(first), {
                "fqbn": "esp32:esp32:esp32",
                "serial_port": "COM5",
                "baud_rate": "921600",
                "build_flags": ["-DDEBUG"],
                "libraries": "Wire\nArduinoJson",
            })

            self.assertTrue(saved["ok"])
            self.assertEqual(environment_profile(config, str(first))["serial_port"], "COM5")
            self.assertEqual(environment_profile(config, str(second))["libraries"], [])
            self.assertEqual(workspace_summary(config)["fqbn"], "esp32:esp32:esp32")

            mapped = workspace_map(config)
            self.assertEqual(mapped["environment_profile"]["baud_rate"], 921600)
            self.assertEqual(mapped["environment_profile"]["libraries"], ["Wire", "ArduinoJson"])

    def test_profile_readiness_validates_fqbn_and_build_properties(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            (root / "Blink.ino").write_text("void setup() {}\n", encoding="utf-8")
            config = {"arduino_profiles": {}, "arduino_workspace_path": str(root), "arduino_fqbn": ""}

            missing = profile_readiness(config)
            self.assertFalse(missing["ready"])
            self.assertEqual(missing["issues"][0]["code"], "missing_fqbn")

            save_environment_profile(config, str(root), {
                "fqbn": "arduino:avr:uno",
                "build_properties": ["bad-property"],
            })
            invalid = profile_readiness(config)
            self.assertFalse(invalid["ready"])
            self.assertEqual(invalid["issues"][0]["code"], "invalid_build_property")

            save_environment_profile(config, str(root), {
                "fqbn": "arduino:avr:uno",
                "build_properties": ["compiler.cpp.extra_flags=-DDEBUG"],
            })
            ready = profile_readiness(config)
            self.assertTrue(ready["ready"])
            self.assertEqual(ready["fqbn"], "arduino:avr:uno")

    def test_legacy_user_state_is_backed_up_and_migrated_without_losing_records(self) -> None:
        with TemporaryDirectory() as tmp:
            config_dir = Path(tmp) / "config"
            config_dir.mkdir()
            config_path = config_dir / "config.json"
            legacy_config = {
                "theme": "dark",
                "arduino_workspace_path": r"C:\Sketches\Blink",
                "arduino_profiles": {"c:\\sketches\\blink": {"fqbn": "arduino:avr:uno"}},
            }
            config_path.write_text(json.dumps(legacy_config), encoding="utf-8")

            with patch.object(core, "CONFIG_PATH", config_path):
                migrated = core.load_config()

            self.assertEqual(migrated["schema_version"], core.CONFIG_SCHEMA_VERSION)
            self.assertEqual(migrated["theme"], "dark")
            self.assertIn("c:\\sketches\\blink", migrated["arduino_profiles"])
            self.assertTrue(list((config_dir / "backups").glob("config.migration.*.json")))

            checkpoint_path = config_dir / "checkpoints.json"
            checkpoint_path.write_text(json.dumps({"checkpoints": [{"id": "legacy-checkpoint"}]}), encoding="utf-8")
            with patch.object(checkpoint_store, "CHECKPOINT_PATH", checkpoint_path):
                checkpoints = checkpoint_store._load()
            self.assertEqual(checkpoints[0]["id"], "legacy-checkpoint")
            self.assertEqual(json.loads(checkpoint_path.read_text(encoding="utf-8"))["schema_version"], 1)

            history_path = config_dir / "run_history.json"
            history_path.write_text(json.dumps({"events": [{"id": "legacy-history"}]}), encoding="utf-8")
            with patch.object(run_history_store, "RUN_HISTORY_PATH", history_path):
                events = run_history_store._load_events()
            self.assertEqual(events[0]["id"], "legacy-history")
            self.assertEqual(json.loads(history_path.read_text(encoding="utf-8"))["schema_version"], 1)
            self.assertTrue(list((config_dir / "backups").glob("*.json")))

    def test_future_schema_is_not_downgraded_or_overwritten(self) -> None:
        with TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "config.json"
            future = {"schema_version": core.CONFIG_SCHEMA_VERSION + 1, "theme": "dark", "future_setting": True}
            config_path.write_text(json.dumps(future), encoding="utf-8")

            with patch.object(core, "CONFIG_PATH", config_path):
                loaded = core.load_config()

            self.assertEqual(loaded["schema_version"], core.CONFIG_SCHEMA_VERSION + 1)
            self.assertTrue(loaded["future_setting"])
            self.assertEqual(json.loads(config_path.read_text(encoding="utf-8")), future)

    def test_arduino_verify_requires_fqbn_before_compile(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            (root / "Blink.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")

            result = run_arduino_compile({"arduino_workspace_path": str(root), "arduino_fqbn": ""})

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "missing_fqbn")
            self.assertIn("prepare", result["timings"])
            self.assertIn("total", result["timings"])

    def test_compile_cache_is_keyed_by_workspace_content_and_can_be_cleared(self) -> None:
        clear_arduino_compile_cache()
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "Blink"
            workspace.mkdir()
            sketch = workspace / "Blink.ino"
            sketch.write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            summary = {"fqbn": "arduino:avr:uno"}
            profile = {"build_flags": [], "build_properties": []}

            initial_key = compile_cache_key(workspace, summary, profile, "arduino-cli", None)
            from talos.arduino import store_compile_result
            store_compile_result(initial_key, {"ok": True, "status": "passed", "output": "ok"})
            cached = cached_compile_result(initial_key)

            self.assertTrue(cached["cache"]["hit"])
            self.assertEqual(cached["output"], "ok")

            sketch.write_text("void setup() { Serial.begin(9600); }\nvoid loop() {}\n", encoding="utf-8")
            changed_key = compile_cache_key(workspace, summary, profile, "arduino-cli", None)
            self.assertNotEqual(initial_key, changed_key)
            self.assertEqual(clear_arduino_compile_cache(), 1)
            self.assertIsNone(cached_compile_result(initial_key))

    def test_compile_cache_key_includes_profile_cli_and_override_changes(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "Blink"
            workspace.mkdir()
            (workspace / "Blink.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            summary = {"fqbn": "arduino:avr:uno"}
            profile = {
                "build_flags": ["-DDEBUG"],
                "build_properties": ["compiler.cpp.extra_flags=-DDEBUG"],
                "serial_port": "COM3",
                "baud_rate": 115200,
                "libraries": ["Wire"],
            }

            base = compile_cache_key(workspace, summary, profile, "arduino-cli-a", None)
            changed_board = compile_cache_key(workspace, {"fqbn": "esp32:esp32:esp32"}, profile, "arduino-cli-a", None)
            changed_profile = compile_cache_key(workspace, summary, {**profile, "serial_port": "COM4"}, "arduino-cli-a", None)
            changed_cli = compile_cache_key(workspace, summary, profile, "arduino-cli-b", None)
            changed_override = compile_cache_key(workspace, summary, profile, "arduino-cli-a", {"Blink.ino": "void setup() {}\n"})

            self.assertEqual(len({base, changed_board, changed_profile, changed_cli, changed_override}), 5)

    def test_compile_cache_clear_result_and_cached_runtime_feedback(self) -> None:
        clear_arduino_compile_cache()
        from talos.arduino import store_compile_result

        store_compile_result("cache-key", {"ok": True, "status": "passed", "output": "ok"})
        cleared = clear_arduino_compile_cache_result()

        self.assertTrue(cleared["ok"])
        self.assertEqual(cleared["cleared"], 1)
        self.assertIn("Cleared 1", cleared["message"])
        self.assertIsNone(cached_compile_result("cache-key"))

    def test_verify_runtime_status_flags_slow_compile_and_total(self) -> None:
        fast = verify_runtime_status({"prepare": 0.01, "compile": 0.5, "total": 0.7})
        slow = verify_runtime_status({"prepare": 0.01, "compile": 13.0, "total": 16.0})

        self.assertFalse(fast["slow"])
        self.assertTrue(slow["slow"])
        self.assertEqual(slow["slow_steps"], ["total", "compile"])
        self.assertGreaterEqual(slow["thresholds"]["total"], 1)

    def test_verify_cancel_feedback_reports_idle_state(self) -> None:
        result = arduino_module.cancel_arduino_compile()

        self.assertFalse(result["ok"])
        self.assertFalse(result["active"])
        self.assertEqual(result["status"], "idle")
        self.assertIn("No Arduino compile", result["message"])

    def test_verify_ui_resets_output_before_new_request(self) -> None:
        script = (Path(__file__).parents[1] / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        verify_fn = re.search(r"async function verifyArduinoWorkspace[\s\S]+?async function recordReleaseEvidence", script)
        self.assertIsNotNone(verify_fn)
        body = verify_fn.group(0)

        self.assertLess(body.index("renderVerifyOutput(null,"), body.index('await api("/api/arduino_verify"'))
        self.assertIn("Compiling the current Talos editor draft", body)
        self.assertIn("Copying sketch folder to sandbox and running arduino-cli compile", body)
        self.assertIn("setArduinoVerifyRunning(true)", body)

    def test_save_and_verify_compiles_editor_draft_before_saving(self) -> None:
        script = (Path(__file__).parents[1] / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        save_verify_fn = re.search(r"async function saveAndVerifyWorkspace[\s\S]+?async function rollbackWorkspaceFile", script)
        self.assertIsNotNone(save_verify_fn)
        body = save_verify_fn.group(0)

        self.assertLess(
            body.index("await verifyArduinoWorkspace"),
            body.index("await saveWorkspaceFile({ skipVerifyWarning: true })"),
        )
        self.assertIn("sandbox verify did not pass. Arduino IDE was not changed", body)
        self.assertIn("Save + Verify runs sandbox compile before saving", body)

    def test_codex_save_warns_without_current_successful_verify(self) -> None:
        script = (Path(__file__).parents[1] / "ui" / "web_frontend" / "app.js").read_text(encoding="utf-8")
        save_fn = re.search(r"async function saveWorkspaceFile[\s\S]+?async function saveAndVerifyWorkspace", script)
        self.assertIsNotNone(save_fn)
        body = save_fn.group(0)

        self.assertIn("shouldWarnUnverifiedCodexSave", body)
        self.assertIn("has not passed a current Verify Sandbox run", body)
        self.assertIn("skipVerifyWarning", body)

    def test_arduino_compile_output_parser_cleans_ansi_and_extracts_summary(self) -> None:
        output = (
            "Sketch uses 322548 bytes (24%) of program storage space. Maximum is 1310720 bytes.\n"
            "Global variables use 13796 bytes (4%) of dynamic memory, leaving 313884 bytes for local variables. Maximum is 327680 bytes.\n\n"
            "\x1b[92mUsed library\x1b[0m \x1b[92mVersion\x1b[0m \x1b[90mPath\x1b[0m\n"
            "\x1b[93mWire\x1b[0m         3.3.6   \x1b[90mC:\\Arduino\\Wire\x1b[0m\n\n"
            "\x1b[92mUsed platform\x1b[0m \x1b[92mVersion\x1b[0m \x1b[90mPath\x1b[0m\n"
            "\x1b[93mesp32:esp32\x1b[0m   3.3.6   \x1b[90mC:\\Arduino\\esp32\x1b[0m\n"
        )

        parsed = parse_compile_output(output)

        self.assertNotIn("\x1b", parsed["output"])
        self.assertEqual(parsed["memory"]["program"]["percent"], 24)
        self.assertEqual(parsed["memory"]["dynamic"]["used"], 13796)
        self.assertEqual(parsed["libraries"][0]["name"], "Wire")
        self.assertEqual(parsed["platforms"][0]["name"], "esp32:esp32")

    def test_arduino_compile_output_parser_extracts_file_line_issues(self) -> None:
        output = (
            r"C:\Sketch\Blink.ino:14:7: error: 'missingValue' was not declared in this scope"
            "\n"
            r"C:\Sketch\helpers.cpp:8: warning: unused variable 'sample'"
        )

        issues = parse_compile_output(output)["issues"]

        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]["file"], r"C:\Sketch\Blink.ino")
        self.assertEqual(issues[0]["line"], 14)
        self.assertEqual(issues[0]["column"], 7)
        self.assertEqual(issues[0]["level"], "error")
        self.assertEqual(issues[1]["line"], 8)
        self.assertEqual(issues[1]["column"], 0)
        self.assertEqual(issues[1]["level"], "warning")
        self.assertEqual(
            format_compile_issue_context(issues),
            "Arduino compile issues:\n"
            "ERROR Blink.ino:14:7 - 'missingValue' was not declared in this scope\n"
            "WARNING helpers.cpp:8 - unused variable 'sample'",
        )

    def test_arduino_sandbox_copy_ignores_build_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            (root / "Blink.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (root / "build").mkdir()
            (root / "build" / "old.o").write_text("ignore\n", encoding="utf-8")

            with patch.object(arduino_module, "SANDBOX_ROOT", Path(tmp) / "sandbox"):
                sandbox = copy_workspace_to_sandbox(root)

            self.assertEqual(sandbox.name, "Blink")
            self.assertTrue((sandbox / "Blink.ino").exists())
            self.assertFalse((sandbox / "build").exists())

    def test_arduino_sandbox_copy_ignores_platformio_cache(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            (root / "Blink.ino").write_text("void setup() {}\nvoid loop() {}\n", encoding="utf-8")
            (root / ".pio").mkdir()
            (root / ".pio" / "cache.o").write_text("ignore\n", encoding="utf-8")

            with patch.object(arduino_module, "SANDBOX_ROOT", Path(tmp) / "sandbox"):
                sandbox = copy_workspace_to_sandbox(root)

            self.assertFalse((sandbox / ".pio").exists())

    def test_arduino_workspace_file_write_read_and_delete_are_scoped(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            config = {"arduino_workspace_path": str(root), "arduino_fqbn": ""}

            write_result = write_workspace_file(config, "Blink.ino", "void setup() {}\nvoid loop() {}\n")
            read_result = read_workspace_file(config, "Blink.ino")
            delete_result = delete_workspace_file(config, "Blink.ino")

            self.assertTrue(write_result["ok"])
            self.assertTrue(read_result["ok"])
            self.assertIn("void setup", read_result["content"])
            self.assertIsInstance(write_result["mtime_ns"], int)
            self.assertIsInstance(read_result["mtime_ns"], int)
            self.assertTrue(delete_result["ok"])
            self.assertFalse((root / "Blink.ino").exists())

    def test_arduino_workspace_file_write_is_atomic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            target = root / "Blink.ino"
            target.write_text("before\n", encoding="utf-8")
            config = {"arduino_workspace_path": str(root), "arduino_fqbn": ""}

            result = write_workspace_file(config, "Blink.ino", "after\n")

            self.assertTrue(result["ok"])
            self.assertEqual(result["write"], "atomic")
            self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
            self.assertEqual(list(root.glob(".talos-write-*")), [])

    def test_arduino_workspace_file_rejects_escape_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            config = {"arduino_workspace_path": str(root), "arduino_fqbn": ""}

            result = write_workspace_file(config, "../outside.ino", "void setup() {}\n")

            self.assertFalse(result["ok"])
            self.assertFalse((Path(tmp) / "outside.ino").exists())

    def test_checkpoint_rolls_back_only_when_talos_saved_version_is_current(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            target = root / "Blink.ino"
            target.write_text("before\n", encoding="utf-8")
            config = {"arduino_workspace_path": str(root), "arduino_fqbn": ""}
            checkpoint_path = Path(tmp) / "checkpoints.json"

            with patch("talos.checkpoints.CHECKPOINT_PATH", checkpoint_path):
                created = create_before_save_checkpoint(config, "Blink.ino")
                self.assertTrue(created["ok"])
                write_workspace_file(config, "Blink.ino", "saved\n")
                marked = mark_checkpoint_saved(created["checkpoint"]["id"], "saved\n")
                self.assertTrue(marked["ok"])
                latest = latest_saved_checkpoint(config, "Blink.ino")
                self.assertIsNotNone(latest["checkpoint"])
                self.assertEqual(len(latest["history"]), 1)
                self.assertEqual(latest["retention"]["history_limit"], 5)

                rolled_back = rollback_last_checkpoint(config, "Blink.ino")
                self.assertTrue(rolled_back["ok"])
                self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

                created = create_before_save_checkpoint(config, "Blink.ino")
                write_workspace_file(config, "Blink.ino", "saved again\n")
                mark_checkpoint_saved(created["checkpoint"]["id"], "saved again\n")
                target.write_text("external change\n", encoding="utf-8")
                blocked = rollback_last_checkpoint(config, "Blink.ino")
                self.assertFalse(blocked["ok"])

    def test_checkpoint_retention_keeps_short_rollback_history(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "Blink"
            root.mkdir()
            target = root / "Blink.ino"
            target.write_text("start\n", encoding="utf-8")
            config = {"arduino_workspace_path": str(root), "arduino_fqbn": ""}
            checkpoint_path = Path(tmp) / "checkpoints.json"

            with patch("talos.checkpoints.CHECKPOINT_PATH", checkpoint_path):
                for index in range(10):
                    target.write_text(f"before {index}\n", encoding="utf-8")
                    created = create_before_save_checkpoint(config, "Blink.ino")
                    write_workspace_file(config, "Blink.ino", f"saved {index}\n")
                    mark_checkpoint_saved(created["checkpoint"]["id"], f"saved {index}\n")

                latest = latest_saved_checkpoint(config, "Blink.ino")
                stored = json.loads(checkpoint_path.read_text(encoding="utf-8"))["checkpoints"]

                self.assertEqual(len(latest["history"]), 5)
                self.assertLessEqual(len(stored), 8)
                self.assertEqual(latest["checkpoint"]["saved_sha256"], stored[-1]["saved_sha256"])

if __name__ == "__main__":
    unittest.main()
