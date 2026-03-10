# wannier90-workflows

Standalone skill for Wannier90 input design, parent DFT handoff checks, localization review, and disentanglement guidance.

## What This Skill Covers

- `.win` template generation for isolated or disentangled manifolds, with projections, optional windows, and optional band-plot paths
- checks for missing `.amn`, `.mmn`, `.eig`, and template placeholders
- quick summaries from `.wout`
- recovery recommendations for missing interface files or non-converged localization runs

## What It Does Not Do

- it does not invent a chemically sensitive projection set without saying so
- it does not guess disentanglement windows for an unknown manifold
- it does not claim the Wannier model is trustworthy if the parent DFT handoff is incomplete

## Install

```bash
npx skills add chatmaterials/wannier90-workflows -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/make_wannier90_inputs.py /tmp/w90-test --num-wann 8 --num-bands 16 --bands-plot
python3 scripts/check_wannier90_project.py /tmp/w90-test
python3 scripts/recommend_wannier90_recovery.py fixtures/not-converged
python3 scripts/export_recovery_plan.py fixtures/not-converged
python3 scripts/export_status_report.py fixtures/not-converged
python3 scripts/export_input_suggestions.py fixtures/not-converged
python3 scripts/run_regression.py
```

## First Release Checklist

1. Initialize a fresh repository from this directory.
2. Run the local validation commands from this directory.
3. Commit the repo root as the first release candidate.
4. Tag the first release, for example `v0.1.0`.

## Suggested First Commit

```bash
git init
git add .
git commit -m "Initial release of wannier90-workflows"
git tag v0.1.0
```
