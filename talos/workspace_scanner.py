from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_SOURCE_EXTENSIONS = frozenset({".ino", ".h", ".hpp", ".c", ".cpp", ".s", ".txt", ".md"})
DEFAULT_IGNORED_DIRS = frozenset({
    ".git",
    ".vs",
    ".vscode",
    "__pycache__",
    ".cache",
    ".pio",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "dist",
    "node_modules",
})
WORKSPACE_SCAN_DEBOUNCE_SECONDS = 0.15


@dataclass(frozen=True)
class WorkspaceScanOptions:
    source_extensions: frozenset[str] = DEFAULT_SOURCE_EXTENSIONS
    ignored_dirs: frozenset[str] = DEFAULT_IGNORED_DIRS


@dataclass(frozen=True)
class WorkspaceScanCacheEntry:
    created_at: float
    key: tuple[Any, ...]
    result: dict[str, Any]


_SCAN_CACHE: dict[str, WorkspaceScanCacheEntry] = {}


def clear_workspace_scan_cache() -> None:
    _SCAN_CACHE.clear()


def _normalized_options(
    source_extensions: Iterable[str] | None = None,
    ignored_dirs: Iterable[str] | None = None,
) -> WorkspaceScanOptions:
    extensions = frozenset(str(item).lower() for item in (source_extensions or DEFAULT_SOURCE_EXTENSIONS))
    ignored = frozenset(str(item) for item in (ignored_dirs or DEFAULT_IGNORED_DIRS))
    return WorkspaceScanOptions(source_extensions=extensions, ignored_dirs=ignored)


def _is_source_file(path: Path, options: WorkspaceScanOptions) -> bool:
    return path.suffix.lower() in options.source_extensions


def _is_ignored(path: Path, workspace: Path, options: WorkspaceScanOptions) -> bool:
    relative_parts = path.relative_to(workspace).parts
    return any(part in options.ignored_dirs or part.startswith(".talos_") for part in relative_parts[:-1])


def _main_sketch_path(workspace: Path, files: list[Path]) -> Path | None:
    ino_files = [path for path in files if path.suffix.lower() == ".ino"]
    if not ino_files:
        return None
    preferred = workspace / f"{workspace.name}.ino"
    for path in ino_files:
        if path.resolve() == preferred.resolve():
            return path
    return ino_files[0]


def _source_sort_key(workspace: Path, path: Path) -> str:
    return path.relative_to(workspace).as_posix().lower()


def _read_line_count(path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return content.count("\n") + (1 if content else 0)


def _file_row(workspace: Path, path: Path, main_sketch: Path | None) -> dict[str, Any]:
    stat = path.stat()
    relative = path.relative_to(workspace).as_posix()
    return {
        "path": relative,
        "bytes": stat.st_size,
        "lines": _read_line_count(path),
        "mtime_ns": stat.st_mtime_ns,
        "extension": path.suffix.lower(),
        "main": bool(main_sketch is not None and path.resolve() == main_sketch.resolve()),
    }


def _scan_candidates(workspace: Path, options: WorkspaceScanOptions) -> tuple[list[Path], tuple[Any, ...]]:
    files: list[Path] = []
    signature: list[tuple[str, int, int]] = []
    if not workspace.exists() or not workspace.is_dir():
        return files, tuple(signature)
    for path in workspace.rglob("*"):
        if not path.is_file() or _is_ignored(path, workspace, options) or not _is_source_file(path, options):
            continue
        files.append(path)
        try:
            stat = path.stat()
            signature.append((path.relative_to(workspace).as_posix(), stat.st_mtime_ns, stat.st_size))
        except OSError:
            signature.append((path.relative_to(workspace).as_posix(), -1, -1))
    return files, tuple(sorted(signature, key=lambda item: item[0].lower()))


def scan_workspace(
    workspace: Path | str | None,
    *,
    source_extensions: Iterable[str] | None = None,
    ignored_dirs: Iterable[str] | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    start = time.perf_counter()
    path = Path(workspace).resolve() if workspace else None
    if path is None:
        return {
            "exists": False,
            "path": "",
            "main_sketch": "",
            "files": [],
            "source_count": 0,
            "timing_ms": round((time.perf_counter() - start) * 1000, 3),
            "cache": {"hit": False, "debounced": False},
        }

    options = _normalized_options(source_extensions, ignored_dirs)
    files, signature = _scan_candidates(path, options)
    cache_key = (str(path).lower(), options.source_extensions, options.ignored_dirs, signature)
    cache_id = str(path).lower()
    entry = _SCAN_CACHE.get(cache_id)
    now = time.monotonic()
    if use_cache and entry and entry.key == cache_key:
        cached = dict(entry.result)
        cached["timing_ms"] = round((time.perf_counter() - start) * 1000, 3)
        cached["cache"] = {
            "hit": True,
            "debounced": (now - entry.created_at) <= WORKSPACE_SCAN_DEBOUNCE_SECONDS,
            "age_ms": round((now - entry.created_at) * 1000, 3),
        }
        return cached

    main_sketch = _main_sketch_path(path, files)
    ordered = sorted(files, key=lambda item: _source_sort_key(path, item))
    result = {
        "exists": path.exists() and path.is_dir(),
        "path": str(path),
        "main_sketch": main_sketch.relative_to(path).as_posix() if main_sketch else "",
        "files": [_file_row(path, item, main_sketch) for item in ordered],
        "source_count": len(ordered),
        "timing_ms": round((time.perf_counter() - start) * 1000, 3),
        "cache": {"hit": False, "debounced": False},
    }
    if use_cache:
        _SCAN_CACHE[cache_id] = WorkspaceScanCacheEntry(created_at=now, key=cache_key, result=dict(result))
    return result
