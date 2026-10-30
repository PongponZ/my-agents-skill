"""Structural tests; generated pixels are synthetic fixtures, not art deliverables."""
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

from package_artifact import package, validate_project


def png():
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="compact-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "test-lantern"
        self.root.mkdir()
        self.output = self.root.parent / "output"
        self.write("main_prompt.md", "# Lantern\nStatic editable mesh, diagnostic views only.\n\n"
                   "[Overview](parts/00-overview/prompt.md)\n[Shell](parts/shell/prompt.md)\n")
        self.add_part("00-overview")
        self.add_part("shell", "\nAttach to [Overview](../00-overview/prompt.md).\n")

    def write(self, relative, text):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def add_part(self, name, extra=""):
        self.write(f"parts/{name}/prompt.md",
                   f"# {name}\n\n## Reference\n![Primary crop](reference.png)\nObserved front view.\n\n"
                   "## Build\nF01: thick raised rim and recessed opening, matte painted surface.\n"
                   + extra + "\n## Check\nF01: compare front close-up, visible depth and continuous rim.\n")
        (self.root / f"parts/{name}/reference.png").write_bytes(png())

    def test_only_main_indexed_parts_and_used_images_are_shipped(self):
        self.write("analysis.json", '{"private_authoring": true}')
        self.write("build_spec.json", "{}")
        self.write("model_prompt.en.md", "Old prompt")
        self.write("concept_qa.md", "Working QA")
        self.write("manifest.json", "Old manifest")
        self.write("parts/shell/unused.png", "Unused file must not be read")
        self.add_part("unused")
        archive_path = package(self.root, self.output)
        expected = {
            "main_prompt.md", "parts/00-overview/prompt.md", "parts/00-overview/reference.png",
            "parts/shell/prompt.md", "parts/shell/reference.png",
        }
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(set(archive.namelist()), {f"test-lantern/{p}" for p in expected})
            self.assertIsNone(archive.testzip())
            for relative in expected:
                self.assertEqual(archive.read(f"test-lantern/{relative}"),
                                 (self.root / relative).read_bytes())
        self.assertTrue((self.root / "analysis.json").exists())

    def test_single_overview_package_and_main_backlink(self):
        self.write("main_prompt.md", "# Prop\n[Overview](parts/00-overview/prompt.md)\n")
        self.add_part("00-overview", "\nUse [global constraints](../../main_prompt.md).\n")
        _, payload = validate_project(self.root)
        self.assertEqual(len(payload), 3)

    def test_multiple_reference_images(self):
        self.add_part("shell", "\nCompare the side too: ![Side](side.png)\n")
        (self.root / "parts/shell/side.png").write_bytes(png())
        _, payload = validate_project(self.root)
        self.assertIn("parts/shell/side.png", payload)

    def test_missing_prompt_or_image_blocks_package(self):
        for relative in ("parts/shell/prompt.md", "parts/shell/reference.png"):
            with self.subTest(relative=relative):
                target = self.root / relative
                original = target.read_bytes()
                target.unlink()
                try:
                    with self.assertRaisesRegex(ValueError, "Missing file"):
                        package(self.root, self.output)
                    self.assertFalse(self.output.exists())
                finally:
                    target.write_bytes(original)

    def test_unindexed_dependency_is_not_silently_added(self):
        self.add_part("hidden")
        self.add_part("shell", "\nDepends on [hidden](../hidden/prompt.md).\n")
        with self.assertRaisesRegex(ValueError, "unindexed dependency"):
            validate_project(self.root)

    def test_no_external_or_excluded_document_dependencies(self):
        for target in ("https://example.com/ref.png", "C:/private/ref.png", "/tmp/ref.png",
                       "../../../private.png", "../../analysis.json", "../00-overview/reference.png"):
            with self.subTest(target=target):
                self.add_part("shell", f"\n[Dependency]({target})\n")
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_no_reference_style_or_html_links(self):
        for extra in ("![View][source]\n[source]: missing.png", '<img src="missing.png">'):
            with self.subTest(extra=extra):
                self.add_part("shell", extra)
                with self.assertRaisesRegex(ValueError, "plain inline Markdown"):
                    validate_project(self.root)

    def test_main_requires_part_index(self):
        for text in ("# Main\nNo parts.", "# Main\n[Analysis](analysis.json)"):
            with self.subTest(text=text):
                self.write("main_prompt.md", text)
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_empty_or_unfinished_prompts_rejected(self):
        for text in ("   \n", "{{unfinished_prompt}}", "[TODO build]"):
            with self.subTest(text=text):
                self.write("parts/shell/prompt.md", text)
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_part_requires_reference_and_build_and_check(self):
        target = self.root / "parts/shell/prompt.md"
        original = target.read_text(encoding="utf-8")
        variants = (
            original.replace("## Build", "## Notes"),
            original.replace("![Primary crop](reference.png)", "Image missing"),
            original[:original.index("## Check")] + "## Check\n",
            original + "\n## Build\nDuplicate instructions\n",
        )
        for text in variants:
            with self.subTest(text=text):
                target.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_invalid_png_rejected(self):
        for data in (b"not a png", png()[:-4], png() + b"garbage",
                     png()[:30] + bytes([png()[30] ^ 1]) + png()[31:]):
            with self.subTest(data=data):
                (self.root / "parts/shell/reference.png").write_bytes(data)
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_archive_cannot_be_overwritten(self):
        archive = package(self.root, self.output)
        before = archive.read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            package(self.root, self.output)
        self.assertEqual(archive.read_bytes(), before)

    def test_name_validation_and_override(self):
        for name in ("../escape", "Uppercase", "", "nul", "x" * 65):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    validate_project(self.root, name)
        archive = package(self.root, self.output, "renamed")
        with zipfile.ZipFile(archive) as result:
            self.assertTrue(all(p.startswith("renamed/") for p in result.namelist()))

    def test_symlink_escape_rejected(self):
        target = self.root / "parts/shell/reference.png"
        outside = self.root.parent / "outside.png"
        outside.write_bytes(png())
        target.unlink()
        try:
            target.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"Symlink creation unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "escapes project"):
            validate_project(self.root)

    def test_cli_success_and_failure(self):
        command = [sys.executable, str(Path(__file__).with_name("package_artifact.py")),
                   "--project", str(self.root), "--output-dir", str(self.output)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(Path(result.stdout.strip()).is_file())
        retry = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(retry.returncode, 1)
        self.assertIn("already exists", retry.stderr)


if __name__ == "__main__":
    unittest.main()
