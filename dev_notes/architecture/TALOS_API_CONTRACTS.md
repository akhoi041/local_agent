# Talos Local API Contract Boundary

Stage: 0.8.0 Stage 3.

## Source Of Truth

`core/talos_core/src/contracts.rs` owns the local API and IPC payload contract list. Python may serialize existing HTTP responses during migration, but Python must not introduce new payload shapes as the source of truth.

## Versioned Payloads

The Rust contract manifest covers the stable Stage 3 surfaces:

- `talos.state`
- `talos.targets`
- `talos.target-context`
- `talos.workspace-map`
- `talos.source-file`
- `talos.codex-context-package`
- `talos.verify-result`
- `talos.runtime-status`
- `talos.diagnostics`
- `talos.command-palette`
- `talos.settings`
- `talos.support-bundle`
- `talos.evidence`

Every crossing payload must include:

- `contract`
- `api_version`
- `compatibility`

## Breaking-Change Rules

- Additive fields may keep `talos.local-api.v1`.
- Removing, renaming, or changing the meaning of a field requires a new API version.
- Target adapters must emit versioned payloads before the UI consumes them.
- Python request handlers are compatibility shims until the API host moves to Rust/Cargo; they must call or mirror the Rust contract manifest rather than becoming the contract owner.
