pub const LOCAL_API_VERSION: &str = "talos.local-api.v1";
pub const LOCAL_API_COMPATIBILITY: &str = "additive-v1";
pub const SCHEMA_VERSION: u32 = 1;

#[cfg(test)]
const REQUIRED_METADATA_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
];

const STATE_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("server", FieldKind::Object),
    ContractField::required("arduino", FieldKind::Object),
    ContractField::required("codex_runtime", FieldKind::Object),
];

const TARGET_CONTEXT_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("target", FieldKind::String),
    ContractField::required("workspace", FieldKind::Object),
    ContractField::required("sources", FieldKind::Array),
    ContractField::optional("profile", FieldKind::Object),
];

const RUNTIME_STATUS_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("status", FieldKind::String),
    ContractField::optional("version", FieldKind::String),
    ContractField::optional("account", FieldKind::Object),
    ContractField::optional("health", FieldKind::Object),
];

const VERIFY_RESULT_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("status", FieldKind::String),
    ContractField::required("summary", FieldKind::Object),
    ContractField::required("timings", FieldKind::Object),
    ContractField::optional("output", FieldKind::String),
    ContractField::optional("issues", FieldKind::Array),
];

const DIAGNOSTICS_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("generated_at", FieldKind::String),
    ContractField::required("checks", FieldKind::Array),
    ContractField::optional("bundle_path", FieldKind::String),
];

const SUPPORT_BUNDLE_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("created_at", FieldKind::String),
    ContractField::required("files", FieldKind::Array),
    ContractField::required("redaction", FieldKind::Object),
];

const EVIDENCE_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("version", FieldKind::String),
    ContractField::required("stage", FieldKind::String),
    ContractField::required("result", FieldKind::String),
    ContractField::required("checks", FieldKind::Array),
];

const GENERAL_OBJECT_FIELDS: &[ContractField] = &[
    ContractField::required("contract", FieldKind::Object),
    ContractField::required("api_version", FieldKind::String),
    ContractField::required("compatibility", FieldKind::Object),
    ContractField::required("payload", FieldKind::Object),
];

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FieldKind {
    Bool,
    Number,
    String,
    Object,
    Array,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ContractField {
    pub name: &'static str,
    pub kind: FieldKind,
    pub required: bool,
}

impl ContractField {
    pub const fn required(name: &'static str, kind: FieldKind) -> Self {
        Self {
            name,
            kind,
            required: true,
        }
    }

    pub const fn optional(name: &'static str, kind: FieldKind) -> Self {
        Self {
            name,
            kind,
            required: false,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PayloadContract {
    pub name: &'static str,
    pub version: &'static str,
    pub compatibility: &'static str,
    pub fields: &'static [ContractField],
}

pub const API_CONTRACTS: &[PayloadContract] = &[
    PayloadContract::new("talos.state", STATE_FIELDS),
    PayloadContract::new("talos.targets", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.target-context", TARGET_CONTEXT_FIELDS),
    PayloadContract::new("talos.workspace-map", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.source-file", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.codex-context-package", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.verify-result", VERIFY_RESULT_FIELDS),
    PayloadContract::new("talos.runtime-status", RUNTIME_STATUS_FIELDS),
    PayloadContract::new("talos.diagnostics", DIAGNOSTICS_FIELDS),
    PayloadContract::new("talos.command-palette", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.settings", GENERAL_OBJECT_FIELDS),
    PayloadContract::new("talos.support-bundle", SUPPORT_BUNDLE_FIELDS),
    PayloadContract::new("talos.evidence", EVIDENCE_FIELDS),
];

impl PayloadContract {
    pub const fn new(name: &'static str, fields: &'static [ContractField]) -> Self {
        Self {
            name,
            version: LOCAL_API_VERSION,
            compatibility: LOCAL_API_COMPATIBILITY,
            fields,
        }
    }
}

pub fn api_contracts() -> &'static [PayloadContract] {
    API_CONTRACTS
}

pub fn api_contract_by_name(name: &str) -> Option<&'static PayloadContract> {
    api_contracts()
        .iter()
        .find(|contract| contract.name == name)
}

pub fn render_api_contract_manifest() -> String {
    let mut output = String::new();
    output.push_str(&format!("schema_version={SCHEMA_VERSION}\n"));
    output.push_str(&format!("api_version={LOCAL_API_VERSION}\n"));
    output.push_str(&format!("compatibility={LOCAL_API_COMPATIBILITY}\n"));
    for contract in api_contracts() {
        output.push_str(&format!(
            "payload={};version={};compatibility={};fields=",
            contract.name, contract.version, contract.compatibility
        ));
        for (index, field) in contract.fields.iter().enumerate() {
            if index > 0 {
                output.push(',');
            }
            output.push_str(field.name);
            output.push(':');
            output.push_str(field_kind_name(field.kind));
            if field.required {
                output.push('!');
            }
        }
        output.push('\n');
    }
    output
}

fn field_kind_name(kind: FieldKind) -> &'static str {
    match kind {
        FieldKind::Bool => "bool",
        FieldKind::Number => "number",
        FieldKind::String => "string",
        FieldKind::Object => "object",
        FieldKind::Array => "array",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const STAGE3_REQUIRED_PAYLOADS: &[&str] = &[
        "talos.state",
        "talos.target-context",
        "talos.runtime-status",
        "talos.verify-result",
        "talos.diagnostics",
        "talos.support-bundle",
        "talos.evidence",
    ];

    #[test]
    fn required_stage3_payloads_are_versioned() {
        for name in STAGE3_REQUIRED_PAYLOADS {
            let contract = api_contract_by_name(name).expect("missing required payload contract");
            assert_eq!(contract.version, LOCAL_API_VERSION);
            assert_eq!(contract.compatibility, LOCAL_API_COMPATIBILITY);
        }
    }

    #[test]
    fn all_contracts_have_metadata_fields() {
        for contract in api_contracts() {
            for metadata in REQUIRED_METADATA_FIELDS {
                assert!(
                    contract
                        .fields
                        .iter()
                        .any(|field| field.name == metadata.name && field.required),
                    "{} missing required metadata field {}",
                    contract.name,
                    metadata.name
                );
            }
        }
    }

    #[test]
    fn manifest_lists_required_payloads() {
        let manifest = render_api_contract_manifest();
        assert!(manifest.contains("schema_version=1"));
        for name in STAGE3_REQUIRED_PAYLOADS {
            assert!(manifest.contains(&format!("payload={name};")));
        }
    }
}
