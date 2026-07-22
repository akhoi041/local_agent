from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from talos import native_bridge as nb

WORKSPACE_SAMPLE_ROOTS = (ROOT / "talos", ROOT / "ui" / "web_frontend")
SAMPLE_SUFFIXES = {".py", ".js", ".css", ".html", ".c", ".h", ".md"}
NATIVE_THRESHOLD_RESULTS = {"native_window_rows", "native_arduino_process_rows", "detection_refresh"}

def sample_workspace_paths() -> list[Path]:
    paths: list[Path] = []
    for sample_root in WORKSPACE_SAMPLE_ROOTS:
        if not sample_root.exists():
            continue
        for path in sample_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SAMPLE_SUFFIXES:
                paths.append(path)
    return sorted(paths)

def benchmark_detection_refresh() -> list[object]:
    return [nb.list_window_rows(), nb.list_arduino_process_rows_native()]

def benchmark_workspace_scan() -> list[str]:
    return [str(path.relative_to(ROOT)) for path in sample_workspace_paths()]

def benchmark_cache_key_hashing() -> list[str]:
    digest = hashlib.sha256()
    for path in sample_workspace_paths():
        stat = path.stat()
        digest.update(str(path.relative_to(ROOT)).encode("utf-8", "replace"))
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(str(stat.st_size).encode("ascii"))
    return [digest.hexdigest()]

def benchmark_diff_hunk_parse() -> list[str]:
    before = [f"line {index}\n" for index in range(240)]
    after = before.copy()
    for index in (12, 72, 144, 210):
        after[index] = f"line {index} changed\n"
    diff = difflib.unified_diff(before, after, fromfile="before.ino", tofile="after.ino", n=3)
    return [line for line in diff if line.startswith("@@")]

def measure(name: str, loader: Callable[[], Any], iterations: int) -> dict[str, Any]:
    durations: list[float] = []
    count = 0
    error = ""
    for _ in range(max(1, iterations)):
        started = time.perf_counter()
        try:
            value = loader()
            count = len(value) if hasattr(value, "__len__") else 1
        except Exception as exc:  # pragma: no cover - diagnostic script path
            error = str(exc)
            count = 0
        durations.append((time.perf_counter() - started) * 1000.0)
        if error:
            break
    return {
        "name": name,
        "ok": not error,
        "count": count,
        "min_ms": round(min(durations), 3),
        "median_ms": round(statistics.median(durations), 3),
        "max_ms": round(max(durations), 3),
        "error": error,
    }

def fallback_status() -> dict[str, bool]:
    return {
        "window_rows_win32": callable(getattr(nb, "list_window_rows_win32", None)),
        "window_titles_win32": callable(getattr(nb, "list_window_titles_win32_fallback", None)),
        "ide_processes_powershell": callable(getattr(nb, "list_arduino_ide_processes_powershell", None)),
        "ide_processes_wmic": callable(getattr(nb, "list_arduino_ide_processes_wmic", None)),
        "tool_processes_powershell": callable(getattr(nb, "list_arduino_tool_processes_powershell", None)),
        "tool_processes_wmic": callable(getattr(nb, "list_arduino_tool_processes_wmic", None)),
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Talos native Windows detection hot paths.")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--max-native-ms", type=float, default=250.0)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args()

    native = nb.native_available()
    results = [
        measure("native_window_rows", nb.list_window_rows, args.iterations),
        measure("native_arduino_process_rows", nb.list_arduino_process_rows_native, args.iterations),
        measure("detection_refresh", benchmark_detection_refresh, args.iterations),
        measure("workspace_scan_sample", benchmark_workspace_scan, args.iterations),
        measure("cache_key_hash_sample", benchmark_cache_key_hashing, args.iterations),
        measure("diff_hunk_parse_sample", benchmark_diff_hunk_parse, args.iterations),
    ]
    fallback = fallback_status()
    payload = {
        "native_available": native,
        "window_rows_export": bool(getattr(nb, "_HAS_NATIVE_WINDOW_ROWS", False)),
        "process_rows_export": bool(getattr(nb, "_HAS_NATIVE_PROCESS_ROWS", False)),
        "iterations": max(1, args.iterations),
        "max_native_ms": args.max_native_ms,
        "results": results,
        "fallback": fallback,
    }

    failures: list[str] = []
    if not native:
        failures.append("native DLL is not available")
    if not payload["window_rows_export"]:
        failures.append("native window-row export is missing")
    if not payload["process_rows_export"]:
        failures.append("native Arduino-process export is missing")
    for result in results:
        if not result["ok"]:
            failures.append(f"{result['name']} failed: {result['error']}")
        elif result["name"] in NATIVE_THRESHOLD_RESULTS and result["max_ms"] > args.max_native_ms:
            failures.append(f"{result['name']} exceeded {args.max_native_ms} ms: {result['max_ms']} ms")
    missing_fallbacks = [name for name, available in fallback.items() if not available]
    if missing_fallbacks:
        failures.append(f"fallback APIs missing: {', '.join(missing_fallbacks)}")
    payload["ok"] = not failures
    payload["failures"] = failures

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Talos native detection benchmark")
        print(f"Native DLL: {'available' if native else 'missing'}")
        print(f"Exports: window_rows={payload['window_rows_export']} process_rows={payload['process_rows_export']}")
        for result in results:
            status = "OK" if result["ok"] else "FAILED"
            print(
                f"{status} {result['name']}: count={result['count']} "
                f"min={result['min_ms']}ms median={result['median_ms']}ms max={result['max_ms']}ms"
            )
        print("Fallback APIs: " + ", ".join(f"{name}={available}" for name, available in fallback.items()))
        if failures:
            print("Failures:")
            for failure in failures:
                print(f"- {failure}")

    return 0 if payload["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
