---
name: reference-to-concept
description: Analyze primary reference images into a detailed concept_sheet.png, component and mesh-feature specifications, material and texture plans, and a structured handoff for 3D modeling.
---

# Reference to Concept

Turn a primary reference into a subject-neutral specification for detailed editable geometry, materials and textures. Support characters, creatures, products, props, vehicles, architecture and environments without imposing mechanical anatomy.

## Inputs and scope

- Inspect actual reference pixels. One image is primary by default; with ambiguous multiple images, resolve which controls identity.
- Optional inputs: name, supporting references, intended use, dimensions, requested changes, detail budget and output directory.
- Default: static editable geometry with detailed materials/textures; physical scale unknown; no invented exact polygon budget. Pivots do not imply a rig.
- Exclude decorative scenes, display pedestals, key/fill/rim setups, HDRI, hero cameras and cinematic/beauty renders. Keep source-subject environments when the environment itself is the requested asset. Standard viewport illumination and diagnostic views are permitted.
- Write artifacts under `<chosen-output>/<slug>/`, never inside the skill. Preserve the display name; use a lowercase ASCII slug for files.
- If the primary image is missing, request it rather than substituting a previous example.

## Workflow

1. Read [references/analysis-contract.md](references/analysis-contract.md). Inspect each image and copy available originals into project `references/`; record primary/supporting roles. Verify actual saved paths.
2. Analyze silhouette, proportions, cross-sections, negative spaces, pose, component hierarchy, attachments and surface appearance. Inspect close-up regions of the primary for identity-critical parts. Decompose complex components into meaningful children; give every required feature a stable ID.
3. Separate source evidence from selected construction decisions. Resolve hidden geometry conservatively but specify its shape, transitions and attachment interfaces. Record what is locked, editable or unresolved. Check image-left/right, subject-left/right and coordinate conventions together. Analyze structural symmetry separately from pose and perspective: define matched pairs/repeated families, symmetry plane/axis, shared dimensions and mirrored attachment locations. For intended matching limbs use symmetric neutral construction by default, with source-supported or user-requested exceptions recorded explicitly. Make symmetry an inspectable required feature.
4. Read [references/detail-evidence.md](references/detail-evidence.md). Write `analysis.json`, `analysis.md` and a draft `details.md` with an affirmative detail inventory: what must exist, where, how many when supported, shape/layer relationships, material versus mesh treatment, and measurable acceptance. Select sources per feature/aspect rather than applying one image priority to every detail. Drafts may leave concept selections pending until the sheet exists.
5. Read [references/concept-sheet.md](references/concept-sheet.md). Write `concept_sheet_prompt.md`, then generate a reference-conditioned sheet using an available image generator. In Codex prefer built-in imagegen and follow its input rules; never silently switch to a paid service.
6. Save the actual generated output as `concept_sheet.png` and inspect the saved pixels. Convert encoding if necessary; copying or conversion cannot substitute for image editing. Do not use the original image or a placeholder as a completed generated sheet.
7. Compare each relevant panel against source features, IDs, selected decisions and material zones. Resolve cross-view conflicts explicitly. Make at most two targeted repair generations per run; if critical details remain unusable, retain `concept_needs_revision` and report the precise blocker.
8. Select usable concept detail panels as binding design targets where appropriate, record their decisions and finalize feature design_source records. Extract and inspect source-pixel crops from the originals and selected concept panels under `detail_crops/`; map each required feature to its comparison crops. Finalize `details.md`, `concept_qa.md`, `handoff.md` and JSON. Approve only when sources, crops and selected decisions support required features without unresolved blockers. Selection does not make generated details observed facts. A nonorthographic panel is advisory only when labeled and not needed for tracing.
9. Continue with `concept-to-model-prompt` only when the user requested the chain; otherwise return the sheet, readiness and file paths. This skill does not automatically build a 3D model.

## Working evidence and handoff

The files below are authoring evidence. When continuing to `concept-to-model-prompt`, distill them into `main_prompt.md` and `parts/<part-id>/prompt.md` with the needed reference images. Keep the analysis and generation history in the working project; do not include them in the final prompt ZIP or require the modeling executor to read them. Preserve feature IDs, source authority and selected decisions in the owning part prompts.

The downstream prompt package requires a FRONT/TOP/SIDE overview as Image 1 and newly generated focused references when separating parts from a multi-part image. Analytical crops produced here remain working evidence; do not reuse those crops as the delivered part references.

Required: `references/<original-images>`, declared `detail_crops/*.png`, `analysis.json`, `analysis.md`, `concept_sheet.png`, `concept_sheet_prompt.md`, `details.md`, `concept_qa.md`, `handoff.md`.

`details.md` is the component/feature construction and acceptance specification, including material/texture assignments and intentional simplifications. `analysis.md` explains source evidence and uncertainties; keep both synchronized with JSON.

If image generation or saving is unavailable, preserve analysis and the generation brief, set `blocked_image_generation`, and explain the unavailable capability. Do not claim a complete handoff.

Example: `Use $reference-to-concept with this image. Name: forest-lantern. Preserve its shape and distinctive details; prepare mesh, material and texture specifications without presentation staging.`

