# Workflow details and recipes

## 0. Connect and inspect

- Call `get_addon_status`, then `get_scene_info`, and record the Blender version.
- Probe the API instead of assuming it:
  - Get valid render engines by setting an invalid value inside `try/except TypeError`; the error message lists them.
  - Get view transforms and looks the same way.
  - Read Cycles devices from `prefs.addons['cycles'].preferences.get_devices_for_type(...)`.
- Render on the GPU. `bv.configure_device(scene, 'AUTO')`, which `Stage(device='AUTO')` calls, enables the best backend at runtime: OptiX > CUDA > HIP > oneAPI > Metal, discrete GPUs only (integrated Radeon/Intel are skipped). Without a usable GPU it falls back to CPU.
- Record `Stage.device_info` in the report.
- The settings are not written to the user's preferences file unless you call `enable_gpu(save_prefs=True)`. Blender may still auto-save preferences on exit.
- `device='CPU'` forces CPU.
- The first OptiX render on a machine loads kernels, about 45 s once; later renders use the cache. Example: a 960×540 / 96 spp preview took 1.4 s on GPU vs ≈8 s on CPU.
- Work inside a dedicated scene: `bl.CTX.update(scene='<Name>_Scene'); sc = bl.get_scene()`. The user's original scene stays as it was.

## 1. Build script pattern

Keep the procedural model in files: `<asset>_build.py` (geometry), `<asset>_mat.py` (materials) and `<asset>_present.py` (cameras/stage). A small runner execs them in Blender.

```python
# inside execute_blender_code
import sys, importlib
sys.path.insert(0, r"<skill>/scripts")
import bl_build as bl, bl_detail as dl, bl_materials as bm_, bl_views as bv
for m in (bl, dl, bm_, bv): importlib.reload(m)
g = {'__name__': 'asset', 'LEVEL': 'detailed'}
exec(open(r"<work>/asset_build.py", encoding='utf-8').read(), g)
```

**Bootstrap without file access from Blender** (the skill runs in a remote sandbox):

```python
import sys, types
def _load(name, src):
    m = types.ModuleType(name)
    exec(compile(src, name + '.py', 'exec'), m.__dict__)
    sys.modules[name] = m
    return m
_load('bl_build', r'''<paste scripts/bl_build.py>''')        # first: the others import it
_load('bl_detail', r'''<paste scripts/bl_detail.py>''')       # then bl_materials, bl_views, bl_check, bl_symmetry, bl_images
```

- **Geometry and pivots.** Build geometry in world coordinates and hand it to `bl.mk()` with the pivot matrix. Pivots are frames such as `frame_matrix(hip, radial, up)`, built as empties: hip → knee → ankle, shoulder → elbow → wrist → tool.
- **Tags.** Tag every object with its component ID, evidence (`observed` / `inferred` / `proposed`) and an optional note. Those tags become the inferred/proposed list in the report.
- **Levels.** One script serves both the blockout and detailed levels through `bl.CTX['detailed']`. Bevels and tertiary details appear only at the detailed level.
- **Re-runs.** The script clears only its own collections and rebuilds deterministically, so every parameter change is one re-run. Keep earlier script versions (`*_v1.py`) before large rewrites.

## 2. Reference-match camera (blockout)

1. Create `REF_MATCH` with a vertical sensor fit at the reference resolution, for example 1131×784.
   - Initial guess: `orbit_eye(target, az, el, dist)` with lens 50–55.
   - Fit the body's centre and diameter first: diameter in pixels / image height ≈ D / frame height.
2. Make a transparent silhouette:

   ```python
   bv.workbench_silhouette(scene, 'REF_MATCH', path, (W, H))
   ```

   Then build the comparison sheet:

   ```
   python img_tools.py overlay <ref> <render> <out>
   ```

   The sheet is a 2×2 of reference, render, cyan edges on the reference, and a 50% blend.
3. Iterate in this order: camera (azimuth from the offset of a centred landmark, elevation from vertical offsets) → body height and stance → limb reach and spread → appendage poses.
   - Colour each limb root differently (`obj.color` + Workbench `OBJECT` colour) to see which limb lands where.
   - Back-projecting tips to the ground with least squares was ambiguous; visual iteration was more reliable.
4. Leave the brief's handedness and symmetry decisions alone while fitting. Do not distort geometry to match perspective.

## 3. Shell panels (spheres and other round bodies)

