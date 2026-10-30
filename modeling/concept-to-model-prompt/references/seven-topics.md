# Seven topics: detailed mesh, materials and textures

Use these topics as an authoring checklist across the compact package. Main owns global scope, axes, pose, part order, phase gates and outputs; each part owns its reference authority, geometry, interfaces, materials and checks. Do not duplicate all seven sections in main and every part.

Ground instructions in component/feature/material IDs. Lead with an affirmative inventory of what must be built; exclusions support that specification rather than replacing it. Every required feature needs its selected design source, detail_spec, construction plan, selected part reference images and observable checks. Adapt vocabulary to the subject; do not impose mechanical parts on anatomy, cloth or architecture.

## Scope preamble

State actual paths, intended use, source precedence, selected decisions, scale and orientation. Default to static editable mesh with detailed materials/textures; pivots alone are not a rig. Preserve unrelated scene content and settings.

Exclude decorative staging, pedestals, key/fill/rim rigs, HDRI, hero cameras and cinematic/beauty rendering. Standard viewport illumination, plain backgrounds, diagnostic cameras/captures and low-cost inspection renders are allowed only to verify the asset. Do not turn fallback inspection into light/exposure polishing. A requested environment remains geometry in scope.

## 1. GEOMETRY & PROPORTIONS

Specify masses, silhouette, pose, depth, cross-sections, taper, thickness, curvature transitions and negative spaces. Tie ratios to evidence; perspective ratios are guides, not exact dimensions. Separate unknown physical size from working units.

Carry numerical targets/ranges with basis (user/estimated/design_choice), unit, frame, datum and tolerance. Define the endpoints of cavity depth, the plates defining a seam, and the pose/feet defining a stance span. Distinguish a body-centered local z=0 from a world ground z=0. Include justified qualitative checks where measurements add no value rather than inventing numbers.

Map image-left/right, subject-left/right and world axes using asymmetric landmarks. Define inspection directions consistently. Establish origins, hierarchy and editable parameters for uncertain geometry.

Choose suitable hard-surface meshes, sculpt/subdivision, cloth forms, curves or modules. A primitive is a starting tool; it cannot replace distinctive required contours.

Acceptance: primary contours, proportions, pose and spaces match at a comparable view; counts and scale conventions are coherent. Correct major mismatches before secondary work.

### Structural symmetry gate

For every intended matching group declare its asset-local symmetry plane/axis and pair correspondence. Lock shared segment lengths, cross-sections, armor thickness/profile and joint-center relationships. Mirror attachment positions about the body-local plane; use rotational repetition only when the design calls for it. In a four-legged design compare left/right front pairs and left/right rear pairs; do not assume the front and rear families are identical.

Construct and verify a symmetric neutral configuration before posing. Preserve it as an editable checkpoint or recorded rest transforms; this does not require a rig. Explicitly specify final stance separately from neutral construction. Name both body-local planes and corresponding mounts/feet if bilateral and front/back symmetry are selected. User-selected concept stance overrides a different primary pose; do not silently revert to the source spread. Use symmetric stance by default when no distinct pose is required. Pose shared geometry without nonuniform per-limb scaling or arbitrary mount shifts. Resolve contacts through pose/body height while preserving segment lengths; report an incompatible pose rather than stretching limbs.

Acceptance: compare neutral local dimensions, mirrored attachment coordinates, pivot locations and paired contours in front/top views. Record measured deltas and a declared scale-relative tolerance, with intentional exceptions. Perspective screenshots alone cannot pass this gate. A failed required symmetry check blocks detailed surfacing and completion.

## 2. REFERENCE FIDELITY & DESIGN DECISIONS

Rank source-specific identity features and state must-preserve, optional and allowed-simplification rules. Compare secondary contours as well as primary landmarks. Use the newly generated focused part references, reviewed against the original evidence; distinguish viewpoint mismatch from geometry errors.

Write an aspect-specific source table: primary for identity/clear observations, reviewed standalone part references for assigned fine details, and user/selected decisions for pose, symmetry, dimensions and hidden construction. Carry design_source records into the operational text. Concept details remain inferred/proposed but become binding design targets once selected; low-resolution primary imagery is not a reason to omit them. Resolve actual conflicts before execution.

