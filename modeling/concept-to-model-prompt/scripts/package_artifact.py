"""Validate a concept/prompt project and package only its declared deliverables.

Python 3 standard library only. Does not generate images or certify visual quality.
"""

import argparse
import hashlib
import json
import math
import re
import struct
import sys
import tempfile
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


TOPIC_HEADINGS = {
    "geometry_proportions": "GEOMETRY & PROPORTIONS",
    "reference_fidelity": "REFERENCE FIDELITY & DESIGN DECISIONS",
    "components_mesh_details": "COMPONENTS & MESH DETAILS",
    "topology_assembly": "TOPOLOGY & ASSEMBLY QUALITY",
    "materials_textures": "MATERIALS & TEXTURES",
    "modeling_progression": "MODELING PROGRESSION",
    "verification_delivery": "VERIFICATION & DELIVERY",
}
TOPICS = tuple(TOPIC_HEADINGS)
SCOPE = {"mesh": True, "materials": True, "textures": True, "presentation": False}
FILES = (
    "analysis.json", "analysis.md", "concept_sheet.png", "concept_sheet_prompt.md",
    "details.md", "concept_qa.md", "handoff.md", "model_prompt.th.md",
    "model_prompt.en.md", "build_spec.json", "usage.th.md", "usage.en.md", "prompt_qa.md",
)
ANALYSIS_FIELDS = (
    "schema_version", "name", "display_name", "status", "subject", "references",
    "constraints", "scale", "coordinate_system", "proportions", "components",
    "materials", "view_plan", "unknowns", "decisions", "concept_sheet", "concept_qa", "scope", "detail_crops",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_file(root, relative):
    require(isinstance(relative, str) and relative, "File paths must be nonempty strings")
    rel = PurePosixPath(relative)
    require(not rel.is_absolute() and ".." not in rel.parts and "\\" not in relative
            and ":" not in relative, f"Unsafe project path: {relative}")
    candidate = root.joinpath(*rel.parts)
    require(candidate.resolve().is_relative_to(root), f"File escapes project: {relative}")
    require(candidate.is_file() and candidate.stat().st_size > 0, f"Missing or empty file: {relative}")
    return candidate


def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"Expected JSON object: {path.name}")
    return value


def string_array(value, label):
    require(isinstance(value, list) and value
            and all(isinstance(v, str) and v.strip() for v in value),
            f"{label} must be a nonempty string array")


