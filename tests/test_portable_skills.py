"""Behavior tests for the portable skill sync and export commands."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "portable_skills.py"
SPEC = importlib.util.spec_from_file_location("portable_skills", SCRIPT)
portable = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portable)


class PortableSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source"
        self.output = self.base / "exported"
        (self.root / "references").mkdir(parents=True)
        (self.root / "references" / "common.md").write_bytes("\ufeff# 共同约束\r\n中文内容\r\n".encode("utf-8"))
        (self.root / "references" / "applications.md").write_bytes("# 应用选择\r可用能力\r".encode("utf-8"))
        for skill in portable.SKILLS:
            source = self.root / "skills" / skill
            (source / "references").mkdir(parents=True)
            (source / "agents").mkdir()
            (source / "assets").mkdir()
            (source / "SKILL.md").write_bytes(
                (f"---\r\nname: {skill}\r\ndescription: 中文说明\r\n---\r\n\r\n"
                 "# 当前任务\r\n[共同约束](references/common.md)\r\n"
                 "[应用选择](references/applications.md)\r\n[场景](references/scenario.md)\r\n").encode("utf-8")
            )
            (source / "references" / "scenario.md").write_text("# 场景指导\n", encoding="utf-8")
            (source / "agents" / "openai.yaml").write_bytes(
                (f'interface:\r\n  default_prompt: "请用 ${skill} 处理当前任务。"\r\n'
                 f'  short_description: "此处保留 ${skill}"\r\n'
                 'policy:\r\n  allow_implicit_invocation: true\r\n').encode("utf-8")
            )
            (source / "assets" / "sample.bin").write_bytes(b"\x00\xff\x10")

    def run_main(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return portable.main(list(args), root=self.root)

    def export(self):
        return portable.export(self.root, self.output)

    def skill_output(self, skill="engineering"):
        return self.output / f"practical-work-{skill}"

    def make_symlink(self, link, target, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"This environment cannot create symbolic links: {exc}")

    def make_junction(self, link, target):
        if os.name != "nt":
            self.skipTest("Directory junctions are Windows-specific")
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, check=False,
        )
        if result.returncode:
            self.skipTest("This environment cannot create directory junctions")
        self.addCleanup(os.rmdir, link)

    def test_sync_check_reports_differences_without_writing_then_passes(self):
        self.assertEqual(self.run_main("sync", "--check"), 1)
        for skill in portable.SKILLS:
            self.assertFalse((self.root / "skills" / skill / "references" / "common.md").exists())
        self.assertEqual(self.run_main("sync"), 0)
        self.assertEqual(self.run_main("sync", "--check"), 0)
        for skill in portable.SKILLS:
            references = self.root / "skills" / skill / "references"
            self.assertEqual((references / "common.md").read_bytes(), "# 共同约束\n中文内容\n".encode("utf-8"))
            self.assertEqual((references / "applications.md").read_bytes(), "# 应用选择\n可用能力\n".encode("utf-8"))
        (self.root / "references" / "common.md").write_text("# 新规则\n", encoding="utf-8")
        self.assertEqual(self.run_main("sync", "--check"), 1)
        self.assertNotIn("新规则", (self.root / "skills" / "research" / "references" / "common.md").read_text(encoding="utf-8"))

    def test_export_prefixes_names_and_prompt_without_changing_other_content(self):
        self.assertEqual(self.run_main("export", "--output", str(self.output)), 0)
        for skill in portable.SKILLS:
            name = f"practical-work-{skill}"
            source = self.root / "skills" / skill
            destination = self.skill_output(skill)
            expected_skill = (source / "SKILL.md").read_bytes().replace(
                f"name: {skill}\r\n".encode(), f"name: {name}\r\n".encode()
            )
            self.assertEqual((destination / "SKILL.md").read_bytes(), expected_skill)
            expected_prompt = (source / "agents" / "openai.yaml").read_bytes().replace(
                f"请用 ${skill}".encode("utf-8"), f"请用 ${name}".encode("utf-8")
            )
            self.assertEqual((destination / "agents" / "openai.yaml").read_bytes(), expected_prompt)
            self.assertEqual((destination / "assets" / "sample.bin").read_bytes(), b"\x00\xff\x10")
            marker = json.loads((destination / portable.MARKER).read_text(encoding="utf-8"))
            self.assertEqual((marker["package"], marker["skill"], marker["version"]), ("practical-work", name, 1))
            self.assertIn("references/common.md", marker["managed_files"])

    def test_one_exported_skill_can_be_moved_and_read_independently(self):
        self.export()
        detached = self.base / "detached-skill"
        shutil.move(str(self.skill_output()), detached)
        content = (detached / "SKILL.md").read_text(encoding="utf-8")
        references = re.findall(r"\[[^]]*\]\(([^)]+)\)", content)
        self.assertEqual(len(references), 3)
        for reference in references:
            target = (detached / reference).resolve()
            self.assertTrue(target.is_relative_to(detached.resolve()))
            self.assertTrue(target.read_text(encoding="utf-8"))
        self.assertEqual((detached / "references" / "common.md").read_bytes(), "# 共同约束\n中文内容\n".encode("utf-8"))

    def test_foreign_same_name_directory_is_rejected_before_any_skill_is_written(self):
        foreign = self.skill_output("delivery")
        foreign.mkdir(parents=True)
        (foreign / "mine.txt").write_text("用户文件", encoding="utf-8")
        unrelated = self.output / "another-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("其他技能", encoding="utf-8")
        with self.assertRaisesRegex(portable.PortableSkillsError, "not managed"):
            self.export()
        self.assertFalse(self.skill_output("research").exists())
        self.assertFalse(self.skill_output("engineering").exists())
        self.assertEqual((foreign / "mine.txt").read_text(encoding="utf-8"), "用户文件")
        self.assertEqual((unrelated / "SKILL.md").read_text(encoding="utf-8"), "其他技能")

    def test_managed_update_keeps_extra_files_and_removes_only_obsolete_managed_files(self):
        self.export()
        destination = self.skill_output()
        (destination / "personal-notes.txt").write_text("保留笔记", encoding="utf-8")
        (destination / "assets" / "extra.bin").write_bytes(b"personal")
        source = self.root / "skills" / "engineering"
        (source / "assets" / "sample.bin").unlink()
        with (source / "SKILL.md").open("ab") as handle:
            handle.write("新增说明\n".encode("utf-8"))
        (self.root / "references" / "common.md").write_text("# 更新规则\n", encoding="utf-8")
        self.export()
        self.assertEqual((destination / "personal-notes.txt").read_text(encoding="utf-8"), "保留笔记")
        self.assertEqual((destination / "assets" / "extra.bin").read_bytes(), b"personal")
        self.assertFalse((destination / "assets" / "sample.bin").exists())
        self.assertTrue((destination / "assets").is_dir())
        self.assertIn("新增说明", (destination / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual((destination / "references" / "common.md").read_text(encoding="utf-8"), "# 更新规则\n")

    def test_new_managed_file_cannot_overwrite_a_user_added_file_or_partly_update(self):
        self.export()
        first_file = self.skill_output("research") / "SKILL.md"
        previous = first_file.read_bytes()
        with (self.root / "skills" / "research" / "SKILL.md").open("ab") as handle:
            handle.write(b"Changed\n")
        target = self.skill_output("delivery") / "references" / "new.md"
        target.write_text("用户内容", encoding="utf-8")
        (self.root / "skills" / "delivery" / "references" / "new.md").write_text("源内容", encoding="utf-8")
        with self.assertRaisesRegex(portable.PortableSkillsError, "unmanaged file"):
            self.export()
        self.assertEqual(first_file.read_bytes(), previous)
        self.assertEqual(target.read_text(encoding="utf-8"), "用户内容")

    def test_output_inside_source_repository_is_rejected(self):
        inside = self.root / "exports"
        with self.assertRaisesRegex(portable.PortableSkillsError, "outside the source repository"):
            portable.export(self.root, inside)
        self.assertFalse(inside.exists())

    def test_output_symlink_is_rejected_without_writing_its_target(self):
        target = self.base / "outside"
        target.mkdir()
        self.make_symlink(self.output, target, directory=True)
        with self.assertRaisesRegex(portable.PortableSkillsError, "Symbolic links"):
            self.export()
        self.assertEqual(list(target.iterdir()), [])

    def test_symlinked_parent_of_output_is_rejected(self):
        target = self.base / "outside"
        target.mkdir()
        link = self.base / "linked-parent"
        self.make_symlink(link, target, directory=True)
        with self.assertRaisesRegex(portable.PortableSkillsError, "Symbolic links"):
            portable.export(self.root, link / "skills")
        self.assertEqual(list(target.iterdir()), [])

    def test_nested_target_symlink_is_rejected_before_other_skills_update(self):
        self.export()
        first_file = self.skill_output("research") / "SKILL.md"
        previous = first_file.read_bytes()
        with (self.root / "skills" / "research" / "SKILL.md").open("ab") as handle:
            handle.write(b"Changed\n")
        reference = self.skill_output("delivery") / "references" / "common.md"
        reference.unlink()
        outside = self.base / "outside.md"
        outside.write_text("不要覆盖", encoding="utf-8")
        self.make_symlink(reference, outside)
        with self.assertRaisesRegex(portable.PortableSkillsError, "Symbolic links"):
            self.export()
        self.assertEqual(outside.read_text(encoding="utf-8"), "不要覆盖")
        self.assertEqual(first_file.read_bytes(), previous)

    def test_source_symlink_is_rejected(self):
        outside = self.base / "outside.md"
        outside.write_text("外部文件", encoding="utf-8")
        link = self.root / "skills" / "delivery" / "references" / "linked.md"
        self.make_symlink(link, outside)
        with self.assertRaisesRegex(portable.PortableSkillsError, "Symbolic links"):
            self.export()
        self.assertFalse(self.output.exists())

    def test_output_directory_junction_is_rejected_without_writing_its_target(self):
        target = self.base / "outside"
        target.mkdir()
        self.make_junction(self.output, target)
        with self.assertRaisesRegex(portable.PortableSkillsError, "junctions"):
            self.export()
        self.assertEqual(list(target.iterdir()), [])

    def test_parent_directory_junction_is_rejected(self):
        target = self.base / "outside"
        target.mkdir()
        link = self.base / "linked-parent"
        self.make_junction(link, target)
        with self.assertRaisesRegex(portable.PortableSkillsError, "junctions"):
            portable.export(self.root, link / "skills")
        self.assertEqual(list(target.iterdir()), [])

    def test_nested_target_directory_junction_is_rejected_before_other_skills_update(self):
        self.export()
        first_file = self.skill_output("research") / "SKILL.md"
        previous = first_file.read_bytes()
        with (self.root / "skills" / "research" / "SKILL.md").open("ab") as handle:
            handle.write(b"Changed\n")
        references = self.skill_output("delivery") / "references"
        outside = self.base / "outside-references"
        references.rename(outside)
        self.make_junction(references, outside)
        original = (outside / "common.md").read_bytes()
        with self.assertRaisesRegex(portable.PortableSkillsError, "junctions"):
            self.export()
        self.assertEqual((outside / "common.md").read_bytes(), original)
        self.assertEqual(first_file.read_bytes(), previous)

    def test_marker_cannot_claim_a_file_outside_its_skill(self):
        self.export()
        outside = self.output / "keep.txt"
        outside.write_text("保留", encoding="utf-8")
        marker_path = self.skill_output("delivery") / portable.MARKER
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        marker["managed_files"].append("../keep.txt")
        marker_path.write_text(json.dumps(marker), encoding="utf-8")
        with self.assertRaisesRegex(portable.PortableSkillsError, "Unsafe managed file path"):
            self.export()
        self.assertEqual(outside.read_text(encoding="utf-8"), "保留")


if __name__ == "__main__":
    unittest.main()
