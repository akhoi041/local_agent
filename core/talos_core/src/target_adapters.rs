#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TargetAdapterStep {
    Detect,
    MapWorkspace,
    DescribeActiveDocument,
    PackageContext,
    StageChanges,
    Verify,
    Simulate,
    Build,
    Rollback,
    Diagnostics,
}

impl TargetAdapterStep {
    pub const fn as_str(self) -> &'static str {
        match self {
            TargetAdapterStep::Detect => "detect",
            TargetAdapterStep::MapWorkspace => "map_workspace",
            TargetAdapterStep::DescribeActiveDocument => "describe_active_document",
            TargetAdapterStep::PackageContext => "package_context",
            TargetAdapterStep::StageChanges => "stage_changes",
            TargetAdapterStep::Verify => "verify",
            TargetAdapterStep::Simulate => "simulate",
            TargetAdapterStep::Build => "build",
            TargetAdapterStep::Rollback => "rollback",
            TargetAdapterStep::Diagnostics => "diagnostics",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TargetAdapterPermission {
    SelectedWorkspaceRead,
    SelectedWorkspaceWrite,
    DiagnosticsRead,
    VerifySandbox,
    RuntimeContextPackage,
    RollbackCheckpoint,
    NoGlobalFilesystemAccess,
}

impl TargetAdapterPermission {
    pub const fn as_str(self) -> &'static str {
        match self {
            TargetAdapterPermission::SelectedWorkspaceRead => "selected_workspace_read",
            TargetAdapterPermission::SelectedWorkspaceWrite => "selected_workspace_write",
            TargetAdapterPermission::DiagnosticsRead => "diagnostics_read",
            TargetAdapterPermission::VerifySandbox => "verify_sandbox",
            TargetAdapterPermission::RuntimeContextPackage => "runtime_context_package",
            TargetAdapterPermission::RollbackCheckpoint => "rollback_checkpoint",
            TargetAdapterPermission::NoGlobalFilesystemAccess => "no_global_filesystem_access",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TargetAdapterHostContract {
    pub adapter: &'static str,
    pub owner: &'static str,
    pub reference: bool,
    pub python_role: &'static str,
    pub scope_policy: &'static str,
    pub lifecycle: &'static [TargetAdapterStep],
    pub permissions: &'static [TargetAdapterPermission],
    pub normal_path: &'static str,
    pub fallback: &'static str,
    pub template_for: &'static [&'static str],
    pub replaces: &'static [&'static str],
}

pub static ADAPTER_LIFECYCLE: &[TargetAdapterStep] = &[
    TargetAdapterStep::Detect,
    TargetAdapterStep::MapWorkspace,
    TargetAdapterStep::DescribeActiveDocument,
    TargetAdapterStep::PackageContext,
    TargetAdapterStep::StageChanges,
    TargetAdapterStep::Verify,
    TargetAdapterStep::Simulate,
    TargetAdapterStep::Build,
    TargetAdapterStep::Rollback,
    TargetAdapterStep::Diagnostics,
];

pub static ADAPTER_PERMISSIONS: &[TargetAdapterPermission] = &[
    TargetAdapterPermission::SelectedWorkspaceRead,
    TargetAdapterPermission::SelectedWorkspaceWrite,
    TargetAdapterPermission::DiagnosticsRead,
    TargetAdapterPermission::VerifySandbox,
    TargetAdapterPermission::RuntimeContextPackage,
    TargetAdapterPermission::RollbackCheckpoint,
    TargetAdapterPermission::NoGlobalFilesystemAccess,
];

pub static FUTURE_TARGETS: &[&str] = &["MATLAB", "STM32CubeIDE", "KiCad", "SolidWorks"];

pub static TARGET_ADAPTER_CONTRACTS: &[TargetAdapterHostContract] = &[
    TargetAdapterHostContract {
        adapter: "arduino",
        owner: "rust_core",
        reference: true,
        python_role: "compatibility_shim_until_stage8_parity",
        scope_policy: "selected_workspace_only",
        lifecycle: ADAPTER_LIFECYCLE,
        permissions: ADAPTER_PERMISSIONS,
        normal_path: "talos_core::target_adapters::arduino_reference",
        fallback: "existing_python_arduino_bridge",
        template_for: &[],
        replaces: &[
            "talos/arduino.py adapter utilities",
            "talos/arduino_events.py detection/event bridge",
            "talos/cache_keys.py workspace cache helper",
            "talos/checkpoints.py rollback helper",
        ],
    },
    TargetAdapterHostContract {
        adapter: "template",
        owner: "rust_core",
        reference: false,
        python_role: "none",
        scope_policy: "selected_workspace_only",
        lifecycle: ADAPTER_LIFECYCLE,
        permissions: ADAPTER_PERMISSIONS,
        normal_path: "talos_core::target_adapters::template",
        fallback: "none",
        template_for: FUTURE_TARGETS,
        replaces: &[],
    },
];

pub fn target_adapter_contracts() -> &'static [TargetAdapterHostContract] {
    TARGET_ADAPTER_CONTRACTS
}

pub fn target_adapter_count() -> usize {
    TARGET_ADAPTER_CONTRACTS.len()
}

pub fn target_adapter_lifecycle_count() -> usize {
    ADAPTER_LIFECYCLE.len()
}

pub fn target_adapter_permission_count() -> usize {
    ADAPTER_PERMISSIONS.len()
}

pub fn stage7_exit_ready() -> bool {
    let Some(reference) = TARGET_ADAPTER_CONTRACTS
        .iter()
        .find(|contract| contract.adapter == "arduino")
    else {
        return false;
    };
    let Some(template) = TARGET_ADAPTER_CONTRACTS
        .iter()
        .find(|contract| contract.adapter == "template")
    else {
        return false;
    };
    reference.owner == "rust_core"
        && reference.reference
        && reference.scope_policy == "selected_workspace_only"
        && reference_has_lifecycle(reference)
        && reference_has_permissions(reference)
        && !reference.replaces.is_empty()
        && template.owner == "rust_core"
        && template.python_role == "none"
        && FUTURE_TARGETS
            .iter()
            .all(|target| template.template_for.contains(target))
}

pub fn render_target_adapter_manifest() -> String {
    let rows: Vec<String> = TARGET_ADAPTER_CONTRACTS
        .iter()
        .map(render_adapter_contract)
        .collect();
    if rows.is_empty() {
        String::new()
    } else {
        format!("{}\n", rows.join("\n"))
    }
}

fn reference_has_lifecycle(contract: &TargetAdapterHostContract) -> bool {
    ADAPTER_LIFECYCLE
        .iter()
        .all(|step| contract.lifecycle.contains(step))
}

fn reference_has_permissions(contract: &TargetAdapterHostContract) -> bool {
    ADAPTER_PERMISSIONS
        .iter()
        .all(|permission| contract.permissions.contains(permission))
}

fn render_adapter_contract(contract: &TargetAdapterHostContract) -> String {
    let lifecycle = contract
        .lifecycle
        .iter()
        .map(|step| step.as_str())
        .collect::<Vec<_>>();
    let permissions = contract
        .permissions
        .iter()
        .map(|permission| permission.as_str())
        .collect::<Vec<_>>();
    format!(
        "{{\"adapter\":\"{}\",\"owner\":\"{}\",\"reference\":{},\"python_role\":\"{}\",\"scope_policy\":\"{}\",\"lifecycle\":[{}],\"permissions\":[{}],\"normal_path\":\"{}\",\"fallback\":\"{}\",\"template_for\":[{}],\"replaces\":[{}]}}",
        json_escape(contract.adapter),
        json_escape(contract.owner),
        contract.reference,
        json_escape(contract.python_role),
        json_escape(contract.scope_policy),
        render_string_array(&lifecycle),
        render_string_array(&permissions),
        json_escape(contract.normal_path),
        json_escape(contract.fallback),
        render_string_array(contract.template_for),
        render_string_array(contract.replaces),
    )
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
    fn arduino_adapter_is_rust_owned_reference_contract() {
        let arduino = TARGET_ADAPTER_CONTRACTS
            .iter()
            .find(|contract| contract.adapter == "arduino")
            .expect("arduino adapter contract");
        assert_eq!(arduino.owner, "rust_core");
        assert!(arduino.reference);
        assert_eq!(arduino.scope_policy, "selected_workspace_only");
        assert_eq!(
            arduino.python_role,
            "compatibility_shim_until_stage8_parity"
        );
        assert!(reference_has_lifecycle(arduino));
        assert!(reference_has_permissions(arduino));
        assert!(arduino
            .replaces
            .iter()
            .any(|entry| entry.contains("talos/arduino.py")));
    }

    #[test]
    fn template_adapter_covers_future_targets_without_python_logic() {
        let template = TARGET_ADAPTER_CONTRACTS
            .iter()
            .find(|contract| contract.adapter == "template")
            .expect("template adapter contract");
        assert_eq!(template.owner, "rust_core");
        assert_eq!(template.python_role, "none");
        for target in FUTURE_TARGETS {
            assert!(template.template_for.contains(target));
        }
        assert!(stage7_exit_ready());
    }

    #[test]
    fn adapter_manifest_is_line_json_for_python_bridge() {
        let manifest = render_target_adapter_manifest();
        assert!(manifest.contains("\"adapter\":\"arduino\""));
        assert!(manifest.contains("\"adapter\":\"template\""));
        assert!(manifest.contains("\"selected_workspace_only\""));
        assert!(manifest.contains("\"no_global_filesystem_access\""));
    }
}
