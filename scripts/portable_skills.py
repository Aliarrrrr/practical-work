#!/usr/bin/env python3
"""Sync shared references and export self-contained Agent Skills.

Uses Python 3.10+ and the standard library. Shared references are generated
from the repository's references directory; edit those source files instead.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile


PACKAGE = "practical-work"
SKILLS = ("research", "engineering", "delivery")
SHARED_FILES = ("common.md", "applications.md")
MARKER = ".practical-work-managed.json"
MARKER_VERSION = 1  # Ownership file format, not the package release version.
TARGETS = {
    "deepseek-harness": (".dsh/skills", ".dsh/skills"),
    "antigravity": (".agents/skills", ".gemini/config/skills"),
    "antigravity-cli": (".agents/skills", ".gemini/antigravity-cli/skills"),
    "codebuddy": (".codebuddy/skills", ".codebuddy/skills"),
}


class PortableSkillsError(ValueError):
    """An input or destination cannot be used without losing unrelated files."""


def target_directory(target: str, scope: str, project: Path | None = None) -> Path:
    """Resolve a documented default; custom host configuration uses --output."""
    if target not in TARGETS or scope not in ("project", "user"):
        raise PortableSkillsError("Unknown target or scope")
    project_path, user_path = TARGETS[target]
    if scope == "user":
        if project is not None:
            raise PortableSkillsError("--project cannot be combined with --scope user")
        if target == "deepseek-harness" and os.environ.get("DSH_HOME"):
            return _absolute(Path(os.environ["DSH_HOME"])) / "skills"
        return Path.home() / user_path
    if project is None:
        raise PortableSkillsError("Project scope requires --project pointing to an existing project")
    project = _absolute(project)
    _check_path(project)
    if not project.is_dir():
        raise PortableSkillsError(f"Project is not an existing directory: {project}")
    if target == "deepseek-harness":
        # The first-party filesystem provider uses the nearest .git ancestor.
        project = next((p for p in (project, *project.parents) if (p / ".git").exists()), project)
    return project / project_path


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(path.expanduser()))


def _check_path(path: Path) -> None:
    """Reject symlinks and Windows junctions in the path and its ancestors."""
    for entry in reversed((path, *path.parents)):
        try:
            info = entry.lstat()
        except FileNotFoundError:
            continue
        tag = getattr(info, "st_reparse_tag", 0)
        link_tags = (
            getattr(stat, "IO_REPARSE_TAG_SYMLINK", 0xA000000C),
            getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003),
        )
        if stat.S_ISLNK(info.st_mode) or tag in link_tags:
            raise PortableSkillsError(f"Symbolic links and junctions are not supported: {entry}")
        if entry != path and not stat.S_ISDIR(info.st_mode):
            raise PortableSkillsError(f"A parent path is not a directory: {entry}")


def _read_file(path: Path) -> bytes:
    _check_path(path)
    if not path.is_file():
        raise PortableSkillsError(f"Expected a regular file: {path}")
    return path.read_bytes()


def _shared_data(root: Path) -> dict[str, bytes]:
    result = {}
    for filename in SHARED_FILES:
        path = root / "references" / filename
        try:
            content = _read_file(path).decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise PortableSkillsError(f"Shared reference is not UTF-8: {path}") from exc
        result[filename] = content.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return result


def _check_file_destination(path: Path) -> None:
    _check_path(path)
    if path.exists() and not path.is_file():
        raise PortableSkillsError(f"File destination is not a regular file: {path}")


def _write_file(path: Path, data: bytes) -> None:
    _check_file_destination(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _check_path(path.parent)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".portable-", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def sync(root: Path, *, check: bool = False) -> list[Path]:
    """Generate the two shared files in each canonical skill; return differences."""
    root = _absolute(root)
    shared = _shared_data(root)
    planned = []
    for skill in SKILLS:
        skill_root = root / "skills" / skill
        _check_path(skill_root)
        if not skill_root.is_dir():
            raise PortableSkillsError(f"Missing canonical skill directory: {skill_root}")
        for filename, data in shared.items():
            destination = skill_root / "references" / filename
            _check_file_destination(destination)
            if not destination.exists() or destination.read_bytes() != data:
                planned.append((destination, data))
    if not check:
        for destination, data in planned:
            _write_file(destination, data)
    return [destination for destination, _ in planned]


def _rename_skill(data: bytes, skill: str, exported_name: str) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PortableSkillsError(f"{skill}/SKILL.md is not UTF-8") from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise PortableSkillsError(f"{skill}/SKILL.md has no YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---")
    except StopIteration as exc:
        raise PortableSkillsError(f"{skill}/SKILL.md has unclosed YAML frontmatter") from exc
    names = []
    for i in range(1, end):
        match = re.fullmatch(r"(name:[ \t]*)(['\"]?)([a-z0-9]+(?:-[a-z0-9]+)*)\2([ \t]*(?:#.*)?)(\r\n|\n|\r)?", lines[i])
        if match:
            if match[3] != skill:
                raise PortableSkillsError(f"{skill}/SKILL.md name does not match its directory")
            names.append(i)
            lines[i] = f"{match[1]}{match[2]}{exported_name}{match[2]}{match[4]}{match[5] or ''}"
        elif re.match(r"name\s*:", lines[i]):
            raise PortableSkillsError(f"Unsupported skill name in {skill}/SKILL.md")
    if len(names) != 1:
        raise PortableSkillsError(f"{skill}/SKILL.md needs exactly one name field")
    return "".join(lines).encode("utf-8")


def _rename_prompt(data: bytes, skill: str, exported_name: str) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PortableSkillsError(f"{skill}/agents/openai.yaml is not UTF-8") from exc
    lines = text.splitlines(keepends=True)
    prompt_fields = [i for i, line in enumerate(lines) if re.match(r"[ \t]*default_prompt:", line)]
    if len(prompt_fields) > 1:
        raise PortableSkillsError(f"Duplicate default_prompt fields in {skill}/agents/openai.yaml")
    if prompt_fields:
        index = prompt_fields[0]
        match = re.match(r"([ \t]*)default_prompt:[ \t]*(.*)", lines[index])
        indent = len(match[1])
        end = index + 1
        # Include YAML block scalars and wrapped quoted scalar lines only.
        while end < len(lines):
            line = lines[end]
            if line.strip() and len(line) - len(line.lstrip(" \t")) <= indent:
                break
            end += 1
        pattern = re.compile(r"\$" + re.escape(skill) + r"(?![a-zA-Z0-9_-])")
        lines[index:end] = [pattern.sub("$" + exported_name, line) for line in lines[index:end]]
    return "".join(lines).encode("utf-8")


def _skill_files(root: Path, skill: str, shared: dict[str, bytes]) -> dict[str, bytes]:
    source = root / "skills" / skill
    _check_path(source)
    if not source.is_dir():
        raise PortableSkillsError(f"Missing canonical skill directory: {source}")
    files = {}
    for directory, subdirectories, filenames in os.walk(source, followlinks=False):
        for name in sorted(subdirectories):
            _check_path(Path(directory) / name)
        for filename in sorted(filenames):
            path = Path(directory) / filename
            relative = path.relative_to(source).as_posix()
            if relative == MARKER:
                raise PortableSkillsError(f"Canonical skill contains reserved marker: {path}")
            files[relative] = _read_file(path)
    for filename, data in shared.items():
        files[f"references/{filename}"] = data
    exported_name = f"{PACKAGE}-{skill}"
    if "SKILL.md" not in files:
        raise PortableSkillsError(f"Missing {skill}/SKILL.md")
    files["SKILL.md"] = _rename_skill(files["SKILL.md"], skill, exported_name)
    if "agents/openai.yaml" in files:
        files["agents/openai.yaml"] = _rename_prompt(files["agents/openai.yaml"], skill, exported_name)
    return files


def _managed_files(directory: Path, exported_name: str) -> set[str]:
    marker = directory / MARKER
    _check_file_destination(marker)
    if not marker.is_file():
        raise PortableSkillsError(f"Refusing an existing directory not managed by this tool: {directory}")
    try:
        metadata = json.loads(marker.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PortableSkillsError(f"Invalid ownership marker: {marker}") from exc
    if not isinstance(metadata, dict) or (
        metadata.get("package"), metadata.get("skill"), metadata.get("version")
    ) != (PACKAGE, exported_name, MARKER_VERSION):
        raise PortableSkillsError(f"Ownership marker does not match this skill: {marker}")
    paths = metadata.get("managed_files")
    if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
        raise PortableSkillsError(f"Invalid managed_files in {marker}")
    if len(paths) != len(set(paths)):
        raise PortableSkillsError(f"Duplicate managed file in {marker}")
    for path in paths:
        pure = PurePosixPath(path)
        if (not path or pure.is_absolute() or pure.as_posix() != path
                or any(part in (".", "..") for part in pure.parts)
                or ":" in path or "\\" in path or path == MARKER):
            raise PortableSkillsError(f"Unsafe managed file path in {marker}: {path}")
    return set(paths)


def export(root: Path, output: Path) -> list[Path]:
    """Export all three skills after checking all destinations for conflicts."""
    root, output = _absolute(root), _absolute(output)
    _check_path(root)
    _check_path(output)
    if output.is_relative_to(root):
        raise PortableSkillsError(f"Export output must be outside the source repository: {output}")
    if output.exists() and not output.is_dir():
        raise PortableSkillsError(f"Export output is not a directory: {output}")
    shared = _shared_data(root)
    plans = []
    for skill in SKILLS:
        exported_name = f"{PACKAGE}-{skill}"
        directory = output / exported_name
        _check_path(directory)
        if root.is_relative_to(directory):
            raise PortableSkillsError(f"Export directory contains the source repository: {directory}")
        files = _skill_files(root, skill, shared)
        old_files = set()
        if directory.exists():
            if not directory.is_dir():
                raise PortableSkillsError(f"Skill destination is not a directory: {directory}")
            old_files = _managed_files(directory, exported_name)
        for relative in sorted(old_files | files.keys()):
            destination = directory / relative
            _check_file_destination(destination)
            if relative in files and destination.exists() and relative not in old_files:
                raise PortableSkillsError(f"Refusing to overwrite an unmanaged file: {destination}")
        metadata = {"package": PACKAGE, "skill": exported_name, "version": MARKER_VERSION,
                    "managed_files": sorted(files)}
        marker_data = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        plans.append((directory, files, old_files - files.keys(), marker_data))
    # No directories or files have been written before every skill passes above.
    for directory, files, obsolete, marker_data in plans:
        for relative, data in sorted(files.items()):
            _write_file(directory / relative, data)
        for relative in sorted(obsolete):
            destination = directory / relative
            _check_file_destination(destination)
            if destination.exists():
                destination.unlink()  # Only a file named in the previous marker.
        _write_file(directory / MARKER, marker_data)
    return [directory for directory, _, _, _ in plans]


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sync_parser = commands.add_parser("sync", help="Generate shared skill references")
    sync_parser.add_argument("--check", action="store_true", help="Report differences without writing")
    export_parser = commands.add_parser("export", help="Export three portable skill directories")
    destination = export_parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path, help="Explicit destination outside this repository")
    destination.add_argument("--target", choices=tuple(TARGETS), help="Use a client's documented default skills directory")
    export_parser.add_argument("--scope", choices=("project", "user"), default=None, help="Target scope (default: project)")
    export_parser.add_argument("--project", type=Path, help="Existing project root for --target")
    args = parser.parse_args(argv)
    root = root if root is not None else Path(__file__).resolve().parent.parent
    try:
        if args.command == "sync":
            differences = sync(root, check=args.check)
            for path in differences:
                print(f"{'Different' if args.check else 'Generated'}: {path}")
            return 1 if args.check and differences else 0
        if args.output is not None:
            if args.scope is not None or args.project is not None:
                raise PortableSkillsError("--scope and --project are only valid with --target")
            output = args.output
        else:
            output = target_directory(args.target, args.scope or "project", args.project)
        for directory in export(root, output):
            print(f"Exported: {directory}")
        return 0
    except (PortableSkillsError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
