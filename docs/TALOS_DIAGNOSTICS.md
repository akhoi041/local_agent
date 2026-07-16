# Talos Diagnostics And Product Feedback

Talos 0.4.0 uses local-only diagnostics for product feedback. Diagnostics are disabled by default and Talos does not upload diagnostics to a server in this version.

## Consent Model

- Diagnostics are off until the user enables them in Settings.
- Talos stores diagnostics locally under the user's Talos app-data folder.
- Remote upload is not available in 0.4.0.
- The user can preview and copy a redacted diagnostics export before sharing it.
- Disabling diagnostics stops new diagnostic events from being recorded.

## Local Storage

Diagnostics are stored as JSON:

```text
%LOCALAPPDATA%\T-Engine\Talos\diagnostics.json
```

When `TALOS_APP_DATA_DIR` is set for testing, diagnostics are stored under that isolated app-data folder instead.

## Event Taxonomy

Allowed diagnostic event names:

- `app_started`
- `arduino_detected`
- `arduino_missing`
- `workspace_selected`
- `profile_ready`
- `profile_not_ready`
- `verify_passed`
- `verify_failed`
- `verify_cancelled`
- `codex_connected`
- `codex_disconnected`
- `codex_turn_completed`
- `codex_turn_failed`
- `support_bundle_copied`
- `installed_app_smoke`
- `installer_smoke`
- `uninstall_result`
- `crash_marker`

Typical payload fields:

- app version/channel
- source vs packaged mode
- Windows/Python platform
- board/FQBN family
- profile readiness
- verify status
- verify timing
- verify cache state
- compile issue count
- hashed workspace identifier
- sketch file extension

## Data Talos Does Not Collect Silently

Talos diagnostics must not include:

- sketch source code
- Codex chat content
- user email or account identifier
- tokens, secrets, credentials, or serial numbers
- raw absolute local paths
- full compiler output unless the user chooses a separate support export

## Export Shape

The diagnostics export is a redacted JSON object:

```json
{
  "schema_version": 1,
  "generated_at": "2026-07-09 10:30:00",
  "consent": {
    "enabled": true,
    "remote_upload": false,
    "user_preview_required": true
  },
  "data_policy": {
    "contains_source_code": false,
    "contains_codex_chat": false,
    "contains_account_identifier": false,
    "contains_raw_absolute_paths": false,
    "redacted": true
  },
  "events": []
}
```

## Future Runtime And Server Steps

Server-side feedback belongs to a later version after policy and consent are complete:

- 0.4.5: policy, consent, retention, deletion, and trust gate.
- 0.5.0: Codex Runtime Manager with sign-in/runtime readiness and VS Code extension fallback treated as one provider.
- Later server phase: opt-in feedback ingestion after consent, retention, deletion, and owner data access rules are implemented.
