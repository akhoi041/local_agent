pub mod backend;
pub mod contracts;
pub mod native_helpers;
pub mod runtime_providers;

pub use backend::{
    backend_service_count, bridge_only_backend_service_count, core_services,
    render_core_service_manifest, stage4_exit_ready, CoreService, CoreServiceKind,
};
pub use contracts::{
    api_contract_by_name, api_contracts, render_api_contract_manifest, FieldKind, PayloadContract,
    SCHEMA_VERSION,
};
pub use native_helpers::{
    bridge_only_native_helper_count, native_helper_count, native_helpers,
    render_native_helper_manifest, stage5_exit_ready, NativeHelper, NativeHelperKind,
};
pub use runtime_providers::{
    bridge_only_runtime_provider_count, render_runtime_provider_manifest,
    runtime_provider_boundaries, runtime_provider_count, runtime_provider_method_count,
    stage6_exit_ready, RuntimeProviderBoundary, RuntimeProviderCapability,
};

use std::fs;
use std::path::{Path, PathBuf};
use std::time::UNIX_EPOCH;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PythonRole {
    DebugLauncher,
    CompatibilityBridge,
    TemporaryAdapterShim,
    LogicOwnerToMigrate,
    TestHarness,
    NativeBoundary,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MigrationTarget {
    Shell,
    ApiHost,
    Core,
    RuntimeHost,
    NativeHelper,
    TargetHost,
    Diagnostics,
    Storage,
    TestHarness,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ModuleOwnership {
    pub path: &'static str,
    pub role: PythonRole,
    pub target: MigrationTarget,
    pub hot_path: bool,
    pub reason: &'static str,
}

pub static PYTHON_MODULES: &[ModuleOwnership] = &[
    ModuleOwnership {
        path: "desktop_app.py",
        role: PythonRole::DebugLauncher,
        target: MigrationTarget::Shell,
        hot_path: false,
        reason: "Source/debug launcher only; the replacement shell owns product lifecycle.",
    },
    ModuleOwnership {
        path: "talos/server.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::ApiHost,
        hot_path: false,
        reason: "Compatibility HTTP bridge while typed IPC/API ownership moves out of Python.",
    },
    ModuleOwnership {
        path: "talos/client.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::ApiHost,
        hot_path: false,
        reason: "Local compatibility client, not product logic.",
    },
    ModuleOwnership {
        path: "talos/shell/profile.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::Shell,
        hot_path: false,
        reason: "Temporary shell profile until the Rust/Tauri shell owns app profile state.",
    },
    ModuleOwnership {
        path: "talos/shell/pywebview_provider.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::Shell,
        hot_path: false,
        reason: "Temporary pywebview provider retained only for source/debug parity.",
    },
    ModuleOwnership {
        path: "talos/arduino.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::TargetHost,
        hot_path: true,
        reason: "Arduino discovery, workspace mapping, profile, verify, and file coordination must move into adapter/core boundaries.",
    },
    ModuleOwnership {
        path: "talos/arduino_adapter.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::TargetHost,
        hot_path: true,
        reason: "Reference adapter shim until the target host contract is implemented outside Python.",
    },
    ModuleOwnership {
        path: "talos/arduino_events.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::NativeHelper,
        hot_path: true,
        reason: "Process/window refresh and file-change watching are OS-heavy native/helper candidates.",
    },
    ModuleOwnership {
        path: "talos/cache_keys.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::Core,
        hot_path: false,
        reason: "Rust talos_core owns cache identity and source hashing primitives; Python keeps compatibility fallback only.",
    },
    ModuleOwnership {
        path: "talos/checkpoints.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Storage,
        hot_path: false,
        reason: "Checkpoint lifecycle belongs to storage/core services.",
    },
    ModuleOwnership {
        path: "talos/codex_bridge.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::RuntimeHost,
        hot_path: true,
        reason: "Runtime process, message, and patch orchestration must become provider-owned.",
    },
    ModuleOwnership {
        path: "talos/codex_runtime.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::RuntimeHost,
        hot_path: true,
        reason: "Runtime discovery and metadata should be provider-owned and replaceable.",
    },
    ModuleOwnership {
        path: "talos/runtime_core.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Task/runtime orchestration is core behavior, not bridge behavior.",
    },
    ModuleOwnership {
        path: "talos/runtime_discovery.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::RuntimeHost,
        hot_path: true,
        reason: "Runtime discovery belongs to the runtime provider boundary.",
    },
    ModuleOwnership {
        path: "talos/runtime_provider.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::RuntimeHost,
        hot_path: false,
        reason: "Compatibility provider facade while runtime host is extracted.",
    },
    ModuleOwnership {
        path: "talos/runtime_service.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::RuntimeHost,
        hot_path: false,
        reason: "Temporary runtime projection facade for the current web workbench.",
    },
    ModuleOwnership {
        path: "talos/state_service.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Workbench state projection belongs behind a typed core/API boundary.",
    },
    ModuleOwnership {
        path: "talos/task_orchestrator.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Task queue ownership belongs to the core backend.",
    },
    ModuleOwnership {
        path: "talos/workspace_scanner.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::NativeHelper,
        hot_path: true,
        reason: "Workspace scanning is a native/helper candidate for speed and predictable IO.",
    },
    ModuleOwnership {
        path: "talos/diff_hunks.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Diff/hunk parsing belongs to review/core services.",
    },
    ModuleOwnership {
        path: "talos/core.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Legacy Python core must become Rust/core-owned during 0.8.x.",
    },
    ModuleOwnership {
        path: "talos/contracts.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::ApiHost,
        hot_path: false,
        reason: "Temporary schema-like contract mirror until typed IPC schemas own payloads.",
    },
    ModuleOwnership {
        path: "talos/diagnostics.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Diagnostics,
        hot_path: false,
        reason: "Diagnostics export should become a structured service, not route-local logic.",
    },
    ModuleOwnership {
        path: "talos/event_bus.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Core,
        hot_path: true,
        reason: "Event stream ownership belongs to core services.",
    },
    ModuleOwnership {
        path: "talos/performance.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Diagnostics,
        hot_path: false,
        reason: "Performance guardrails should be emitted by core/native services.",
    },
    ModuleOwnership {
        path: "talos/run_history.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::Storage,
        hot_path: true,
        reason: "History persistence belongs to storage/core services.",
    },
    ModuleOwnership {
        path: "talos/detection.py",
        role: PythonRole::LogicOwnerToMigrate,
        target: MigrationTarget::NativeHelper,
        hot_path: true,
        reason: "Detection state should be fed by native/helper watchers.",
    },
    ModuleOwnership {
        path: "talos/native_bridge.py",
        role: PythonRole::NativeBoundary,
        target: MigrationTarget::NativeHelper,
        hot_path: true,
        reason: "FFI bridge remains only as native boundary glue.",
    },
    ModuleOwnership {
        path: "talos/native_boundary.py",
        role: PythonRole::NativeBoundary,
        target: MigrationTarget::NativeHelper,
        hot_path: true,
        reason: "Boundary report remains while native helper expands.",
    },
    ModuleOwnership {
        path: "talos/targets.py",
        role: PythonRole::TemporaryAdapterShim,
        target: MigrationTarget::TargetHost,
        hot_path: false,
        reason: "Target contract shim until target host is language-neutral.",
    },
    ModuleOwnership {
        path: "talos/arduino_smoke.py",
        role: PythonRole::TestHarness,
        target: MigrationTarget::TestHarness,
        hot_path: false,
        reason: "Regression harness is allowed during migration.",
    },
    ModuleOwnership {
        path: "talos/stage_baseline.py",
        role: PythonRole::TestHarness,
        target: MigrationTarget::TestHarness,
        hot_path: false,
        reason: "Version evidence harness is allowed during migration.",
    },
    ModuleOwnership {
        path: "talos/core_bridge.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::Core,
        hot_path: false,
        reason: "Thin Cargo/Rust bridge for native core primitives; no product logic should live here.",
    },
    ModuleOwnership {
        path: "talos/python_ownership.py",
        role: PythonRole::CompatibilityBridge,
        target: MigrationTarget::Core,
        hot_path: false,
        reason: "Legacy mirror only; Rust talos_core is the Stage 1 source of architectural gating.",
    },
];

pub fn python_ownership_manifest() -> &'static [ModuleOwnership] {
    PYTHON_MODULES
}

pub fn python_expansion_allowed(role: PythonRole) -> bool {
    matches!(
        role,
        PythonRole::DebugLauncher
            | PythonRole::CompatibilityBridge
            | PythonRole::TemporaryAdapterShim
            | PythonRole::TestHarness
            | PythonRole::NativeBoundary
    )
}

pub fn logic_owner_count() -> usize {
    PYTHON_MODULES
        .iter()
        .filter(|module| module.role == PythonRole::LogicOwnerToMigrate)
        .count()
}

pub fn hot_path_count() -> usize {
    PYTHON_MODULES
        .iter()
        .filter(|module| module.hot_path)
        .count()
}

pub fn bridge_surface_count() -> usize {
    PYTHON_MODULES
        .iter()
        .filter(|module| python_expansion_allowed(module.role))
        .count()
}

pub fn stage1_exit_ready() -> bool {
    PYTHON_MODULES.iter().all(|module| match module.role {
        PythonRole::LogicOwnerToMigrate => module.hot_path || !module.reason.is_empty(),
        _ => !module.reason.is_empty(),
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SourceFileRow {
    pub path: String,
    pub bytes: u64,
    pub lines: u64,
    pub mtime_ns: u128,
}

const SOURCE_SUFFIXES: &[&str] = &[".ino", ".h", ".hpp", ".c", ".cpp", ".s", ".S"];
const IGNORED_DIRS: &[&str] = &[
    ".git",
    ".vs",
    ".vscode",
    "__pycache__",
    ".cache",
    ".pio",
    "build",
    "dist",
    "node_modules",
];

pub fn stable_text_hash(value: &str, length: usize) -> String {
    if value.is_empty() || length == 0 {
        return String::new();
    }
    let seeds = [
        0xcbf29ce484222325_u64,
        0x100000001b3_u64,
        0x84222325cbf29ce4_u64,
        0x517cc1b727220a95_u64,
    ];
    let mut hex = String::with_capacity(64);
    for seed in seeds {
        let mut hash = seed;
        for byte in value.as_bytes() {
            hash ^= u64::from(*byte);
            hash = hash.wrapping_mul(0x100000001b3);
            hash ^= hash.rotate_left(13);
        }
        hex.push_str(&format!("{hash:016x}"));
    }
    hex.truncate(length.min(64));
    hex
}

pub fn stable_file_hash(path: &Path, length: usize) -> Option<String> {
    let bytes = fs::read(path).ok()?;
    Some(stable_text_hash(&String::from_utf8_lossy(&bytes), length))
}

pub fn workspace_identity_hash_core(path_text: &str, length: usize) -> String {
    let mut value = path_text.trim().to_string();
    if value.is_empty() {
        return String::new();
    }
    let path = PathBuf::from(&value);
    if let Ok(canonical) = path.canonicalize() {
        value = canonical.to_string_lossy().to_string();
    }
    stable_text_hash(&value.replace('\\', "/").to_lowercase(), length)
}

pub fn scan_source_files(workspace: &Path) -> Vec<SourceFileRow> {
    let mut rows = Vec::new();
    if !workspace.is_dir() {
        return rows;
    }
    scan_source_dir(workspace, workspace, &mut rows);
    rows.sort_by(|a, b| a.path.to_lowercase().cmp(&b.path.to_lowercase()));
    rows
}

fn scan_source_dir(root: &Path, dir: &Path, rows: &mut Vec<SourceFileRow>) {
    let entries = match fs::read_dir(dir) {
        Ok(entries) => entries,
        Err(_) => return,
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let name = entry.file_name().to_string_lossy().to_string();
        if path.is_dir() {
            if IGNORED_DIRS
                .iter()
                .any(|ignored| name.eq_ignore_ascii_case(ignored))
            {
                continue;
            }
            scan_source_dir(root, &path, rows);
            continue;
        }
        if !path.is_file() || name.starts_with(".talos_") || !is_source_file(&path) {
            continue;
        }
        let bytes = match fs::read(&path) {
            Ok(bytes) => bytes,
            Err(_) => continue,
        };
        let stat = match fs::metadata(&path) {
            Ok(stat) => stat,
            Err(_) => continue,
        };
        let relative = path
            .strip_prefix(root)
            .unwrap_or(&path)
            .to_string_lossy()
            .replace('\\', "/");
        rows.push(SourceFileRow {
            path: relative,
            bytes: stat.len(),
            lines: count_lines(&bytes),
            mtime_ns: stat
                .modified()
                .ok()
                .and_then(|time| time.duration_since(UNIX_EPOCH).ok())
                .map(|duration| duration.as_nanos())
                .unwrap_or(0),
        });
    }
}

fn is_source_file(path: &Path) -> bool {
    let path_text = path.to_string_lossy();
    SOURCE_SUFFIXES
        .iter()
        .any(|suffix| path_text.ends_with(suffix))
}

fn count_lines(bytes: &[u8]) -> u64 {
    if bytes.is_empty() {
        return 0;
    }
    bytes.iter().filter(|byte| **byte == b'\n').count() as u64 + 1
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn desktop_app_is_debug_launcher_only() {
        let desktop = PYTHON_MODULES
            .iter()
            .find(|module| module.path == "desktop_app.py")
            .expect("desktop_app.py must be classified");
        assert_eq!(desktop.role, PythonRole::DebugLauncher);
        assert_eq!(desktop.target, MigrationTarget::Shell);
        assert!(!desktop.hot_path);
    }

    #[test]
    fn python_logic_owners_are_not_expansion_safe() {
        for module in PYTHON_MODULES {
            if module.role == PythonRole::LogicOwnerToMigrate {
                assert!(!python_expansion_allowed(module.role), "{}", module.path);
            }
        }
    }

    #[test]
    fn hot_paths_have_replacement_targets() {
        for module in PYTHON_MODULES.iter().filter(|module| module.hot_path) {
            assert_ne!(
                module.target,
                MigrationTarget::TestHarness,
                "{}",
                module.path
            );
            assert!(!module.reason.is_empty(), "{}", module.path);
        }
    }

    #[test]
    fn bridge_boundary_has_real_migration_debt() {
        assert!(logic_owner_count() > 0);
        assert!(hot_path_count() > 0);
        assert!(bridge_surface_count() > 0);
        assert!(stage1_exit_ready());
    }

    #[test]
    fn stable_hashes_are_deterministic_and_sized() {
        let first = stable_text_hash("Talos", 16);
        let second = stable_text_hash("Talos", 16);
        assert_eq!(first, second);
        assert_eq!(first.len(), 16);
        assert_eq!(stable_text_hash("", 16), "");
        assert_eq!(stable_text_hash("Talos", 128).len(), 64);
    }

    #[test]
    fn workspace_hash_normalizes_slashes_and_case() {
        let left = workspace_identity_hash_core(r"C:\Users\Admin\Sketch", 16);
        let right = workspace_identity_hash_core("c:/users/admin/sketch", 16);
        assert_eq!(left, right);
    }

    #[test]
    fn source_scanner_filters_and_counts_source_files() {
        let root = env::temp_dir().join(format!(
            "talos_core_scan_{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(root.join("build")).unwrap();
        fs::write(root.join("Main.ino"), b"void setup() {}\nvoid loop() {}").unwrap();
        fs::write(root.join("Config.h"), b"#pragma once\n").unwrap();
        fs::write(root.join("notes.txt"), b"skip").unwrap();
        fs::write(root.join("build").join("Skip.cpp"), b"skip").unwrap();

        let rows = scan_source_files(&root);
        let paths: Vec<_> = rows.iter().map(|row| row.path.as_str()).collect();
        assert_eq!(paths, vec!["Config.h", "Main.ino"]);
        assert_eq!(
            rows.iter()
                .find(|row| row.path == "Main.ino")
                .unwrap()
                .lines,
            2
        );

        fs::remove_dir_all(root).unwrap();
    }
}
