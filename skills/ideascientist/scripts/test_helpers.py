#!/usr/bin/env python3
"""Offline regression tests. Fixtures are synthetic and are not research findings."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import init_run
import validate_run


def fixture() -> dict:
    """Synthetic structurally complete proposal, deliberately not scientific evidence."""
    base = {"schema_version": "1.0", "status": "complete", "synthetic_not_scientific_evidence": True}
    return {
        "input.json": {**base, "problem": "Synthetic fixture problem", "challenge": "Synthetic fixture challenge",
                       "mode": "adapted", "cutoff_date": "2026-10-13"},
        "evidence.json": {**base, "papers": [{
            "id": "p1", "title": "Synthetic test record", "url": "https://example.org/paper",
            "read_status": "read", "claims": [{"text": "Synthetic claim for validator testing only",
                "locator": "Synthetic section 1", "source_url": "https://example.org/paper#section1"}]}]},
        "gaps.json": {**base, "gaps": [{"id": "g1", "description": "Synthetic gap",
            "evidence_ids": ["p1"], "near_misses": [{"paper_id": "p1", "why_insufficient": "Synthetic missing property"}]}]},
        "candidates.json": {**base, "candidates": [{"id": "c1", "gap_ids": ["g1"],
            "source_mechanism": "Synthetic source mechanism", "shared_structure": "Synthetic shared structure",
            "target_adaptation": "Synthetic adaptation", "transfer_assumption": "Synthetic assumption",
            "main_risk": "Synthetic risk", "closest_work": ["p1"], "difference": "Synthetic difference",
            "evidence_ids": ["p1"]}]},
        "report.json": {**base, "selected_candidate_id": "c1", "summary": "Synthetic summary",
            "method": "Synthetic method", "evidence_ids": ["p1"], "predictions": ["Synthetic falsifiable prediction"],
            "limitations": ["This entire fixture is synthetic"], "empirical_status": "untested"},
        "experiment_plan.json": {**base, "candidate_id": "c1", "design": "Synthetic paired design",
            "variants": [{"name": name, "description": "Synthetic " + name}
                         for name in ("baseline", "direct_transfer", "adapted")],
            "metrics": [{"name": "synthetic accuracy", "definition": "Synthetic correct fraction",
                         "unit": "fraction", "direction": "maximize"}],
            "success_criteria": ["Synthetic improvement greater than 0.1"],
            "stop_rules": ["Stop after one synthetic batch"],
            "budget": {"max_cost": 0, "currency": "USD", "max_runtime_hours": 1, "compute": "local CPU"},
            "controls": ["Same synthetic data and seed"], "empirical_status": "untested"},
    }


def write_fixture(directory: Path, docs: dict) -> None:
    directory.mkdir()
    for filename, data in docs.items():
        (directory / filename).write_text(json.dumps(data), encoding="utf-8")


class HelpersTest(unittest.TestCase):
    def setUp(self):
        # The current working directory is intentionally used rather than the
        # OS temp directory, which may be outside a coding agent's write scope.
        self.temp = tempfile.TemporaryDirectory(prefix="ideascientist-test-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "run"

    def assert_invalid(self, docs: dict, error_fragment: str):
        write_fixture(self.directory, docs)
        result = validate_run.validate_run(self.directory)
        self.assertFalse(result["passed"])
        self.assertTrue(any(error_fragment in err for err in result["errors"]), result)

    def test_scaffold_is_incomplete(self):
        init_run.create_run(self.directory, "Research problem", "Current challenge")
        self.assertTrue((self.directory / "plan.md").exists())
        result = validate_run.validate_run(self.directory)
        self.assertFalse(result["passed"])
        self.assertEqual(result["empirical_status"], "untested")
        self.assertTrue(any("scaffold/pending" in err for err in result["errors"]))
        for filename in validate_run.FILES[1:]:
            data = json.loads((self.directory / filename).read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "pending")

    def test_complete_synthetic_fixture_passes_structural_only(self):
        write_fixture(self.directory, fixture())
        result = validate_run.validate_run(self.directory)
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["validation_scope"], "structural_only")
        self.assertEqual(result["empirical_status"], "untested")

    def test_unread_citation_fails(self):
        docs = fixture()
        docs["evidence.json"]["papers"][0]["read_status"] = "abstract_only"
        self.assert_invalid(docs, "must be declared read")

    def test_uncited_unread_lead_needs_no_invented_claims(self):
        docs = fixture()
        docs["evidence.json"]["papers"].append({"id": "lead", "title": "Synthetic unread lead",
            "url": "https://example.org/unread", "read_status": "unread", "claims": []})
        write_fixture(self.directory, docs)
        self.assertTrue(validate_run.validate_run(self.directory)["passed"])

    def test_unknown_citation_fails(self):
        docs = fixture()
        docs["candidates.json"]["candidates"][0]["closest_work"] = ["missing"]
        self.assert_invalid(docs, "unknown evidence ID")

    def test_unsupported_source_url_fails(self):
        docs = fixture()
        docs["evidence.json"]["papers"][0]["claims"][0]["source_url"] = "javascript:alert(1)"
        self.assert_invalid(docs, "absolute http(s)")

    def test_placeholder_fails(self):
        docs = fixture()
        docs["candidates.json"]["candidates"][0]["transfer_assumption"] = "TODO: assess"
        self.assert_invalid(docs, "must not be a placeholder")

    def test_measured_results_rejected(self):
        docs = fixture()
        docs["report.json"]["measured_results"] = {"score": 0.99}
        self.assert_invalid(docs, "cannot contain measured_results")

    def test_mismatched_selection_fails(self):
        docs = fixture()
        docs["experiment_plan.json"]["candidate_id"] = "other"
        self.assert_invalid(docs, "must match report.json")

    def test_overwrite_prevented(self):
        init_run.create_run(self.directory, "First problem", "First challenge")
        before = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        with self.assertRaises(FileExistsError):
            init_run.create_run(self.directory, "Second problem", "Second challenge")
        after = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        self.assertEqual(before, after)

    def test_existing_empty_directory_preserved(self):
        self.directory.mkdir()
        with contextlib.redirect_stderr(io.StringIO()):
            code = init_run.main(["--output", str(self.directory), "--problem", "p", "--challenge", "c"])
        self.assertEqual(code, 3)
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_invalid_json_and_duplicate_keys_fail_cleanly(self):
        write_fixture(self.directory, fixture())
        (self.directory / "report.json").write_text('{"status":"complete","status":"pending"}', encoding="utf-8")
        result = validate_run.validate_run(self.directory)
        self.assertFalse(result["passed"])
        self.assertTrue(any("duplicate JSON key" in err for err in result["errors"]))

    def test_missing_field_and_wrong_type_do_not_crash(self):
        docs = fixture()
        docs["evidence.json"]["papers"][0]["id"] = ["wrong"]
        docs["candidates.json"]["candidates"][0]["gap_ids"] = [None]
        docs["experiment_plan.json"]["budget"]["max_runtime_hours"] = True
        del docs["report.json"]["summary"]
        self.assert_invalid(docs, "must be a nonempty string")

    def test_cli_help_and_exit_codes(self):
        scripts = Path(__file__).parent
        for filename in ("init_run.py", "validate_run.py"):
            result = subprocess.run([sys.executable, str(scripts / filename), "--help"],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout)
        result = subprocess.run([sys.executable, str(scripts / "validate_run.py"), str(self.directory)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["passed"])

    def test_date_validation(self):
        self.assertEqual(init_run.iso_date("2026-10-13"), "2026-10-13")
        for value in ("2026-02-30", "20261013", "2026-1-2"):
            with self.assertRaises(argparse.ArgumentTypeError):
                init_run.iso_date(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
