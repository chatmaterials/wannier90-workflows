#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def inspect(path: Path, seedname: str | None) -> dict[str, object]:
    root = path
    if path.is_file():
        root = path.parent
        if seedname is None:
            seedname = path.stem.split(".")[0]
    if seedname is None:
        for candidate in sorted(root.glob("*.win")) + sorted(root.glob("*.win.template")):
            seedname = candidate.stem.split(".")[0]
            break
    seedname = seedname or "wannier90"
    expected = [f"{seedname}.amn", f"{seedname}.mmn", f"{seedname}.eig"]
    missing = [name for name in expected if not (root / name).exists()]
    warnings = []
    template = root / f"{seedname}.win.template"
    win = root / f"{seedname}.win"
    active = win if win.exists() else template if template.exists() else None
    if active is None:
        missing.insert(0, f"{seedname}.win or {seedname}.win.template")
    else:
        text = active.read_text(errors="ignore")
        if "replace-with-chemically-sensible-projections" in text:
            warnings.append("Projection block still contains the placeholder text.")
        num_wann_match = re.search(r"num_wann\s*=\s*(\d+)", text, re.IGNORECASE)
        num_bands_match = re.search(r"num_bands\s*=\s*(\d+)", text, re.IGNORECASE)
        if num_wann_match and num_bands_match and int(num_bands_match.group(1)) < int(num_wann_match.group(1)):
            warnings.append("num_bands is smaller than num_wann, which is not a sane Wannier90 setup.")
        if "dis_win_min" in text and "dis_froz_min" not in text:
            warnings.append("A disentanglement window appears incomplete.")
        if "dis_win_min" not in text and "num_bands" in text and "num_wann" in text:
            try:
                num_wann = int(num_wann_match.group(1)) if num_wann_match else 0
                num_bands = int(num_bands_match.group(1)) if num_bands_match else 0
            except (AttributeError, ValueError):
                num_wann = 0
                num_bands = 0
            if num_bands > num_wann:
                warnings.append("num_bands exceeds num_wann but no disentanglement window is present.")
        if "begin kpoint_path" in text and "G  0.0 0.0 0.0   X  0.5 0.0 0.0" in text:
            warnings.append("The band-plot k-point path still contains the placeholder example.")
        if active.suffix == ".template":
            warnings.append("The active input is still a template, not a finalized .win file.")
    return {
        "path": str(root),
        "seedname": seedname,
        "missing_files": missing,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a Wannier90 working directory.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--seedname")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    record = inspect(Path(args.path).expanduser().resolve(), args.seedname)
    if args.json:
        print(json.dumps(record, indent=2))
        return
    print(f"Path: {record['path']}")
    print(f"Seedname: {record['seedname']}")
    if record["missing_files"]:
        print("Missing files: " + ", ".join(record["missing_files"]))
    if record["warnings"]:
        print("Warnings: " + "; ".join(record["warnings"]))


if __name__ == "__main__":
    main()
