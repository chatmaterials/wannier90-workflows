# Wannier90 Reference

Load this file for Wannier90-specific workflow choices and file expectations.

## Minimum working set

- required input: `seedname.win`
- interface files from the parent stage: typically `seedname.amn`, `seedname.mmn`, `seedname.eig`
- runtime outputs: `seedname.wout`, optionally `seedname.chk` and `seedname_hr.dat`

## Workflow logic

### Isolated manifold

- simpler than disentanglement
- number of bands and number of Wannier functions often match the intended subspace
- projection choice still matters for localization quality

### Entangled manifold

- requires explicit window thinking
- projection choice and disentanglement windows interact strongly
- poor windows can hide a parent-band problem or create a misleading model

## Conservative defaults

- start with physically obvious projections
- keep the parent DFT, k-mesh, and band ordering story clear
- treat `spinors` as a deliberate modeling choice, not a cosmetic toggle
- do not claim `hr.dat` is trustworthy if localization never really converged
