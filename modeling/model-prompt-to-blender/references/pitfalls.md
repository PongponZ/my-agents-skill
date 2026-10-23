# Pitfalls found in practice (and the fix)

Each item cost real time in a production run. Most fixes are already built into `scripts/`.

## Fidelity and process

1. **Silhouette match ≠ detail match.** The first delivery passed every count and silhouette check, yet the user found the legs and body "too smooth". The fix is Phase A close-up comparisons against the crops, with a written detail inventory, *before* materials. See [preflight.md](preflight.md) §3 and [workflow.md](workflow.md) §4.
2. **A tube-shaped procedural default looks generic.** Superellipse lofts and plain spheres read as toys. Use faceted gable sections, panel seams, layered plates, stepped discs, bezels and rivets from [detail-techniques.md](detail-techniques.md).
3. **Missed brief instructions.** One brief said the top band "narrows toward the ring" and the first build made it constant-width. Keep every adjective from the brief as an inventory row.
4. **Perspective asymmetry copied into structure.** Copying a generated reference's uneven leg spread produced a lopsided top view. Build symmetric neutral families by default; pose only by documented decision.

## Geometry and Blender API

5. **Normals.** `bmesh.ops.recalc_face_normals` sometimes picks the inside for closed primitives (cylinders, revolves). `bl.finish_mesh` enforces positive signed volume. `bl_check` also checks winding consistency, because signed volume alone is not enough.
6. **Booleans.** One modifier with a collection operand of many overlapping cutters silently failed to separate panels; apply cutters one at a time (`bl.bool_sequential`). After a Boolean the mesh carries an empty material slot: clear the slots before assigning materials, otherwise solid view shows default grey.
7. **Rotation sign of seam cutters.** `Matrix.Rotation(-az, 'Z')` sent "meridian" slabs off-meridian. The panels still separated by luck, which hid the bug for three revisions. Use `bl.slab_cutter` with explicit axes, or `bl.meridian_rotation(az)`.
8. **Seam gaps.** Two adjoining seam slabs with a 2 mm gap between them (front tapered, rear vertical) left a bridge, and two panels became one. Use one shared plane or overlap the slabs. Verify panel extents numerically.
9. **Recessed emitter hidden.** Deepening the eye pushed the core inside the dark chassis sphere and it vanished. Cut a pocket in the chassis behind recessed parts.
10. **Depsgraph from another scene.** With a dedicated scene, `bpy.context.scene` may still be the user's scene. Evaluate with that scene's `view_layers[0].depsgraph` plus `update()`, as `bl.get_dg()` does.
11. **Bevel side effects.**
    - A width above about 0.45 × thickness collapses edges, giving zero-length edges.
    - Angle-limited Bevel adds zero-area miter triangles where seams meet. `bl_check` reports these as `modifier_artifacts`, separate from base defects.
    - Bevel shrinks a blade's tip by about 0.00023. Compensate so ground contact stays exactly at Z = 0 (`faceted_wedge(ground_z=0)` does this).
12. **Mirror symmetry breakers.**
    - A right-handed frame built from mirrored axes flips its local Y, so any offset along local Y lands on the wrong side. Keep offsets in X/Z, or multiply by `mirror_factor`.
    - Revolve and sphere tessellation phase: `bl.frame_z` starts at world-up for horizontal axes, so mirrored discs match vertex for vertex.
    - Name side-specific parts by mirror-consistent roles (`P`/`N` from `s * mirror_factor`), not by raw `+1`/`-1`, or `bl_symmetry` compares the wrong parts.

## Rendering, MCP and files

13. **MCP timeout.** `execute_blender_code` returns "No data received" or "moved to background" after about 120 s while Blender keeps rendering. End long scripts with a marker file and wait for it in a background shell. Never re-launch: that queues a second render.
14. **Display transform.** AgX desaturated the orange paint and the emitter. Khronos PBR Neutral kept them. Very bright saturated emitters still desaturate, so lower the gain and dim the emitter's base colour rather than raising exposure.
15. **Workbench silhouettes** need `film_transparent` and RGBA PNG. Restore the engine and settings afterwards (`bv.workbench_silhouette` does).
16. **Wear masks** built on the Bevel node work only in Cycles. EEVEE shows clean paint.
17. **Reopening** the final file in the live session would replace the user's open file. Use `verify_blend.py` in a background Blender.
18. **`.blend1` backups** appear when you overwrite checkpoints. Mention them in the report; do not delete files the user did not ask you to delete.
19. **User scene and GPU.** Build in a dedicated scene.
    - Cycles defaulted to CPU on a machine with an RTX GPU because the compute device preference was `NONE`, so renders were about 5× slower.
    - `bl_views.configure_device('AUTO')` now enables the best discrete GPU backend at runtime and falls back to CPU. Note the device in the report.
    - Expect the first OptiX render to spend ~45 s loading kernels.
    - With a mix of HIP/oneAPI devices, integrated GPUs are skipped unless `allow_integrated=True`.