def validate_scope(value):
    require(isinstance(value, dict) and set(value) == set(SCOPE)
            and all(value[k] is expected for k, expected in SCOPE.items()),
            "Scope must enable mesh, materials and textures and disable presentation")


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_detail_evidence(analysis, inventory, root, paths):
    """Validate declared source/crop links; pixel provenance still needs visual review."""
    references = {v["id"] for v in analysis["references"]}
    require("concept_sheet" not in references, "concept_sheet is a reserved source ID")
    decisions = {v["id"]: v for v in analysis["decisions"]}
    records = analysis["detail_crops"]
    require(isinstance(records, list) and records, "detail_crops must contain declared comparison images")
    crops = {}
    used_paths = {p.casefold() for p in paths}
    for crop in records:
        require(isinstance(crop, dict), "Invalid crop record")
        for field in ("id", "path", "source_id", "caption"):
            require(isinstance(crop.get(field), str) and crop[field].strip(), f"Crop needs {field}")
        crop_id = crop["id"]
        require(crop_id not in crops, f"Duplicate crop ID: {crop_id}")
        require(crop["source_id"] in references | {"concept_sheet"}, f"Unknown crop source: {crop_id}")
        relative = crop["path"]
        require(relative.startswith("detail_crops/") and relative.endswith(".png"),
                "Crop paths must be PNG files under detail_crops/")
        require(relative.casefold() not in used_paths, f"Duplicate crop path: {relative}")
        bbox = crop.get("bbox")
        require(isinstance(bbox, list) and len(bbox) == 4 and all(finite_number(v) for v in bbox),
                f"Invalid normalized crop bbox: {crop_id}")
        x, y, width, height = bbox
        require(x >= 0 and y >= 0 and width > 0 and height > 0
                and x + width <= 1 + 1e-9 and y + height <= 1 + 1e-9,
                f"Crop bbox outside source: {crop_id}")
        string_array(crop.get("feature_ids"), f"{crop_id}.feature_ids")
        require(len(set(crop["feature_ids"])) == len(crop["feature_ids"])
                and all(fid in inventory for fid in crop["feature_ids"]), f"Invalid crop feature links: {crop_id}")
        path = local_file(root, relative)
        png_dimensions(path.read_bytes(), relative)
        paths[relative] = path
        used_paths.add(relative.casefold())
        crops[crop_id] = crop
    for fid, (cid, feature) in inventory.items():
        for field in ("detail_spec", "measurement_note"):
            require(isinstance(feature.get(field), str) and feature[field].strip(), f"{fid} needs {field}")
        source = feature.get("design_source")
        require(isinstance(source, dict) and source.get("kind") in ("reference", "concept", "decision"),
                f"Invalid design_source for {fid}")
        for field in ("source_id", "region", "reason"):
            require(isinstance(source.get(field), str) and source[field].strip(), f"{fid}.design_source needs {field}")
        kind, source_id = source["kind"], source["source_id"]
        if kind == "reference":
            require(source_id in references and "decision_id" in source and source["decision_id"] is None,
                    f"Invalid reference design source for {fid}")
        else:
            decision_id = source.get("decision_id")
            require(isinstance(decision_id, str) and decision_id in decisions,
                    f"Selected design decision missing for {fid}")
            decision = decisions[decision_id]
            require(decision["status"] == "selected" and cid in decision["component_ids"],
                    f"Design decision is not selected for component {cid}")
            require(source_id == ("concept_sheet" if kind == "concept" else decision_id),
                    f"Design source/decision mismatch for {fid}")
        measurements = feature.get("measurements")
        require(isinstance(measurements, list), f"{fid}.measurements must be an array")
        for measurement in measurements:
            require(isinstance(measurement, dict), f"Invalid measurement on {fid}")
            for field in ("name", "unit", "frame", "datum"):
                require(isinstance(measurement.get(field), str) and measurement[field].strip(),
                        f"{fid} measurement needs {field}")
            target = measurement.get("target")
            require(finite_number(target) or (isinstance(target, list) and len(target) == 2
                    and all(finite_number(v) for v in target) and target[0] <= target[1]),
                    f"Invalid measurement target on {fid}")
            require(measurement.get("basis") in ("user", "estimated", "design_choice")
                    and finite_number(measurement.get("tolerance")) and measurement["tolerance"] >= 0,
                    f"Invalid measurement basis/tolerance on {fid}")
        links = feature.get("comparison_crop_ids")
        require(isinstance(links, list) and all(isinstance(v, str) for v in links), f"{fid} needs comparison_crop_ids")
        require(len(set(links)) == len(links), f"Duplicate comparison crops on {fid}")
        if feature["required"]:
            require(links, f"Required feature {fid} needs comparison crops")
        require(all(c in crops and fid in crops[c]["feature_ids"] for c in links),
                f"Invalid comparison crop links on {fid}")
        if links and kind in ("reference", "concept"):
            require(any(crops[c]["source_id"] == source_id for c in links),
                    f"Comparison crops do not include selected design source for {fid}")
    for crop_id, crop in crops.items():
        require(all(crop_id in inventory[fid][1]["comparison_crop_ids"] for fid in crop["feature_ids"]),
                f"Crop/feature links must be bidirectional: {crop_id}")
    return crops


