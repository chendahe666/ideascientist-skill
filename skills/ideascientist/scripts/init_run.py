#!/usr/bin/env python3
"""Create an incomplete, isolated IdeaScientist run without network access.

The generated files are planning templates, not research findings. The target
directory must not already exist; existing work is never overwritten.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sys

SCHEMA_VERSION = "1.0"


def nonempty(value: str) -> str:
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("must contain non-whitespace text")
    return value


def iso_date(value: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a date in YYYY-MM-DD format") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("must be a date in YYYY-MM-DD format")
    return value


def build_artifacts(problem: str, challenge: str, mode: str, cutoff_date: str | None) -> dict:
    """Return explicit incomplete templates; this function makes no findings."""
    pending = {"schema_version": SCHEMA_VERSION, "status": "pending"}
    return {
        "input.json": {
            "schema_version": SCHEMA_VERSION,
            "status": "complete",
            "problem": problem,
            "challenge": challenge,
            "mode": mode,
            "cutoff_date": cutoff_date,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        "evidence.json": {**pending, "papers": []},
        "gaps.json": {**pending, "gaps": []},
        "candidates.json": {**pending, "candidates": []},
        "report.json": {
            **pending,
            "selected_candidate_id": "",
            "summary": "",
            "method": "",
            "evidence_ids": [],
            "predictions": [],
            "limitations": [],
            "empirical_status": "untested",
        },
        "experiment_plan.json": {
            **pending,
            "candidate_id": "",
            "design": "",
            "variants": [
                {"name": "baseline", "description": ""},
                {"name": "direct_transfer", "description": ""},
                {"name": "adapted", "description": ""},
            ],
            "metrics": [],
            "success_criteria": [],
            "stop_rules": [],
            "budget": {
                "max_cost": None,
                "currency": "",
                "max_runtime_hours": None,
                "compute": "",
            },
            "controls": [],
            "empirical_status": "untested",
        },
    }


def create_run(output: Path, problem: str, challenge: str, mode: str = "adapted",
               cutoff_date: str | None = None) -> Path:
    """Create files exclusively. Raise FileExistsError for any existing target."""
    output = output.expanduser().absolute()
    # mkdir(..., exist_ok=False) is deliberate: even an empty existing directory
    # might belong to another run, and symlinks must not redirect these writes.
    output.mkdir(parents=True, exist_ok=False)
    for filename, data in build_artifacts(problem, challenge, mode, cutoff_date).items():
        with (output / filename).open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
    plan = """# IdeaScientist run plan

Status: incomplete; all research stages are pending.
Empirical status: untested.

The supplied problem and challenge are user input, not validated findings.
No papers have been read and no experiments have been run by this initializer.

- [ ] Freeze the problem, challenge, scope, cutoff date, and compute budget.
- [ ] Read primary sources and record locators and source URLs in evidence.json.
- [ ] Fill gaps.json with cited gaps and near misses.
- [ ] Fill candidates.json with grounded mechanism-transfer candidates.
- [ ] Review assumptions, closest work, differences, and failure risks.
- [ ] Fill report.json with a selected proposal, predictions, and limitations.
- [ ] Fill experiment_plan.json with baseline, direct transfer, adapted method,
      metrics, success criteria, stop rules, budget, and fixed controls.
- [ ] Change a JSON artifact's status to complete only after filling it.
- [ ] Run validate_run.py; success confirms structure and citation links only.

Keep empirical outputs separately. A structural pass is not a scientific
validity, novelty, reproducibility, or experimental-success certificate.
"""
    with (output / "plan.md").open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(plan)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "--run-dir", dest="output", type=Path, required=True,
                        help="new run directory (must not already exist)")
    parser.add_argument("--problem", type=nonempty, required=True,
                        help="explicit research problem")
    parser.add_argument("--challenge", type=nonempty, required=True,
                        help="specific challenge in current approaches")
    parser.add_argument("--mode", choices=("adapted", "upstream"), default="adapted",
                        help="workflow label; upstream mode does not launch upstream code")
    parser.add_argument("--cutoff-date", type=iso_date,
                        help="optional literature cutoff, YYYY-MM-DD")
    args = parser.parse_args(argv)
    try:
        output = create_run(args.output, args.problem, args.challenge,
                            args.mode, args.cutoff_date)
    except FileExistsError:
        print(f"error: target already exists; nothing was overwritten: {args.output}",
              file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"error: could not finish initialization: {exc}. "
              "Inspect any partial directory before choosing a new target.", file=sys.stderr)
        return 4
    print(json.dumps({"run_dir": str(output), "status": "incomplete",
                      "empirical_status": "untested", "mode": args.mode}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
