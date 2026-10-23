---
name: blender-model-verify
description: Verify and deliver a Blender asset - targeted topology checks (winding, degenerate faces, duplicates, base mesh vs modifier artifacts), structural symmetry measurements, ground contacts, diagnostic (or in-scope presentation) renders with a marker-file pattern for long jobs, contact sheets and feature comparison pairs, background reopen of saved .blend files, PNG checks and pixel metrics, then write or update verification.md with coverage, gates and revision sections. Use when the user asks to re-render, re-check, validate, finalize or report on a Blender model ("render ใหม่ทั้งหมด", "ตรวจโมเดลแล้วอัปเดต verification.md"), or as the delivery step of $model-prompt-to-blender / $blender-detail-repair.
---

# Blender Model Verify

The delivery and verification stage. Uses `../model-prompt-to-blender/scripts/`; install both side by side. Report what was actually checked; never certify appearance from object statistics alone.

## Workflow

1. **Deliverables.**
   - List the required outputs from `build_spec.outputs` or the brief: checkpoints, final .blend, diagnostic images, comparisons, `verification.md`.
   - Follow `scope`: with `presentation: false`, use `bl_views.Stage(mode='diagnostic')` only (grey world light, plain floor, Workbench clay). Add hero, sweep and lights only when they are in scope.
2. **Live checks**, run in Blender before rendering:

   ```python
   import bl_check as bc, bl_symmetry as bs
   res = bc.check('<COLL>', '<Name>_Scene', ground_z=0.0, counts={...})
   print(bc.summary(res))
   ```

   - Fix every entry in `issues` (base mesh). Inspect `modifier_artifacts` and `open_boundaries` and decide whether each is intended.
   - `bs.measure_pairs(pairs, plane='X' | 'Y', tolerance=...)` on the neutral build, then paste `bs.table(rows)` into the report.
   - Confirm the required counts (legs, arms, emitters …), contacts at Z = 0, clearances of parts that must not touch the floor, empty material slots and hidden objects.
3. **Renders.** Use one batch script that saves the detailed checkpoint, renders everything and saves the final file. Templates: `../model-prompt-to-blender/assets/run_pass.template.py`.
   - The MCP call times out after about 120 s, but Blender continues. Wait in a background shell (`until [ -f done.txt ]; do sleep 5; done`). Never resend the batch.
   - Orthographic FRONT / RIGHT / REAR / TOP share one ortho scale and one unchanged pose. Detail close-ups must resolve the feature.
   - Remove temporary cameras and restore the scene state before the final save. Checkpoints use `save_as_mainfile(copy=True)`.
4. **Compose.**
   - `img_tools.py sheet` for contact sheets (`IMG::LABEL`).
   - `img_tools.py pair` for each feature crop vs model view (the v3 `feature_plan.comparison`).
5. **File checks.**
   - Every .blend: `blender -b <file> --factory-startup --python verify_blend.py -- out.json <COLL> <SCENE>` → VERIFY_OK. Never reopen in the user's live session.
   - `img_tools.py check a.png@1920x1080 ...`: decodable, expected size, opaque, white clipping.
   - `img_tools.py measure img name:x0,y0,x1,y1 ...`: emitter vs brightest paint luma, dark mechanisms not crushed.
6. **Look.** Open every delivered image yourself and compare it with the reference/crops. Write findings per view.
7. **Report.** Fill or update `verification.md` from `../model-prompt-to-blender/assets/verification.template.md`:
   - files, environment, decisions
   - gates: blockout, symmetry, Phase A, topology, Phase B, delivery
   - feature coverage with status pass / fail / not_verified / allowed_simplification
   - view table, symmetry table, measurements vs guides (with deviations), materials, reopen results
   - honest differences, the inferred/proposed list, what was not done

   Every user-requested change gets a "Revision N" section. `.blend1` backups are mentioned, not deleted.

## Notes

- **No local shell** (desktop/web chat clients):
  - Run the image checks inside Blender with `bl_images` (`check`, `measure`, `sheet`, `pair`, `overlay`).
  - Use `bl_check.inspect_saved_blend(path)` instead of a background reopen, and record that the verification is reduced.

- **GPU.** `Stage(device='AUTO')` renders on the best discrete GPU (OptiX > CUDA > HIP > oneAPI > Metal) and falls back to CPU.
  - Report `Stage.device_info` (backend + device names) under Environment.
  - Use `device='CPU'` to force CPU, for example when comparing noise.
  - The first OptiX render loads kernels once (~45 s).
  - Manual equivalent: Preferences → System → Cycles Render Devices → OptiX, then Render Properties → Device → GPU Compute.
- **Colour.** Khronos PBR Neutral kept saturated paint; AgX desaturated it. Bright emitters still desaturate, so report the brightness-vs-saturation trade-off with measured luma.
- **Failures.** A required feature that fails, or a check you could not run, leaves the status partial / needs_revision. State the exact blocker.
