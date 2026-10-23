# Concept sheet for mesh, materials and textures

## Layout

Use the primary to preserve identity and clear observed features, with selected design decisions controlling intended pose, symmetry and detail targets. Choose enough resolution for important details, with a plain background and even descriptive illumination. Do not request decorative scenery, pedestals, dramatic light rigs, HDRI, hero shots or cinematic framing.

Include a reference-matching diagnostic overall view; useful front/side/rear views at consistent pose and scale; top/underside where construction requires them; and close-ups of identity-critical components. Use component and feature IDs. Include palette/material swatches and surface-detail patches when they help specify textures. Avoid shrinking structural details to make room for decorative headings or oversized swatches.

Select close-ups from the feature inventory, not an arbitrary count. Show silhouettes, cross-sections where defensible, layered edges, recesses, attachment interfaces and negative spaces. A source crop is evidence; a generated detail is an interpretation. Do not label a regenerated overall panel as the original reference.

For characters retain defining anatomy and pose; for architecture align orientation and floor heights; for props preserve handle/opening handedness. An environment that is the subject remains in scope; unrelated staging does not.

For matching appendages/modules, include a neutral front/top construction view when useful, with a readable centerline or symmetry-axis indication and matched paired geometry. Label this view separately from posed reference views. Request equal base segment lengths, plate profiles and corresponding mounts; do not bake perspective foreshortening into the design. Label intentional geometric/pose exceptions in sidecar records. Resolve generated paired-part disagreements against the symmetric specification or repair the sheet before using it as a guide.

## Generation brief

Write a resolved brief covering:
1. Purpose and intended asset use, limited to construction and surface specification.
2. Primary/supporting input roles and reference-conditioning mechanism.
3. Identity locks and required feature IDs.
4. Components, subcomponents, counts, relationships, ratios and orientation mapping.
5. Views and close-ups: what each must reveal, matched pose/scale, and which are inferred.
6. Materials/textures: zones, palette, surface response, supported wear or pattern, scale/direction.
7. Selected hidden-geometry decisions and editable uncertainties.
8. Plain layout, readable labels, clear contours and uniform descriptive illumination.
9. Avoid missing details, mirrored asymmetry, inconsistent joins, invented decoration and false dimensions.

Use the image tool's actual reference inputs. Inspect local images first; use paths or recent-image inputs as supported. Never claim conditioning when no image was passed.

## QA and conflict resolution

Inspect saved pixels against the primary and required feature inventory:
- Overall shape/count/pose and asymmetric landmarks.
- Structural and secondary features remain readable, with enough image area.
- Connections, contours and material boundaries agree across views.
- Matching parts have consistent neutral dimensions and mirrored/radial mounts as specified; pose differences do not silently change segment lengths. Compare front/top views and group close-ups, not only a perspective overview.
- View labels reflect the actual projection. An oblique side view is not a tracing elevation.
- Texture patches agree with source-supported appearance and scale.
- Inferred regions are identified; no unsupported measurements.
- No melted joins, essential cropped parts or accidental duplicated subjects.

For each cross-view conflict record the affected IDs, source observation, selected resolution and downstream instruction. Select specific clear close-up panels as binding detail targets where the primary is indistinct; record which features each controls and the associated decision. Detail differences cannot silently become optional. Critical conflicts require repair or a clear written resolution consistent with identity/user constraints; otherwise mark concept_needs_revision. Minor inconsistent scratches can be advisory when their intended treatment is specified.

After selection, extract faithful pixel crops from source references and chosen concept panels as defined in detail-evidence.md. Confirm crop IDs, normalized bounds, source provenance and feature links. Inspect crops at useful display size; they must support later side-by-side detail checking. A crop cannot reveal detail absent from its source.

The sheet and source together must support every required feature. A pretty sheet or complete part count alone is not approval. Record pass/fail/N/A, repairs, remaining limitations and readiness in concept_qa.md and synchronize JSON. Mark approved only with no unresolved blocking items; disclosed hidden surfaces may remain inferred.

