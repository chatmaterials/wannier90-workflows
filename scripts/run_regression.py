#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    fixture = ROOT / "fixtures" / "completed"
    checked = run_json("scripts/check_wannier90_project.py", str(fixture), "--json")
    ensure(checked["missing_files"] == [], "fixture should not miss interface files")
    ensure(checked["warnings"] == [], "fixture should not emit warnings")

    summary = run_json("scripts/summarize_wannier90_run.py", str(fixture), "--json")
    ensure(summary["completed"] is True, "fixture should be marked completed")
    ensure(abs(summary["total_spread"] - 3.21) < 1e-6, "fixture spread should be parsed")

    failure = ROOT / "fixtures" / "not-converged"
    checked_failure = run_json("scripts/check_wannier90_project.py", str(failure), "--json")
    ensure(checked_failure["warnings"] == [], "non-converged fixture should have complete interface files and no template warnings")
    summary_failure = run_json("scripts/summarize_wannier90_run.py", str(failure), "--json")
    ensure(summary_failure["completed"] is False, "non-converged fixture should not be marked completed")
    ensure(any("converged cleanly" in warning.lower() for warning in summary_failure["warnings"]), "non-converged fixture should report failed convergence")
    recovery = run_json("scripts/recommend_wannier90_recovery.py", str(failure), "--json")
    ensure(recovery["severity"] == "warning", "non-converged Wannier90 run should be a warning-level recovery case")
    ensure(any("projection" in action.lower() or "disentanglement" in action.lower() for action in recovery["recommended_actions"]), "recovery advice should mention projection or disentanglement review")
    ensure(recovery["safe_to_reuse_existing_state"] is True, "non-converged Wannier90 run should allow interface-file reuse")

    temp_dir = Path(tempfile.mkdtemp(prefix="wannier90-regression-"))
    disentangled_dir = Path(tempfile.mkdtemp(prefix="wannier90-dis-regression-"))
    try:
        run("scripts/make_wannier90_inputs.py", str(temp_dir), "--num-wann", "8", "--num-bands", "16", "--bands-plot")
        generated = run_json("scripts/check_wannier90_project.py", str(temp_dir), "--json")
        ensure("Projection block still contains the placeholder text." in generated["warnings"], "generated template should keep projection placeholder warning")
        ensure(any("template" in warning for warning in generated["warnings"]), "generated template should be marked as template")
        ensure(any("no disentanglement window" in warning.lower() for warning in generated["warnings"]), "generated isolated template with num_bands > num_wann should warn about missing disentanglement windows")
        workflow_plan = (temp_dir / "WORKFLOW_PLAN.md").read_text()
        ensure("# Workflow Plan" in workflow_plan, "generated workflow should include WORKFLOW_PLAN.md")
        ensure("Interface Preparation" in workflow_plan, "workflow plan should describe the interface-preparation stage")
        plan_path = Path(run("scripts/export_recovery_plan.py", str(failure), "--output", str(temp_dir / "RESTART_PLAN.md")).stdout.strip())
        plan_text = plan_path.read_text()
        ensure("# Recovery Plan" in plan_text, "exported plan should have a recovery-plan heading")
        ensure("disentanglement" in plan_text.lower() or "projection" in plan_text.lower(), "exported plan should mention Wannier recovery guidance")
        status_path = Path(run("scripts/export_status_report.py", str(failure), "--output", str(temp_dir / "STATUS_REPORT.md")).stdout.strip())
        status_text = status_path.read_text()
        ensure("# Status Report" in status_text, "exported status should have a status-report heading")
        ensure("Wannier90 appears not to have converged cleanly." in status_text, "status report should include convergence warning text")
        suggest_path = Path(run("scripts/export_input_suggestions.py", str(failure), "--output", str(temp_dir / "INPUT_SUGGESTIONS.md")).stdout.strip())
        suggest_text = suggest_path.read_text()
        ensure("# Input Suggestions" in suggest_text, "exported suggestions should have an input-suggestions heading")
        ensure("dis_win_min" in suggest_text or "projection" in suggest_text.lower(), "Wannier90 suggestions should mention windows or projections")
        run("scripts/make_wannier90_inputs.py", str(disentangled_dir), "--mode", "disentangled", "--num-wann", "8", "--num-bands", "16")
        disentangled = run_json("scripts/check_wannier90_project.py", str(disentangled_dir), "--json")
        ensure(not any("no disentanglement window" in warning.lower() for warning in disentangled["warnings"]), "disentangled mode should not warn about missing windows")
    finally:
        shutil.rmtree(temp_dir)
        shutil.rmtree(disentangled_dir)

    print("wannier90-workflows regression passed")


if __name__ == "__main__":
    main()
