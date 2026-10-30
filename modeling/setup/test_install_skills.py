"""Verify standalone workflow installs and ZIPs have their stage resources."""
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from install_skills import BUNDLED_STAGES, SKILLS, SRC, validate


class MainWorkflowInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="reference-workflow-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.installer = SRC / "setup/install_skills.py"

    def run_installer(self, target, dest, *options):
        result = subprocess.run(
            [sys.executable, "-B", str(self.installer), target, "--dest", str(dest), *options],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_standalone(self, main):
        self.assertEqual(validate(main), [])
        content = (main / "SKILL.md").read_text(encoding="utf-8")
        for name in BUNDLED_STAGES["reference-to-prompt"]:
            self.assertIn(f"(workflows/{name}/SKILL.md)", content)
            self.assertNotIn(f"(../{name}/SKILL.md)", content)
            self.assertEqual(validate(main / "workflows" / name), [])
        concept = main / "workflows/reference-to-concept"
        prompts = main / "workflows/concept-to-model-prompt"
        self.assertTrue((concept / "references/analysis-contract.md").is_file())
        self.assertTrue((prompts / "assets/part-prompt.template.md").is_file())
        self.assertTrue((prompts / "assets/model-prompt.template.md").is_file())
        result = subprocess.run(
            [sys.executable, "-B", str(prompts / "scripts/package_artifact.py"), "--help"],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_main_only_install_contains_both_stages(self):
        dest = self.root / "installed"
        self.run_installer("codex", dest, "--skills", "reference-to-prompt")
        self.assertEqual({p.name for p in dest.iterdir()}, {"reference-to-prompt"})
        self.assert_standalone(dest / "reference-to-prompt")

    def test_single_main_zip_works_after_extraction(self):
        for target in ("claude-app", "chatgpt-web"):
            with self.subTest(target=target):
                dest = self.root / target
                self.run_installer(target, dest, "--skills", "reference-to-prompt")
                self.assertEqual({p.name for p in dest.iterdir()}, {"reference-to-prompt.zip"})
                extracted = self.root / (target + "-extracted")
                with zipfile.ZipFile(dest / "reference-to-prompt.zip") as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertTrue(all(n.startswith("reference-to-prompt/")
                                        for n in archive.namelist()))
                    archive.extractall(extracted)
                self.assert_standalone(extracted / "reference-to-prompt")

    def test_default_install_preserves_source_and_includes_three_skills(self):
        source = SRC / "reference-to-prompt/SKILL.md"
        before = source.read_bytes()
        dest = self.root / "default"
        self.run_installer("claude-code", dest)
        self.assertEqual(set(SKILLS), {"reference-to-prompt", "reference-to-concept",
                                      "concept-to-model-prompt"})
        self.assertEqual({p.name for p in dest.iterdir()}, set(SKILLS))
        self.assert_standalone(dest / "reference-to-prompt")
        self.assertEqual(source.read_bytes(), before)
        self.assertFalse((SRC / "reference-to-prompt/workflows").exists())


if __name__ == "__main__":
    unittest.main()
