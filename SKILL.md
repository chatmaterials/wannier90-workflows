---
name: "wannier90-workflows"
description: "Use when the task involves Wannier90 workflows, including .win input design for isolated or disentangled manifolds, projection choices, disentanglement windows, parent DFT handoff from VASP, QE, or ABINIT, localization review, and diagnosis of .wout, .amn, .mmn, .eig, or .chk issues."
---

# Wannier90 Workflows

This skill handles real Wannier90 workflows rather than generic tight-binding discussion. Use it when the user needs help designing a `.win` file, checking the parent DFT handoff, debugging localization or disentanglement, or reviewing `.wout` output.

## When to use

Use this skill when the request mentions or implies:

- `wannier90`, `.win`, `.wout`, `.amn`, `.mmn`, `.eig`, `.chk`, `hr.dat`
- projections, frozen or disentanglement windows, spread minimization, localization
- parent DFT interfaces from VASP, QE, or ABINIT
- interpolation-ready tight-binding output for bands, Berry properties, or downstream topological analysis

## Operating stance

Prioritize missing information in this order:

1. parent code and which interface files already exist
2. target subspace: isolated bands or entangled manifold
3. number of Wannier functions and physically sensible projections
4. whether the user wants interpolation only, localized orbitals, or downstream transport or topology

Never silently invent:

- a projection set for a chemistry-sensitive system without explaining the assumption
- disentanglement windows for an unknown entangled manifold
- whether spinors, SOC, or symmetry-reduced assumptions are appropriate
- whether the parent DFT calculation produced the right interface files

## Workflow

### 1. Classify the request

- **Setup**: draft or edit a `.win` file and parent-stage checklist.
- **Review**: inspect `.win`, `.wout`, and interface files and summarize readiness or failure.
- **Recovery**: explain why localization or disentanglement failed and what to change first.

### 2. Gather the minimum viable context

Before recommending projections or windows, establish:

- parent code and whether `.amn`, `.mmn`, `.eig`, or a compatible interface already exist
- orbital character of the target bands
- isolated vs entangled manifold
- spinless vs spinor treatment
- whether the result feeds only interpolation, or a downstream tool such as WannierTools

### 3. Use the bundled helpers

- `scripts/make_wannier90_inputs.py`
  Create a conservative `.win.template` and workflow checklist.
- `scripts/check_wannier90_project.py`
  Check a Wannier90 working directory for missing interface files and obvious template issues.
- `scripts/summarize_wannier90_run.py`
  Summarize a `.wout` file or working directory using auditable heuristics.
- `scripts/recommend_wannier90_recovery.py`
  Turn incomplete or non-converged Wannier90 runs into concrete recovery guidance.
- `scripts/export_status_report.py`
  Export a shareable markdown status report from a Wannier90 working directory.
- `scripts/export_input_suggestions.py`
  Export conservative Wannier90 input suggestion snippets based on detected recovery patterns.

### 4. Load focused references only when needed

- core Wannier90 guidance: `references/wannier90.md`
- projection and window design: `references/projection-design.md`
- failure handling: `references/failure-modes.md`

### 5. Deliver an auditable answer

Whenever you recommend a projection or window change, include:

- the parent-code assumption
- the target orbital manifold you are modeling
- unresolved choices the user still needs to confirm
- which files must exist before running the next stage

## Guardrails

- A good Wannier90 workflow starts with a good parent DFT stage; do not hide a poor handoff behind `.win` edits.
- If the user requests a disentangled manifold, explain that projection choice and window choice interact.
- If downstream topology or surface-state analysis is intended, insist on a clean, physically sensible low-energy model first.

## Quality bar

- Prefer explicit assumptions over vague advice.
- Distinguish interface-file issues from physics-model issues.
- If the current directory lacks the required parent files, say so plainly.
