# Analysis contract, version 3

Write valid UTF-8 JSON. Paths are project-relative with forward slashes. This contract describes design evidence and construction choices, not a finished model.

## Required top-level fields

| Field | Content |
|---|---|
| schema_version | `3` |
| name / display_name | Lowercase ASCII hyphen slug (at most 64 characters) / user-facing name |
| status | `analysis_ready`, `blocked_image_generation`, `concept_needs_revision`, or `concept_ready` |
| scope | `{"mesh": true, "materials": true, "textures": true, "presentation": false}` |
| subject | Category, style, intended use, pose/configuration and identity summary |
| references | Array of `{id, path, role, description}`; exactly one primary; files under references/ |
| detail_crops | Nonempty array of `{id, path, source_id, bbox, feature_ids, caption}`; faithful PNG crops under detail_crops/, normalized source bbox, linked features |
| constraints | `{must_preserve: [], requested_changes: [], avoid: []}` |
| scale | `{mode: "unknown" or "physical", dimensions: null or object, modeling_scale: string}` |
| coordinate_system | Object with `up`, `front`, `subject_right`, `reference_view_mapping`; values are descriptive strings. Explain conventions and any subject-relative N/A |
| proportions | Relative ratios linked to components, evidence and uncertainty |
| components | Component records below, including child components where useful |
| materials | Material/texture records below |
| view_plan | Diagnostic/reference views and close-ups, linked component/feature IDs, orientation, scale and questions each resolves |
| unknowns | Unobserved or ambiguous details, their impact and associated decision IDs |
| decisions | Decision records below; an empty array is valid when none are needed |
| concept_sheet | `"concept_sheet.png"` when generated, otherwise null |
| concept_qa | `{approved: boolean, report: "concept_qa.md", unresolved: []}` |

Each unresolved QA entry is `{id, severity: "blocking" or "advisory", finding, resolution}`. A blocking entry cannot remain in an approved handoff. Advisory findings need a usable resolution/limitation; do not relabel critical missing geometry as advisory to proceed.

## Components and features

Components retain:
- `id`, `name`, `category`, `parent_id` (null for a root), `count` (integer or null).
- `evidence`: observed/inferred/proposed; `confidence` plus reason; `reference_ids`.
- `shape`: silhouette, cross-section, curvature, thickness, edge transitions and negative spaces.
- `proportions`, `connections`, `material_ids`, `details`, `symmetry`.
- `modeling_priority`: primary/secondary/tertiary; `inspection_criteria`.
- `features`: a nonempty array of feature records below.

Decompose an identity-critical complex component until its contours, layers, openings and connections are individually testable. Use child IDs such as C03A with parent C03. For a simple component one well-specified shape feature can suffice. For repeated complex parts specify a representative prototype, shared features and per-instance differences. Never impose a fixed number of subparts on all subjects.

Every feature has:
- `id`: globally unique, e.g. F_C03_01.
- `description`: location and concrete shape/surface treatment.
- `evidence`: observed/inferred/proposed, distinct from priority or design approval.
- `source_region`: reference ID plus identifiable image location or normalized crop coordinates. For unseen parts state not visible and link the decision.
- `representation`: geometry/material/texture/both. In `both`, identify which effect belongs to mesh and which to shading in `construction`.
- `required`: boolean; `must_preserve`: boolean. Identity-defining features must be required.
- `construction`: cross-section, taper, contour, relief depth, connection or surface method as appropriate.
- `detail_spec`: affirmative location, count/count uncertainty, profile and layer/neighbor relationships; avoid only naming a generic part.
- `design_source`: `{kind: reference/concept/decision, source_id, region, reason, decision_id}`. Reference uses a declared reference ID and decision_id null; concept uses reserved source_id `concept_sheet` plus a selected decision ID; decision uses the same selected decision ID in both source_id and decision_id. Region/reason are nonempty strings. This selects the construction target independently of evidence certainty.
- `measurements`: array of `{name, target, unit, frame, datum, basis, tolerance}`. Target is a finite number or ordered two-number range, tolerance a nonnegative finite number; basis is user/estimated/design_choice. Frame and datum define coordinates/measurement endpoints. Empty array is allowed with `measurement_note` explaining why quantitative targets are not useful. Include measurement_note as a nonempty string in all cases to explain scope/uncertainty.
- `comparison_crop_ids`: crop IDs covering this feature; nonempty for required features. Crop feature_ids and this list must agree.
- `allowed_simplification`: specific permitted reduction, or "none"; no blanket "simplify details".
- `inspection_views`: nonempty view names from view_plan.
- `acceptance`: nonempty array of observable checks.

