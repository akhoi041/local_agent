# Talos 0.6.0 Evidence

## Baseline

- Source branch: `develop/0.6.0`
- Baseline commit: `ddf0744` (`Complete Talos 0.5.5 architecture slimming`)
- Closed prior release markers:
  - `develop/0.5.5`
  - `release/0.5.5-beta`
  - `v0.5.5-beta`

## Scope

0.6.0 is the architecture foundation release. It should define and validate the long-term contracts before new target products are added.

Required evidence for completion:

- Target-adapter contract documented and covered by tests.
- Local API/IPC contract documented and covered by compatibility tests.
- Python responsibilities classified into bridge, fallback, or legacy-removal paths.
- Native-helper boundary and benchmark gates recorded.
- Desktop shell migration decision recorded with parity requirements.
- Existing Arduino workflow passes smoke/regression checks after boundary work.
