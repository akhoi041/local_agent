#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CoreServiceKind {
    WorkspaceState,
    TaskQueue,
    PolicyPermissions,
    Diagnostics,
    AdapterOrchestration,
    Cancellation,
    CacheInvalidation,
    SupportEvidence,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CoreService {
    pub name: &'static str,
    pub kind: CoreServiceKind,
    pub owner: &'static str,
    pub python_role: &'static str,
    pub normal_path: &'static str,
    pub bridge_endpoint: &'static str,
    pub preserves: &'static [&'static str],
}

pub static CORE_SERVICES: &[CoreService] = &[
    CoreService {
        name: "workspace_state",
        kind: CoreServiceKind::WorkspaceState,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::workspace_state",
        bridge_endpoint: "GET /api/state",
        preserves: &["state_snapshot", "support_evidence"],
    },
    CoreService {
        name: "task_queue",
        kind: CoreServiceKind::TaskQueue,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::task_queue",
        bridge_endpoint: "GET /api/run_history",
        preserves: &["task_status", "cancellation"],
    },
    CoreService {
        name: "policy_permissions",
        kind: CoreServiceKind::PolicyPermissions,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::policy_permissions",
        bridge_endpoint: "POST /api/codex_context_package",
        preserves: &["permission_scope", "support_evidence"],
    },
    CoreService {
        name: "diagnostics",
        kind: CoreServiceKind::Diagnostics,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::diagnostics",
        bridge_endpoint: "GET /api/diagnostics_export",
        preserves: &["diagnostics", "support_evidence"],
    },
    CoreService {
        name: "adapter_orchestration",
        kind: CoreServiceKind::AdapterOrchestration,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::adapter_orchestration",
        bridge_endpoint: "GET /api/arduino_context",
        preserves: &["target_context", "cache_invalidation"],
    },
    CoreService {
        name: "cancellation",
        kind: CoreServiceKind::Cancellation,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::cancellation",
        bridge_endpoint: "POST /api/arduino_verify_cancel",
        preserves: &["cancellation", "task_status"],
    },
    CoreService {
        name: "cache_invalidation",
        kind: CoreServiceKind::CacheInvalidation,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::cache_invalidation",
        bridge_endpoint: "POST /api/arduino_verify_cache_clear",
        preserves: &["cache_invalidation", "task_status"],
    },
    CoreService {
        name: "support_evidence",
        kind: CoreServiceKind::SupportEvidence,
        owner: "rust_core",
        python_role: "bridge_only",
        normal_path: "talos_core::backend::support_evidence",
        bridge_endpoint: "POST /api/release_evidence",
        preserves: &["support_evidence", "diagnostics"],
    },
];

pub fn core_services() -> &'static [CoreService] {
    CORE_SERVICES
}

pub fn backend_service_count() -> usize {
    CORE_SERVICES.len()
}

pub fn bridge_only_backend_service_count() -> usize {
    CORE_SERVICES
        .iter()
        .filter(|service| service.python_role == "bridge_only")
        .count()
}

pub fn stage4_exit_ready() -> bool {
    let required = [
        CoreServiceKind::WorkspaceState,
        CoreServiceKind::TaskQueue,
        CoreServiceKind::PolicyPermissions,
        CoreServiceKind::Diagnostics,
        CoreServiceKind::AdapterOrchestration,
        CoreServiceKind::Cancellation,
        CoreServiceKind::CacheInvalidation,
        CoreServiceKind::SupportEvidence,
    ];
    let has_required = required.iter().all(|kind| has_service_kind(*kind));
    let bridge_only = CORE_SERVICES
        .iter()
        .all(|service| service.owner == "rust_core" && service.python_role == "bridge_only");
    let preserves_cancellation = preserves("cancellation");
    let preserves_cache = preserves("cache_invalidation");
    let preserves_evidence = preserves("support_evidence");
    has_required && bridge_only && preserves_cancellation && preserves_cache && preserves_evidence
}

pub fn render_core_service_manifest() -> String {
    let rows: Vec<String> = CORE_SERVICES
        .iter()
        .map(|service| {
            format!(
                "{{\"service\":\"{}\",\"kind\":\"{}\",\"owner\":\"{}\",\"python_role\":\"{}\",\"normal_path\":\"{}\",\"bridge_endpoint\":\"{}\",\"preserves\":[{}]}}",
                json_escape(service.name),
                kind_name(service.kind),
                json_escape(service.owner),
                json_escape(service.python_role),
                json_escape(service.normal_path),
                json_escape(service.bridge_endpoint),
                render_string_array(service.preserves)
            )
        })
        .collect();
    if rows.is_empty() {
        String::new()
    } else {
        format!("{}\n", rows.join("\n"))
    }
}

fn has_service_kind(kind: CoreServiceKind) -> bool {
    CORE_SERVICES.iter().any(|service| service.kind == kind)
}

fn preserves(name: &str) -> bool {
    CORE_SERVICES
        .iter()
        .any(|service| service.preserves.iter().any(|item| *item == name))
}

fn kind_name(kind: CoreServiceKind) -> &'static str {
    match kind {
        CoreServiceKind::WorkspaceState => "workspace_state",
        CoreServiceKind::TaskQueue => "task_queue",
        CoreServiceKind::PolicyPermissions => "policy_permissions",
        CoreServiceKind::Diagnostics => "diagnostics",
        CoreServiceKind::AdapterOrchestration => "adapter_orchestration",
        CoreServiceKind::Cancellation => "cancellation",
        CoreServiceKind::CacheInvalidation => "cache_invalidation",
        CoreServiceKind::SupportEvidence => "support_evidence",
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
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn required_backend_services_are_core_owned() {
        assert_eq!(backend_service_count(), 8);
        assert!(stage4_exit_ready());
        assert_eq!(backend_service_count(), bridge_only_backend_service_count());
    }

    #[test]
    fn backend_manifest_is_line_json_for_python_bridge() {
        let manifest = render_core_service_manifest();
        assert!(manifest.contains("\"service\":\"workspace_state\""));
        assert!(manifest.contains("\"python_role\":\"bridge_only\""));
        assert!(manifest.contains("\"preserves\":[\"cache_invalidation\""));
    }

    #[test]
    fn stage4_preserves_runtime_guards() {
        assert!(preserves("cancellation"));
        assert!(preserves("cache_invalidation"));
        assert!(preserves("support_evidence"));
    }
}