Use geometry for silhouette changes, significant depth, openings, layered edges and visible interfaces. Small flat wear, pigment, pores or scratches can be texture/normal/bump according to viewing scale and use. Do not hide missing mesh beneath a wear shader. Record approximate ratios/ranges without inventing precision.

For organic subjects use masses, anatomical landmarks, transitions and folds; for cloth use drape, seams and thickness; for architecture use volumes, apertures, supports and modular joins. Do not add bolts, metals, mechanical joints or bevels to every subject.

## Symmetry contract

Expand each component's `symmetry` field into a concrete construction/checking record where relevant: `mode` (bilateral/radial/repeated/none/unknown), `plane_or_axis` in asset-local coordinates, `group_members` (component IDs or named instances), `shared_dimensions`, `attachment_rule`, `pose_policy`, `exceptions`, and `checks`. For none/unknown explain the reason rather than inventing symmetry. Specify neutral construction and final stance separately; explicitly name both planes if bilateral and front/back symmetry are intended.

Distinguish base geometry symmetry, attachment-layout symmetry, and posed/projected appearance. Perspective, occlusion and a bent joint are not evidence that paired segments have different lengths. For intended matching pairs start with equal local segment lengths, cross-sections, armor thickness and corresponding joint centers. Use mirrored mounts about a declared body-local plane. Front and rear families may differ; four legs do not imply fourfold/radial symmetry.

Default uncertain matching limbs to a symmetric neutral construction and record it as a selected inference. Use a symmetric stance when no distinct pose is required; preserve clearly intended poses or user-requested asymmetry without changing shared segment dimensions. Record intentional geometric differences separately (different tools, damage, anatomy, ornament); do not mirror unique parts into identical copies.

Create a required feature for each applicable symmetry group in its owning component, with group IDs, measurable comparisons and diagnostic views. Add a selected decision for inferred layouts or intentional exceptions. Choose a model-scale numerical tolerance for mirrored positions/dimensions; this is a validation tolerance, not a physical measurement or permission for visible drift. `details.md` must state what matches, what may differ and why.

## Material and texture records

Retain `id`, `name`, `component_ids`, `appearance`, `color_description`, `surface_response`, `evidence`, `confidence`.
Add:
- `texture_plan`: source-supported surface features, their locations and scale; maps/channels needed, mapping or UV approach, and seams/directionality to preserve. Explain when a simple material or procedural mapping is sufficient.
- `inspection_criteria`: nonempty observable checks for zones, detail scale, continuity and resources.

Separate painted dielectric appearance from inferred substrate. Screen-sampled color is approximate, not calibrated base color. Parameter ranges are artistic starting decisions. Keep detailed materials and textures, including emission where part of the subject, without prescribing presentation light rigs. Do not invent wear or transparency where unsupported.

## Evidence and selected decisions

Use aspect-specific authority: user constraints and resolved design decisions control the selected result; primary reference controls identity and clear observed features; selected concept panels may control detailed construction where primary evidence is unclear. Record design_source per feature and resolve conflicts before selection. Do not let vague primary imagery silently override a selected concept detail. A generated view never proves hidden anatomy. Read [detail-evidence.md](detail-evidence.md) for selection, measurement and crop rules.

Each decision has `id`, `component_ids`, `issue`, `alternatives`, `selected`, `rationale`, `status` (selected/unresolved), `locked` (boolean), `impact`, `revisit_when`.
A selected locked design remains binding downstream unless user changes or conflicting higher-priority evidence require revision. It remains inferred/proposed, not observed. Routine nonblocking choices may be selected autonomously; user approval must never be fabricated. Blocking unresolved choices prevent readiness.

Specify hidden shapes, cross-sections, transitions, thickness and attachment logic to the extent needed for coherent geometry. "Conservative" means supported and editable, not automatically flat, round or detail-free. Avoid spending effort on elaborate unseen mechanisms without a need.

## Orientation and handoff

Distinguish image-left/right, subject-left/right and world axes. Map asymmetric features to their expected screen positions in the selected reference view. Check front, side and rear direction names against the convention; do not equate Blender's Right view with subject-right without checking.

`details.md` lists each component and feature ID, source region, required construction, representation, simplification limits, materials and acceptance. `handoff.md` includes scope, locked decisions, required feature IDs, view mapping, known limitations and readiness. The concept is a modeling aid, not an engineering blueprint.

Version 1/2 handoffs need an evidence-based upgrade in a new project/version: select detail sources, enrich inventories and measurements, extract comparison crops and redo QA. Do not merely change the version number or reuse old approved QA.