def feature_inventory(analysis):
    """Check traceability structure, not whether geometry actually matches pixels."""
    axes = analysis["coordinate_system"]
    require(isinstance(axes, dict) and all(isinstance(axes.get(k), str) and axes[k].strip()
            for k in ("up", "front", "subject_right", "reference_view_mapping")),
            "Coordinate system needs axes and reference-view handedness mapping")
    components = {v["id"] for v in analysis["components"]}
    material_ids = {v["id"] for v in analysis["materials"]}
    inventory = {}
    for component in analysis["components"]:
        cid = component["id"]
        require("parent_id" in component and (component["parent_id"] is None
                or component["parent_id"] in components and component["parent_id"] != cid),
                f"Invalid parent for {cid}")
        assigned = component.get("material_ids")
        require(isinstance(assigned, list) and all(v in material_ids for v in assigned),
                f"Unknown material assignment on {cid}")
        features = component.get("features")
        require(isinstance(features, list) and features, f"Missing feature inventory for {cid}")
        for feature in features:
            require(isinstance(feature, dict), f"Invalid feature record on {cid}")
            for field in ("id", "description", "source_region", "construction", "allowed_simplification"):
                require(isinstance(feature.get(field), str) and feature[field].strip(),
                        f"Feature on {cid} needs {field}")
            fid = feature["id"]
            require(fid not in inventory, f"Duplicate feature ID: {fid}")
            require(feature.get("evidence") in ("observed", "inferred", "proposed"),
                    f"Invalid evidence on {fid}")
            require(feature.get("representation") in ("geometry", "material", "texture", "both"),
                    f"Invalid representation on {fid}")
            require(type(feature.get("required")) is bool and type(feature.get("must_preserve")) is bool,
                    f"Feature flags must be booleans: {fid}")
            require(not feature["must_preserve"] or feature["required"],
                    f"Must-preserve feature must be required: {fid}")
            string_array(feature.get("inspection_views"), f"{fid}.inspection_views")
            string_array(feature.get("acceptance"), f"{fid}.acceptance")
            inventory[fid] = (cid, feature)
    require(any(feature["required"] for _, feature in inventory.values()), "No required features declared")
    for material in analysis["materials"]:
        plan = material.get("texture_plan")
        require((isinstance(plan, str) and plan.strip()) or (isinstance(plan, dict) and plan),
                f"Missing texture plan for {material['id']}")
        string_array(material.get("inspection_criteria"), f"{material['id']}.inspection_criteria")
    decisions = analysis["decisions"]
    require(isinstance(decisions, list), "Decisions must be an array")
    seen = set()
    for decision in decisions:
        require(isinstance(decision, dict), "Invalid decision record")
        for field in ("id", "issue", "rationale", "impact", "revisit_when"):
            require(isinstance(decision.get(field), str) and decision[field].strip(),
                    f"Decision needs {field}")
        require(decision["id"] not in seen, "Duplicate decision ID")
        seen.add(decision["id"])
        string_array(decision.get("component_ids"), "decision.component_ids")
        require(all(cid in components for cid in decision["component_ids"]), "Decision references unknown component")
        require(isinstance(decision.get("alternatives"), list), "Decision alternatives must be an array")
        require(decision.get("status") in ("selected", "unresolved")
                and type(decision.get("locked")) is bool, "Invalid decision status/lock")
        if decision["status"] == "selected":
            require(isinstance(decision.get("selected"), str) and decision["selected"].strip(),
                    "Selected decision needs its chosen interpretation")
        else:
            require(not decision["locked"], "An unresolved decision cannot be locked")
    return inventory


def png_dimensions(data, label="concept_sheet.png"):
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"{label} is not encoded as PNG")
    offset, dims, idat, ended = 8, None, False, False
    while offset + 12 <= len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        end = offset + 12 + size
        require(end <= len(data), "Truncated PNG chunk")
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + size]
        crc = struct.unpack_from(">I", data, offset + 8 + size)[0]
        require(zlib.crc32(kind + body) & 0xffffffff == crc, "PNG chunk checksum mismatch")
        if kind == b"IHDR":
            require(offset == 8 and size == 13 and dims is None, "Invalid PNG header")
            dims = struct.unpack_from(">II", body)
            require(all(dims), "PNG dimensions must be positive")
        elif kind == b"IDAT":
            idat = idat or bool(size)
        elif kind == b"IEND":
            require(size == 0, "Invalid PNG end chunk")
            ended = True
            offset = end
            break
        offset = end
    require(dims and idat and ended and offset == len(data), "Incomplete PNG or trailing data")
    return list(dims)


