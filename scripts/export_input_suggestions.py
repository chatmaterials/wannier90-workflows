#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from check_wannier90_project import inspect
from summarize_wannier90_run import summarize


def render_markdown(path: Path, seedname: str | None = None) -> str:
    check = inspect(path, seedname)
    summary = summarize(path)
    warnings = list(check.get("warnings") or []) + list(summary.get("warnings") or [])
    lines = ["# Input Suggestions", "", f"Source: `{path}`", ""]

    if any("projection block" in warning.lower() for warning in warnings):
        lines.extend(
            [
                "Conservative `.win` snippet reminder:",
                "",
                "```text",
                "begin projections",
                "# Replace with chemically sensible orbitals for the target manifold",
                "end projections",
                "```",
                "",
            ]
        )

    if any("no disentanglement window" in warning.lower() for warning in warnings):
        lines.extend(
            [
                "Conservative disentanglement window scaffold:",
                "",
                "```text",
                "dis_win_min = -8.0",
                "dis_win_max = 8.0",
                "dis_froz_min = -4.0",
                "dis_froz_max = 4.0",
                "```",
                "",
            ]
        )

    if any("k-point path" in warning.lower() for warning in warnings):
        lines.extend(
            [
                "Placeholder path reminder:",
                "",
                "```text",
                "begin kpoint_path",
                "# Replace with a path from SeeK-path or literature",
                "end kpoint_path",
                "```",
                "",
            ]
        )

    if any("converged cleanly" in warning.lower() for warning in warnings):
        lines.extend(
            [
                "No direct low-risk parameter patch is guaranteed here.",
                "",
                "```text",
                "# Revisit projections and disentanglement choices before rerunning.",
                "```",
                "",
            ]
        )

    if len(lines) == 3:
        lines.extend(["No conservative input snippet was required for this path.", ""])

    return "\n".join(lines).rstrip() + "\n"


def default_output(source: Path) -> Path:
    if source.is_file():
        return source.parent / f"{source.stem}.INPUT_SUGGESTIONS.md"
    return source / "INPUT_SUGGESTIONS.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export conservative Wannier90 input suggestion snippets.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--seedname")
    parser.add_argument("--output")
    args = parser.parse_args()

    source = Path(args.path).expanduser().resolve()
    output = Path(args.output).expanduser().resolve() if args.output else default_output(source)
    output.write_text(render_markdown(source, args.seedname))
    print(output)


if __name__ == "__main__":
    main()
