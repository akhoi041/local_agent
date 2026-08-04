use std::path::Path;

use talos_core::{
    backend_service_count, bridge_only_backend_service_count, bridge_only_native_helper_count,
    bridge_only_runtime_provider_count, bridge_surface_count, hot_path_count, logic_owner_count,
    native_helper_count, python_ownership_manifest, render_api_contract_manifest,
    render_arduino_parity_report, render_core_service_manifest, render_native_helper_manifest,
    render_release_handoff_report, render_runtime_provider_manifest,
    render_target_adapter_manifest, runtime_provider_count, runtime_provider_method_count,
    scan_source_files, stable_file_hash, stable_text_hash, stage1_exit_ready, stage4_exit_ready,
    stage5_exit_ready, stage6_exit_ready, stage7_exit_ready, stage9_exit_ready,
    target_adapter_count, target_adapter_lifecycle_count, target_adapter_permission_count,
    workspace_identity_hash_core, MigrationTarget, ModuleOwnership, PythonRole,
};

fn main() {
    let mut args = std::env::args().skip(1);
    let command = args.next().unwrap_or_else(|| String::from("summary"));
    let command_args: Vec<String> = args.collect();
    match command.as_str() {
        "summary" => print_summary(),
        "manifest" => print_manifest(),
        "manifest-json" => print_manifest_json(),
        "hash-text" => print_hash_text(&command_args),
        "hash-file" => print_hash_file(&command_args),
        "workspace-hash" => print_workspace_hash(&command_args),
        "scan-sources" => print_scan_sources(&command_args),
        "api-contracts" => print_api_contracts(),
        "backend-services" => print_backend_services(),
        "native-helpers" => print_native_helpers(),
        "runtime-providers" => print_runtime_providers(),
        "target-adapters" => print_target_adapters(),
        "arduino-parity" => print_arduino_parity(),
        "release-handoff" => print_release_handoff(),
        _ => {
            eprintln!(
                "usage: talos-core-audit [summary|manifest|manifest-json|hash-text|hash-file|workspace-hash|scan-sources|api-contracts|backend-services|native-helpers|runtime-providers|target-adapters|arduino-parity|release-handoff]"
            );
            std::process::exit(2);
        }
    }
}

fn print_arduino_parity() {
    print!("{}", render_arduino_parity_report());
}

fn print_release_handoff() {
    print!("{}", render_release_handoff_report());
}

fn print_target_adapters() {
    print!("{}", render_target_adapter_manifest());
}

fn print_runtime_providers() {
    print!("{}", render_runtime_provider_manifest());
}

fn print_native_helpers() {
    print!("{}", render_native_helper_manifest());
}

fn print_backend_services() {
    print!("{}", render_core_service_manifest());
}

fn print_api_contracts() {
    print!("{}", render_api_contract_manifest());
}

fn print_summary() {
    println!("Talos core boundary audit");
    println!("python_modules={}", python_ownership_manifest().len());
    println!("bridge_or_debug_surfaces={}", bridge_surface_count());
    println!("logic_owners_to_migrate={}", logic_owner_count());
    println!("hot_paths_to_migrate={}", hot_path_count());
    println!("stage1_exit_ready={}", stage1_exit_ready());
    println!("core_backend_services={}", backend_service_count());
    println!(
        "bridge_only_backend_services={}",
        bridge_only_backend_service_count()
    );
    println!("stage4_exit_ready={}", stage4_exit_ready());
    println!("native_helper_boundaries={}", native_helper_count());
    println!(
        "bridge_only_native_helpers={}",
        bridge_only_native_helper_count()
    );
    println!("stage5_exit_ready={}", stage5_exit_ready());
    println!("runtime_provider_boundaries={}", runtime_provider_count());
    println!(
        "runtime_provider_methods={}",
        runtime_provider_method_count()
    );
    println!(
        "bridge_only_runtime_providers={}",
        bridge_only_runtime_provider_count()
    );
    println!("stage6_exit_ready={}", stage6_exit_ready());
    println!("target_adapter_contracts={}", target_adapter_count());
    println!(
        "target_adapter_lifecycle_steps={}",
        target_adapter_lifecycle_count()
    );
    println!(
        "target_adapter_permissions={}",
        target_adapter_permission_count()
    );
    println!("stage7_exit_ready={}", stage7_exit_ready());
    println!("stage9_exit_ready={}", stage9_exit_ready());
}