def validate_project(root):
    paths = {name: local_file(root, name) for name in FILES}
    analysis = read_json(paths["analysis.json"])
    require(analysis.get("schema_version") == 3,
            "Analysis schema version 3 required; re-inspect and migrate version 1/2 in a new project, then reapprove QA")
    require(all(k in analysis for k in ANALYSIS_FIELDS), "analysis.json lacks required handoff fields")
    validate_scope(analysis["scope"])
    name = analysis["name"]
    require(isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
            and len(name) <= 64, "name must be an ASCII lowercase hyphen slug, at most 64 characters")
    require(analysis["status"] == "concept_ready", "Concept is not ready for prompt packaging")
    qa = analysis["concept_qa"]
    require(isinstance(qa, dict) and qa.get("approved") is True
            and qa.get("report") == "concept_qa.md", "Concept visual QA has not been approved")
    unresolved = qa.get("unresolved")
    require(isinstance(unresolved, list), "Concept QA needs an unresolved array")
    for issue in unresolved:
        require(isinstance(issue, dict) and issue.get("severity") == "advisory"
                and all(isinstance(issue.get(k), str) and issue[k].strip()
                        for k in ("id", "finding", "resolution")),
                "Approved concept cannot contain unresolved blocking or undocumented QA issues")
    require(analysis["concept_sheet"] == "concept_sheet.png", "Concept sheet path must be concept_sheet.png")
    require(isinstance(analysis["components"], list) and analysis["components"], "Component inventory is empty")
    require(isinstance(analysis["materials"], list) and analysis["materials"], "Material inventory is empty")
    for key in ("components", "materials"):
        items = analysis[key]
        require(all(isinstance(v, dict) and isinstance(v.get("id"), str) and v["id"] for v in items),
                f"{key} entries need nonempty IDs")
        require(len({v["id"] for v in items}) == len(items), f"Duplicate IDs in {key}")
    inventory = feature_inventory(analysis)
    refs = analysis["references"]
    require(isinstance(refs, list) and refs, "Reference inventory is empty")
    require(all(isinstance(v, dict) and v.get("role") in ("primary", "supporting") for v in refs),
            "Every reference needs a primary/supporting role")
    require(sum(v["role"] == "primary" for v in refs) == 1, "Exactly one primary reference is required")
    require(all(isinstance(v.get("id"), str) and v["id"] for v in refs)
            and len({v["id"] for v in refs}) == len(refs), "Reference IDs must be nonempty and unique")
    for ref in refs:
        relative = ref.get("path")
        require(isinstance(relative, str) and relative.startswith("references/"),
                "Reference paths must be inside references/")
        require(relative not in paths, f"Duplicate reference path: {relative}")
        paths[relative] = local_file(root, relative)
    dims = png_dimensions(paths["concept_sheet.png"].read_bytes())
    crops = validate_detail_evidence(analysis, inventory, root, paths)
    for language in ("th", "en"):
        filename = f"model_prompt.{language}.md"
        content = paths[filename].read_text(encoding="utf-8-sig")
        require(not re.search(r"\{\{[^}]*\}\}|\[TODO\b", content, re.I),
                f"Unresolved template slot in {filename}")
        headings = list(re.finditer(r"^## ([0-9]+)\. ([^\r\n]+?)[ \t]*\r?$", content, re.M))
        require([(int(m[1]), m[2]) for m in headings] == list(enumerate(TOPIC_HEADINGS.values(), 1)),
                f"Missing, duplicate or out-of-order topic sections in {filename}")
        for index, heading in enumerate(headings):
            following = re.search(r"^## ", content[heading.end():], re.M)
            end = heading.end() + following.start() if following else len(content)
            require(content[heading.end():end].strip(), f"Empty {heading[2]} section in {filename}")
        for fid, (_, feature) in inventory.items():
            if feature["required"]:
                require(re.search(r"(?<![\w-])" + re.escape(fid) + r"(?![\w-])", content),
                        f"Required feature {fid} is not referenced in {filename}")
        if language == "th":
            require(re.search(r"[\u0e00-\u0e7f]", content), "Thai prompt has no Thai text")
    review = paths["prompt_qa.md"].read_text(encoding="utf-8-sig")
    require(re.search(r"^approved: true\s*$", review, re.M), "Prompt semantic QA has not been approved")
    spec = read_json(paths["build_spec.json"])
    require(spec.get("schema_version") == 3 and spec.get("name") == name
            and spec.get("artifact_type") == "modeling_prompt_package"
            and spec.get("source_analysis") == "analysis.json", "Build specification metadata mismatch")
    validate_scope(spec.get("scope"))
    topics = spec.get("topics")
    require(isinstance(topics, dict) and set(topics) == set(TOPICS), "Build specification needs all seven topics")
    for topic in TOPICS:
        item = topics[topic]
        require(isinstance(item, dict), f"Invalid build specification topic: {topic}")
        for field in ("requirements", "acceptance"):
            values = item.get(field)
            require(isinstance(values, list) and values and all(isinstance(v, str) and v.strip() for v in values),
                    f"{topic}.{field} must be a nonempty string array")
    plans = spec.get("feature_plan")
    require(isinstance(plans, list) and plans, "Build specification needs a feature_plan")
    covered = set()
    for plan in plans:
        require(isinstance(plan, dict) and isinstance(plan.get("feature_id"), str), "Invalid feature plan")
        fid = plan["feature_id"]
        require(fid in inventory, f"Unknown feature in build plan: {fid}")
        require(fid not in covered, f"Duplicate feature plan: {fid}")
        require(plan.get("component_id") == inventory[fid][0], f"Wrong component for feature {fid}")
        for field in ("requirements", "acceptance"):
            string_array(plan.get(field), f"{fid}.{field}")
        comparison = plan.get("comparison")
        require(isinstance(comparison, dict), f"{fid} needs a side-by-side comparison plan")
        for field in ("crop_ids", "model_views", "checks"):
            string_array(comparison.get(field), f"{fid}.comparison.{field}")
        crop_ids = comparison["crop_ids"]
        require(len(set(crop_ids)) == len(crop_ids)
                and all(c in crops and fid in crops[c]["feature_ids"] for c in crop_ids)
                and set(inventory[fid][1]["comparison_crop_ids"]).issubset(crop_ids),
                f"Comparison plan has missing or unrelated crops for {fid}")
        covered.add(fid)
    missing = {fid for fid, (_, feature) in inventory.items() if feature["required"]} - covered
    require(not missing, f"Required features missing from build plan: {', '.join(sorted(missing))}")
    phases = spec.get("phases")
    require(isinstance(phases, dict) and set(phases) == {"mesh_details", "materials_textures"},
            "Build specification needs mesh_details and materials_textures phases")
    for phase, gates in phases.items():
        require(isinstance(gates, dict), f"Invalid phase: {phase}")
        for field in ("entry_criteria", "exit_criteria"):
            string_array(gates.get(field), f"{phase}.{field}")
    string_array(spec.get("outputs"), "outputs")
    return name, paths, dims


