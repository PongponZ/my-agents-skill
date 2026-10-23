---
name: model-prompt-to-blender
description: Execute a modeling prompt package (model_prompt.*.md, analysis.json, build_spec.json, references, detail crops, concept_sheet.png) in a live Blender through the Blender MCP and deliver an editable, verified asset - procedural blockout, reference-match fit, symmetric prototypes, gated detailed mesh with close-up comparisons, procedural materials/textures, diagnostic renders, checkpoints and verification.md. Use when the user asks to build or model an asset in Blender from a prompt package or artifact ZIP (e.g. "read model_prompt.en.md and build the model", "สร้างโมเดล Blender ตาม prompt"), as the step after $concept-to-model-prompt.
---

# Model Prompt to Blender

Turn a prompt package into a real, editable .blend with checkpoints, diagnostic images and an honest `verification.md`. This is the third stage after `reference-to-concept` and `concept-to-model-prompt`.

## Inputs and scope

- Package folder or extracted ZIP: `model_prompt.en.md` (operational) or `.th.md`, `analysis.json`, `build_spec.json`, `details.md`, `concept_qa.md`, `handoff.md`, `references/`, `detail_crops/`, `concept_sheet.png`. Older v1/v2 packages work too: derive the feature list from `analysis.json` components.
- Scope comes from `build_spec.scope`. With `presentation: false` (v3 default), make diagnostic views only: no hero shot, sweep, key/fill/rim or HDRI. Add presentation only when the brief or user asks.
- Output: the user's directory, else `<package>/model_output/`. Preserve unrelated files. Expect Blender `.blend1` backups.
- Tools: Blender MCP (`execute_blender_code`, `look`, `get_scene_info`), the Blender executable for background checks, and system Python with Pillow and numpy.
- Rendering: Cycles on the GPU by default. `bl_views` picks OptiX > CUDA > HIP > oneAPI > Metal, discrete GPUs only, and falls back to CPU. Record the chosen device in the report.

## Toolkit (`scripts/`, tested by `scripts/tests/smoke_test.py`)

| Module | Use |
|---|---|
| `bl_build.py` | scene/collections, frames, bmesh primitives, `mk()` world→local objects with evidence tags, sequential Booleans, island split, cutters, `mirror_factor` |
| `bl_detail.py` | `Spine`, `ArmourProfile` (faceted ridged plates, V splits, seams), stepped discs, domed hubs, faceted wedges + keel strips, slot bezels, rivets, side plates, `panelize_sphere_shell` |
| `bl_materials.py` | `painted` (edge chips/specks/flecks biased by `oow_wear`), `plain`, `emitter` (radial, per-object `oow_emit_scale`), `clay` |
| `bl_views.py` | GPU setup (`enable_gpu`, `configure_device`, `Stage(device='AUTO')`), cameras, `standard_cameras` (shared ortho scale), `Stage` (diagnostic / presentation), `render`, `workbench_silhouette` |
| `bl_check.py`, `bl_symmetry.py` | targeted mesh checks (base vs modifier artifacts), mirrored-pair measurements, `inspect_saved_blend` (read-only, in-session) |
| `verify_blend.py`, `img_tools.py` | background reopen; crop / overlay / pair / sheet / measure / check images (system Python + Pillow) |
| `bl_images.py` | the same image checks and sheets INSIDE Blender (numpy only), for clients without a local shell |

**Loading the library in Blender**, first option that works:
1. `import bl_build as bl`: works after `setup/install_skills.py blender` has copied the modules into Blender's `scripts/modules`.
2. `sys.path.insert(0, r"<skill dir>/scripts")`. In Claude Code the skill dir is `${CLAUDE_SKILL_DIR}`.
3. When Blender cannot see the skill folder, for example in a remote sandbox: send each module's source through `execute_blender_code` and register it with `types.ModuleType` + `sys.modules`, in the order `bl_build`, then the rest. See [references/workflow.md](references/workflow.md) §1.

