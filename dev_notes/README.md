# Talos Developer Notes

Internal planning records for Talos. These files are not packaged user documentation and should not be linked from user-facing copy unless a release explicitly chooses to expose them.

- `roadmap/TALOS_ROADMAP.md`: source of truth for version-level product direction.
- `pipelines/`: source of truth for version-specific implementation stages and exit conditions.
- `evidence/`: one version-level evidence file per release track. Stage details stay in the matching pipeline.
- `archive/`: inactive planning notes that are no longer referenced by runtime, packaging, tests, or active pipelines.

User, release, legal, support, and trust documentation stays in `../docs`.

Use `../docs/DOCS_INDEX.md` for the packaged documentation inventory, and run `../scripts/check_docs_links.ps1` before release to catch broken docs and developer-note references.
