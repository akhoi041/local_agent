"""Versioned local API/IPC contracts for Talos.

Rules for this boundary:
- Every UI-facing and runtime-facing payload carries a top-level ``contract``.
- Additive fields may keep the same ``LOCAL_API_VERSION``.
- Removing or renaming fields must introduce a new local API version.
- Internal helper dictionaries should pass through one of these serializers
  before crossing the HTTP/local IPC boundary.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LOCAL_API_VERSION = "talos.local-api.v1"

STATE_CONTRACT = "talos.state"
TARGETS_CONTRACT = "talos.targets"
TARGET_CONTEXT_CONTRACT = "talos.target-context"
CODEX_CONTEXT_CONTRACT = "talos.codex-context-package"
VERIFY_RESULT_CONTRACT = "talos.verify-result"
DIAGNOSTICS_CONTRACT = "talos.diagnostics"
EVIDENCE_CONTRACT = "talos.evidence"

def contract_metadata(name: str, version: str = LOCAL_API_VERSION) -> dict[str, str]:
    return {"name": name, "version": version}

def with_contract(payload: Mapping[str, Any], name: str, version: str = LOCAL_API_VERSION) -> dict[str, Any]:
    result = dict(payload)
    result["contract"] = contract_metadata(name, version)
    return result

def require_contract(payload: Mapping[str, Any], name: str, version: str = LOCAL_API_VERSION) -> None:
    contract = payload.get("contract")
    if not isinstance(contract, Mapping):
        raise ValueError("Missing local API contract metadata.")
    if contract.get("name") != name:
        raise ValueError(f"Expected contract {name!r}, got {contract.get('name')!r}.")
    if contract.get("version") != version:
        raise ValueError(f"Unsupported contract version {contract.get('version')!r}.")

def state_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, STATE_CONTRACT)

def targets_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, TARGETS_CONTRACT)

def target_context_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, TARGET_CONTEXT_CONTRACT)

def codex_context_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, CODEX_CONTEXT_CONTRACT)

def verify_result_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, VERIFY_RESULT_CONTRACT)

def diagnostics_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, DIAGNOSTICS_CONTRACT)

def evidence_contract(payload: Mapping[str, Any]) -> dict[str, Any]:
    return with_contract(payload, EVIDENCE_CONTRACT)
