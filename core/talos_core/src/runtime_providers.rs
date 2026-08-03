#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RuntimeProviderCapability {
    Discovery,
    Health,
    AccountMetadata,
    RuntimeVersion,
    SafeReconnect,
    ContextPackage,
    MessageSend,
    ManualFallback,
    CredentialsExternal,
    ProviderMethods,
    RetryPolicy,
}

impl RuntimeProviderCapability {
    pub fn as_str(self) -> &'static str {
        match self {
            RuntimeProviderCapability::Discovery => "discovery",
            RuntimeProviderCapability::Health => "health",
            RuntimeProviderCapability::AccountMetadata => "account_metadata",
            RuntimeProviderCapability::RuntimeVersion => "runtime_version",
            RuntimeProviderCapability::SafeReconnect => "safe_reconnect",
            RuntimeProviderCapability::ContextPackage => "context_package",
            RuntimeProviderCapability::MessageSend => "message_send",
            RuntimeProviderCapability::ManualFallback => "manual_fallback",
            RuntimeProviderCapability::CredentialsExternal => "credentials_external",
            RuntimeProviderCapability::ProviderMethods => "provider_methods",
            RuntimeProviderCapability::RetryPolicy => "retry_policy",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RuntimeProviderBoundary {
    pub provider: &'static str,
    pub owner: &'static str,
    pub python_role: &'static str,
    pub credential_policy: &'static str,
    pub normal_path: &'static str,
    pub fallback: &'static str,
    pub replaces: &'static [&'static str],
    pub capabilities: &'static [RuntimeProviderCapability],
    pub methods: &'static [&'static str],
    pub checks: &'static [&'static str],
}

const PROVIDER_METHODS: &[&str] = &[
    "discover",
    "health",
    "account_metadata",
    "runtime_version",
    "safe_reconnect",
    "context_package",
    "send_message",
    "cancel_turn",
];

const CODEX_CAPABILITIES: &[RuntimeProviderCapability] = &[
    RuntimeProviderCapability::Discovery,
    RuntimeProviderCapability::Health,
    RuntimeProviderCapability::AccountMetadata,
    RuntimeProviderCapability::RuntimeVersion,
    RuntimeProviderCapability::SafeReconnect,
    RuntimeProviderCapability::ContextPackage,
    RuntimeProviderCapability::MessageSend,
    RuntimeProviderCapability::ManualFallback,
    RuntimeProviderCapability::CredentialsExternal,
    RuntimeProviderCapability::ProviderMethods,
    RuntimeProviderCapability::RetryPolicy,
];

const FUTURE_PROVIDER_CAPABILITIES: &[RuntimeProviderCapability] = &[
    RuntimeProviderCapability::Discovery,
    RuntimeProviderCapability::Health,
    RuntimeProviderCapability::AccountMetadata,
    RuntimeProviderCapability::RuntimeVersion,
    RuntimeProviderCapability::SafeReconnect,
    RuntimeProviderCapability::ContextPackage,
    RuntimeProviderCapability::ManualFallback,
    RuntimeProviderCapability::CredentialsExternal,
    RuntimeProviderCapability::ProviderMethods,
    RuntimeProviderCapability::RetryPolicy,
];

const RUNTIME_PROVIDER_BOUNDARIES: &[RuntimeProviderBoundary] = &[
    RuntimeProviderBoundary {
        provider: "codex",
        owner: "rust_core",
        python_role: "subprocess_http_bridge_only",
        credential_policy: "external_to_talos",
        normal_path: "runtime_provider_boundary",
        fallback: "manual_context_package",
        replaces: &[
            "talos/codex_runtime.py",
            "talos/runtime_discovery.py",
            "talos/codex_bridge.py provider status branches",
        ],
        capabilities: CODEX_CAPABILITIES,
        methods: PROVIDER_METHODS,
        checks: &[
            "runtime executable can be discovered or pinned",
            "health metadata is normalized before UI display",
            "retry status is explicit and never replays a user turn automatically",
            "credentials and ChatGPT account state stay outside Talos",
        ],
    },
    RuntimeProviderBoundary {
        provider: "claude",
        owner: "rust_core",
        python_role: "contract_only_until_runtime_available",
        credential_policy: "external_to_talos",
        normal_path: "runtime_provider_boundary",
        fallback: "manual_context_package",
        replaces: &[],
        capabilities: FUTURE_PROVIDER_CAPABILITIES,
        methods: PROVIDER_METHODS,
        checks: &[
            "provider can implement the same lifecycle without changing target adapters",
            "credentials remain inside the vendor runtime",
            "manual package copy remains available when direct runtime calls fail",
        ],
    },
];

