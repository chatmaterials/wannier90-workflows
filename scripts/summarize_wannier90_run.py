#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def find_wout(path: Path) -> Path | None:
    if path.is_file():
        return path
    files = sorted(path.glob("*.wout")) + sorted(path.glob("*.werr"))
    return files[0] if files else None


def summarize(path: Path) -> dict[str, object]:
    output = find_wout(path)
    text = output.read_text(errors="ignore") if output else ""
    total_spread = None
    for pattern in (
        r"Omega Total\s*=\s*([\-0-9.Ee+]+)",
        r"Final Spread.*?([\-0-9.Ee+]+)",
        r"Sum of centres and spreads.*?([\-0-9.Ee+]+)",
    ):
        match = re.search(pattern, text, re.DOTALL)
        if match:
            total_spread = float(match.group(1))
            break
    warnings = []
    lower = text.lower()
    if "warning" in lower:
        warnings.append("The Wannier90 output contains warning lines.")
    if "error" in lower:
        warnings.append("The Wannier90 output contains error lines.")
    if "not converged" in lower:
        warnings.append("Wannier90 appears not to have converged cleanly.")
    if output is None:
        warnings.append("No .wout or .werr file was found in this path yet.")
    return {
        "path": str(path),
        "output_file": str(output) if output else None,
        "completed": "All done" in text or "Wannierisation convergence criteria satisfied" in text,
        "total_spread": total_spread,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a Wannier90 run directory or .wout file.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    record = summarize(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print(f"Path: {record['path']}")
    print(f"Output: {record['output_file']}")
    print(f"Completed: {record['completed']}")
    if record["total_spread"] is not None:
        print(f"Total spread: {record['total_spread']:.6f}")
    if record["warnings"]:
        print("Warnings: " + "; ".join(record["warnings"]))


if __name__ == "__main__":
    main()
