#!/usr/bin/env python3
"""Verify bundled original sources; optionally extract pinned code, without running it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile

SKILL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = SKILL_ROOT / "assets" / "sources" / "manifest.json"
MAX_FILES = 1000
MAX_UNCOMPRESSED = 32 * 1024 * 1024


def verify_sources(skill_root: Path = SKILL_ROOT) -> dict:
    manifest = json.loads((skill_root / "assets/sources/manifest.json").read_text(encoding="utf-8"))
    checked = []
    for entry in manifest["files"]:
        target = (skill_root / entry["path"]).resolve()
        if not target.is_relative_to(skill_root.resolve()):
            raise ValueError("Manifest path escapes the skill directory")
        data = target.read_bytes()
        if len(data) != entry["size_bytes"]:
            raise ValueError(f"Size mismatch: {entry['path']}")
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {entry['path']}")
        checked.append(entry["path"])
    return {"status": "source_integrity_verified", "upstream_commit": manifest["upstream_commit"],
            "paper_version": manifest["paper_version"], "checked_files": checked,
            "upstream_execution": "not_run", "scientific_results": "not_reproduced"}


def checked_members(archive: zipfile.ZipFile, commit: str) -> list[tuple[zipfile.ZipInfo, PurePosixPath]]:
    infos = archive.infolist()
    if len(infos) > MAX_FILES or sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
        raise ValueError("Archive exceeds bounded extraction limits")
    prefix = f"IdeaScientist-{commit}"
    members = []
    seen = set()
    for info in infos:
        name = info.filename
        path = PurePosixPath(name)
        if "\\" in name or ":" in name or path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe archive path: {name}")
        if not path.parts or path.parts[0] != prefix:
            raise ValueError(f"Unexpected archive root: {name}")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError(f"Archive symlink rejected: {name}")
        relative = PurePosixPath(*path.parts[1:])
        if str(relative) == ".":
            continue
        canonical = str(relative).casefold()
        if canonical in seen:
            raise ValueError(f"Duplicate archive path: {name}")
        seen.add(canonical)
        members.append((info, relative))
    return members


def extract_sources(destination: Path, skill_root: Path = SKILL_ROOT) -> Path:
    result = verify_sources(skill_root)
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise ValueError("Extraction target already exists; choose a new directory")
    source = skill_root / "assets/sources/upstream-code.zip"
    with zipfile.ZipFile(source) as archive:
        members = checked_members(archive, result["upstream_commit"])
        destination.mkdir(parents=True, exist_ok=False)
        for info, relative in members:
            target = destination.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError("Extraction target escapes destination")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-to", type=Path, help="Extract verified code into a NEW directory; no install or execution")
    args = parser.parse_args()
    try:
        result = verify_sources()
        if args.extract_to:
            result["extracted_to"] = str(extract_sources(args.extract_to))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