Retain evidence labels independently of selected decisions. Preserve locked interpretations; uncertainty alone does not justify deleting selected hidden detail. Higher-priority contradictions require a recorded revision. Specify coherent unseen shapes rather than making everything flat/round.

Require a verification coverage table: feature ID, source region, expected geometry/surface, implementation, evidence image, status (pass/fail/not_verified/allowed_simplification), correction. A simplification must cite its predeclared allowance or explicit scope change.

Acceptance: every required feature is implemented and checked. Part counts and "same subject" alone do not establish detailed fidelity. Disclosed missing required detail remains a failure.

## 3. COMPONENTS & MESH DETAILS

Expand identity-critical components into meaningful subparts. For each required geometry/both feature specify contour, cross-section, placement, depth/thickness, layers, recess/opening, edge transitions and interfaces as relevant. Link source region and inspection view.

Each detail inventory entry states location, count or chosen count uncertainty, profile, neighboring parts/layer order and measurable or visual acceptance. “Small recesses” is incomplete when the selected panel shows framed openings: specify the frames, placement, depth and count. Quantities and dimensions come from evidence or labeled design choices; never add an arbitrary bolt/panel count as generic detail.

Choose the construction method after reviewing the inventory. A ridged/faceted shell may need a shaped cross-section and separate plates from the start; a smooth loft plus material cannot supply those forms. Procedural construction is valid when its parameters actually represent the required details. Preserve source-supported taper and contour variation explicitly.

Separate material boundaries from physical seams. Model silhouette detail, substantial relief, openings, layered edges and visible supports. Use texture for appropriate small surface features; never substitute wear for missing geometry.

For complex repeated components, build one prototype, compare its close-up against required features and correct it until it passes before replication. Build matching partners using a Mirror modifier, mirrored duplication, linked geometry or shared parametric dimensions with explicit local transforms; choose what suits the asset. Do not independently eyeball/model each matching leg. Keep unique decorations/tools and intentional asymmetry separate. Check normals, winding, bevels and UV/text direction after mirroring. Pose instances independently only under the declared pose policy; recheck copies that change materially.

Acceptance: required features pass before replication or detailed surfacing. No generic cones, spheres or curved sleeves where the source requires distinct shapes. Avoid arbitrary decoration.

## 4. TOPOLOGY & ASSEMBLY QUALITY

Specify use-appropriate editable objects/modifiers, curvature, bevel widths, thickness, anatomical transitions or fitted interfaces. Preserve deliberate overlaps; remove unintended intersections, coplanar faces, floating pieces and gaps.

Inspect local face orientation, shading, normals, degenerates, duplicates, holes and Boolean/subdivision defects. Signed volume alone cannot establish correct local normals; counts/centroids cannot establish absence of duplicates. Use targeted mesh inspection. Do not universally require all-quads or watertightness; distinguish intended open boundaries from defects.

Inspect repeated parts, hidden attachment roots and material-independent clay. Keep known defects in the failure list; invisibility in a shaded image is not a repair.

Acceptance: no unresolved unintended defects affecting required appearance, editability or use. Document intentional boundaries and allowed approximations. Manufacturing/game-specific checks require the corresponding scope.

## 5. MATERIALS & TEXTURES

Keep a full detailed surface stage after mesh gates pass. Map material IDs to feature/component zones. Specify approximate color, roughness, metallic/dielectric interpretation, opacity/transmission and other supported response. Parameter values are starting choices, not measurements.

Define needed channels and painting/procedural methods: base color, roughness, normal/bump, justified displacement, masks, patterns and supported wear/dirt. Specify location, scale, direction, coverage, intensity and boundary behavior. Do not invent scratches, metals or transparency. Shape-changing displacement requires geometry rechecks.

Replace vague “restrained” treatment with region-specific targets, focused reference images and justified scales/ranges or labeled design choices. Define the surface region when describing coverage percentages. For competing goals state which wins and how to check it, e.g. retain the selected emitter hue and readable rim before increasing brightness. Do not introduce an unconditional “brightest pixel” requirement or a presentation exposure loop.

Choose UVs for directional patterns/export; procedural/local mapping can suit other assets. Check seams, stretching, texel density at inspection distance, repeat scale and stability under posing. Do not require a universal texture size or map set.

