---
name: blender-detail-repair
description: Repair or enrich detail on an existing Blender model so it matches its reference or concept sheet - crop the references, render matching close-ups, write a gap list, rebuild parametrically (faceted ridged plates, panel seams, colour V-splits, slot bezels, rivets, stepped joints, wedge blades, layered recesses, wear bias), recheck topology and symmetry, re-render and add a revision section to verification.md. Use when the user gives visual-fidelity feedback such as "legs are too smooth", "the body doesn't look like the reference", "make the legs symmetric", "the eye is not centred / not deep enough" ("detail ยังเรียบไป", "ไม่เหมือน reference"), typically after $model-prompt-to-blender.
---

# Blender Detail Repair

A focused revision loop for a model that already exists. Uses the scripts and references of the sibling skill `model-prompt-to-blender`; install both side by side.

- Library: `../model-prompt-to-blender/scripts/` (`bl_build`, `bl_detail`, `bl_materials`, `bl_views`, `bl_check`, `bl_symmetry`, `img_tools.py`, plus `bl_images` when no local shell is available).
- Technique catalogue: [../model-prompt-to-blender/references/detail-techniques.md](../model-prompt-to-blender/references/detail-techniques.md).
- Pitfalls: [../model-prompt-to-blender/references/pitfalls.md](../model-prompt-to-blender/references/pitfalls.md).

## Workflow

1. **Locate.**
   - Find the asset's build script(s). Parametric re-runs are strongly preferred over one-off manual edits.
   - Note which components the feedback targets.
   - Collect the sources: `detail_crops/`, the primary reference and the concept panels. Make extra zoom crops with `img_tools.py crop` or `cropn`.
2. **Baseline.**
   - Add a temporary camera matching each crop's viewpoint and render the current state (materials, plus clay when the issue is form).
   - Build `img_tools.py pair before_<part>.png <crop> <render>`. Look at the image yourself.
3. **Gap list.** Write concrete, checkable differences, not "add more detail". Check each axis:
   - shape language: round tube vs ridged/faceted plate
   - seams and panel count
   - layering: raised or overlapping plates, depth of recesses
   - hardware: bolts, latches, rivets, bezels, hubs
   - colour splits: V tongue, coverage ratios
   - exposed mechanism under the armour
   - wear density
   - symmetry, centring and position
   - proportions: span, height, depth
4. **Plan.**
   - Map each gap to a technique and a parameter.
   - Back up the script before large edits (`*_v<N>.py`).
   - Keep unrelated components untouched. Keep evidence tags truthful: concept-derived detail stays a design choice, and hidden detail stays inferred.
5. **Implement.**
   - Edit the build script and re-run it.
   - When seams or Booleans change, print each panel/part count and its extents, and compare them with the plan. A seam that does not close leaves merged panels.
   - Deepened recesses may need a pocket in the inner body.
   - Mirrored families use shared parameters, `bl.mirror_factor` and mirror-consistent part names.
6. **Compare again.**
   - Same cameras, then `after_<part>.png` pairs.
   - Iterate until each gap is resolved, or explicitly deferred with a reason.
7. **Validate.**
   - `bl_check.check(...)`: no base-mesh issues; review modifier artifacts.
   - `bl_symmetry.measure_pairs(...)` for paired families.
   - Ground contacts at Z = 0 and clearances.
   - Emissive or recessed parts visible.
   - Delete the temporary cameras.
8. **Deliver** through `$blender-model-verify`:
   - re-save the detailed and final checkpoints and re-render every deliverable that shows the changed parts
   - re-verify the files
   - add `## 0x. Revision N (user request: …)` to `verification.md` (what changed, bugs found, re-done outputs, remaining differences)
   - update the counts and measurements the change affects

## Typical requests → first moves

| Request | First move |
|---|---|
| "Legs/limbs too smooth" | `ArmourProfile(profile='gable')`, plate split + seam, V colour split, latch/bolts via `surface_dot`, `stepped_disc` + `domed_hub`, side plates (reduce the wrap so they show), `faceted_wedge` + `keel_strip`, `oow_wear = 1` |
| "Body doesn't look like the reference" | More seams (crown, meridians reaching the band, lower split), tapered band, raised lower plates, `capsule_cutter` + `slot_bezel`, `rivet_cluster`, wider surround, skirt, `oow_wear` + flecks |
| "Not symmetric" | Shared-parameter family (front ± az, rear ± az, same reach); measure in the neutral pose; report the table |
| "Feature not centred / wrong height" | Change the parameter (e.g. ring axis Z = 0), then move its dependants (chin, arch, seams, emblem) |
| "Not deep enough" | Layered revolve profile with a deeper seat, collar, chassis pocket; check the emitter stays visible and saturated |
| "Colour coverage differs" | Move split parameters (`vsplit`, belt height, band taper) and re-measure them in the render |

Report the remaining differences honestly (noise-based wear vs hand-painted chips, uniform seam widths, and similar). Do not claim pixel parity.
