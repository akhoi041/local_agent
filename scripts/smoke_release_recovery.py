from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from talos import codex_bridge as codex_bridge_module
from talos.codex_bridge import CodexBridge, staged_patch_files

def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        review_path = root / "codex_reviews.json"
        workspace = root / "RecoverySketch"
        staging = root / "RecoverySketch_staging"
        workspace.mkdir()
        staging.mkdir()
        source_file = workspace / "RecoverySketch.ino"
        staging_file = staging / "RecoverySketch.ino"
        source_file.write_text("before\n", encoding="utf-8")
        staging_file.write_text("codex change\n", encoding="utf-8")

        original_review_path = codex_bridge_module.REVIEW_STATE_PATH
        codex_bridge_module.REVIEW_STATE_PATH = review_path
        try:
            files = staged_patch_files(workspace, staging, [{"path": "RecoverySketch.ino", "kind": "update"}])
            initial_bridge = CodexBridge()
            initial_bridge._patches.append({
                "id": "patch-recovery-smoke",
                "workspace": str(workspace),
                "staging_workspace": str(staging),
                "review_status": "staged",
                "files": files,
            })
            initial_bridge._persist_reviews_locked()

            restarted_bridge = CodexBridge()
            recovery = restarted_bridge.status(start=False)["review_recovery"]
            if not recovery.get("pending") or int(recovery.get("count") or 0) != 1:
                raise RuntimeError(f"pending review was not restored after restart: {recovery}")

            restored = restarted_bridge.restore_reviews()
            if not restored.get("ok") or int(restored.get("restored") or 0) != 1:
                raise RuntimeError(f"review restore failed: {restored}")

            source_file.write_text("external arduino edit\n", encoding="utf-8")
            conflict_status = restarted_bridge.status(start=False)
            conflict_file = conflict_status["patches"][0]["files"][0]
            if conflict_file.get("review_status") != "conflict":
                raise RuntimeError(f"external edit was not guarded as a conflict: {conflict_file}")

            kept = restarted_bridge.keep_external_conflict(
                "patch-recovery-smoke",
                str(workspace),
                "RecoverySketch.ino",
            )
            if not kept.get("ok"):
                raise RuntimeError(f"keep external resolution failed: {kept}")
            if source_file.read_text(encoding="utf-8") != "external arduino edit\n":
                raise RuntimeError("external Arduino change was overwritten")

            print(json.dumps({
                "ok": True,
                "scenario": "restart-pending-review-external-change-guard",
                "restored": restored["restored"],
                "resolution": kept["file"]["conflict_resolution"],
                "workspace_content": source_file.read_text(encoding="utf-8"),
            }, indent=2))
            return 0
        finally:
            codex_bridge_module.REVIEW_STATE_PATH = original_review_path

if __name__ == "__main__":
    raise SystemExit(main())
