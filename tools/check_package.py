#!/usr/bin/env python3
"""Offline checks of packaged links, source integrity and extraction behavior."""
from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/ideascientist"


def main() -> int:
    spec = importlib.util.spec_from_file_location("prepare_upstream", SKILL / "scripts/prepare_upstream.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    verified = module.verify_sources()
    checked_links = 0
    for path in ROOT.rglob("*.md"):
        relative_parts = path.relative_to(ROOT).parts
        if any(part in {".git", "work", "runs", "__pycache__"} for part in relative_parts):
            continue
        # Unmodified source snapshots retain links relative to their original
        # repository. Their integrity is covered by hashes, not local links.
        if "assets" in relative_parts and "sources" in relative_parts:
            continue
        for match in re.finditer(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = match.group(1).split("#", 1)[0].strip("<>")
            if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            if not (path.parent / target).exists():
                raise ValueError(f"Broken local link in {path.relative_to(ROOT)}: {target}")
            checked_links += 1
    with tempfile.TemporaryDirectory(prefix="ideascientist-package-", dir=ROOT) as temp:
        destination = Path(temp) / "upstream"
        module.extract_sources(destination)
        if not (destination / "ideascientist/harness/runner.py").is_file():
            raise ValueError("Extracted upstream runner is missing")
        try:
            module.extract_sources(destination)
        except ValueError:
            pass
        else:
            raise ValueError("Extraction unexpectedly overwrote an existing target")
        for bad_name in ("../escape.py", "/absolute.py", "C:/escape.py",
                         f"IdeaScientist-{verified['upstream_commit']}/../escape.py"):
            data = io.BytesIO()
            with zipfile.ZipFile(data, "w") as archive:
                archive.writestr(bad_name, "no execution")
            data.seek(0)
            with zipfile.ZipFile(data) as archive:
                try:
                    module.checked_members(archive, verified["upstream_commit"])
                except ValueError:
                    pass
                else:
                    raise ValueError(f"Unsafe ZIP member was accepted: {bad_name}")
    subprocess.run([sys.executable, str(SKILL / "scripts/test_helpers.py")], check=True)
    print(f"Package checks passed: {checked_links} local links, {len(verified['checked_files'])} source hashes, safe extraction, offline helper tests.")
    print("Validation scope: packaging/software behavior; upstream scientific results not reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
