#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NativeHelperKind {
    ProcessWindowDetection,
    FileWatching,
    Hashing,
    WorkspaceScanning,
    DiffHunkPreparation,
    FilesystemOperations,
    PerformanceTelemetry,
    FallbackCompatibility,
}

#[derive(Debug, Clone, Copy)]
pub struct NativeHelper {
    pub name: &'static str,
    pub kind: NativeHelperKind,
    pub owner: &'static str,
    pub python_role: &'static str,
    pub normal_path: &'static str,
    pub fallback: &'static str,
    pub replaces: &'static [&'static str],
    pub checks: &'static [&'static str],
}

const NATIVE_HELPERS: &[NativeHelper] = &[
    NativeHelper {
        name: "process_window_detection",
        kind: NativeHelperKind::ProcessWindowDetection,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "native_helper",
        fallback: "python_compatibility",
        replaces: &["talos.detection", "talos.native_bridge"],
        checks: &[
            "window_rows",
            "process_rows",
            "unsupported_windows_fallback",
        ],
    },
    NativeHelper {
        name: "file_watching",
        kind: NativeHelperKind::FileWatching,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "native_helper",
        fallback: "polling_fallback",
        replaces: &["talos.arduino_events", "talos.workspace_scanner"],
        checks: &[
            "workspace_events",
            "debounce",
            "missed_event_polling_fallback",
        ],
    },
    NativeHelper {
        name: "hashing",
        kind: NativeHelperKind::Hashing,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core",
        fallback: "python_compatibility",
        replaces: &["talos.cache_keys"],
        checks: &[
            "stable_file_hash",
            "workspace_identity_hash",
            "cache_key_hash",
        ],
    },
    NativeHelper {
        name: "workspace_scanning",
        kind: NativeHelperKind::WorkspaceScanning,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core",
        fallback: "python_compatibility",
        replaces: &["talos.workspace_scanner", "talos.arduino"],
        checks: &["scan_source_files", "source_filtering", "tab_discovery"],
    },
    NativeHelper {
        name: "diff_hunk_preparation",
        kind: NativeHelperKind::DiffHunkPreparation,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core",
        fallback: "python_compatibility",
        replaces: &["talos.diff_hunks"],
        checks: &["diff_hunk_scan", "apply_patch_preview", "review_restore"],
    },
    NativeHelper {
        name: "filesystem_operations",
        kind: NativeHelperKind::FilesystemOperations,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "native_helper",
        fallback: "python_compatibility",
        replaces: &["talos.checkpoints", "talos.arduino"],
        checks: &["atomic_write", "checkpoint_rotation", "safe_delete"],
    },
    NativeHelper {
        name: "performance_telemetry",
        kind: NativeHelperKind::PerformanceTelemetry,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core",
        fallback: "python_compatibility",
        replaces: &["talos.performance"],
        checks: &["timing_probe", "before_after_ms", "fallback_label"],
    },
    NativeHelper {
        name: "fallback_compatibility",
        kind: NativeHelperKind::FallbackCompatibility,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "policy_boundary",
        fallback: "required",
        replaces: &[],
        checks: &["unsupported_windows_fallback", "native_unavailable_message"],
    },
];

pub fn native_helpers() -> &'static [NativeHelper] {
    NATIVE_HELPERS
}

pub fn native_helper_count() -> usize {
    NATIVE_HELPERS.len()
}

pub fn bridge_only_native_helper_count() -> usize {
    NATIVE_HELPERS
        .iter()
        .filter(|helper| helper.python_role == "bridge_only")
        .count()
}

pub fn stage5_exit_ready() -> bool {
    has_kind(NativeHelperKind::ProcessWindowDetection)
        && has_kind(NativeHelperKind::FileWatching)
        && has_kind(NativeHelperKind::Hashing)
        && has_kind(NativeHelperKind::WorkspaceScanning)
        && has_kind(NativeHelperKind::DiffHunkPreparation)
        && has_kind(NativeHelperKind::FilesystemOperations)
        && has_kind(NativeHelperKind::PerformanceTelemetry)
        && has_kind(NativeHelperKind::FallbackCompatibility)
        && NATIVE_HELPERS
            .iter()
            .all(|helper| helper.owner == "rust_core" && helper.python_role == "bridge_only")
}

fn has_kind(kind: NativeHelperKind) -> bool {
    NATIVE_HELPERS.iter().any(|helper| helper.kind == kind)
}

pub fn render_native_helper_manifest() -> String {
    let mut output = String::new();
    for helper in NATIVE_HELPERS {
        output.push_str(&format!(
            "{{\"helper\":\"{}\",\"kind\":\"{}\",\"owner\":\"{}\",\"python_role\":\"{}\",\"normal_path\":\"{}\",\"fallback\":\"{}\",\"replaces\":[{}],\"checks\":[{}]}}\n",
            json_escape(helper.name),
            helper_kind_name(helper.kind),
            json_escape(helper.owner),
            json_escape(helper.python_role),
            json_escape(helper.normal_path),
            json_escape(helper.fallback),
            render_string_array(helper.replaces),
            render_string_array(helper.checks)
        ));
    }
    output
}

fn helper_kind_name(kind: NativeHelperKind) -> &'static str {
    match kind {
        NativeHelperKind::ProcessWindowDetection => "process_window_detection",
        NativeHelperKind::FileWatching => "file_watching",
        NativeHelperKind::Hashing => "hashing",
        NativeHelperKind::WorkspaceScanning => "workspace_scanning",
        NativeHelperKind::DiffHunkPreparation => "diff_hunk_preparation",
        NativeHelperKind::FilesystemOperations => "filesystem_operations",
        NativeHelperKind::PerformanceTelemetry => "performance_telemetry",
        NativeHelperKind::FallbackCompatibility => "fallback_compatibility",
    }
}

fn render_string_array(values: &[&str]) -> String {
    values
        .iter()
        .map(|value| format!("\"{}\"", json_escape(value)))
        .collect::<Vec<_>>()
        .join(",")
}

fn json_escape(value: &str) -> String {
    value
        .chars()
        .flat_map(|character| match character {
            '\\' => "\\\\".chars().collect::<Vec<_>>(),
            '"' => "\\\"".chars().collect::<Vec<_>>(),
            '\n' => "\\n".chars().collect::<Vec<_>>(),
            '\r' => "\\r".chars().collect::<Vec<_>>(),
            '\t' => "\\t".chars().collect::<Vec<_>>(),
            _ => vec![character],
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn required_native_helpers_are_rust_owned() {
        assert!(stage5_exit_ready());
        assert_eq!(native_helper_count(), bridge_only_native_helper_count());
        assert!(native_helpers()
            .iter()
            .any(|helper| helper.replaces.contains(&"talos.detection")));
        assert!(native_helpers()
            .iter()
            .any(|helper| helper.replaces.contains(&"talos.diff_hunks")));
    }

    #[test]
    fn native_helper_manifest_is_line_json_for_python_bridge() {
        let manifest = render_native_helper_manifest();
        assert!(manifest.contains("\"helper\":\"process_window_detection\""));
        assert!(manifest.contains("\"python_role\":\"bridge_only\""));
        assert!(manifest.contains("\"checks\":[\"timing_probe\""));
    }

    #[test]
    fn native_helper_plan_keeps_fallbacks_explicit() {
        let fallback = native_helpers()
            .iter()
            .find(|helper| helper.name == "fallback_compatibility")
            .unwrap();
        assert!(fallback.checks.contains(&"unsupported_windows_fallback"));
        assert!(native_helpers()
            .iter()
            .any(|helper| helper.checks.contains(&"before_after_ms")));
    }
}
