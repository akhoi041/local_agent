use talos_shell::ShellLifecycle;

fn main() {
    let contract = ShellLifecycle::from_env();
    if let Err(errors) = contract.validate() {
        for error in errors {
            eprintln!("talos_shell_contract_error={error}");
        }
        std::process::exit(2);
    }

    print!("{}", contract.render_manifest());
}