def package(project, output_dir):
    root = Path(project).resolve(strict=True)
    require(root.is_dir(), "Project must be a directory")
    name, paths, dims = validate_project(root)
    # Freeze the selected bytes so manifest hashes match exactly what enters the ZIP.
    payload = {rel: path.read_bytes() for rel, path in paths.items()}
    manifest = {
        "schema_version": 3, "name": name, "artifact_type": "modeling_prompt_package",
        "contains_finished_model": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "concept_sheet_dimensions": dims,
        "validation_scope": "Structural integrity; visual and semantic QA are recorded by the author.",
        "files": [{"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                  for rel, data in sorted(payload.items())],
    }
    payload["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    destination_dir = Path(output_dir).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{name}_artifact.zip"
    require(not destination.exists(), f"Archive already exists; choose another output directory: {destination}")
    # Create a temporary complete archive, then publish without replacing existing files.
    with tempfile.TemporaryDirectory(prefix="modeling-package-") as temporary:
        staged = Path(temporary) / "artifact.zip"
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for rel, data in sorted(payload.items()):
                archive.writestr(f"{name}/{rel}", data)
        with zipfile.ZipFile(staged) as archive:
            require(archive.testzip() is None, "ZIP integrity validation failed")
            for entry in manifest["files"]:
                data = archive.read(f"{name}/{entry['path']}")
                require(hashlib.sha256(data).hexdigest() == entry["sha256"], "Archive hash mismatch")
        created = False
        try:
            with destination.open("xb") as target:
                created = True
                target.write(staged.read_bytes())
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        output = package(args.project, args.output_dir)
    except (OSError, ValueError, TypeError, KeyError, struct.error, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
