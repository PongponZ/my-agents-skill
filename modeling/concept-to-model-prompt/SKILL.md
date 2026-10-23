---
name: concept-to-model-prompt
description: Convert a reference/concept handoff into detailed Thai and English Blender prompts for mesh fidelity, assembly, materials, textures and verification, then package a named artifact ZIP. Authors instructions rather than directly building the model.
---

# Concept to Model Prompt

Author instructions for detailed editable geometry, materials and textures, and package `<name>_artifact.zip`. This skill does not execute the modeling prompt or promise an already finished model.

## Inputs and scope

Use the version 3 handoff from `reference-to-concept`: primary/supporting images, declared detail crops, `analysis.json`, `analysis.md`, `details.md`, `concept_sheet.png`, `concept_sheet_prompt.md`, `concept_qa.md`, `handoff.md`.

If only a primary image is supplied, run the first skill when available. Normalize equivalent evidence-based handoffs to [references/input-contract.md](references/input-contract.md). Do not fake a missing sheet or silently promote an older handoff by changing its version.

Default to static editable mesh with detailed materials/textures. Exclude decorative staging, pedestals, key/fill/rim rigs, HDRI, hero cameras and cinematic/beauty renders. Retain standard viewport illumination and diagnostic views, including surface inspection. Do not remove environments that are themselves the requested asset.

## Workflow

1. Read [references/input-contract.md](references/input-contract.md), inspect actual primary/concept pixels, and read analysis, details, decisions and QA.
2. Check affirmative detail inventories, per-feature design sources, crop links, measurement frames, selected decisions and orientation mappings. Selected concept close-ups control their assigned details even when primary resolution is insufficient; they remain generated interpretations. Resolve contradictions before writing prompts. Missing detail cannot become an unspecified simplification.
3. Require concept_ready and approved QA with no unresolved blockers before final packaging. For version 1/2 inputs, prepare a new project version, enrich source/feature/measurement records, extract crops and reapprove QA. Check any project-local prompt generator for stale embedded instructions before using it; do not run it blindly or modify an unrelated project implicitly. Preserve existing outputs.
4. Read [references/seven-topics.md](references/seven-topics.md) fully. Translate each required feature into a component-specific construction instruction and observable acceptance. Include a prototype gate for complex repeated components. Carry symmetry groups into required feature plans: shared local geometry, mirrored attachment rules, neutral-pose checks, allowed pose differences and explicit asymmetry exceptions. Do not resize individual legs to imitate perspective.
5. Write self-contained `model_prompt.th.md` and `model_prompt.en.md` using [assets/model-prompt.template.md](assets/model-prompt.template.md). Keep the same seven numbered English anchor headings and equivalent decisions in both languages. Resolve every slot; preserve IDs and paths.
6. Write `build_spec.json` version 3 with scope, seven topics, per-feature comparison plans and explicit Phase A mesh / Phase B materials gates from the input contract. Both prompts must require a full close-up comparison review after detailed mesh, a missing/wrong-feature list, and repair/recheck of failures before Phase B. First-pass success does not require artificial edits.
7. Write `usage.th.md` and `usage.en.md`: input paths, execution in a Blender-capable agent, editable settings, inferences and outputs. Distinguish this prompt archive from future .blend/textures/diagnostic images. Do not execute the prompt implicitly.
8. Review both prompts against source features and each other. Verify geometry versus texture assignments, permitted simplifications, locked decisions, coordinate mapping and concrete pass/fail gates. Write `prompt_qa.md` with `approved: true` only after review passes. The packager cannot certify visual fidelity or bilingual equivalence.
9. Run the packager, fix errors, inspect the ZIP listing and return actual paths. Do not overwrite an existing archive; use a new output directory.

## Packaging

Python 3.10+; standard library only:

```text
python "<this-skill>/scripts/package_artifact.py" --project "<project-directory>" --output-dir "<output-directory>"
```

The ZIP contains one named root, declared references and detail crops, the fixed handoff/prompt files and a SHA-256 manifest. It excludes undeclared images and unrelated workspace files and does not contain a finished model by default.

Example: `Use $concept-to-model-prompt on ./forest-lantern. Create detailed mesh/material/texture prompts in Thai and English and forest-lantern_artifact.zip without presentation staging.`

