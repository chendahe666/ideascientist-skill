#!/usr/bin/env python3
"""Validate IdeaScientist planning structure and declared citation links.

This offline checker does NOT fetch sources, determine whether they were read,
fact-check claims, assess novelty, or certify empirical results. A successful
run is structural_only and its empirical_status remains untested.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

FILES = ("input.json", "evidence.json", "gaps.json", "candidates.json",
         "report.json", "experiment_plan.json")
PLACEHOLDER = re.compile(r"^(todo|tbd|pending|placeholder|incomplete|fill in|replace me)(?:\b|:)", re.I)


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.papers: dict[str, dict] = {}

    def error(self, location: str, message: str) -> None:
        self.errors.append(f"{location}: {message}")

    def text(self, value, location: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            self.error(location, "must be a nonempty string")
            return False
        if PLACEHOLDER.match(value.strip()) or (value.strip().startswith("<") and value.strip().endswith(">")):
            self.error(location, "must not be a placeholder")
            return False
        return True

    def obj(self, value, location: str) -> bool:
        if not isinstance(value, dict):
            self.error(location, "must be an object")
            return False
        return True

    def array(self, value, location: str, minimum: int = 1) -> bool:
        if not isinstance(value, list) or len(value) < minimum:
            self.error(location, f"must be an array with at least {minimum} item(s)")
            return False
        return True

    def texts(self, value, location: str) -> None:
        if self.array(value, location):
            for index, item in enumerate(value):
                self.text(item, f"{location}[{index}]")

    def url(self, value, location: str) -> bool:
        if not self.text(value, location):
            return False
        try:
            parsed = urlsplit(value)
            valid = (parsed.scheme in ("http", "https") and bool(parsed.hostname)
                     and not parsed.username and not parsed.password and not re.search(r"\s", value))
            # Force malformed numeric-port detection, which urlsplit delays.
            _ = parsed.port
        except ValueError:
            valid = False
        if not valid:
            self.error(location, "must be an absolute http(s) source URL without credentials or whitespace")
        return valid

    def number(self, value, location: str, positive: bool = False) -> None:
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or value < 0 or (positive and value == 0)):
            self.error(location, "must be a finite positive number" if positive
                       else "must be a finite nonnegative number")

    def citations(self, value, location: str) -> None:
        if not self.array(value, location):
            return
        seen: set[str] = set()
        for index, paper_id in enumerate(value):
            loc = f"{location}[{index}]"
            if not self.text(paper_id, loc):
                continue
            if paper_id in seen:
                self.error(loc, "duplicate evidence ID")
            seen.add(paper_id)
            paper = self.papers.get(paper_id)
            if paper is None:
                self.error(loc, f"unknown evidence ID {paper_id!r}")
            elif paper.get("read_status") != "read":
                self.error(loc, f"evidence {paper_id!r} must be declared read before citation")

    def base(self, value, location: str) -> bool:
        if not self.obj(value, location):
            return False
        if value.get("schema_version") != "1.0":
            self.error(location + ".schema_version", "must equal '1.0'")
        if value.get("status") != "complete":
            self.error(location + ".status", "must equal 'complete'; scaffold/pending artifacts are incomplete")
        self.reject_results(value, location)
        return True

    def reject_results(self, value, location: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "measured_results":
                    self.error(location + "." + key,
                               "planning files cannot contain measured_results; keep actual run outputs separately")
                self.reject_results(item, location + "." + key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                self.reject_results(item, f"{location}[{index}]")


def strict_json(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"nonstandard JSON numeric constant {value!r}")

    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle, object_pairs_hook=pairs, parse_constant=constant)


def validate_run(directory: Path) -> dict:
    check = Check()
    docs = {}
    for filename in FILES:
        try:
            value = strict_json(directory / filename)
        except (OSError, ValueError, UnicodeError) as exc:
            check.error(filename, f"cannot read valid JSON: {exc}")
            continue
        if check.base(value, filename):
            docs[filename] = value

    data = docs.get("input.json")
    if data is not None:
        for field in ("problem", "challenge"):
            check.text(data.get(field), "input.json." + field)
        if data.get("mode") not in ("adapted", "upstream"):
            check.error("input.json.mode", "must be 'adapted' or 'upstream'")
        cutoff = data.get("cutoff_date")
        if cutoff is not None:
            try:
                if not isinstance(cutoff, str) or date.fromisoformat(cutoff).isoformat() != cutoff:
                    raise ValueError
            except ValueError:
                check.error("input.json.cutoff_date", "must be null or YYYY-MM-DD")

    evidence = docs.get("evidence.json", {}).get("papers")
    if check.array(evidence, "evidence.json.papers"):
        for index, paper in enumerate(evidence):
            loc = f"evidence.json.papers[{index}]"
            if not check.obj(paper, loc):
                continue
            if check.text(paper.get("id"), loc + ".id"):
                if paper["id"] in check.papers:
                    check.error(loc + ".id", "duplicate evidence ID")
                else:
                    check.papers[paper["id"]] = paper
            check.text(paper.get("title"), loc + ".title")
            check.url(paper.get("url"), loc + ".url")
            if paper.get("read_status") not in ("read", "abstract_only", "unread"):
                check.error(loc + ".read_status", "must be 'read', 'abstract_only', or 'unread'")
            claims = paper.get("claims")
            # Unread search leads may be retained without inventing claims.
            # They still cannot be cited anywhere in the completed proposal.
            if check.array(claims, loc + ".claims", minimum=1 if paper.get("read_status") == "read" else 0):
                for claim_index, claim in enumerate(claims):
                    cloc = f"{loc}.claims[{claim_index}]"
                    if not check.obj(claim, cloc):
                        continue
                    check.text(claim.get("text"), cloc + ".text")
                    check.text(claim.get("locator"), cloc + ".locator")
                    check.url(claim.get("source_url"), cloc + ".source_url")

    gap_ids: set[str] = set()
    gaps = docs.get("gaps.json", {}).get("gaps")
    if check.array(gaps, "gaps.json.gaps"):
        for index, gap in enumerate(gaps):
            loc = f"gaps.json.gaps[{index}]"
            if not check.obj(gap, loc):
                continue
            if check.text(gap.get("id"), loc + ".id"):
                if gap["id"] in gap_ids:
                    check.error(loc + ".id", "duplicate gap ID")
                gap_ids.add(gap["id"])
            check.text(gap.get("description"), loc + ".description")
            check.citations(gap.get("evidence_ids"), loc + ".evidence_ids")
            misses = gap.get("near_misses")
            if check.array(misses, loc + ".near_misses"):
                for miss_index, miss in enumerate(misses):
                    mloc = f"{loc}.near_misses[{miss_index}]"
                    if check.obj(miss, mloc):
                        check.citations([miss.get("paper_id")], mloc + ".paper_id")
                        check.text(miss.get("why_insufficient"), mloc + ".why_insufficient")

    candidate_ids: set[str] = set()
    candidates = docs.get("candidates.json", {}).get("candidates")
    if check.array(candidates, "candidates.json.candidates"):
        for index, candidate in enumerate(candidates):
            loc = f"candidates.json.candidates[{index}]"
            if not check.obj(candidate, loc):
                continue
            if check.text(candidate.get("id"), loc + ".id"):
                if candidate["id"] in candidate_ids:
                    check.error(loc + ".id", "duplicate candidate ID")
                candidate_ids.add(candidate["id"])
            for field in ("source_mechanism", "shared_structure", "target_adaptation",
                          "transfer_assumption", "main_risk", "difference"):
                check.text(candidate.get(field), loc + "." + field)
            check.citations(candidate.get("evidence_ids"), loc + ".evidence_ids")
            check.citations(candidate.get("closest_work"), loc + ".closest_work")
            linked_gaps = candidate.get("gap_ids")
            if check.array(linked_gaps, loc + ".gap_ids"):
                for gap_index, gap_id in enumerate(linked_gaps):
                    gloc = f"{loc}.gap_ids[{gap_index}]"
                    if check.text(gap_id, gloc) and gap_id not in gap_ids:
                        check.error(gloc, f"unknown gap ID {gap_id!r}")

    report = docs.get("report.json")
    if report is not None:
        for field in ("summary", "method"):
            check.text(report.get(field), "report.json." + field)
        check.citations(report.get("evidence_ids"), "report.json.evidence_ids")
        for field in ("predictions", "limitations"):
            check.texts(report.get(field), "report.json." + field)
        if report.get("empirical_status") != "untested":
            check.error("report.json.empirical_status", "must equal 'untested' in a proposal run")
        selected = report.get("selected_candidate_id")
        if check.text(selected, "report.json.selected_candidate_id") and selected not in candidate_ids:
            check.error("report.json.selected_candidate_id", f"unknown candidate ID {selected!r}")

    experiment = docs.get("experiment_plan.json")
    if experiment is not None:
        check.text(experiment.get("design"), "experiment_plan.json.design")
        selected = experiment.get("candidate_id")
        if check.text(selected, "experiment_plan.json.candidate_id") and selected not in candidate_ids:
            check.error("experiment_plan.json.candidate_id", f"unknown candidate ID {selected!r}")
        if report is not None and selected != report.get("selected_candidate_id"):
            check.error("experiment_plan.json.candidate_id", "must match report.json.selected_candidate_id")
        if experiment.get("empirical_status") != "untested":
            check.error("experiment_plan.json.empirical_status", "must equal 'untested' in a proposal run")
        variants = experiment.get("variants")
        names: set[str] = set()
        if check.array(variants, "experiment_plan.json.variants", minimum=3):
            for index, variant in enumerate(variants):
                loc = f"experiment_plan.json.variants[{index}]"
                if check.obj(variant, loc):
                    name = variant.get("name")
                    if check.text(name, loc + ".name"):
                        if name in names:
                            check.error(loc + ".name", "duplicate variant name")
                        names.add(name)
                    check.text(variant.get("description"), loc + ".description")
            for required in ("baseline", "direct_transfer", "adapted"):
                if required not in names:
                    check.error("experiment_plan.json.variants", f"missing required variant {required!r}")
        metrics = experiment.get("metrics")
        if check.array(metrics, "experiment_plan.json.metrics"):
            for index, metric in enumerate(metrics):
                loc = f"experiment_plan.json.metrics[{index}]"
                if check.obj(metric, loc):
                    for field in ("name", "definition", "unit"):
                        check.text(metric.get(field), loc + "." + field)
                    if metric.get("direction") not in ("minimize", "maximize", "target"):
                        check.error(loc + ".direction", "must be 'minimize', 'maximize', or 'target'")
        for field in ("success_criteria", "stop_rules", "controls"):
            check.texts(experiment.get(field), "experiment_plan.json." + field)
        budget = experiment.get("budget")
        if check.obj(budget, "experiment_plan.json.budget"):
            check.number(budget.get("max_cost"), "experiment_plan.json.budget.max_cost")
            check.number(budget.get("max_runtime_hours"), "experiment_plan.json.budget.max_runtime_hours", positive=True)
            for field in ("currency", "compute"):
                check.text(budget.get(field), "experiment_plan.json.budget." + field)

    return {
        "passed": not check.errors,
        "validation_scope": "structural_only",
        "empirical_status": "untested",
        "errors": check.errors,
        "limitations": [
            "Source URLs and read_status are user declarations; this checker does not verify source content or access.",
            "A pass does not establish factual correctness, novelty, scientific merit, or experimental success.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="IdeaScientist run directory to check (read-only)")
    args = parser.parse_args(argv)
    result = validate_run(args.run_dir.expanduser())
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
