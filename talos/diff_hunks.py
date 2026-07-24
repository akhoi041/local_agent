from __future__ import annotations

import hashlib
import time
from difflib import SequenceMatcher, unified_diff
from pathlib import Path
from typing import Any

from talos.arduino import is_source_file


def diff_workspace_snapshots(
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for path in sorted(set(before) | set(after), key=str.lower):
        old = before.get(path)
        new = after.get(path)
        if old is None and new is not None:
            kind = "add"
        elif old is not None and new is None:
            kind = "delete"
        elif old != new:
            kind = "update"
        else:
            continue
        changes.append(
            {
                "path": path,
                "kind": kind,
                "before_bytes": int((old or {}).get("bytes") or 0),
                "after_bytes": int((new or {}).get("bytes") or 0),
            }
        )
    return changes


def build_patch_hunks(before: str, after: str) -> list[dict[str, Any]]:
    if before == after:
        return []
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    if not before_lines and after_lines:
        return [{
            "id": "hunk-1",
            "kind": "insert",
            "old_start": 0,
            "old_end": 0,
            "new_start": 0,
            "new_end": len(after_lines),
            "old_lines": [],
            "new_lines": after_lines,
            "review_status": "staged",
        }]
    if before_lines and not after_lines:
        return [{
            "id": "hunk-1",
            "kind": "delete",
            "old_start": 0,
            "old_end": len(before_lines),
            "new_start": 0,
            "new_end": 0,
            "old_lines": before_lines,
            "new_lines": [],
            "review_status": "staged",
        }]
    hunks: list[dict[str, Any]] = []
    matcher = SequenceMatcher(a=before_lines, b=after_lines, autojunk=False)
    for index, (kind, old_start, old_end, new_start, new_end) in enumerate(matcher.get_opcodes(), start=1):
        if kind == "equal":
            continue
        hunks.append(
            {
                "id": f"hunk-{index}",
                "kind": kind,
                "old_start": old_start,
                "old_end": old_end,
                "new_start": new_start,
                "new_end": new_end,
                "old_lines": before_lines[old_start:old_end],
                "new_lines": after_lines[new_start:new_end],
                "review_status": "staged",
            }
        )
    return hunks


def content_with_applied_hunks(base_content: str, hunks: list[dict[str, Any]]) -> str:
    trailing_newline = base_content.endswith("\n")
    original_lines = base_content.split("\n")
    if trailing_newline:
        original_lines.pop()
    output: list[str] = []
    cursor = 0
    for hunk in sorted(hunks, key=lambda item: int(item.get("old_start") or 0)):
        start = int(hunk.get("old_start") or 0)
        end = int(hunk.get("old_end") or start)
        output.extend(original_lines[cursor:start])
        if hunk.get("review_status") == "applied-to-editor":
            output.extend(str(line) for line in hunk.get("new_lines") or [])
        else:
            output.extend(original_lines[start:end])
        cursor = end
    output.extend(original_lines[cursor:])
    return "\n".join(output) + ("\n" if trailing_newline else "")


def staged_patch_files(
    source_workspace: str | Path,
    staging_workspace: str | Path,
    changes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source = Path(source_workspace).resolve()
    staging = Path(staging_workspace).resolve()
    files: list[dict[str, Any]] = []
    for change in changes:
        relative = str(change.get("path") or "").replace("\\", "/")
        source_path = (source / relative).resolve()
        staging_path = (staging / relative).resolve()
        try:
            source_path.relative_to(source)
            staging_path.relative_to(staging)
        except ValueError:
            continue
        if not is_source_file(staging_path if staging_path.exists() else source_path):
            continue
        before = source_path.read_text(encoding="utf-8", errors="replace") if source_path.exists() else ""
        after = staging_path.read_text(encoding="utf-8", errors="replace") if staging_path.exists() else ""
        kind = str(change.get("kind") or "update")
        hunks = build_patch_hunks(before, after)
        item = {
            **change,
            "path": relative,
            "kind": kind,
            "diff": "".join(unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=relative,
                tofile=relative,
            )),
            "review_status": "staged",
            "base_content": before,
            "base_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest(),
            "hunks": hunks,
            **({"content": after} if kind != "delete" else {}),
        }
        item["review_summary"] = review_summary_for_file(item)
        files.append(item)
    return files


def review_summary_for_file(file: dict[str, Any]) -> dict[str, int]:
    statuses = [str(hunk.get("review_status") or "staged") for hunk in file.get("hunks") or []]
    if not statuses:
        statuses = [str(file.get("review_status") or "staged")]
    summary = {
        "total": len(statuses),
        "pending": 0,
        "applied_to_editor": 0,
        "rejected": 0,
        "saved": 0,
        "conflict": 0,
        "recovered": 0,
    }
    for status in statuses:
        if status in {"staged", "reviewing"}:
            summary["pending"] += 1
        elif status == "applied-to-editor":
            summary["applied_to_editor"] += 1
        elif status == "rejected":
            summary["rejected"] += 1
        elif status == "saved":
            summary["saved"] += 1
        elif status == "conflict":
            summary["conflict"] += 1
        elif status == "recovered":
            summary["recovered"] += 1
    return summary


def review_summary_for_patch(patch: dict[str, Any]) -> dict[str, int]:
    summary = {
        "files": 0,
        "pending": 0,
        "applied_to_editor": 0,
        "rejected": 0,
        "saved": 0,
        "conflict": 0,
        "recovered": 0,
    }
    for file in patch.get("files") or []:
        file_summary = review_summary_for_file(file)
        file["review_summary"] = file_summary
        summary["files"] += 1
        for key in ("pending", "applied_to_editor", "rejected", "saved", "conflict", "recovered"):
            summary[key] += int(file_summary.get(key) or 0)
    return summary


def measure_hunk_timing(before: str, after: str) -> dict[str, Any]:
    started = time.perf_counter()
    hunks = build_patch_hunks(before, after)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "elapsed_ms": elapsed_ms,
        "hunks": len(hunks),
        "before_bytes": len(before.encode("utf-8")),
        "after_bytes": len(after.encode("utf-8")),
    }
