#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_wannier90_project import inspect
from summarize_wannier90_run import summarize


def build_recommendation(path: Path, seedname: str | None = None) -> dict[str, object]:
    check = inspect(path, seedname)
    summary = summarize(path)
    warnings = list(check.get("warnings") or []) + list(summary.get("warnings") or [])
    missing_files = list(check.get("missing_files") or [])
    issues: list[str] = []
    actions: list[str] = []
    severity = "info"
    safe_restart = False
    restart_strategy = "No recovery action is needed yet."

    if missing_files:
        severity = "error"
        issues.append("The Wannier90 working directory is missing required interface files.")
        actions.append("Restore or regenerate the missing .win, .amn, .mmn, or .eig files from the parent DFT workflow before rerunning Wannier90.")
        restart_strategy = "Do not restart Wannier90 until the missing interface files are restored."

    if any("template" in warning.lower() for warning in warnings):
        severity = "error" if severity == "info" else severity
        issues.append("The active Wannier90 input is still a template.")
        actions.append("Finalize the .win file before running or rerunning Wannier90.")
        restart_strategy = "Do not restart yet; finish the input first."

    if any("projection block" in warning.lower() for warning in warnings):
        severity = "error" if severity == "info" else severity
        issues.append("The projection set has not been finalized.")
        actions.append("Replace the placeholder projection block with physically justified orbitals for the target manifold.")

    if any("k-point path" in warning.lower() for warning in warnings):
        severity = "warning" if severity == "info" else severity
        issues.append("The interpolated band path still uses a placeholder example.")
        actions.append("Replace the placeholder k-point path with a path from SeeK-path or a literature reference.")

    if any("num_bands is smaller than num_wann" in warning for warning in warnings):
        severity = "error"
        issues.append("The Wannier subspace definition is internally inconsistent.")
        actions.append("Increase num_bands or reduce num_wann before rerunning.")
        restart_strategy = "Correct the .win file and rerun from scratch."

    if summary.get("output_file") and not summary.get("completed"):
        severity = "warning" if severity == "info" else severity
        issues.append("Wannier90 ran but did not converge cleanly.")
        actions.append("Inspect the projection set and disentanglement choices before rerunning.")
        actions.append("If the projection set is physically sensible, try a more careful disentanglement strategy rather than only increasing iterations.")
        restart_strategy = "You can rerun after revising the .win choices; existing interface files can usually be reused if the parent DFT stage is unchanged."
        safe_restart = True

    if summary.get("output_file") is None and not issues:
        severity = "warning"
        issues.append("No Wannier90 output file is present yet.")
        actions.append("Run Wannier90 first or confirm whether output was written elsewhere.")
        restart_strategy = "No restart is possible yet because there is no output state to reuse."

    if not issues:
        issues.append("No critical recovery issues were detected.")
        actions.append("Proceed with downstream interpolation or post-processing.")

    return {
        "path": str(path),
        "severity": severity,
        "issues": issues,
        "recommended_actions": actions,
        "restart_strategy": restart_strategy,
        "safe_to_reuse_existing_state": safe_restart,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend Wannier90 recovery or restart actions from a working directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--seedname")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    record = build_recommendation(Path(args.path).expanduser().resolve(), args.seedname)
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print(f"[{Path(record['path']).name}] {record['severity']}")
    print("Issues: " + "; ".join(record["issues"]))
    for action in record["recommended_actions"]:
        print("- " + action)
    print("Restart strategy: " + record["restart_strategy"])


if __name__ == "__main__":
    main()
