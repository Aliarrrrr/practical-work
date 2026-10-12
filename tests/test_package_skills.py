"""Archive layout, content, metadata, and destination protection tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import package_skills as packaging
sys.path.pop(0)

try:
    import yaml
except ImportError:
    yaml = None


class PackageSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source"
        self.output = self.base / "packages"
        (self.root / "references").mkdir(parents=True)
        (self.root / "references" / "common.md").write_bytes("# 共同约束\r\n具体内容\r\n".encode("utf-8"))
        (self.root / "references" / "applications.md").write_text("# 选择可用能力\n", encoding="utf-8")
        (self.root / "plugin.json").write_text(json.dumps({
            "name": "practical-work", "version": "0.3.0", "description": "科研、工程与交付",
            "repository": "https://example.com/practical-work", "extensions": {"com.openai": {"interface": {"category": "Productivity"}}},
        }, ensure_ascii=False), encoding="utf-8")
        (self.root / ".claude-plugin").mkdir()
        (self.root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"author": {"name": "Aliarrrrr"}}), encoding="utf-8")
        for skill in packaging.portable.SKILLS:
            source = self.root / "skills" / skill
            (source / "references").mkdir(parents=True)
            (source / "agents").mkdir()
            (source / "assets").mkdir()
            (source / "SKILL.md").write_bytes(
                (f"---\r\nname: {skill}\r\ndescription: 处理当前{skill}任务\r\n---\r\n"
                 "[共同约束](references/common.md)\r\n[应用](references/applications.md)\r\n"
                 "[场景](references/scenario.md)\r\n").encode("utf-8")
            )
            (source / "references" / "scenario.md").write_text("# 场景材料\n", encoding="utf-8")
            (source / "agents" / "openai.yaml").write_text(
                f'interface:\n  default_prompt: "请用 ${skill} 完成当前任务"\n', encoding="utf-8"
            )
            (source / "assets" / "binary.bin").write_bytes(b"\x00\xff\x10")

    def package(self, format_name="skills", **options):
        return packaging.package(self.root, self.output, format_name=format_name, **options)

    def unpack(self, archive_path, suffix):
        directory = self.base / suffix
        with zipfile.ZipFile(archive_path) as archive:
            self.assertIsNone(archive.testzip())
            for member in archive.namelist():
                self.assertFalse(Path(member).is_absolute())
                self.assertNotIn("..", Path(member).parts)
            archive.extractall(directory)
        return directory

    def assert_skill_complete(self, directory, skill):
        name = f"practical-work-{skill}"
        content = (directory / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(f"name: {name}\n", content)
        for reference in re.findall(r"\[[^]]*\]\(([^)]+)\)", content):
            target = (directory / reference).resolve()
            self.assertTrue(target.is_relative_to(directory.resolve()))
            self.assertTrue(target.read_text(encoding="utf-8"))
        prompt = (directory / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn(f"${name}", prompt)
        self.assertEqual((directory / "assets" / "binary.bin").read_bytes(), b"\x00\xff\x10")
        self.assertEqual((directory / "references" / "common.md").read_bytes(), "# 共同约束\n具体内容\n".encode("utf-8"))

    def test_skills_zips_have_skill_files_directly_at_archive_root(self):
        archives = self.package()
        self.assertEqual(len(archives), 3)
        for path in archives:
            self.assertEqual(path.parent, self.output / "skills")
            self.assertTrue(path.name.endswith("-0.3.0.zip"))
            skill = path.name.removeprefix("practical-work-").removesuffix("-0.3.0.zip")
            with zipfile.ZipFile(path) as archive:
                self.assertIn("SKILL.md", archive.namelist())
                self.assertNotIn(f"practical-work-{skill}/SKILL.md", archive.namelist())
                self.assertNotIn("manifest.yaml", archive.namelist())
            self.assert_skill_complete(self.unpack(path, f"standalone-{skill}"), skill)

    def test_antigravity_zip_has_two_field_manifest_and_complete_prefixed_skills(self):
        archives = self.package("antigravity")
        self.assertEqual([path.name for path in archives], ["practical-work-0.3.0.zip"])
        unpacked = self.unpack(archives[0], "antigravity-unpacked")
        manifest = json.loads((unpacked / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest, {"name": "practical-work", "description": "科研、工程与交付"})
        self.assertEqual(set(entry.name for entry in unpacked.iterdir()), {"plugin.json", "skills"})
        self.assertFalse((unpacked / ".codex-plugin").exists())
        self.assertFalse((unpacked / ".claude-plugin").exists())
        for skill in packaging.portable.SKILLS:
            self.assert_skill_complete(unpacked / "skills" / f"practical-work-{skill}", skill)

    def test_antigravity_optional_rule_uses_current_canonical_common(self):
        archive_path = self.package("antigravity", include_common_rule=True)[0]
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(archive.read("rules/practical-work-common.md"),
                             "---\ntrigger: always_on\n---\n\n# 共同约束\n具体内容\n".encode("utf-8"))
        self.package("antigravity")
        with zipfile.ZipFile(archive_path) as archive:
            self.assertNotIn("rules/practical-work-common.md", archive.namelist())

    def test_enterprise_zips_have_one_prefixed_folder_and_exact_metadata_fields(self):
        archives = self.package("workbuddy-enterprise", category="企业配置分类")
        for path in archives:
            skill = path.name.removeprefix("practical-work-").removesuffix("-0.3.0.zip")
            name = f"practical-work-{skill}"
            unpacked = self.unpack(path, f"enterprise-{skill}")
            self.assertEqual([entry.name for entry in unpacked.iterdir()], [name])
            self.assert_skill_complete(unpacked / name, skill)
            data = (unpacked / name / "manifest.yaml").read_text(encoding="utf-8")
            # Each emitted value is a JSON string, a valid YAML scalar.
            manifest = {line.split(":", 1)[0]: json.loads(line.split(":", 1)[1]) for line in data.splitlines()}
            self.assertEqual(manifest, {"name": name, "version": "0.3.0",
                "description": f"处理当前{skill}任务", "category": "企业配置分类", "author": "Aliarrrrr"})

    @unittest.skipIf(yaml is None, "PyYAML is unavailable for independent parsing of enterprise metadata")
    def test_enterprise_metadata_is_accepted_by_yaml_safe_load_with_special_strings(self):
        category = '研发: "数据" # 企业\n第二行'
        author = '发布者: 张三 "A"'
        for path in self.package("workbuddy-enterprise", category=category, author=author):
            with zipfile.ZipFile(path) as archive:
                filename = next(name for name in archive.namelist() if name.endswith("/manifest.yaml"))
                manifest = yaml.safe_load(archive.read(filename).decode("utf-8"))
            self.assertEqual(manifest["category"], category)
            self.assertEqual(manifest["author"], author)
            self.assertEqual(manifest["version"], "0.3.0")

    def test_enterprise_author_falls_back_to_package_name_without_claude_manifest(self):
        (self.root / ".claude-plugin" / "plugin.json").unlink()
        path = self.package("workbuddy-enterprise", category="configured-category")[0]
        with zipfile.ZipFile(path) as archive:
            filename = next(name for name in archive.namelist() if name.endswith("/manifest.yaml"))
            self.assertIn('author: "practical-work"', archive.read(filename).decode("utf-8"))

    def test_enterprise_requires_nonempty_category_before_any_output_is_written(self):
        for category in (None, "", " \t"):
            with self.subTest(category=category), self.assertRaisesRegex(packaging.PackageError, "non-empty --category"):
                self.package("workbuddy-enterprise", category=category)
        self.assertFalse(self.output.exists())

    def test_common_rule_option_is_only_valid_for_antigravity(self):
        for format_name in ("skills", "workbuddy-enterprise"):
            with self.subTest(format_name=format_name), self.assertRaisesRegex(packaging.PackageError, "only valid for antigravity"):
                self.package(format_name, include_common_rule=True, category="category" if format_name == "workbuddy-enterprise" else None)
        self.assertFalse(self.output.exists())

    def test_foreign_same_name_archive_rejects_entire_batch_before_writing(self):
        directory = self.output / "skills"
        directory.mkdir(parents=True)
        foreign = directory / "practical-work-research-0.3.0.zip"
        foreign.write_bytes(b"owned by somebody else")
        with self.assertRaisesRegex(packaging.PackageError, "unmanaged archive"):
            self.package()
        self.assertEqual(foreign.read_bytes(), b"owned by somebody else")
        self.assertEqual(list(directory.iterdir()), [foreign])

    def test_managed_update_preserves_extra_files_other_formats_and_previous_versions(self):
        archives = self.package()
        previous_bytes = {path.name: path.read_bytes() for path in archives}
        directory = self.output / "skills"
        extra = directory / "personal.zip"
        extra.write_bytes(b"preserve")
        note = directory / "note.txt"
        note.write_text("用户笔记", encoding="utf-8")
        native_archive = self.package("antigravity")[0]
        native_bytes = native_archive.read_bytes()
        self.package()
        self.assertEqual({path.name: path.read_bytes() for path in archives}, previous_bytes)
        (self.root / "references" / "common.md").write_text("# 更新内容\n", encoding="utf-8")
        self.package()
        with zipfile.ZipFile(archives[0]) as archive:
            self.assertEqual(archive.read("references/common.md"), "# 更新内容\n".encode("utf-8"))
        source_manifest = json.loads((self.root / "plugin.json").read_text(encoding="utf-8"))
        source_manifest["version"] = "0.3.1"
        (self.root / "plugin.json").write_text(json.dumps(source_manifest), encoding="utf-8")
        newer = self.package()
        self.assertTrue(all(path.name.endswith("-0.3.1.zip") for path in newer))
        self.assertTrue(all(path.exists() for path in archives))
        self.assertEqual(extra.read_bytes(), b"preserve")
        self.assertEqual(note.read_text(encoding="utf-8"), "用户笔记")
        self.assertEqual(native_archive.read_bytes(), native_bytes)

    def test_collision_after_successful_package_does_not_partly_update_existing_archives(self):
        archives = self.package()
        previous = {path: path.read_bytes() for path in archives}
        marker = self.output / "skills" / packaging.MARKER
        metadata = json.loads(marker.read_text(encoding="utf-8"))
        metadata["managed_files"].remove("practical-work-research-0.3.0.zip")
        marker.write_text(json.dumps(metadata), encoding="utf-8")
        (self.root / "references" / "common.md").write_text("# 新内容\n", encoding="utf-8")
        with self.assertRaisesRegex(packaging.PackageError, "unmanaged archive"):
            self.package()
        self.assertEqual({path: path.read_bytes() for path in archives}, previous)

    def test_source_repository_output_is_rejected(self):
        with self.assertRaisesRegex(packaging.PackageError, "outside the source repository"):
            packaging.package(self.root, self.root / "output", format_name="skills")
        self.assertFalse((self.root / "output").exists())

    def test_symlink_output_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            self.output.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"This environment cannot create symbolic links: {exc}")
        with self.assertRaisesRegex(packaging.PackageError, "Symbolic links"):
            self.package()
        self.assertEqual(list(outside.iterdir()), [])

    def test_junction_output_is_rejected(self):
        if os.name != "nt":
            self.skipTest("Directory junctions are Windows-specific")
        outside = self.base / "outside"
        outside.mkdir()
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(self.output), str(outside)], capture_output=True, check=False)
        if result.returncode:
            self.skipTest("This environment cannot create directory junctions")
        self.addCleanup(os.rmdir, self.output)
        with self.assertRaisesRegex(packaging.PackageError, "junctions"):
            self.package()
        self.assertEqual(list(outside.iterdir()), [])

    def test_marker_cannot_claim_a_file_outside_format_directory(self):
        self.package()
        marker_path = self.output / "skills" / packaging.MARKER
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        marker["managed_files"].append("../foreign.zip")
        marker_path.write_text(json.dumps(marker), encoding="utf-8")
        with self.assertRaisesRegex(packaging.PackageError, "Unsafe archive filename"):
            self.package()

    def test_cli_uses_requested_format_and_returns_error_for_missing_category(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(packaging.main(["--format", "workbuddy-enterprise", "--output", str(self.output)], root=self.root), 2)
            self.assertEqual(packaging.main(["--format", "antigravity", "--output", str(self.output)], root=self.root), 0)
        self.assertTrue((self.output / "antigravity" / "practical-work-0.3.0.zip").is_file())
        self.assertFalse((self.output / "workbuddy-enterprise").exists())


if __name__ == "__main__":
    unittest.main()