Use `importlib.reload` while iterating.

**No local shell** (Claude or ChatGPT desktop/web chat):
- Do every check through Blender: `bl_images` for image checks, sheets and pairs; `bl_check.inspect_saved_blend` instead of the background reopen.
- Wait for long renders by polling for the marker file from short Blender calls.
- In the report, note that this verification is weaker than a background reopen.

## Workflow (gates are blocking)

1. **Preflight.** Read every input and inspect the actual pixels; zoom crops with `img_tools.py crop`. Run [references/preflight.md](references/preflight.md): handedness, symmetry intent, centred parts, ranges vs concept, conflicting goals.
   - Record each decision.
   - Ask the user only when identity or scope would change.
2. **Scene.** Put the asset in a dedicated scene `<Name>_Scene` with collection `<NAME>` (BODY / LEGS / TOOLS / DETAILS / PRESENTATION) and a root empty.
   - Write one re-runnable build script per asset from [assets/build_asset.template.py](assets/build_asset.template.py), parameters in a `P` dict.
   - It may clear only its own collections.
3. **Blockout + reference match.**
   - Fit `REF_MATCH` with silhouette overlays (`workbench_silhouette` + `img_tools.py overlay`). Iterate masses, stance and camera before any detail.
   - Check true ortho front, side and top.
   - Save the `_blockout.blend` and `_blockout.png` checkpoints.
4. **Prototype + symmetry gate.**
   - Build one prototype of each repeated family and compare its close-up with the crops.
   - Then mirror it: shared parameters, `mirror_factor`, mirror-consistent part names.
   - `bl_symmetry.measure_pairs` on the neutral build must pass.
5. **Phase A - detailed mesh.**
   - Implement every required feature from `feature_plan` / `details.md`, choosing from [references/detail-techniques.md](references/detail-techniques.md).
   - **Close-up review:** render each feature's model view and place it beside its crop with `img_tools.py pair`. List missing or wrong features, repair them, recheck.
   - `bl_check` must report no base-mesh issues.
   - Save `_detailed.blend`.
6. **Phase B - materials and textures.**
   - Use `bl_materials` zones and per-object wear/emission properties.
   - Verify the geometry in clay with emission off.
   - Measure brightness and saturation with `img_tools.py measure`; do not tune lights in a loop.
7. **Delivery.** Follow [references/workflow.md](references/workflow.md):
   - render the diagnostic set and contact sheets
   - write the symmetry table
   - reopen the .blend in background with `verify_blend.py`
   - `img_tools.py check` every PNG
   - fill `verification.md` from [assets/verification.template.md](assets/verification.template.md): per-feature coverage, gate statuses, inferences, failures

A failed gate returns to its stage. Never mark complete with required features failing or not verified.

## Hard rules (details in [references/pitfalls.md](references/pitfalls.md))

- **Silhouette is not detail.** Plan the close-up comparisons from the start, not after the user complains.
- **Mirrored pairs** must be built from shared parameters and verified numerically. Never eyeball each limb separately.
- **Shell Booleans** go one cutter at a time. After cutting, check that the panel count and extents are what you planned.
- **Long renders:** the MCP call times out after about 120 s while Blender keeps rendering. Write a marker file at the end of the script and wait for it in a background shell; never re-launch the render.
- **Unrelated work:** never reopen the saved file in the user's live session, and never touch the user's other scenes.
- **Honest reporting:** report deviations (ranges, brightness vs saturation, inferred parts) instead of hiding them.

## Follow-ups

- Detail feedback ("legs are too smooth", "body doesn't match the reference") → `$blender-detail-repair`.
- Re-render, re-verify or update the report → `$blender-model-verify`.
- A full worked example (orange-orb-walker: blockout → 4 revisions) is in [examples/orange-orb-walker/](examples/orange-orb-walker/README.md).

Example: `Use $model-prompt-to-blender on C:\...\orange-orb-walker. Build the full model and save the .blend files, inspection images and verification.md to model_output.`
