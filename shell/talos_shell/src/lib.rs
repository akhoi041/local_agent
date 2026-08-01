use std::env;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ShellMode {
    Prototype,
    Production,
}

impl ShellMode {
    fn as_str(self) -> &'static str {
        match self {
            Self::Prototype => "prototype",
            Self::Production => "production",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FrameMode {
    Native,
    Custom,
}

impl FrameMode {
    fn from_env_value(value: &str) -> Self {
        if value.eq_ignore_ascii_case("custom") {
            Self::Custom
        } else {
            Self::Native
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Native => "native",
            Self::Custom => "custom",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ShellLifecycle {
    pub app_name: String,
    pub local_url: String,
    pub theme: String,
    pub mode: ShellMode,
    pub frame_mode: FrameMode,
    pub owns_window: bool,
    pub owns_tray: bool,
    pub owns_app_identity: bool,
    pub owns_native_frame: bool,
    pub owns_installer_hooks: bool,
    pub owns_update_hooks: bool,
    pub owns_workbench_hosting: bool,
    pub python_debug_launcher_only: bool,
}

impl ShellLifecycle {
    pub fn production_contract() -> Self {
        Self {
            app_name: "Talos".to_string(),
            local_url: "http://127.0.0.1:8787".to_string(),
            theme: "system".to_string(),
            mode: ShellMode::Production,
            frame_mode: FrameMode::Native,
            owns_window: true,
            owns_tray: true,
            owns_app_identity: true,
            owns_native_frame: true,
            owns_installer_hooks: true,
            owns_update_hooks: true,
            owns_workbench_hosting: true,
            python_debug_launcher_only: true,
        }
    }

    pub fn from_env() -> Self {
        let mut contract = Self::production_contract();
        contract.app_name = env::var("TALOS_APP_NAME").unwrap_or(contract.app_name);
        contract.local_url = env::var("TALOS_LOCAL_URL").unwrap_or(contract.local_url);
        contract.theme = env::var("TALOS_THEME").unwrap_or(contract.theme);
        contract.frame_mode = env::var("TALOS_FRAME_MODE")
            .map(|value| FrameMode::from_env_value(&value))
            .unwrap_or(contract.frame_mode);
        contract
    }

    pub fn validate(&self) -> Result<(), Vec<&'static str>> {
        let mut errors = Vec::new();
        if self.app_name.trim().is_empty() {
            errors.push("app_name is empty");
        }
        if !self.local_url.starts_with("http://127.0.0.1:") {
            errors.push("local_url must target the local Talos API");
        }
        if !self.owns_window {
            errors.push("shell must own window lifecycle");
        }
        if !self.owns_app_identity {
            errors.push("shell must own app identity");
        }
        if !self.owns_native_frame {
            errors.push("shell must own native frame policy");
        }
        if !self.owns_workbench_hosting {
            errors.push("shell must own workbench hosting");
        }
        if !self.python_debug_launcher_only {
            errors.push("python must remain debug launcher only");
        }
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }

    pub fn render_manifest(&self) -> String {
        format!(
            concat!(
                "talos_shell_contract\n",
                "app_name={}\n",
                "local_url={}\n",
                "theme={}\n",
                "mode={}\n",
                "frame_mode={}\n",
                "window={}\n",
                "tray={}\n",
                "app_identity={}\n",
                "native_frame={}\n",
                "installer_hooks={}\n",
                "update_hooks={}\n",
                "workbench_hosting={}\n",
                "python_debug_launcher_only={}\n"
            ),
            self.app_name,
            self.local_url,
            self.theme,
            self.mode.as_str(),
            self.frame_mode.as_str(),
            self.owns_window,
            self.owns_tray,
            self.owns_app_identity,
            self.owns_native_frame,
            self.owns_installer_hooks,
            self.owns_update_hooks,
            self.owns_workbench_hosting,
            self.python_debug_launcher_only
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn production_contract_validates_without_python_shell_ownership() {
        let contract = ShellLifecycle::production_contract();

        assert_eq!(contract.validate(), Ok(()));
        assert_eq!(contract.mode, ShellMode::Production);
        assert!(contract.python_debug_launcher_only);
        assert!(contract.owns_window);
        assert!(contract.owns_native_frame);
    }

    #[test]
    fn manifest_names_all_shell_lifecycle_responsibilities() {
        let manifest = ShellLifecycle::production_contract().render_manifest();

        for expected in [
            "window=true",
            "tray=true",
            "app_identity=true",
            "native_frame=true",
            "installer_hooks=true",
            "update_hooks=true",
            "workbench_hosting=true",
            "python_debug_launcher_only=true",
        ] {
            assert!(manifest.contains(expected), "missing {expected}");
        }
    }

    #[test]
    fn validation_rejects_python_owned_product_shell() {
        let mut contract = ShellLifecycle::production_contract();
        contract.python_debug_launcher_only = false;
        contract.owns_window = false;

        let errors = contract.validate().expect_err("contract should fail");
        assert!(errors.contains(&"python must remain debug launcher only"));
        assert!(errors.contains(&"shell must own window lifecycle"));
    }
}