fn print_manifest() {
    for module in python_ownership_manifest() {
        println!(
            "{} | {:?} | {:?} | hot_path={} | {}",
            module.path, module.role, module.target, module.hot_path, module.reason
        );
    }
}

fn print_manifest_json() {
    for module in python_ownership_manifest() {
        println!(
            "{{\"module\":\"{}\",\"path\":\"{}\",\"owner\":\"{}\",\"role\":\"{}\",\"migration_target\":\"{}\",\"hot_path\":{},\"fallback_required\":{},\"notes\":\"{}\"}}",
            json_escape(&module_name(module.path)),
            json_escape(module.path),
            module_owner(module.target),
            module_role(module.role),
            module_target(module.target),
            module.hot_path,
            module_fallback_required(module),
            json_escape(module.reason)
        );
    }
}

fn module_name(path: &str) -> String {
    let stem = path.strip_suffix(".py").unwrap_or(path);
    stem.replace('/', ".").replace('\\', ".")
}

fn module_owner(target: MigrationTarget) -> &'static str {
    match target {
        MigrationTarget::Shell => "shell",
        MigrationTarget::ApiHost => "api",
        MigrationTarget::Core => "core",
        MigrationTarget::RuntimeHost => "runtime",
        MigrationTarget::NativeHelper => "native",
        MigrationTarget::TargetHost => "targets",
        MigrationTarget::Diagnostics => "diagnostics",
        MigrationTarget::Storage => "storage",
        MigrationTarget::TestHarness => "tests",
    }
}

fn module_role(role: PythonRole) -> &'static str {
    match role {
        PythonRole::DebugLauncher => "launcher",
        PythonRole::CompatibilityBridge => "compatibility_bridge",
        PythonRole::TemporaryAdapterShim => "temporary_adapter_shim",
        PythonRole::LogicOwnerToMigrate => "migration_candidate",
        PythonRole::TestHarness => "test_harness",
        PythonRole::NativeBoundary => "native_boundary",
    }
}

fn module_target(target: MigrationTarget) -> &'static str {
    match target {
        MigrationTarget::Shell => "shell",
        MigrationTarget::ApiHost => "api_host",
        MigrationTarget::Core => "core",
        MigrationTarget::RuntimeHost => "runtime_host",
        MigrationTarget::NativeHelper => "native_helper",
        MigrationTarget::TargetHost => "target_host",
        MigrationTarget::Diagnostics => "diagnostics",
        MigrationTarget::Storage => "storage",
        MigrationTarget::TestHarness => "test_harness",
    }
}

fn module_fallback_required(module: &ModuleOwnership) -> bool {
    matches!(
        module.role,
        PythonRole::LogicOwnerToMigrate | PythonRole::NativeBoundary
    )
}

fn parse_length(args: &[String], index: usize, default_length: usize) -> usize {
    args.get(index)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(default_length)
}

fn print_hash_text(args: &[String]) {
    let value = args.first().map(String::as_str).unwrap_or("");
    let length = parse_length(args, 1, 16);
    println!("{}", stable_text_hash(value, length));
}

fn print_hash_file(args: &[String]) {
    let Some(path) = args.first() else {
        eprintln!("usage: talos-core-audit hash-file <path> [length]");
        std::process::exit(2);
    };
    let length = parse_length(args, 1, 64);
    match stable_file_hash(Path::new(path), length) {
        Some(hash) => println!("{hash}"),
        None => {
            eprintln!("unreadable file: {path}");
            std::process::exit(1);
        }
    }
}

fn print_workspace_hash(args: &[String]) {
    let Some(path) = args.first() else {
        eprintln!("usage: talos-core-audit workspace-hash <path> [length]");
        std::process::exit(2);
    };
    let length = parse_length(args, 1, 16);
    println!("{}", workspace_identity_hash_core(path, length));
}

fn print_scan_sources(args: &[String]) {
    let Some(workspace) = args.first() else {
        eprintln!("usage: talos-core-audit scan-sources <workspace>");
        std::process::exit(2);
    };
    for row in scan_source_files(Path::new(workspace)) {
        println!(
            "{{\"path\":\"{}\",\"bytes\":{},\"lines\":{},\"mtime_ns\":{}}}",
            json_escape(&row.path),
            row.bytes,
            row.lines,
            row.mtime_ns
        );
    }
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
