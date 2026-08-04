#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ArduinoParityFlow {
    pub flow: &'static str,
    pub user_surface: &'static str,
    pub core_boundary: &'static str,
    pub rust_or_native_owner: &'static str,
    pub python_role: &'static str,
    pub parity: &'static str,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ArduinoPythonAllowance {
    pub path: &'static str,
    pub category: &'static str,
    pub retained_for: &'static str,
}

pub fn arduino_parity_flows() -> &'static [ArduinoParityFlow] {
    &[
        ArduinoParityFlow {
            flow: "detection",
            user_surface: "open_sketches",
            core_boundary: "target_adapter.discovery",
            rust_or_native_owner: "native_helper.window_process_detection",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "workspace_mapping",
            user_surface: "sketch_folder",
            core_boundary: "target_adapter.workspace_identity",
            rust_or_native_owner: "core.workspace_hash_and_source_scan",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "source_file_list",
            user_surface: "files_panel",
            core_boundary: "target_adapter.source_inventory",
            rust_or_native_owner: "core.scan_sources",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "board_profile",
            user_surface: "board_and_profile",
            core_boundary: "target_adapter.profile",
            rust_or_native_owner: "backend.profile_state",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "verify",
            user_surface: "verify_sandbox",
            core_boundary: "target_adapter.verify_job",
            rust_or_native_owner: "backend.verify_cache_and_native_process_boundary",
            python_role: "subprocess_bridge",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "context_package",
            user_surface: "codex_context_preview",
            core_boundary: "runtime_provider.context_package",
            rust_or_native_owner: "runtime_provider.contract",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "codex_review",
            user_surface: "codex_panel",
            core_boundary: "runtime_provider.review_turn",
            rust_or_native_owner: "runtime_provider.contract",
            python_role: "http_bridge",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "save",
            user_surface: "save_file",
            core_boundary: "target_adapter.writeback",
            rust_or_native_owner: "native_helper.atomic_file_write",
            python_role: "bridge_only",
            parity: "covered",
        },
        ArduinoParityFlow {
            flow: "rollback",
            user_surface: "undo_saved_file",
            core_boundary: "target_adapter.rollback",
            rust_or_native_owner: "backend.checkpoint_state",
            python_role: "bridge_only",
            parity: "covered",
        },
    ]
}

pub fn arduino_python_allowances() -> &'static [ArduinoPythonAllowance] {
    &[
        ArduinoPythonAllowance {
            path: "talos/arduino.py",
            category: "temporary_adapter_shim",
            retained_for:
                "compatibility facade while the Rust target host replaces the HTTP bridge",
        },
        ArduinoPythonAllowance {
            path: "talos/arduino_adapter.py",
            category: "temporary_adapter_shim",
            retained_for: "legacy adapter entry point for the current desktop shell",
        },
        ArduinoPythonAllowance {
            path: "talos/arduino_events.py",
            category: "native_watcher_bridge",
            retained_for: "event delivery bridge until the native host owns watcher dispatch",
        },
        ArduinoPythonAllowance {
            path: "talos/arduino_smoke.py",
            category: "test_harness",
            retained_for: "manual and installed-app smoke checks",
        },
    ]
}

pub fn arduino_parity_exit_ready() -> bool {
    arduino_parity_flows()
        .iter()
        .all(|flow| flow.parity == "covered" && flow.python_role != "product_logic")
        && arduino_python_allowances()
            .iter()
            .all(|allowance| allowance.category != "product_logic")
}

pub fn render_arduino_parity_report() -> String {
    let flows = arduino_parity_flows()
        .iter()
        .map(render_flow)
        .collect::<Vec<_>>()
        .join(",");
    let allowances = arduino_python_allowances()
        .iter()
        .map(render_allowance)
        .collect::<Vec<_>>()
        .join(",");
    format!(
        "{{\"stage\":\"8\",\"target\":\"arduino\",\"status\":\"{}\",\"baseline\":\"0.7.5 evidence plus 0.8.0 core boundary checks\",\"flows\":[{}],\"python_allowances\":[{}],\"regressions\":[]}}",
        if arduino_parity_exit_ready() { "covered" } else { "blocked" },
        flows,
        allowances
    )
}

fn render_flow(flow: &ArduinoParityFlow) -> String {
    format!(
        "{{\"flow\":\"{}\",\"user_surface\":\"{}\",\"core_boundary\":\"{}\",\"rust_or_native_owner\":\"{}\",\"python_role\":\"{}\",\"parity\":\"{}\"}}",
        json_escape(flow.flow),
        json_escape(flow.user_surface),
        json_escape(flow.core_boundary),
        json_escape(flow.rust_or_native_owner),
        json_escape(flow.python_role),
        json_escape(flow.parity)
    )
}

fn render_allowance(allowance: &ArduinoPythonAllowance) -> String {
    format!(
        "{{\"path\":\"{}\",\"category\":\"{}\",\"retained_for\":\"{}\"}}",
        json_escape(allowance.path),
        json_escape(allowance.category),
        json_escape(allowance.retained_for)
    )
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
    fn covers_required_arduino_flows() {
        let flows = arduino_parity_flows()
            .iter()
            .map(|flow| flow.flow)
            .collect::<Vec<_>>();
        for required in [
            "detection",
            "workspace_mapping",
            "source_file_list",
            "board_profile",
            "verify",
            "context_package",
            "codex_review",
            "save",
            "rollback",
        ] {
            assert!(flows.contains(&required));
        }
    }

    #[test]
    fn python_is_not_allowed_as_product_logic() {
        assert!(arduino_parity_exit_ready());
        assert!(arduino_parity_flows()
            .iter()
            .all(|flow| flow.python_role != "product_logic"));
        assert!(arduino_python_allowances()
            .iter()
            .all(|allowance| allowance.category != "product_logic"));
    }
}
