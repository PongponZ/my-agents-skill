---
name: reference-to-prompt
description: Run the complete reference-image to modeling-prompt workflow through reference-to-concept and concept-to-model-prompt. Use when the user wants one entry point that produces a reviewed concept and a compact main/part prompt ZIP, without building a model.
---

# Reference to Prompt

Coordinate the two stages below in the same task, from the supplied images through the final `<name>_artifact.zip`. Invoking this skill requests the full chain; proceed between stages when their checks pass without asking the user to invoke the next skill.

## Inputs and setup

- Use the supplied primary reference, optional supporting images, asset name, output directory and explicit design constraints. Infer a short descriptive name and use `<workspace>/output/<slug>/` when these are unspecified. Ask for the primary image if it is missing; never substitute an unrelated example.
- Keep one project directory and stable part/feature IDs across stages. Preserve existing files and archives; use a new version directory when a changed brief would overwrite prior work.
- Defaults come from the stage skills: editable static geometry instructions, detailed materials/textures and diagnostic checks. The deliverable is a prompt package; this workflow does not execute Blender or create a finished model.
- Read only the current stage's skill and relevant references. The relative links below resolve the maintained source skills; the installer bundles those same skills under this folder for standalone installation/ZIP use.

## 1. Reference → reviewed concept

Read and follow [reference-to-concept](../reference-to-concept/SKILL.md), resolving its resources relative to that skill's folder.

Pass the user's inputs, project path and constraints to this stage. Include the final reference requirement in the generation brief from the start: the complete assembled subject in labeled **FRONT, TOP, SIDE** views with consistent pose, scale and orientation. Extra concept panels may support analysis, but the final overview must satisfy the second stage's layout.

Inspect the saved concept pixels, resolve design conflicts and complete the stage's feature evidence and visual QA. Proceed only when the concept is ready with no unresolved blocking items. Analytical crops remain working evidence; they do not become delivered part references.

If required image generation or saving is unavailable, preserve the stage's drafts and report the capability needed. Respect the stage's repair limits; do not reset them by repeatedly restarting the skill. A failed QA state is not a completed handoff.

## 2. Reviewed concept → compact prompt ZIP

Once stage 1 passes, read and follow [concept-to-model-prompt](../concept-to-model-prompt/SKILL.md). Give it the same project directory, selected design decisions, required feature IDs and the reviewed image paths. Load additional analysis only for the current part or an unresolved handoff detail.

Preserve these package rules:

- Image 1 is `parts/00-overview/reference.png`, showing FRONT/TOP/SIDE. Reuse a reviewed image only if its pixels satisfy the required layout; otherwise generate it anew.
- When separating parts from a multi-part image, generate new focused references from the full source and overview. Never substitute crops, sliced panels or enlarged cutouts. Inspect each generated part and its interfaces against the overview.
- Ship only `main_prompt.md`, indexed `parts/<part-id>/prompt.md` and their linked PNGs. Each part pairs its image with concrete modeling instructions and checks. Keep analysis, QA, generation history and progress notes out of the ZIP.

Run the second stage's packager from its resolved skill directory, inspect the ZIP contents and confirm that all links are usable inside the archive. Structural validation does not replace visual review.

## Resume and context management

If the user supplies an existing project, inspect its actual outputs and saved QA before choosing a starting stage. A reviewed concept that still matches the brief can enter stage 2 directly; incomplete concepts resume stage 1. Reuse valid part outputs and regenerate only those affected by changed constraints or failed checks.

Keep a short progress section in the working project's existing `handoff.md`: current stage, project/source paths, selected decisions, completed/pending part IDs, blockers and next action. Do not create a parallel analysis document or copy all part details there. This progress section is working evidence, never a shipped artifact. After context loss, reload this skill, that section and the active stage/part; verify files before trusting a saved completion claim.

## Delivery

Return the actual archive path and the `main_prompt.md` entry point, with a brief readiness result and any unresolved limitation. Complete means the visual/semantic checks and packaging have passed. If blocked, report the specific unfinished stage and preserved work; do not label a draft ZIP ready.

Example: `Use $reference-to-prompt with this image. Name: forest-lantern. Save under ./output and deliver the compact prompt ZIP with FRONT/TOP/SIDE overview and newly generated part references.`
