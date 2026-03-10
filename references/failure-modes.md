# Wannier90 Failure Modes

Load this file when localization, disentanglement, or file handoff is failing.

## Common patterns

### Missing interface files

- if `.amn`, `.mmn`, or `.eig` are missing, the issue is in the parent handoff, not spread minimization

### Poor localization or exploding spreads

- projections may be physically poor
- the target manifold may not be isolated the way the user thinks
- the parent DFT stage may not have produced the right subspace

### Disentanglement stalls or behaves erratically

- windows may be too broad or too narrow
- the projection set may not span the intended manifold
- downstream advice is not trustworthy until the low-energy model is sane
