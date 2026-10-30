---
name: concept-to-model-prompt
description: Create a compact Blender prompt ZIP with one main prompt, a front/top/side overview reference, and newly generated part references paired with modeling prompts. Authors instructions without building the model.
---

# Concept to Model Prompt

Deliver `<name>_artifact.zip` with only `main_prompt.md` and `parts/<part-id>/prompt.md` plus the images each part uses. Keep global decisions in main and local construction detail beside its reference. Do not duplicate the analysis into several operational documents.

## Inputs and scope

Use inspected primary/concept images and the selected design decisions from `reference-to-concept`, or equivalent supplied evidence. With only a primary image, use that skill when concept development is needed. Generate missing construction views from the supplied references, label unseen surfaces as inferred, and inspect the results. Never present generated views as original observations or claim an unreviewed image is approved.

Existing analysis, detail inventories and QA are authoring evidence, not required runtime files. Read them selectively to recover required features and resolve conflicts. Keep originals and working documents outside the shipped package; do not delete previous work.

Default to static editable geometry, detailed materials/textures and diagnostic views. Exclude decorative staging, pedestals, HDRI and hero renders unless requested. Retain environments when they are the subject. Preserve explicit pose, tool and output constraints from the handoff or user.

## Reference images

- **Image 1 is the overview:** `parts/00-overview/reference.png` shows the complete assembled subject in three clearly labeled orthographic views, **FRONT, TOP, SIDE**, in that reading order. Keep the same design, pose, scale and orientation across views; state whether SIDE is left or right. Keep the subject fully visible on a plain background. Reuse an existing image only if its actual pixels meet this layout; otherwise generate a new reference-conditioned image.
- **Separate parts require new images:** when a source image or sheet contains multiple parts, generate a new focused reference image for each meaningful part, using the inspected full source and approved overview as conditioning. Do not crop, slice, mask out, enlarge or reuse a cut panel as the delivered part reference. Show the complete part, its attachment interfaces and enough views to define its shape; omit unrelated parts. A matched repeated family may share one reference with explicit differences.
- Save the generated output under that part's `reference.png`, inspect it against the source and overview, and pair it with the part's modeling `prompt.md`. Add another newly generated image only when a required detail needs it. Preserve identity, proportions, handedness, materials and selected decisions; identify generated/inferred details in the prompt.
- Use an available image generator with actual reference inputs; follow its skill/tool instructions. In Codex prefer built-in imagegen. Inspect local input images before generation. Do not silently switch to a paid service. If generation or saving is unavailable, preserve drafts and report the missing capability; do not substitute crops or claim the final package is ready.

Source crops from an earlier analysis stage may remain working evidence. They are not deliverable reference images for this package. PNG encoding conversion is allowed; it does not replace required image generation.

## Workflow

1. Read [references/input-contract.md](references/input-contract.md). Inspect source pixels and resolve source authority, pose, orientation and global proportions. Unresolved identity or required-detail conflicts block final packaging.
2. Group features into meaningful modeling parts, not one file per tiny feature. Prepare Image 1 in `00-overview` with FRONT/TOP/SIDE views, then generate focused part images under the Reference images rules above. Use stable component/feature IDs from existing evidence; introduce them only where absent.
3. Use [references/seven-topics.md](references/seven-topics.md) as an authoring checklist, not seven duplicated sections in every prompt. Assign each requirement one home: shared constraints and gates in main, local shape/material/acceptance in its part. Preserve required features, selected interpretations, symmetry, interfaces, measurements and allowed simplifications.
4. Write `main_prompt.md` from [assets/model-prompt.template.md](assets/model-prompt.template.md): brief, scope, axes/scale/pose, global decisions, ordered part index, dependencies, phase gates and outputs. Each index row links its part prompt and says when to load it. Main must not repeat the detailed feature inventory.
5. Write each `parts/<part-id>/prompt.md` from [assets/part-prompt.template.md](assets/part-prompt.template.md). Link its `reference.png` first, followed only by necessary supplementary images. Identify source versus generated provenance, view directions, selected design targets and uncertainty. Describe concrete geometry, attachment interfaces, materials/textures and observable checks beside the relevant image. Shared interfaces belong to one owner; dependent parts link to that owner and state only their connection requirement.
6. Use one operational language, English by default or the user's requested language. Do not generate duplicate translations, `build_spec.json`, usage, QA or handoff files for the ZIP. Keep necessary decisions inside the main/part prompts, never as dependencies on excluded working files.
7. Review coverage against the source inventory before packaging: every required feature has an owning part, usable reference and acceptance check; dependencies and interfaces agree; no unresolved slots or inaccessible paths. Inspect actual pixels: Image 1 really contains FRONT/TOP/SIDE, part references are newly generated rather than cut panels, and their shape/joins agree with the overview. Repair conflicting generated views before delivery. Review is the author's responsibility; the packager checks structure, not view content, generation provenance or fidelity.
8. Run the packager, fix errors and inspect the ZIP listing. Return the actual archive path and `main_prompt.md` entry point. Do not execute the modeling prompt implicitly.

## Context use during modeling

Main instructs the executor to read main plus overview first, then only the active part and its necessary dependencies. Revisit a part for its material pass or verification. Track completed/failed/pending part and feature IDs in the model output's existing verification report so unloading detail does not drop work. After a context reset, reload main, that progress record and the active part. Completion still requires all indexed parts to pass.

## Packaging

Python 3.10+, standard library only:

```text
python "<this-skill>/scripts/package_artifact.py" --project "<project-directory>" --output-dir "<output-directory>"
```

Use an ASCII lowercase hyphen slug for the project directory, or supply `--name <slug>`. The ZIP contains one named root and only linked main/part prompts and part PNGs. The tool checks paths, links, nonempty sections, PNG containers and ZIP byte integrity without adding a manifest or replacing an existing archive. Existing broad packages must be distilled into this layout before repackaging; changing a version number is not conversion.
