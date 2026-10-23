# Version 3 handoff and artifact contract

Read the actual content, not only file existence. The authoritative analysis schema is in the first skill's references/analysis-contract.md; integration requirements are summarized here for independent validation.

## Analysis input

Required fields: schema_version=3, name, display_name, status=concept_ready, scope, subject, references, detail_crops, constraints, scale, coordinate_system, proportions, components, materials, view_plan, unknowns, decisions, concept_sheet="concept_sheet.png", concept_qa.

Scope is exactly `{"mesh": true, "materials": true, "textures": true, "presentation": false}`. Exactly one primary reference exists under references/. Concept QA is approved, links concept_qa.md, and has no unresolved blocking items. Unresolved records have id, severity (blocking/advisory), finding and resolution.

Components retain stable IDs, names, categories, parent/count, source/evidence/confidence, shape/proportions, connections, material IDs, details, symmetry, priority and inspection criteria. Each has nonempty features with globally unique IDs, description, evidence, source_region, representation (geometry/material/texture/both), required, must_preserve, construction, allowed_simplification, inspection_views and acceptance. Must-preserve implies required. Unknown count is not zero.

Material records include IDs, component links, appearance/color/surface response, evidence/confidence, texture_plan and inspection_criteria. The texture plan explains source-supported features, scale, mapping/UV approach and appropriate channels. A simple material is valid where the reference supports one.

Coordinate_system has up, front, subject_right and reference_view_mapping strings; the latter maps asymmetric features into the reference image. Explain a subject-relative N/A for a rotationally symmetric object.

Decisions contain id, component_ids, issue, alternatives, selected, rationale, status (selected/unresolved), locked, impact and revisit_when. Selected design decisions are separate from evidence certainty; lock status never implies user approval unless the user gave it. Preserve locked choices unless a higher-priority conflict is resolved and documented.

Require a construction/acceptance plan for observed secondary details, not only primary mass/counts. Conservative hidden geometry remains coherent and editable. View conflicts must have a written selected resolution or block readiness.

For applicable symmetry groups, the component's symmetry record specifies mode, plane/axis, members, shared dimensions, attachment rule, pose policy, exceptions and checks. Carry a required symmetry feature for each group into feature_plan and both prompts. Validate paired geometry and mounts in neutral asset-local coordinates separately from final pose. Distinguish front/rear families and unique tools; do not confuse perspective differences with structural asymmetry. The required-feature coverage mechanism tracks these symmetry checks alongside detail comparisons.

## Detail authority, measurements and crops

Every feature also has detail_spec, design_source, measurements, measurement_note and comparison_crop_ids. Detail_spec affirmatively states location, count or uncertainty, shape/layers and relationships. Design_source is `{kind, source_id, region, reason, decision_id}`: reference uses a declared reference ID with decision_id null; concept uses source_id `concept_sheet` and a selected decision; decision uses its selected ID in both fields. The decision must include the feature's component. Selected concept panels are binding for assigned details, independently of evidence certainty. Resolve clear identity conflicts before selecting them.

Measurements contain `{name, target, unit, frame, datum, basis, tolerance}`. Target is a finite number or ordered numeric pair; tolerance is finite and nonnegative; basis is user/estimated/design_choice. Explain coordinate origins/endpoints (body-local center differs from world floor), target pose and uncertainty. An empty measurements array requires a meaningful measurement_note explaining why numeric targets are not applicable; all features carry this note.

Detail_crops is a nonempty array of `{id, path, source_id, bbox, feature_ids, caption}`. Paths are unique PNGs under detail_crops/. Source_id names an original reference or reserved concept_sheet; bbox is normalized [x,y,width,height], top-left origin, within that source. Captions explain provenance/inspection. These are faithful extracted pixels, not regenerated or enhanced evidence. Required features link nonempty comparison_crop_ids; crop/feature links are bidirectional. For reference/concept design targets, at least one linked crop must come from the selected source.

## Build specification

Write:
- schema_version: 3
- name: same slug as analysis
- artifact_type: modeling_prompt_package
- source_analysis: analysis.json
- scope: same fixed scope as analysis
- topics: exactly the seven keys below, each with nonempty requirements and acceptance string arrays
- feature_plan: one record per required source feature, with feature_id, component_id, nonempty requirements and acceptance string arrays, and comparison `{crop_ids, model_views, checks}` (all nonempty string arrays). Include all assigned feature comparison crops; preserve required features and do not add untracked IDs. Optional features may be included when documented with comparison crops.
- phases: `mesh_details` and `materials_textures`, each with nonempty entry_criteria and exit_criteria string arrays. Phase A includes a full close-up review; Phase B requires Phase A pass. Plan review/repair/recheck, not a mandatory edit when no defect exists.
- outputs: nonempty string array of future deliverables.

| Key | Exact numbered prompt heading |
|---|---|
| geometry_proportions | ## 1. GEOMETRY & PROPORTIONS |
| reference_fidelity | ## 2. REFERENCE FIDELITY & DESIGN DECISIONS |
| components_mesh_details | ## 3. COMPONENTS & MESH DETAILS |
| topology_assembly | ## 4. TOPOLOGY & ASSEMBLY QUALITY |
| materials_textures | ## 5. MATERIALS & TEXTURES |
| modeling_progression | ## 6. MODELING PROGRESSION |
| verification_delivery | ## 7. VERIFICATION & DELIVERY |

Prompts use these anchors in both languages, mention feature IDs beside their instructions and carry all operational decisions. Headings do not dictate stage order: mesh/detail gates pass before detailed material/texture work.

Future deliverables include editable .blend checkpoints/final, used textures or packed images, diagnostic images, side-by-side detail comparisons and verification.md with review rounds, missing/wrong features and repairs. Each required feature must be visible in at least one comparison or recorded not_verified. Do not require hero renders or staged scenes. Additional export/rig requirements depend on explicit intended use.

## Semantic QA

Review source fidelity, construction detail, representation choices, prototype gate, selected decisions, orientation, complete materials/textures, scope and bilingual parity. Prompt QA starts with `approved: true` only after these pass. Reporting a deviation does not approve it: required omissions remain incomplete unless a predeclared simplification or explicit user scope change covers them.

## Packaging and migration

Fixed files:
analysis.json, analysis.md, concept_sheet.png, concept_sheet_prompt.md, details.md, concept_qa.md, handoff.md, model_prompt.th.md, model_prompt.en.md, build_spec.json, usage.th.md, usage.en.md, prompt_qa.md, plus declared references and detail_crops PNGs.

The packager adds manifest.json. It validates schema/feature coverage, readiness, prompt structure, PNG container and archive hashes; authors inspect images and semantics. The ZIP is a prompt package, not a model delivery.

The version 3 packager rejects version 1/2 with a migration message. Upgrade in a new project/version: re-inspect sources, select detail authorities, enrich inventory/measurements, extract crops, resolve orientation, rewrite prompts/spec/usage and rerun QA. Check stale project-local generators such as author_model_prompts.py before reusing them. Never only edit schema_version or reuse approval from a materially different brief.

