# Worked example: orange-orb-walker

These are the real production scripts from the run that produced this skill. The package was `playground/orange-orb-walker`, a v1-style prompt package with `model_prompt.en.md`, R01 and a concept sheet. Read them for proven construction code. For new work, start from `../../assets/` and `../../scripts/`, the generalized and tested libraries.

## What happened (useful as a checklist)

| Round | Request | What changed |
|---|---|---|
| Rev 1 | Build the model from the prompt | Blockout fitted to R01 by silhouette overlay (5 iterations), with asymmetric legs copied from R01. 13 shell panels, materials, presentation lights, 1920×1080 renders, `verification.md`. |
| Rev 2 | "Legs not symmetric like the concept; the eye is not centred; the eye lacks depth" | Symmetric legs (±54° / ±126°, same reach). Eye axis at the body centre. Layered bezel (rim, groove, lip, funnel, ribbed barrel, collar) with the core 0.09 deep and a chassis pocket. Saturated emitter. |
| Rev 3 | "Legs too smooth compared with the reference" | Faceted ridged armour, panel seams, V colour split, latch, bolts, stepped discs, domed hubs, joint block, exposed side plates, faceted blade with keel strip, `oow_wear` bias, mirrored details. |
| Rev 4 | "Body detail like the reference" | Tapered top band, crown seam (21 panels), layered lower plates, slot bezels, holes, rivets, wider surround, skirt, flecks. Fixed the meridian rotation sign and switched to sequential Booleans. |

The lesson behind Rev 2–4: the brief's acceptance checks were silhouette and counts. Detail needed close-up comparisons against the concept panels from the start, which is why Phase A is now a hard gate.

## Files

- `scripts/oow_lib.py`: the first version of the helpers. `bl_build.py` is its successor.
- `scripts/oow_build.py`: the full asset: shell panelization with tapered band and crown seams, eye, roof, chin, arms with tools C09/C10, and legs with all Rev 3 detail.
- `scripts/oow_mat.py`: M01–M05 with wear, flecks and the emitter.
- `scripts/oow_present.py`, `scripts/oow_cam.py`: presentation stage. This brief required hero renders; v3 packages do not. The delivered images were rendered on CPU; the script now prefers GPU (OptiX) with a CPU fallback.
- `scripts/oow_all.py`, `scripts/oow_final_pass.py`: pipeline runner and final pass with the marker file.
- `scripts/oow_refrender.py`, `scripts/oow_wbrender.py`, `scripts/overlay.py`: REF_MATCH fitting loop.
- `scripts/oow_check.py`, `scripts/verify_blend.py`, `scripts/compose_details.py`: checks and contact sheet.
- `scripts/oow_notes.txt`: the scene notes embedded in the final .blend (decisions, inferences).
- `verification.example.md`: the final report with revision sections, gates, measurements and honest deviations.

## Adapting

- The scripts hard-code a scratch path (`SP = ...`) and the project output folder. Replace both, or port the code onto `bl_build` / `bl_detail` calls.
- Component IDs (C01–C13) and materials (M01–M05) come from that package's `analysis.json`.
