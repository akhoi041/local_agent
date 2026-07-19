# Talos Documentation Index

This index keeps the documentation set navigable after separating user/release docs from developer planning notes.

- `docs/` is for packaged user, release, legal, support, and trust documentation.
- `dev_notes/` is for internal planning, version pipelines, roadmap decisions, and stage evidence.

## Active Product Docs

These are the first files a user, tester, or developer should read.

| File | Role |
| --- | --- |
| `README.md` | Project overview, setup, release notes summary, and developer entry point. |
| `TALOS_USER_GUIDE.md` | User-facing install, first-run, Arduino, Codex, verify, save, and recovery guide. |
| `TALOS_FIRST_RUN_CHECKLIST.md` | New-tester checklist for the normal Arduino/Codex path. |
| `TALOS_TROUBLESHOOTING.md` | Common failure paths and fixes. |
| `TALOS_RECOVERY_GUIDE.md` | Safe recovery path for Codex review, Arduino external edits, and rollback conflicts. |
| `TALOS_SUPPORT_DEBUG.md` | Support bundle, run-history filters, and release-evidence workflow. |

## Release, Legal, And Trust Docs

These files should stay packaged with release artifacts.

| File | Role |
| --- | --- |
| `LICENSE` | Project license. |
| `EULA.md` | Packaged-app terms. |
| `PRIVACY.md` | Local data and Codex data-flow notes. |
| `THIRD_PARTY_NOTICES.md` | Dependency and tooling notices. |
| `CODE_SIGNING.md` | Signing policy, unsigned Beta path, and verification commands. |
| `DISTRIBUTION_COPY.md` | Release copy explaining Talos as a local AI control bridge. |
| `RELEASE_NOTES.md` | Current release highlights, known limitations, and upgrade notes. |
| `TALOS_DIAGNOSTICS.md` | Local-only diagnostics, consent, redaction, and export shape. |
| `TALOS_INSTALL_LIFECYCLE.md` | Clean install, upgrade, uninstall, and app-data lifecycle validation. |

## Validation And Evidence Docs

These are user/tester-facing smoke checklists that can ship with releases.

| File | Role |
| --- | --- |
| `ARDUINO_SMOKE_TEST.md` | Manual Arduino/Codex smoke-test matrix. |
| `INSTALLED_APP_SMOKE_TEST.md` | Installed-app Arduino/Codex smoke-test checklist. |
| `TALOS_UI_UX_CHECKLIST.md` | UI/UX smoke checklist across window sizes and workflows. |

## Developer Planning Notes

These files intentionally live outside `docs/` because they are planning notes for the developer team, not packaged product documentation.

| File | Role |
| --- | --- |
| `../dev_notes/roadmap/TALOS_ROADMAP.md` | Version-level product direction across Talos releases. |
| `../dev_notes/pipelines/TALOS_PIPELINE_010.md` | Completed 0.1.0 Beta first-version pipeline. |
| `../dev_notes/pipelines/TALOS_PIPELINE_020.md` | Completed 0.2.0 Beta pipeline. |
| `../dev_notes/pipelines/TALOS_PIPELINE_030.md` | Completed 0.3.0 Beta pipeline. |
| `../dev_notes/pipelines/TALOS_PIPELINE_040.md` | Completed 0.4.0 Beta product-readiness pipeline. |
| `../dev_notes/pipelines/TALOS_PIPELINE_050.md` | Completed 0.5.0 Beta Codex Runtime Manager pipeline. |
| `../dev_notes/pipelines/TALOS_PIPELINE_055.md` | Active 0.5.5 Beta architecture-slimming pipeline. |
| `../dev_notes/evidence/TALOS_020_EVIDENCE.md` | 0.2.0 version-level evidence. |
| `../dev_notes/evidence/TALOS_030_EVIDENCE.md` | 0.3.0 version-level evidence. |
| `../dev_notes/evidence/TALOS_040_EVIDENCE.md` | 0.4.0 version-level evidence. |
| `../dev_notes/evidence/TALOS_050_EVIDENCE.md` | 0.5.0 version-level evidence. |
| `../dev_notes/evidence/TALOS_055_EVIDENCE.md` | 0.5.5 version-level evidence. |

## Cleanup Direction

The 0.5.5 Architecture Slimming release should convert this index into an enforced taxonomy:

- Keep active user/release docs at `docs/`.
- Keep version pipelines and roadmap under `dev_notes/`.
- Move old planning notes to `dev_notes/archive/` only when no runtime, release, or installer path references them.
- Move stage evidence to `dev_notes/evidence/` unless it is meant for packaged users/testers.
- Run `scripts/check_docs_links.ps1` before release so packaged, in-app, and developer-note references do not drift.
