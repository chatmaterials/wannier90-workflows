#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a conservative Wannier90 input template.")
    parser.add_argument("directory", help="Output directory for the workflow.")
    parser.add_argument("--seedname", default="wannier90")
    parser.add_argument("--parent-code", choices=["vasp", "qe", "abinit", "unknown"], default="unknown")
    parser.add_argument("--mode", choices=["isolated", "disentangled"], default="isolated")
    parser.add_argument("--num-wann", type=int, required=True)
    parser.add_argument("--num-bands", type=int, required=True)
    parser.add_argument("--mp-grid", default="6 6 6")
    parser.add_argument("--projections", default="replace-with-chemically-sensible-projections")
    parser.add_argument("--disentangle", action="store_true")
    parser.add_argument("--spinors", action="store_true")
    parser.add_argument("--bands-plot", action="store_true")
    parser.add_argument("--write-unk", action="store_true")
    return parser.parse_args()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def write_workflow_plan(root: Path, seedname: str, parent_code: str, notes: list[str]) -> None:
    lines = [
        "# Workflow Plan",
        "",
        f"- Seedname: `{seedname}`",
        f"- Parent code: `{parent_code}`",
        f"- Mode: `{notes[0].split(': ', 1)[1]}`",
        "",
        "## Stages",
        "",
        "### Interface Preparation",
        "- Directory: `.`",
        "- Purpose: Prepare a finalized `.win` file and matching parent-interface files.",
        "- Depends on: Parent DFT output with matching seedname and k-mesh",
        f"- Files: `{seedname}.win.template`, `README.next-steps`",
        "",
        "## Notes",
        "",
    ]
    lines.extend(f"- {note}" for note in notes)
    write(root / "WORKFLOW_PLAN.md", "\n".join(lines))


def template(args: argparse.Namespace) -> str:
    lines = [
        f"num_wann = {args.num_wann}",
        f"num_bands = {args.num_bands}",
        f"mp_grid = {args.mp_grid}",
        "",
        f"spinors = {'true' if args.spinors else 'false'}",
        f"bands_plot = {'true' if args.bands_plot else 'false'}",
        f"write_unk = {'true' if args.write_unk else 'false'}",
        "",
        "begin projections",
        args.projections,
        "end projections",
    ]
    if args.mode == "disentangled" or args.disentangle:
        lines.extend(
            [
                "",
                "# Replace with physically justified windows for the target manifold.",
                "dis_win_min = -8.0",
                "dis_win_max = 8.0",
                "dis_froz_min = -4.0",
                "dis_froz_max = 4.0",
            ]
        )
    if args.bands_plot:
        lines.extend(
            [
                "",
                "# Replace with a real path source before running interpolation plots.",
                "begin kpoint_path",
                "G  0.0 0.0 0.0   X  0.5 0.0 0.0",
                "end kpoint_path",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    if args.num_bands < args.num_wann:
        raise SystemExit("--num-bands must be greater than or equal to --num-wann")
    root = Path(args.directory).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    win_name = f"{args.seedname}.win.template"
    write(root / win_name, template(args))
    notes = [
        f"Mode: {args.mode}",
        f"Seedname: {args.seedname}",
        f"Parent code assumption: {args.parent_code}",
        "Ensure the parent stage produces matching .amn, .mmn, and .eig files for the same seedname.",
        "Do not run the template until projections and any disentanglement windows are physically justified.",
    ]
    if args.mode == "isolated":
        notes.append("Use isolated mode only when the target manifold is genuinely isolated and does not need disentanglement windows.")
    else:
        notes.append("Disentangled mode requires physically justified frozen and outer windows before the template is run.")
    if args.parent_code != "unknown":
        notes.append(f"Confirm the {args.parent_code} interface produces files with the same seedname and k-mesh.")
    if args.bands_plot:
        notes.append("Replace the placeholder k-point path with one from SeeK-path or literature before plotting interpolated bands.")
    write(root / "README.next-steps", "\n".join(f"- {line}" for line in notes))
    write_workflow_plan(root, args.seedname, args.parent_code, notes)


if __name__ == "__main__":
    main()