- **Cutting.** Use `dl.panelize_sphere_shell(center, R, thick, z_bottom, cutters, classify, ...)`.
  - Seams are thin slabs from `bl.slab_cutter`, with the long axis along the seam and the thin axis across it. Holes are `cyl_cutter`, sectors are `prism_cutter`, slots are `dl.capsule_cutter`.
  - A seam separates panels only as part of a CLOSED boundary. Combine meridians with a band, crown or belt seam that closes them. Make adjoining slabs overlap: a 2 mm gap between a tapered and a vertical slab left a bridge that merged two panels.
  - After building, print each panel's vertex count and its az/z/|x| extents. Compare them with the plan.
- **Layered armour.** In `classify`, return `raise_amount` to lift plates radially (lower plates +0.010, band +0.004).
- **Recessed parts.** When a recess goes deeper than the inner chassis, cut a pocket in the chassis; otherwise the chassis hides the recessed part. Keep the chassis closed: extrude the hole edge inward and fill it.

## 4. Close-up review loop (Phase A gate)

1. For each feature, create a temporary camera that matches the crop's viewpoint. Render at 640–960 px; materials help zoning, clay shows form.
2. Build the comparison:

   ```
   python img_tools.py pair <out> <crop> <render> --labels reference model
   ```

3. Write the gaps as concrete items, for example "armour is a round tube, reference is ridged and faceted with a seam and a V split".
4. Repair each item with [detail-techniques.md](detail-techniques.md), re-render, and compare again.
5. Run `bl_check.check(...)`. `issues` (base-mesh defects) must be empty. Review `modifier_artifacts` visually.
6. Delete the temporary cameras before saving.

## 5. Materials (Phase B)

- **Paint.** Shared IDs (M01…Mn) come from `bl_materials`. Use `painted` for paint with wear, `plain` for mechanisms and `emitter` for glows.
  - Set `obj['oow_wear']` (0–1) per object group. Exposed legs and body panels around 1.0 matched the reference wear.
  - Set `obj['oow_emit_scale']`: 1.0 for the main emitter, about 0.3 for secondary apertures.
- **Colour management.**
  - AgX desaturated saturated orange to salmon and emitters to white.
  - *Khronos PBR Neutral* kept the paint colours; use exposure around −0.45 with the presentation lights.
  - The emitter's base colour is dimmed so scene light cannot wash it out.
- **Measuring.** Use `img_tools.py measure img name:x0,y0,x1,y1` to get the p99 luma of the emitter versus the brightest paint highlight, plus the white-clipped pixel count. Report the trade-off rather than looping.

## 6. Renders and long-running jobs

- **Stage.** `Stage(scene, pres_coll, mode='diagnostic' | 'presentation', device='AUTO')`. Cycles renders use the GPU when available.
  - Diagnostic mode: pale grey world light and a plain floor. Clay renders use Workbench (viewport-like studio light); material renders use Cycles.
- **Cameras.** `standard_cameras()` builds FRONT / RIGHT (from +X) / REAR / TOP orthographic cameras sharing ONE ortho scale, plus DIAG_34, UNDERSIDE, REF_MATCH and detail cameras.
- **Long batches.** Any batch that may run over ~100 s: put it in one script that ends by writing `<scratch>/done.txt`. Launch it through MCP; when the call times out, Blender keeps working. Then wait in a background shell:

  ```
  until [ -f done.txt ]; do sleep 5; done
  ```

  Do not resend the batch, and do not poll in the foreground.
- **Contact sheets.** Build them with `img_tools.py sheet out --cols 2 --tile 960x540 a.png::LABEL ...`.

## 7. Verification and delivery

- **Saves.**
  - Checkpoints: `bpy.ops.wm.save_as_mainfile(filepath=..., copy=True)`. A copy keeps the live session's file path unchanged.
  - Final: save normally. Before saving, restore the hero/diagnostic state and remove temporary cameras.
  - Embed notes (`OOW_NOTES.txt`) and the build scripts as text datablocks.
- **Reopen in background.** Never reopen in the live session:

  ```
  blender -b file.blend --factory-startup --python verify_blend.py -- out.json <COLL> <SCENE>
  ```

- **Images.** `img_tools.py check file.png@1920x1080 ...` must report decodable, opaque, the expected size and no white clipping, unless clipping is intended.
- **Symmetry.** `bl_symmetry.measure_pairs(...)` on the neutral build. Paste `table(rows)` into the report.
- **Report.** `verification.md` follows [../assets/verification.template.md](../assets/verification.template.md). Each user revision gets a "Revision N" section listing what changed and why, re-done outputs and new deviations.