Retain emissive materials intrinsic to the subject. Check masks/color and adjacent geometry with emission disabled or clay; do not run a lighting/exposure tuning loop. Standard viewport material preview or a basic inspection render can check response without external HDRI setup.

Pack images in the .blend or ship used textures with relative paths. Preserve editable graphs; distinguish baked maps from procedural source materials.

Acceptance: correct zones, supported detail/response, consistent scale, no missing resources/stretching/unintended seams, and geometry passes without materials/emission. Surface quality is its own gate, not compensation for missing mesh detail.

## 6. MODELING PROGRESSION

State two explicit phases in the main prompt. Detailed material work is Phase B and cannot displace unfinished Phase A features. Execute in this order, loading each part's details only when needed:

### Phase A — model and detail
1. Inspect references, selected decisions, required features, existing scene and tools.
2. Block out primary shapes; compare reference and useful orthographic views; correct proportions/pose.
3. Build interfaces and a complete prototype for each complex repeated family. Validate the neutral symmetry construction and mount layout before posing or replication; recheck paired geometry after duplication.
4. Complete required secondary/tertiary mesh features, then replicate with documented differences.
5. Perform at least one complete detailed close-up review: save side-by-side selected part references versus neutral model images, list missing/wrong features, verify symmetry/topology and repair every required failure. Re-capture affected comparisons after repairs. First-pass success needs evidence but no artificial edit. Save the detailed mesh checkpoint only after the Phase A gate passes.

### Phase B — materials, textures and delivery

6. Enter only after Phase A passes. Build detailed materials/textures and compare surface features against selected part references. Geometry-changing displacement or newly discovered mesh defects return to the affected Phase A gate.
7. Verify saved outputs/resources, record review rounds and per-feature results, and save the final editable asset. Delivery images remain diagnostic; no presentation scene or beauty-render phase.

Save useful blockout/detailed/final checkpoints without per-stage human approval. A failed gate returns to its stage before advancement. Tool limitations yield partial/not_verified, never automatic pass. Avoid unchanged failed loops; preserve work and identify the blocker.

Acceptance: record actual corrections and gate results. Do not advance into presentation work or declare completion with required mesh/surface features missing.

## 7. VERIFICATION & DELIVERY

Use plain diagnostic overall views and close-ups: reference-match, front/side/rear/top/underside as useful, same pose and comparable scale. No hero shot. Check clay and material/texture appearance. Wireframe/overlays are useful when they reveal a concern.

Capture actual viewport images; if unavailable use minimal low-cost diagnostic renders without staging/custom light rigs. Resolution must reveal the inspected feature. A tool close-up must resolve the tool, not show it tiny within a whole-subject shot. Unavailable visual checks are not_verified.

Save side-by-side comparison sheets under comparisons/ (or an equivalent declared directory): selected part reference next to an actual model close-up, with feature/part IDs and reference provenance. Use comparable orientation and on-image scale; add views for occluded features and label any diagnostic reposing. All required geometry and surface features must be inspectable across these sheets. A whole-model silhouette overlay cannot replace detail comparisons. Do not change geometry only for one camera. Preserve the reviewed reference images and actual model captures; generating reference images never permits synthesizing a model result.

The verification report lists each review round, absent/incorrect features, fixes and recheck results. Generated part references express reviewed design choices, not newly observed source facts; do not certify detail that neither selected references nor explicit design decisions define.

Deliver editable .blend and useful checkpoints, used texture resources or packed images, diagnostic images and verification.md with paths, methods, coverage, mesh/topology/material gate statuses, inferences and issues. Include a symmetry comparison for applicable groups: members, plane/axis, neutral segment dimensions, mirrored mount/pivot deltas, tolerance, pose differences, explicit exceptions and pass/fail. Keep neutral construction checks separate from final posed views. Exports/rigs depend on explicit scope.

Verify saves, image decoding and resource paths; reopen when supported and state limits. Required failures or unavailable required verification mean partial/needs_revision, not complete. Never replace missing model outputs with concept images.

## Package consistency

Use one operational language unless the user explicitly requests translations. Each required feature has one owning part and matching reference/checks. Main and part prompts must agree on scope, pose, shared interfaces and outputs; no instruction may require excluded authoring files.

