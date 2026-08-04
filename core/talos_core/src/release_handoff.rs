use crate::{MigrationTarget, PythonRole, PYTHON_MODULES};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PythonPurgeLedgerEntry {
    pub path: &'static str,
    pub status: &'static str,
    pub retained_reason: &'static str,
    pub replacement_owner: &'static str,
    pub target_removal_version: &'static str,
    pub normal_execution: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ReleaseHandoffGap {
    pub area: &'static str,
    pub owner: &'static str,
    pub required_before: &'static str,
}

static RELEASE_HANDOFF_GAPS: &[ReleaseHandoffGap] = &[
    ReleaseHandoffGap {
        area: "runtime_independence",
        owner: "Rust runtime provider host",
        required_before: "0.9.x runtime gate",
    },
    ReleaseHandoffGap {
        area: "consent_and_policy",
        owner: "Rust policy and permission service",
        required_before: "0.9.x trust gate",
    },
    ReleaseHandoffGap {
        area: "diagnostics",
        owner: "Rust diagnostics and local evidence",
        required_before: "0.9.x support gate",
    },
    ReleaseHandoffGap {
        area: "recovery",
        owner: "Rust checkpoint and recovery service",
        required_before: "0.9.x recovery gate",
    },
    ReleaseHandoffGap {
        area: "installer",
        owner: "Rust shell and Windows installer",
        required_before: "0.9.x release packaging gate",
    },
    ReleaseHandoffGap {
        area: "update_channel",
        owner: "Rust shell updater contract",
        required_before: "0.9.x release packaging gate",
    },
    ReleaseHandoffGap {
        area: "python_purge",
        owner: "Rust core/API/runtime/adapter owners",
        required_before: "0.9.x architecture exit",
    },
    ReleaseHandoffGap {
        area: "next_target_readiness",
        owner: "Rust target adapter host",
        required_before: "before MATLAB/STM32/KiCad/SolidWorks implementation",
    },
];

pub fn python_purge_ledger() -> Vec<PythonPurgeLedgerEntry> {
    PYTHON_MODULES
        .iter()
        .map(|module| PythonPurgeLedgerEntry {
            path: module.path,
            status: role_status(module.role),
            retained_reason: module.reason,
            replacement_owner: target_owner(module.target),
            target_removal_version: removal_target(module.role),
            normal_execution: normal_execution(module.role),
        })
        .collect()
}

pub fn release_handoff_gaps() -> &'static [ReleaseHandoffGap] {
    RELEASE_HANDOFF_GAPS
}

pub fn stage9_exit_ready() -> bool {
    !RELEASE_HANDOFF_GAPS.is_empty()
        && python_purge_ledger().iter().all(|entry| {
            !entry.retained_reason.is_empty()
                && !entry.replacement_owner.is_empty()
                && (!entry.normal_execution || !entry.target_removal_version.is_empty())
        })
}

pub fn render_release_handoff_report() -> String {
    let ledger = python_purge_ledger();
    let must_migrate = ledger
        .iter()
        .filter(|entry| entry.status == "must_migrate")
        .count();
    let temporary = ledger
        .iter()
        .filter(|entry| entry.status == "temporary_exception")
        .count();
    let normal = ledger.iter().filter(|entry| entry.normal_execution).count();

    let mut output = String::new();
    output.push_str("{\"status\":\"");
    output.push_str(if stage9_exit_ready() {
        "ready"
    } else {
        "blocked"
    });
    output.push_str("\",\"stage9_exit_ready\":");
    output.push_str(if stage9_exit_ready() { "true" } else { "false" });
    output.push_str(",\"normal_execution_python\":");
    output.push_str(&normal.to_string());
    output.push_str(",\"must_migrate\":");
    output.push_str(&must_migrate.to_string());
    output.push_str(",\"temporary_exceptions\":");
    output.push_str(&temporary.to_string());
    output.push_str(",\"python_purge_ledger\":[");
    for (index, entry) in ledger.iter().enumerate() {
        if index > 0 {
            output.push(',');
        }
        output.push('{');
        output.push_str("\"path\":");
        push_json_string(&mut output, entry.path);
        output.push_str(",\"status\":");
        push_json_string(&mut output, entry.status);
        output.push_str(",\"retained_reason\":");
        push_json_string(&mut output, entry.retained_reason);
        output.push_str(",\"replacement_owner\":");
        push_json_string(&mut output, entry.replacement_owner);
        output.push_str(",\"target_removal_version\":");
        push_json_string(&mut output, entry.target_removal_version);
        output.push_str(",\"normal_execution\":");
        output.push_str(if entry.normal_execution {
            "true"
        } else {
            "false"
        });
        output.push('}');
    }
    output.push_str("],\"handoff_gaps\":[");
    for (index, gap) in RELEASE_HANDOFF_GAPS.iter().enumerate() {
        if index > 0 {
            output.push(',');
        }
        output.push('{');
        output.push_str("\"area\":");
        push_json_string(&mut output, gap.area);
        output.push_str(",\"owner\":");
        push_json_string(&mut output, gap.owner);
        output.push_str(",\"required_before\":");
        push_json_string(&mut output, gap.required_before);
        output.push('}');
    }
    output.push_str("]}");
    output
}

