# Detail inventory, design authority and close-up evidence

## Select a source for each aspect

Primary reference normally controls identity, main components and palette. Selected concept close-ups may control fine construction when the primary is indistinct. User requirements/selected decisions control intended pose, symmetry, dimensions and hidden surfaces. This is an aspect-specific design agreement, not a claim that generated detail was observed in the original.

For each feature choose a design_source: reference region, concept panel or selected decision. Explain why it controls this feature. If a concept changes clear primary identity, resolve that conflict before selecting it. Once a concept detail is selected, its required shapes are binding; the executor must not omit them merely because it is a generated construction aid. Keep source evidence labels separate. Never claim the user approved a choice unless they did.

## Write affirmative inventories

Describe what to build before stating exclusions. An inventory entry needs location, count or justified count uncertainty, silhouette/profile, relationship to adjacent parts, representation and a check. Replace “detailed armor” with specified ridges, folds, layered boundaries or attachment forms that actually appear in the chosen design.

Example only, not a default mechanical recipe: “One raised central ridge on the outer plate; two sloping faces meet at the ridge; a clip straddles the upper seam; a V-shaped orange mask follows the centerline on the cream surface.” Ridge/clip are geometry; a flat color V is a mask. Adopt such details only when selected sources support them. Organic, cloth and architectural subjects need their own feature vocabulary.

Do not manufacture a panel count or bolt pattern to make prose longer. Resolve an unclear detail as a labeled selected design if needed. Keep layer order explicit, e.g. outer rim → groove → inner lip → cavity wall; dimensions must identify the surfaces being measured.

## Numeric targets and reference frames

Use numbers/ranges where they affect construction: aperture depth, seam width, plate thickness, taper ratio, feature placement, repeat spacing or texture coverage. Label each target user/estimated/design_choice and define units, frame, datum and acceptance tolerance. Unknown real scale stays unknown. Do not turn a rough image ratio into a claimed measured dimension.

For “center at z=0”, specify the object-local origin at the body center; world floor z=0 is a different frame. For a stance span, specify which feet, which axis and which neutral/final pose. For depth specify start/end surfaces and direction. For wear coverage define the inspected surface region and mask/coverage interpretation. Avoid arbitrary percentages where evidence is insufficient; choose a labeled target or explain why a qualitative check suffices.

Define pose intent separately from structure: neutral construction, final stance and view projection. If bilateral and front/back symmetry are requested, name both body-local planes and matched point sets explicitly. Do not silently restore an asymmetric source pose after the user selected a symmetric concept stance.

## Crop package

Save faithful source-pixel crops as PNG under detail_crops/. Follow active image-tool rules. Do not regenerate/enhance missing details or label AI enlargement as source evidence. Prefer original-resolution crops; zooming changes display size, not evidence. Keep labels and explanations in details.md/JSON so they do not cover pixels.

Each crop record has id, path, source_id (reference ID or reserved concept_sheet), bbox ([x,y,width,height], normalized to the unmodified source, top-left origin), feature_ids and caption. Captions state what to inspect and whether pixels come from a source reference or generated concept. Keep originals and the full sheet. If a selected detail needs both primary and concept context, include both crops with separate IDs. Never register a concept crop as independent supporting evidence.

Cover every required feature with at least one declared comparison crop. For a selected concept/reference source, at least one crop must come from that source. An inferred feature may use a selected concept depiction or the related source area with an explicit not-visible limitation and a written decision; its dimensional/symmetry checks still apply. If extraction cannot be completed, preserve drafts and report the missing crop step before packaging.

## Close-up acceptance handoff

For each feature specify which crop, which model view, which dimensional/shape/surface checks and what is allowed to differ. During Phase A the executor must save side-by-side source/design-crop versus neutral model close-up comparisons for required mesh details. Phase B repeats comparisons for material/texture features. Match visible orientation and image scale where practical, add views for occluded details and label diagnostic reposing. Never change geometry only to make one comparison pass.

Every required feature must be inspectable in at least one comparison, or explicitly not_verified. The executor runs at least one complete detailed review, lists missing/wrong features, repairs any failures and repeats affected checks before advancing. Passing on the first review is valid; arbitrary edits solely to reach a repair count are not required. Record rounds and changes in verification.md.