pub fn runtime_provider_boundaries() -> &'static [RuntimeProviderBoundary] {
    RUNTIME_PROVIDER_BOUNDARIES
}

pub fn runtime_provider_count() -> usize {
    RUNTIME_PROVIDER_BOUNDARIES.len()
}

pub fn runtime_provider_method_count() -> usize {
    RUNTIME_PROVIDER_BOUNDARIES
        .iter()
        .map(|provider| provider.methods.len())
        .sum()
}

pub fn bridge_only_runtime_provider_count() -> usize {
    RUNTIME_PROVIDER_BOUNDARIES
        .iter()
        .filter(|provider| {
            provider.python_role.contains("bridge") || provider.python_role.contains("contract")
        })
        .count()
}

pub fn stage6_exit_ready() -> bool {
    let codex_ready = RUNTIME_PROVIDER_BOUNDARIES.iter().any(|provider| {
        provider.provider == "codex"
            && provider.owner == "rust_core"
            && provider.credential_policy == "external_to_talos"
            && provider.fallback == "manual_context_package"
            && provider.methods == PROVIDER_METHODS
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::Discovery)
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::Health)
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::AccountMetadata)
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::RuntimeVersion)
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::SafeReconnect)
            && provider
                .capabilities
                .contains(&RuntimeProviderCapability::RetryPolicy)
    });

    codex_ready
        && RUNTIME_PROVIDER_BOUNDARIES
            .iter()
            .any(|provider| provider.provider != "codex")
        && RUNTIME_PROVIDER_BOUNDARIES.iter().all(|provider| {
            provider.owner == "rust_core"
                && provider.credential_policy == "external_to_talos"
                && provider.fallback == "manual_context_package"
                && provider
                    .capabilities
                    .contains(&RuntimeProviderCapability::ProviderMethods)
                && provider
                    .capabilities
                    .contains(&RuntimeProviderCapability::CredentialsExternal)
        })
}

pub fn render_runtime_provider_manifest() -> String {
    let mut output = String::new();
    for provider in RUNTIME_PROVIDER_BOUNDARIES {
        output.push_str(&format!(
            "{{\"provider\":\"{}\",\"owner\":\"{}\",\"python_role\":\"{}\",\"credential_policy\":\"{}\",\"normal_path\":\"{}\",\"fallback\":\"{}\",\"replaces\":{},\"capabilities\":{},\"methods\":{},\"checks\":{}}}\n",
            json_escape(provider.provider),
            json_escape(provider.owner),
            json_escape(provider.python_role),
            json_escape(provider.credential_policy),
            json_escape(provider.normal_path),
            json_escape(provider.fallback),
            render_string_array(provider.replaces),
            render_capability_array(provider.capabilities),
            render_string_array(provider.methods),
            render_string_array(provider.checks)
        ));
    }
    output
}

fn render_capability_array(values: &[RuntimeProviderCapability]) -> String {
    let parts: Vec<String> = values
        .iter()
        .map(|value| format!("\"{}\"", value.as_str()))
        .collect();
    format!("[{}]", parts.join(","))
}

fn render_string_array(values: &[&str]) -> String {
    let parts: Vec<String> = values
        .iter()
        .map(|value| format!("\"{}\"", json_escape(value)))
        .collect();
    format!("[{}]", parts.join(","))
}

fn json_escape(value: &str) -> String {
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn runtime_provider_boundaries_are_rust_owned() {
        assert!(stage6_exit_ready());
        for provider in runtime_provider_boundaries() {
            assert_eq!(provider.owner, "rust_core");
            assert_eq!(provider.credential_policy, "external_to_talos");
            assert_eq!(provider.fallback, "manual_context_package");
        }
    }

    #[test]
    fn codex_boundary_has_replaceable_runtime_contract() {
        let codex = runtime_provider_boundaries()
            .iter()
            .find(|provider| provider.provider == "codex")
            .expect("codex provider boundary");
        assert!(codex.replaces.contains(&"talos/codex_runtime.py"));
        assert!(codex
            .capabilities
            .contains(&RuntimeProviderCapability::SafeReconnect));
        assert!(codex.methods.contains(&"context_package"));
        assert!(runtime_provider_boundaries()
            .iter()
            .any(|provider| provider.provider == "claude"));
    }

    #[test]
    fn runtime_provider_manifest_is_json_lines() {
        let manifest = render_runtime_provider_manifest();
        assert!(manifest.contains("\"provider\":\"codex\""));
        assert!(manifest.contains("\"provider\":\"claude\""));
        assert!(manifest.contains("\"credential_policy\":\"external_to_talos\""));
    }
}
