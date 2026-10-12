#!/usr/bin/env python3
"""Package portable skills or native import bundles using Python 3.10+."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import sys
import zipfile

import portable_skills as portable


FORMATS = ("skills", "antigravity", "workbuddy-enterprise")
MARKER = ".practical-work-packages.json"
MARKER_VERSION = 1
PackageError = portable.PortableSkillsError


def _json_file(path: Path) -> dict:
    try:
        value = json.loads(portable._read_file(path).decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError(f"Invalid UTF-8 JSON file: {path}") from exc
    if not isinstance(value, dict):
        raise PackageError(f"Expected a JSON object: {path}")
    return value


def _package_metadata(root: Path) -> dict[str, str]:
    manifest = _json_file(root / "plugin.json")
    result = {}
    for field in ("name", "version", "description"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value.strip():
            raise PackageError(f"Root plugin.json needs a non-empty {field}")
        result[field] = value
    if result["name"] != portable.PACKAGE:
        raise PackageError(f"Root package name must match the skill exporter: {portable.PACKAGE}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", result["version"]):
        raise PackageError("Package version cannot be used in an archive filename")
    return result


def _default_author(root: Path) -> str:
    path = root / ".claude-plugin" / "plugin.json"
    portable._check_path(path)
    if path.exists():
        author = _json_file(path).get("author")
        if isinstance(author, dict):
            name = author.get("name")
            if isinstance(name, str) and name.strip():
                return name
    return portable.PACKAGE


def _skill_description(data: bytes) -> str:
    text = data.decode("utf-8")
    frontmatter = text.split("---", 2)[1]
    match = re.search(r"^description:[ \t]*(.+)$", frontmatter, flags=re.MULTILINE)
    if not match:
        raise PackageError("Skill frontmatter needs a one-line description")
    value = match[1].strip()
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise PackageError("Unsupported quoted skill description") from exc
    elif value.startswith("'"):
        if not value.endswith("'"):
            raise PackageError("Unclosed quoted skill description")
        value = value[1:-1].replace("''", "'")
    elif value in ("|", ">", "|-", ">-", "|+", ">+"):
        raise PackageError("Enterprise packaging requires a one-line skill description")
    if not isinstance(value, str) or not value.strip():
        raise PackageError("Skill description must be a non-empty string")
    return value


def _yaml_strings(values: dict[str, str]) -> bytes:
    # JSON double-quoted strings are YAML-compatible and preserve punctuation,
    # newlines, and Unicode without requiring a production YAML dependency.
    return "".join(f"{key}: {json.dumps(value, ensure_ascii=False)}\n" for key, value in values.items()).encode("utf-8")


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for relative, data in sorted(files.items()):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return buffer.getvalue()


def _previous_archives(directory: Path, package_name: str, format_name: str) -> set[str]:
    marker = directory / MARKER
    portable._check_file_destination(marker)
    if not marker.exists():
        return set()
    metadata = _json_file(marker)
    if (metadata.get("package"), metadata.get("format"), metadata.get("version")) != (
        package_name, format_name, MARKER_VERSION
    ):
        raise PackageError(f"Ownership marker does not match this package format: {marker}")
    files = metadata.get("managed_files")
    if not isinstance(files, list) or any(not isinstance(name, str) for name in files):
        raise PackageError(f"Invalid managed_files in {marker}")
    if len(files) != len(set(files)):
        raise PackageError(f"Duplicate archive filename in {marker}")
    for name in files:
        if (not name.endswith(".zip") or Path(name).name != name
                or any(character in name for character in ("/", "\\", ":"))):
            raise PackageError(f"Unsafe archive filename in {marker}: {name}")
    return set(files)


def package(root: Path, output: Path, *, format_name: str, category: str | None = None,
            author: str | None = None, include_common_rule: bool = False) -> list[Path]:
    """Build archives in output/<format>, preserving unrelated destination files."""
    if format_name not in FORMATS:
        raise PackageError(f"Unknown package format: {format_name}")
    if include_common_rule and format_name != "antigravity":
        raise PackageError("--include-common-rule is only valid for antigravity")
    if format_name == "workbuddy-enterprise":
        if not isinstance(category, str) or not category.strip():
            raise PackageError("workbuddy-enterprise requires a non-empty --category")
        if author is not None and (not isinstance(author, str) or not author.strip()):
            raise PackageError("--author must be non-empty")
    elif category is not None or author is not None:
        raise PackageError("--category and --author are only valid for workbuddy-enterprise")

    root, output = portable._absolute(root), portable._absolute(output)
    portable._check_path(root)
    portable._check_path(output)
    if output.is_relative_to(root):
        raise PackageError(f"Package output must be outside the source repository: {output}")
    if output.exists() and not output.is_dir():
        raise PackageError(f"Package output is not a directory: {output}")
    directory = output / format_name
    portable._check_path(directory)
    if root.is_relative_to(directory):
        raise PackageError(f"Package directory contains the source repository: {directory}")
    if directory.exists() and not directory.is_dir():
        raise PackageError(f"Package format destination is not a directory: {directory}")

    metadata = _package_metadata(root)
    shared = portable._shared_data(root)
    skill_files = {skill: portable._skill_files(root, skill, shared) for skill in portable.SKILLS}
    archives = {}
    if format_name == "antigravity":
        native_manifest = {key: metadata[key] for key in ("name", "description")}
        files = {"plugin.json": (json.dumps(native_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}
        for skill, contents in skill_files.items():
            name = f"{metadata['name']}-{skill}"
            files.update({f"skills/{name}/{relative}": data for relative, data in contents.items()})
        if include_common_rule:
            files["rules/practical-work-common.md"] = b"---\ntrigger: always_on\n---\n\n" + shared["common.md"]
        archives[f"{metadata['name']}-{metadata['version']}.zip"] = _zip_bytes(files)
    else:
        publisher = author or _default_author(root) if format_name == "workbuddy-enterprise" else None
        for skill, contents in skill_files.items():
            name = f"{metadata['name']}-{skill}"
            files = dict(contents)
            if format_name == "workbuddy-enterprise":
                if "manifest.yaml" in files:
                    raise PackageError(f"Canonical skill has a reserved enterprise manifest: {skill}")
                files["manifest.yaml"] = _yaml_strings({
                    "name": name, "version": metadata["version"],
                    "description": _skill_description(files["SKILL.md"]),
                    "category": category, "author": publisher,
                })
                files = {f"{name}/{relative}": data for relative, data in files.items()}
            archives[f"{name}-{metadata['version']}.zip"] = _zip_bytes(files)

    owned = _previous_archives(directory, metadata["name"], format_name)
    for filename in sorted(archives):
        destination = directory / filename
        portable._check_file_destination(destination)
        if destination.exists() and filename not in owned:
            raise PackageError(f"Refusing to overwrite an unmanaged archive: {destination}")
    marker_data = (json.dumps({
        "package": metadata["name"], "format": format_name, "version": MARKER_VERSION,
        "managed_files": sorted(owned | archives.keys()),
    }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    # Build all archives and check every collision before the first filesystem write.
    for filename, data in sorted(archives.items()):
        portable._write_file(directory / filename, data)
    portable._write_file(directory / MARKER, marker_data)
    return [directory / filename for filename in sorted(archives)]


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=FORMATS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--category", help="Enterprise category configured by the administrator")
    parser.add_argument("--author", help="Enterprise publisher (defaults to the Claude manifest author)")
    parser.add_argument("--include-common-rule", action="store_true", help="Include an always_on rule in the Antigravity bundle")
    args = parser.parse_args(argv)
    root = root if root is not None else Path(__file__).resolve().parent.parent
    try:
        paths = package(root, args.output, format_name=args.format, category=args.category,
                        author=args.author, include_common_rule=args.include_common_rule)
        for path in paths:
            print(f"Packaged: {path}")
        return 0
    except (PackageError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
