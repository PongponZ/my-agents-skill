"""Structural packaging tests; synthetic fixtures are not usable art deliverables."""

import copy
import hashlib
import json
import struct
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

from package_artifact import FILES, TOPICS, TOPIC_HEADINGS, SCOPE, package, validate_project


def png():
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="modeling-skill-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        for filename in FILES:
            (self.root / filename).write_text("Synthetic test fixture.\n", encoding="utf-8")
        (self.root / "references").mkdir()
        (self.root / "references/primary.png").write_bytes(png())
        (self.root / "concept_sheet.png").write_bytes(png())
        self.analysis = {
            "schema_version": 3, "name": "test-lantern", "display_name": "Test Lantern",
            "scope": dict(SCOPE),
            "status": "concept_ready", "subject": {"category": "prop"},
            "references": [{"id": "R01", "path": "references/primary.png", "role": "primary"}],
            "constraints": {}, "scale": {"mode": "unknown"},
            "coordinate_system": {"up": "+Z", "front": "-Y", "subject_right": "-X",
                                  "reference_view_mapping": "Handle on image-left in front view."},
            "proportions": [],
            "components": [{"id": "C01", "parent_id": None, "material_ids": ["M01"], "features": [
                {"id": "F01", "description": "Raised lip around opening", "evidence": "observed",
                 "source_region": "R01 upper rim", "representation": "geometry", "required": True,
                 "must_preserve": True, "construction": "Thick lip with a recessed opening",
                 "allowed_simplification": "none", "inspection_views": ["RIM_DETAIL"],
                 "acceptance": ["Opening depth and lip thickness are visible in close-up."]},
                {"id": "F02", "description": "Paint pattern", "evidence": "observed",
                 "source_region": "R01 shell", "representation": "texture", "required": True,
                 "must_preserve": True, "construction": "Map painted stripes around shell",
                 "allowed_simplification": "none", "inspection_views": ["SURFACE_DETAIL"],
                 "acceptance": ["Stripes align without stretching."]},
            ]}],
            "materials": [{"id": "M01", "texture_plan": "Directional stripe mask with UV mapping",
                           "inspection_criteria": ["No seam in the visible stripes."]}],
            "view_plan": [], "unknowns": [], "decisions": [], "concept_sheet": "concept_sheet.png",
            "concept_qa": {"approved": True, "report": "concept_qa.md", "unresolved": []},
        }
        (self.root / "detail_crops").mkdir()
        (self.root / "detail_crops/primary-detail.png").write_bytes(png())
        self.analysis["detail_crops"] = [{"id": "P01", "path": "detail_crops/primary-detail.png",
            "source_id": "R01", "bbox": [0, 0, 1, 1], "feature_ids": ["F01", "F02"],
            "caption": "Synthetic primary detail crop: rim and stripes"}]
        for feature in self.analysis["components"][0]["features"]:
            feature.update(detail_spec=feature["construction"],
                design_source={"kind": "reference", "source_id": "R01", "region": "upper shell",
                               "reason": "Primary clearly shows this feature", "decision_id": None},
                measurements=[], measurement_note="Qualitative synthetic fixture; no numeric target needed",
                comparison_crop_ids=["P01"])
        self.write_analysis()
        self.spec = {
            "schema_version": 3, "name": "test-lantern", "artifact_type": "modeling_prompt_package",
            "scope": dict(SCOPE),
            "source_analysis": "analysis.json", "outputs": ["test-lantern_final.blend"],
            "topics": {topic: {"requirements": ["Build C01 according to R01."],
                               "acceptance": ["Inspect the visible silhouette."]} for topic in TOPICS},
            "feature_plan": [{"feature_id": fid, "component_id": "C01",
                              "requirements": ["Implement the feature using its source region."],
                              "acceptance": ["Inspect the matching close-up."],
                              "comparison": {"crop_ids": ["P01"], "model_views": ["DETAIL"],
                                             "checks": ["Compare the required profile side by side."]}}
                             for fid in ("F01", "F02")],
            "phases": {
                "mesh_details": {"entry_criteria": ["Concept ready"],
                                 "exit_criteria": ["All mesh comparison checks pass after repairs if needed"]},
                "materials_textures": {"entry_criteria": ["Mesh/detail gate passed"],
                                       "exit_criteria": ["Surface comparisons and saved resources pass"]}},
        }
        self.write_spec()
        for language in ("th", "en"):
            body = "คำสั่งทดสอบ\n" if language == "th" else "Test instructions.\n"
            body += "\n".join(f"## {i}. {heading}\nConcrete fixture instruction.\n"
                              for i, heading in enumerate(TOPIC_HEADINGS.values(), 1))
            body += "\nImplement F01 and F02 using the source specification.\n"
            (self.root / f"model_prompt.{language}.md").write_text(body, encoding="utf-8")
        (self.root / "prompt_qa.md").write_text("approved: true\nSynthetic QA fixture.\n", encoding="utf-8")
        self.output = Path(self.temporary.name) / "output"

    def write_analysis(self):
        (self.root / "analysis.json").write_text(json.dumps(self.analysis), encoding="utf-8")

    def write_spec(self):
        (self.root / "build_spec.json").write_text(json.dumps(self.spec), encoding="utf-8")

    def test_archive_contents_hashes_and_no_unrelated_files(self):
        (self.root / "private.txt").write_text("Must not enter the archive.", encoding="utf-8")
        (self.root / "detail_crops/undeclared.png").write_bytes(png())
        path = package(self.root, self.output)
        self.assertEqual(path.name, "test-lantern_artifact.zip")
        with zipfile.ZipFile(path) as archive:
            self.assertIsNone(archive.testzip())
            expected = {f"test-lantern/{v}" for v in FILES}
            expected.update({"test-lantern/references/primary.png", "test-lantern/manifest.json",
                             "test-lantern/detail_crops/primary-detail.png"})
            self.assertEqual(set(archive.namelist()), expected)
            manifest = json.loads(archive.read("test-lantern/manifest.json"))
            self.assertFalse(manifest["contains_finished_model"])
            for entry in manifest["files"]:
                actual = archive.read("test-lantern/" + entry["path"])
                self.assertEqual(hashlib.sha256(actual).hexdigest(), entry["sha256"])

    def test_does_not_overwrite_existing_archive(self):
        path = package(self.root, self.output)
        original = path.read_bytes()
        with self.assertRaises(ValueError):
            package(self.root, self.output)
        self.assertEqual(path.read_bytes(), original)

    def test_missing_reference_is_rejected(self):
        (self.root / "references/primary.png").unlink()
        with self.assertRaises(ValueError):
            validate_project(self.root)

    def test_path_traversal_and_absolute_paths_are_rejected(self):
        for path in ("references/../../outside.png", "C:/outside.png", "/outside.png"):
            with self.subTest(path=path):
                self.analysis["references"][0]["path"] = path
                self.write_analysis()
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_unapproved_or_unready_concept_is_rejected(self):
        initial = copy.deepcopy(self.analysis)
        for field, value in (("status", "concept_needs_revision"), ("concept_qa", {"approved": False})):
            self.analysis = copy.deepcopy(initial)
            self.analysis[field] = value
            self.write_analysis()
            with self.assertRaises(ValueError):
                validate_project(self.root)

    def test_corrupt_png_is_rejected(self):
        data = bytearray(png())
        data[20] ^= 1
        (self.root / "concept_sheet.png").write_bytes(data)
        with self.assertRaises(ValueError):
            validate_project(self.root)

    def test_empty_section_and_unresolved_slot_are_rejected(self):
        path = self.root / "model_prompt.en.md"
        original = path.read_text(encoding="utf-8")
        for content in (original.replace("Concrete fixture instruction.\n", "", 1), original + "{{subject}}"):
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_project(self.root)

    def test_build_spec_name_mismatch_is_rejected(self):
        self.spec["name"] = "different-asset"
        self.write_spec()
        with self.assertRaises(ValueError):
            validate_project(self.root)

    def test_unapproved_prompt_is_rejected(self):
        (self.root / "prompt_qa.md").write_text("approved: false\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate_project(self.root)

    def test_legacy_analysis_requires_migration(self):
        for version in (1, 2):
            self.analysis["schema_version"] = version
            self.write_analysis()
            with self.assertRaisesRegex(ValueError, "migrate version 1/2"):
                validate_project(self.root)

    def test_presentation_or_missing_texture_scope_is_rejected(self):
        for document, filename in ((self.analysis, "analysis.json"), (self.spec, "build_spec.json")):
            for key, value in (("presentation", True), ("textures", False)):
                with self.subTest(document=filename, key=key):
                    document["scope"][key] = value
                    (self.root / filename).write_text(json.dumps(document), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Scope must"):
                        validate_project(self.root)
                    document["scope"] = dict(SCOPE)
                    (self.root / filename).write_text(json.dumps(document), encoding="utf-8")

    def test_required_mesh_and_texture_coverage(self):
        original = copy.deepcopy(self.spec["feature_plan"])
        for missing in ("F01", "F02"):
            with self.subTest(missing=missing):
                self.spec["feature_plan"] = [p for p in original if p["feature_id"] != missing]
                self.write_spec()
                with self.assertRaisesRegex(ValueError, "Required features missing"):
                    validate_project(self.root)

    def test_optional_feature_can_be_omitted(self):
        feature = self.analysis["components"][0]["features"][1]
        feature.update(required=False, must_preserve=False)
        self.spec["feature_plan"] = self.spec["feature_plan"][:1]
        self.write_analysis()
        self.write_spec()
        validate_project(self.root)

    def test_wrong_duplicate_and_unknown_feature_links(self):
        initial = copy.deepcopy(self.spec["feature_plan"])
        for case in ("wrong_component", "duplicate", "unknown"):
            with self.subTest(case=case):
                self.spec["feature_plan"] = copy.deepcopy(initial)
                if case == "wrong_component":
                    self.spec["feature_plan"][0]["component_id"] = "C99"
                elif case == "duplicate":
                    self.spec["feature_plan"].append(copy.deepcopy(initial[0]))
                else:
                    self.spec["feature_plan"][0]["feature_id"] = "F99"
                self.write_spec()
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_blocking_concept_issue_cannot_be_packaged_as_approved(self):
        self.analysis["concept_qa"]["unresolved"] = [{"id": "Q01", "severity": "blocking",
            "finding": "Required opening is missing", "resolution": "Still needs repair"}]
        self.write_analysis()
        with self.assertRaisesRegex(ValueError, "unresolved blocking"):
            validate_project(self.root)

    def test_material_plan_and_orientation_mapping_are_required(self):
        initial = copy.deepcopy(self.analysis)
        for case in ("texture", "orientation"):
            self.analysis = copy.deepcopy(initial)
            if case == "texture":
                del self.analysis["materials"][0]["texture_plan"]
            else:
                del self.analysis["coordinate_system"]["reference_view_mapping"]
            self.write_analysis()
            with self.assertRaises(ValueError):
                validate_project(self.root)

    def test_both_prompts_must_reference_required_features(self):
        for language in ("th", "en"):
            path = self.root / f"model_prompt.{language}.md"
            original = path.read_text(encoding="utf-8")
            path.write_text(original.replace("F01", "F010"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Required feature F01"):
                validate_project(self.root)
            path.write_text(original, encoding="utf-8")

    def test_must_preserve_feature_cannot_be_optional(self):
        self.analysis["components"][0]["features"][0]["required"] = False
        self.write_analysis()
        with self.assertRaisesRegex(ValueError, "Must-preserve"):
            validate_project(self.root)

    def test_selected_decisions_keep_evidence_and_lock_separate(self):
        self.analysis["decisions"] = [{"id": "D01", "component_ids": ["C01"],
            "issue": "Hidden attachment", "alternatives": ["Inset", "Raised"],
            "selected": "Inset continuation of the visible lip", "rationale": "Matches visible contour",
            "status": "selected", "locked": True, "impact": "Rim attachment geometry",
            "revisit_when": "New reference reveals the attachment"}]
        self.write_analysis()
        validate_project(self.root)
        self.analysis["decisions"][0]["status"] = "unresolved"
        self.write_analysis()
        with self.assertRaisesRegex(ValueError, "unresolved decision cannot be locked"):
            validate_project(self.root)

    def test_missing_and_invalid_crop_images_are_rejected(self):
        path = self.root / "detail_crops/primary-detail.png"
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing or empty"):
            validate_project(self.root)
        path.write_bytes(b"not a PNG")
        with self.assertRaisesRegex(ValueError, "not encoded as PNG"):
            validate_project(self.root)

    def test_crop_bounds_and_paths_are_validated(self):
        original = copy.deepcopy(self.analysis["detail_crops"][0])
        changes = [("bbox", [0.8, 0, 0.5, 1]), ("bbox", [0, 0, 0, 1]),
                   ("bbox", [False, 0, 1, 1]), ("bbox", [float("nan"), 0, 1, 1]),
                   ("path", "detail_crops/../../outside.png"), ("path", "references/primary.png")]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                self.analysis["detail_crops"][0] = copy.deepcopy(original)
                self.analysis["detail_crops"][0][key] = value
                self.write_analysis()
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_unknown_duplicate_and_one_way_crop_links_are_rejected(self):
        initial = copy.deepcopy(self.analysis)
        for case in ("source", "feature", "duplicate_id", "duplicate_path", "one_way", "no_feature_crop"):
            with self.subTest(case=case):
                self.analysis = copy.deepcopy(initial)
                crop = self.analysis["detail_crops"][0]
                if case == "source":
                    crop["source_id"] = "R99"
                elif case == "feature":
                    crop["feature_ids"] = ["F99"]
                elif case.startswith("duplicate"):
                    second = copy.deepcopy(crop)
                    if case == "duplicate_path":
                        second["id"] = "P02"
                    self.analysis["detail_crops"].append(second)
                elif case == "one_way":
                    crop["feature_ids"] = ["F01"]
                else:
                    self.analysis["components"][0]["features"][0]["comparison_crop_ids"] = []
                self.write_analysis()
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_selected_concept_detail_is_accepted_and_packaged(self):
        self.analysis["decisions"] = [{"id": "D01", "component_ids": ["C01"], "issue": "Indistinct rim",
            "alternatives": ["Primary approximation", "Concept rim"], "selected": "Concept rim panel",
            "rationale": "Selected detail target preserves identity", "status": "selected", "locked": True,
            "impact": "Rim detail", "revisit_when": "User changes the selected design"}]
        feature = self.analysis["components"][0]["features"][0]
        feature["evidence"] = "proposed"
        feature["design_source"] = {"kind": "concept", "source_id": "concept_sheet", "region": "rim panel",
                                    "reason": "Primary lacks detail", "decision_id": "D01"}
        feature["comparison_crop_ids"].append("P02")
        self.analysis["detail_crops"].append({"id": "P02", "path": "detail_crops/concept-rim.png",
            "source_id": "concept_sheet", "bbox": [0, 0, 1, 1], "feature_ids": ["F01"],
            "caption": "Generated concept: selected rim design"})
        (self.root / "detail_crops/concept-rim.png").write_bytes(png())
        self.spec["feature_plan"][0]["comparison"]["crop_ids"].append("P02")
        self.write_analysis()
        self.write_spec()
        path = package(self.root, self.output)
        with zipfile.ZipFile(path) as archive:
            self.assertIn("test-lantern/detail_crops/concept-rim.png", archive.namelist())
            saved = json.loads(archive.read("test-lantern/analysis.json"))
            self.assertEqual(saved["components"][0]["features"][0]["evidence"], "proposed")
        self.analysis["decisions"][0].update(status="unresolved", locked=False)
        self.write_analysis()
        with self.assertRaisesRegex(ValueError, "not selected"):
            validate_project(self.root)

    def test_selected_source_needs_matching_crop(self):
        self.analysis["detail_crops"][0]["source_id"] = "concept_sheet"
        self.write_analysis()
        with self.assertRaisesRegex(ValueError, "do not include selected design source"):
            validate_project(self.root)

    def test_measurements_need_frames_basis_and_valid_numbers(self):
        feature = self.analysis["components"][0]["features"][0]
        valid = {"name": "Rim depth", "target": [0.08, 0.1], "unit": "D",
                 "frame": "body-local, D=body width", "datum": "outer lip to cavity floor along local Y",
                 "basis": "design_choice", "tolerance": 0.005}
        feature["measurements"] = [valid]
        self.write_analysis()
        validate_project(self.root)
        for key, value in (("frame", ""), ("datum", ""), ("target", [0.1, 0.08]),
                           ("target", True), ("target", float("inf")), ("basis", "fact"), ("tolerance", -1)):
            with self.subTest(key=key):
                invalid = copy.deepcopy(valid)
                invalid[key] = value
                feature["measurements"] = [invalid]
                self.write_analysis()
                with self.assertRaises(ValueError):
                    validate_project(self.root)

    def test_comparison_plan_and_phase_gates_are_required(self):
        initial = copy.deepcopy(self.spec)
        for case in ("no_comparison", "wrong_crop", "no_checks", "no_phases", "no_exit"):
            self.spec = copy.deepcopy(initial)
            comparison = self.spec["feature_plan"][0]["comparison"]
            if case == "no_comparison":
                del self.spec["feature_plan"][0]["comparison"]
            elif case == "wrong_crop":
                comparison["crop_ids"] = ["P99"]
            elif case == "no_checks":
                comparison["checks"] = []
            elif case == "no_phases":
                del self.spec["phases"]
            else:
                self.spec["phases"]["mesh_details"]["exit_criteria"] = []
            self.write_spec()
            with self.assertRaises(ValueError):
                validate_project(self.root)


if __name__ == "__main__":
    unittest.main()