fn role_status(role: PythonRole) -> &'static str {
    match role {
        PythonRole::DebugLauncher | PythonRole::CompatibilityBridge | PythonRole::TestHarness => {
            "retained"
        }
        PythonRole::TemporaryAdapterShim | PythonRole::NativeBoundary => "temporary_exception",
        PythonRole::LogicOwnerToMigrate => "must_migrate",
    }
}

fn target_owner(target: MigrationTarget) -> &'static str {
    match target {
        MigrationTarget::Shell => "Rust shell",
        MigrationTarget::ApiHost => "Rust API host",
        MigrationTarget::Core => "Rust core",
        MigrationTarget::RuntimeHost => "Rust runtime host",
        MigrationTarget::NativeHelper => "Rust/native helper",
        MigrationTarget::TargetHost => "Rust target adapter host",
        MigrationTarget::Diagnostics => "Rust diagnostics service",
        MigrationTarget::Storage => "Rust storage service",
        MigrationTarget::TestHarness => "Python test harness",
    }
}

fn removal_target(role: PythonRole) -> &'static str {
    match role {
        PythonRole::DebugLauncher => "permanent debug launcher",
        PythonRole::CompatibilityBridge => "after Rust shell/API bridge is default",
        PythonRole::TemporaryAdapterShim => "0.9.x or target owner replacement",
        PythonRole::LogicOwnerToMigrate => "0.9.x architecture exit",
        PythonRole::TestHarness => "test-only",
        PythonRole::NativeBoundary => "after native boundary is fully Rust-owned",
    }
}

fn normal_execution(role: PythonRole) -> bool {
    !matches!(role, PythonRole::DebugLauncher | PythonRole::TestHarness)
}

fn push_json_string(output: &mut String, value: &str) {
    output.push('"');
    for ch in value.chars() {
        match ch {
            '\\' => output.push_str("\\\\"),
            '"' => output.push_str("\\\""),
            '\n' => output.push_str("\\n"),
            '\r' => output.push_str("\\r"),
            '\t' => output.push_str("\\t"),
            c => output.push(c),
        }
    }
    output.push('"');
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn stage9_release_handoff_names_remaining_python_owners() {
        let ledger = python_purge_ledger();
        assert!(!ledger.is_empty());
        assert!(ledger.iter().any(|entry| entry.status == "must_migrate"));
        assert!(stage9_exit_ready());
        for entry in ledger {
            assert!(!entry.replacement_owner.is_empty());
            if entry.normal_execution {
                assert!(!entry.target_removal_version.is_empty());
            }
        }
    }

    #[test]
    fn release_handoff_report_is_json_like() {
        let report = render_release_handoff_report();
        assert!(report.contains("\"status\":\"ready\""));
        assert!(report.contains("\"python_purge_ledger\""));
        assert!(report.contains("\"handoff_gaps\""));
        assert!(report.contains("\"runtime_independence\""));
    }
}
