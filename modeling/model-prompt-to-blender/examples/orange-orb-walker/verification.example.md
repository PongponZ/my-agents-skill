# Orange Orb Walker — verification report

Executed from `model_prompt.en.md` on 2026-10-23. All paths are absolute. Statements below are what was actually produced and checked in this run. They are not a claim of pixel-perfect or engineering accuracy. R01 is a single perspective image.

Output directory: `C:\Users\User\Desktop\projects\playground\orange-orb-walker\model_output\`

## 0c. Revision 4 (user request: body detail like the reference)

I compared the body against R01 and the concept hero/front/rear views, then rebuilt the armour shell and its surface detail.

**Panels.**
- **Top band (C03).** Now a wedge: one tapered seam plane (half-width 0.185 at the crown, narrowing toward the ring by 0.2 per unit of height), shared front and back. Below the band end the rear seams continue vertically. This now matches the brief's wedge description.
- **Seams.** I added a crown latitude seam (el ≈ 45°), extended the meridian seams to the band, and added a front split of the lower plates at ±56°. The shell is now **21 panels**:
  - band
  - front, side and crown panels on each side
  - rear upper L/C/R and rear crown L/R
  - lower front and lower side on each side
  - rear lower L/C/R
- **Layering.** The lower orange plates (and the rear lower plates) are raised 0.010 and the band 0.004, so they read as overlapping armour.
- **Bug fixes found along the way.**
  - The meridian seam cutters had a mirrored rotation (−a instead of a) since rev 1. They happened to separate panels before, but did not follow true meridians.
  - Shell Booleans are now applied one cutter at a time.
  - Side effect: the earlier non-manifold edges on `C13_RearLower_R` are gone.

**Surface hardware.**
- **Recess slots.** Rounded recess slots have raised dark bezels: two diagonal front slots, two side slots above the shoulders, two small holes in the lower orange plates, and one rear lower vent (rear vent inferred from the concept rear).
- **Rivets.** About 36 sparse dark rivet heads near panel edges, on band, ivory, crown and lower plates. The rear ones are inferred.
- **Surround.** The C04 surround is wider (outer radius 0.315, ends 22° below the ring axis), so it reaches the lower plates as in R01/concept.
- **Skirt.** A dark skirt lip with 16 warm bolts sits under the armour rim (inferred, after R01's dark mechanism between body and legs).

**Paint.**
- Body panels now use `oow_wear` = 1.0, giving heavier edge chips and specks like R01.
- M01 gained sparse orange paint flecks (procedural, wear-gated).

**Re-done.** Detailed and final .blend files, every Cycles image and this report. The blockout is unchanged; these are detailed-level features only. The rev 3 build script is kept in the scratchpad as `oow_build_v3_legs.py`.

## 0b. Revision 3 (user request: more leg detail)

The user said the legs were too smooth compared with the reference. I compared the leg against R01's legs and the concept C11 panel, then rebuilt the leg detail.

**Armour.**
- Faceted gable section with a centre ridge and near-vertical side skirts, replacing the round tube section.
- The orange plates are split into a raised cap, a main plate and a side strip, so the seams read as panel lines.
- The orange tongue runs deeper into the ivory (V split moved from 0.50 to 0.60, with a deeper point).
- A separate ivory tip plate sits at the chisel end.

**Hardware.**
- Bolt heads on the orange plates, and a dark bolt hole with a rim on the ivory plate.
- The latch is on the cap.
- A dark joint block bridges the knee and the cap.
- A dark under-lip plate sits at the blade root.

**Joints and mechanism.**
- Knee and ankle are stepped discs: raised rim plus recessed face, with domed warm hubs.
- The ankle disc is widened so its hub shows beside the armour.
- Two pairs of dark side plates with warm dots sit under the armour edge, now exposed because the armour wrap was reduced from 106° to 96°.
- Strut details: orange collar near the hip, plus a secondary dark rod with a warm inner section into the knee.

**Blade.** Faceted wedge (keel, shoulders, chamfers, flat inner face) with an orange inset that follows the facets.

**Wear.**
- A new object property, `oow_wear`, is read by the shared M01/M02 graphs and lowers the chip and speck thresholds.
- It is set to 1 on all leg parts, so the legs carry heavier edge wear than the body. The material IDs are unchanged.

**Symmetry.** Off-centre details (seam side, bolt positions) use a mirror factor, so all four legs are exact mirror images, left/right and front/rear.

**Contacts.** The blade tip is offset by 0.00023 to compensate for the Bevel modifier's tip shrink. Evaluated lowest points are at Z = 0.000.

**Re-done.**
- Detailed and final .blend files, every Cycles image and this report.
- The blockout checkpoint is unchanged from rev 2. Leg detail exists only at detailed level, and the blockout stance is identical.
- The rev 2 build script is kept in the scratchpad as `oow_build_v2_sym.py`.

## 0. Revision 2 (user request, same day)

The user asked for three changes:

1. Legs to match the concept sheet: the four legs were visibly asymmetric.
2. The C04+C05 eye to be centred.
3. The eye's depth detail to match the reference.

Changes made:

- **Legs (C11/C12).**
  - The layout is now mirror-symmetric left/right and front/back: front legs at azimuth ±54°, rear legs at ±126°, same knee radius 0.56 and same reach.
  - The profile follows the concept front/rear views: armour goes out from the knee, then turns down to a near-vertical blade.
  - Detail follows the concept C11 panel:
    - domed warm knee and ankle hubs, each with a dark ring
    - an orange/ivory V-shaped split on the armour
    - a small ivory latch with a dark slot
    - dark inner shin plates with warm dots
    - an orange strip along the blade's outer keel
  - This **replaces the earlier R01-derived asymmetric stance**. The user constraint takes precedence; the cost is that REF_MATCH no longer reproduces R01's exact asymmetric blade-tip positions.
  - H was raised from 0.88 to 1.00 so the taller concept-style legs keep exact Z = 0 contacts.
- **C04/C05 eye.**
  - The axis now passes through the body centre (core centre x = 0.000, z − H = 0.000).
  - New layered bezel after the concept C04+C05 panel: raised outer rim, groove, inner lip, funnel face, ribbed barrel and a dark inner collar.
  - The core is recessed 0.091 behind the bezel front, up from 0.05.
  - A pocket was cut in `C01_Chassis` so the deeper core is not hidden by the chassis skin. The chassis stays closed (manifold).
  - The surround is thicker, with chamfered edges and 4 warm bolts.
  - The emitter ramp is more saturated (yellow → orange) to match the concept core.
- **Re-done.** Blockout, detailed and final .blend files; every PNG; this report.
  - The previous asymmetric versions remain only as Blender `.blend1` backups.
  - The previous build script is kept in the scratchpad as `oow_build_v1_asym.py`.

## 1. Delivered files (existence and decode verified)

| File | Status | Check |
|---|---|---|
| `orange-orb-walker_blockout.blend` | saved (rev 2, symmetric) | Reopened in a separate background Blender 5.2 process (`blender -b … --python verify_blend.py`); 4 leg roots, 2 arms present |
| `orange-orb-walker_blockout.blend1` | Blender auto-backup | Rev 1 asymmetric blockout. Kept, not required |
| `orange-orb-walker_blockout.png` | 1920×1080 PNG RGB | Workbench clay render from `REF_MATCH` (blockout stage) |
| `orange-orb-walker_detailed.blend` | saved (rev 4) | Reopened in background Blender; 240 asset meshes, M01–M05, 10 cameras |
| `orange-orb-walker_detailed.blend1` | Blender auto-backup | Rev 3 detailed checkpoint. Kept, not required |
| `orange-orb-walker_preview.png` | 960×540 PNG RGB | Cycles, 96 spp, inspected before finals |
| `orange-orb-walker_final.blend` | saved (current session file) | Reopened in background Blender (see §8) |
| `orange-orb-walker_final.blend1` | Blender auto-backup | Rev 3 final file. Kept, not required |
| `orange-orb-walker_hero.png` | 1920×1080 PNG RGB | Cycles 256 spp, visually inspected |
| `orange-orb-walker_clay.png` | 1920×1080 PNG RGB | Cycles, clay material override, `REF_MATCH` camera |
| `orange-orb-walker_front.png` | 1920×1080 PNG RGB | True ortho, same scale as right/rear/top |
| `orange-orb-walker_right.png` | 1920×1080 PNG RGB | True ortho |
| `orange-orb-walker_rear.png` | 1920×1080 PNG RGB | True ortho |
| `orange-orb-walker_top.png` | 1920×1080 PNG RGB | True ortho |
| `orange-orb-walker_details.png` | 1920×1080 PNG RGB | 2×2 contact sheet of four 960×540 Cycles renders with labels |
| `verification.md` | this file | |

Pillow opened every PNG at the stated size: opaque RGB, 0 fully clipped (255,255,255) pixels. I visually inspected each image after writing it.

## 2. Environment and settings actually used

- Blender 5.2.2 LTS, driven live through the MCP for Blender add-on (protocol 14). No asset libraries or generators were used. All geometry is procedural Python.
- Render engine: Cycles, **CPU** device (AMD Ryzen 7 9800X3D). An RTX 4070 Ti SUPER was detected, but Cycles' compute device preference was `NONE`. I did not change the user's preferences, so CPU was used.
- Sampling: adaptive (threshold 0.015), max 256 spp for the hero, 128–160 spp for inspection views. Denoiser: OpenImageDenoise. Bounces: 8 total, 3 diffuse, 3 glossy, caustics off.
- Measured render times (rev 4 pass):

  | Image | Time |
  |---|---|
  | Preview | 7.5 s |
  | Hero | 40.3 s |
  | Clay | 35.1 s |
  | Front / right / rear | 11.2 / 10.5 / 11.4 s |
  | Top | 34.3 s |
  | Four detail views | 37.1 s total |

- The MCP call that ran this batch returned "Communication error: No data received" (client timeout). Blender itself finished every render. I confirmed this with a completion marker file written by the script, file timestamps, and decoding every image.
- Colour management: display `sRGB`, view transform **Khronos PBR Neutral**, look `None`, exposure −0.45, gamma 1.0.
  - AgX was tested first. It desaturated the orange to salmon and the core to near-white. Khronos PBR Neutral is also highlight-preserving and kept the paint saturation closer to R01.
- Blockout image: Workbench, studio light, single clay colour, cavity on.

## 3. Scene organisation

- A dedicated scene, **`OOW_Scene`**, holds all work. The pre-existing default scene `Scene` (Cube, Light, Camera, EEVEE render settings) was left untouched; the reopened final file confirms it is unchanged.
- Collection `ORANGE_ORB_WALKER` contains:
  - `BODY`, `LEGS`, `TOOLS`, `DETAILS`, `PRESENTATION`
  - root empty `OOW_ROOT`, placed at the ground projection of the chassis centre
- Hierarchy:
  - `OOW_ROOT` → `C01_Chassis` → panels C02/C03/C13
  - `C04_RingAssembly` → `C04_CoreRing`, `C04_InnerCollar`, `C04_UpperSurround`, `C05_Core`, `C04_AccentStud_*` (×4)
  - `C06_RoofAssembly` → housing, apertures, rear mass
  - `C07_ChinAssembly` → pod, aperture, neck
  - `C08_Arm_R|L` → `*_Elbow` → `*_Wrist` → `C09_Tool` / `C10_Tool`
  - `C11_RF|RR|LF`, `C12_LR_PROPOSED` (hip empty) → `*_Knee` → shin/cowl, and `*_Ankle` → blade
- The asset is not joined; it has 240 separate meshes.
- 186 modifiers remain live (Bevel on panels and parts). The shell Booleans were applied, because separating the panels required it.
- Scene convention: D = 1 scene unit (body diameter), **not metres**; +Z up; front −Y; support plane Z = 0. Body centre height H = 1.00, chosen so that four blade tips touch Z = 0.

### Handedness decision (important)

The brief states "+X = robot right" and "source-left C09 on +X". With front = −Y and +Z up, a front view shows +X on the **image right**. Following the text literally would therefore mirror the tools against R01. Using the brief's own precedence (R01 > proposed convention), I placed:

- robot-right parts (C09, C11_RF, C11_RR) on **−X**
- robot-left parts (C10, C11_LF, C12_LR_PROPOSED) on **+X**

Result: `FRONT` and `REF_MATCH` show C09 image-left and C10 image-right, as in R01. The `RIGHT` camera follows the brief's camera spec literally (from +X looking along −X, i.e. Blender's Right view), so it shows the robot-**left** side. This is recorded on `OOW_ROOT`, on the RIGHT camera and in the text datablock `OOW_NOTES.txt`.

## 4. Stage log

1. **Intake.**
   - Read model_prompt.en.md, analysis.json, analysis.md, details.md, concept_qa.md, handoff.md and build_spec.json.
   - Inspected the pixels of R01 (with a grid and zoomed crops) and of concept_sheet.png (front/side/rear crops).
   - Noted the concept_qa limits: the RIGHT SIDE panel is oblique and not used for tracing; small details vary between sheet views; the rear roof light is inferred and omitted.
   - Inventoried the scene and recorded the four-leg and hidden-surface decisions.
2. **Blockout.**
   - Built primary masses for all components, including four leg chains.
   - Fitted `REF_MATCH` to R01 (1131×784, vertical sensor fit; azimuth −7°, elevation 13°, distance 5.9, 55 mm) by overlaying silhouette edges on R01 over five iterations.
   - Corrections made autonomously during fitting:
     - Legs and arms were initially far too thin and arched; I thickened them.
     - The stance was too tall and narrow; I lowered the body from 1.0 to 0.88 and spread the legs asymmetrically, as in R01.
     - **Rev 2:** at the user's request I replaced this with the symmetric concept-sheet stance at H = 1.0 and rebuilt the blockout (§0).
   - Front, side and top checks passed. Saved the blockout .blend and .png.
3. **Structure.**
   - Real ring recess: layered revolved bezel, with the core 0.091 behind the bezel front (rev 2). The chassis is pocketed behind the ring.
   - Sockets are seated half into the chassis. Strut, knee, shin and ankle are each separate objects with pivots.
   - Blades have finite thickness and rounded edges, and their lowest points were snapped exactly to Z = 0.
   - Tools are attached through mount struts to the wrist pivots.
4. **Secondary forms.**
   - Armour shell (thickness 0.025) is split by thin Boolean cutters into 13 panels with ~0.01 dark seams:
     - C03 top band (≈0.34D wide) running front-to-back over the top
     - front and side ivory C02 panels with capsule recess slots
     - lower orange C03 plates
     - inferred C13 rear upper/lower panels and under-plate
   - Lower front strip left open around the chin; shoulder holes; horseshoe surround conformed to the sphere.
   - C06 housing has a Boolean front aperture and top recess. C07 pod has a Boolean aperture.
   - Saved the detailed checkpoint after these geometry checks passed.
   - After seeing colour renders I made further proportion refinements (chunkier legs and arms, longer blades, orange cowl tips), then re-saved the detailed checkpoint. The earlier version is the `.blend1` file.
5. **Surface.**
   - Shared M01–M05 graphs (procedural, editable, no image textures), described in §6.
   - Emission tuned against exposure: gain tested at 1.8 / 3.2 / 3.5 / 4.0 / 4.6 / 5.5.
   - At 4.0 the core only equalled the ivory highlight, so I lowered the key light from 420 W to 320 W, raised the fill, and kept gain 4.6. I then re-rendered all final images with these settings.
   - Checked with emission disabled via the clay override.
6. **Presentation.**
   - Separate inspection setup: pale floor plane, light-grey world, optional clay override.
   - Separate hero setup: matte dark sweep, dark world.
   - 960×540 preview checked for framing, contacts, exposure and clipping, then finals rendered.
7. **Delivery.**
   - Final .blend saved and reopened in a separate background process.
   - Images decoded and inspected, and this report written.

## 5. View-by-view inspection

All views use the same, unchanged pose. Ad-hoc viewport checks used the MCP `look` tool (solid shading). Saved images are Cycles renders.

| View | Method | Finding | Status |
|---|---|---|---|
| REF_MATCH | Workbench silhouette overlay on R01 (5 iterations, rev 1); Cycles clay at 1920×1080 (rev 2) | Orb outline, roof stack, core and both tool endpoints still read as R01. After the symmetric-leg change, the blade tips no longer sit at R01's asymmetric positions: R01's far-left tip is further out, and C12 is partly visible. | Pass for identity; leg positions deviate by user request |
| FRONT | True ortho along +Y | Core exactly centred on the body; layered recessed ring; surround; chin below; C09 image-left, C10 image-right; legs mirror-symmetric (front pair covering the rear pair); no part crosses the floor. | Pass |
| RIGHT | True ortho from +X along −X | Shows the robot-left side (C10 arm and shoulder seated in the shell hole, C11_LF, C12). Body depth is near-spherical (inferred). | Pass (handedness note in §3) |
| REAR | True ortho from +Y along −Y | Inferred C13: ivory upper panels, orange lower, dark under-plate; top band ends behind the roof. No rear core, no rear roof emitter. | Pass (inferred surfaces) |
| TOP | True ortho from +Z, front at image bottom | Round body; symmetric four-leg X layout (±54° / ±126°); C09 on −X, C10 on +X. | Pass |
| UNDERSIDE | Perspective from below/behind, floor hidden | C12_LR_PROPOSED socket, strut and knee are visible; C13 under-plate closure; the tucked chassis. | Pass |
| CORE_DETAIL | Perspective close-up | Layered bezel (outer rim, groove, inner lip, funnel, ribbed barrel, dark collar); core deeply recessed with an orange glow on the barrel; yellow centre to orange rim; 4 bolts on the surround. | Pass |
| LEG_DETAIL | Perspective, C11_RF | Rev 3 detail is readable: ridged and faceted plates with seams, deep orange V into ivory, bolt hole, ivory tip plate, stepped ankle disc with domed hub, faceted blade with orange inset meeting the floor, exposed side plates on the neighbouring legs. No gaps at the joins. The knee is partly cropped at the top of this frame (it is visible in CORE_DETAIL and the hero). | Pass |
| TOOLS_DETAIL | Perspective, front-high | C09 (rim, dark recess, hub, curls) and C10 (oval head, dark oval detail, hanging blade) are clearly different, each attached through its own mount. Neither touches the floor. | Pass |

## 6. Counts, measurements and geometry checks (scripted, final scene)

- **Counts.**
  - Walking legs: 4 — `C11_LF`, `C11_RF`, `C11_RR`, `C12_LR_PROPOSED`
  - Auxiliary arms: 2 — `C08_Arm_L`, `C08_Arm_R`
  - Tools: 1 `C09_Tool` + 1 `C10_Tool`
  - Major front core: 1 (`C05_Core`)
  - Roof assembly: 1, with 2 masses (`C06_Housing`, `C06_RearMass`)
  - Chin: 1 (`C07_ChinPod`)
- **Emissive objects:** `C05_Core` (scale 1.0), plus the observed front apertures `C06_FrontAperture`, `C06_RearMassAperture` and `C07_Aperture` (scale 0.32 via the object property `oow_emit_scale`). No orange paint is emissive.
- **Measured proportions** (D = 1):

  | Feature | Measured | Brief guide |
  |---|---|---|
  | Armour diameter | 1.008 | — |
  | C04 ring outer diameter | 0.444 | 0.4–0.5 |
  | Upper surround width | 0.610 | — |
  | C05 core diameter | 0.236 | 0.18–0.25 |
  | Core recess behind bezel front | 0.091 | — |
  | Roof protrusion above the shell | 0.225 | 0.2–0.3 |
  | Chin width | 0.200 | ≈0.2 |
  | C09 tool width | 0.234 | ≈0.2 |
  | C10 blade drop | 0.256 | ≈0.25 |
  | Arm reach beyond the body surface | ≈0.34 (C09 side), ≈0.52 (C10 incl. blade) | 0.3–0.5 |
  | Leg span, front view | **1.64** | 1.8–2.1 |

  The leg span is now slightly *below* the starting guide. It matches my reading of the concept front view (≈1.7D), which the user asked to follow. The guide is not an acceptance tolerance, but this is reported as a deviation.
- **Contacts.**

  | Blade tip | Position (x, y, z) |
  |---|---|
  | C11_RF | (−0.778, −0.565, 0.000) |
  | C11_RR | (−0.778, 0.565, 0.000) |
  | C11_LF | (0.778, −0.565, 0.000) |
  | C12_LR_PROPOSED | (0.778, 0.565, 0.000) |

  - The tips are exactly mirror-symmetric.
  - Lowest point of C07: Z = 0.589. Lowest point of the C10 hanging blade: Z = 0.964.
  - No asset vertex lies below Z = 0.
- **Normals.** All closed meshes have positive signed volume (outward normals) after a fix during this run: bmesh `recalc_face_normals` had inverted 15 cylinder parts. The build now enforces positive volume.
- **Duplicates.** None: no two meshes share both vertex count and centroid.
- **Hidden objects.** Only `PRES_InspectFloor`, which is hidden in the hero setup by design. No hidden duplicates.
- **Non-manifold (rev 4).** None. The rev 1–3 report below listed `C13_RearLower_R` with 8 non-manifold edges: Boolean degeneracies at a hidden bottom-rim corner of an inferred panel. A remove-doubles and dissolve-degenerate pass reduced them from 16. The pocketed `C01_Chassis` is closed. Nothing was visible in the rear or underside renders. **Resolved in rev 4** by applying the shell Booleans one cutter at a time.
- **Size.** 131.2k evaluated faces across 240 meshes. No polygon budget was specified.

## 7. Materials and lighting

| ID | Assignment | Settings used (artistic, not measured) |
|---|---|---|
| M01_Ivory | C02 panels, ivory cowls, inferred C13 upper | Base linear (0.64, 0.51, 0.37), roughness 0.64, specular 0.38, metallic 0, broad ±6% value noise, sparse edge chips (Cycles Bevel-normal mask × noise) and tiny specks |
| M02_Orange | C03 band and lower plates, C06/C07 accents, C08 sleeves, C09/C10 shells, cowls, blade plates, C13 lower | Base (0.86, 0.17, 0.014), roughness 0.58, specular 0.32, metallic 0, same restrained wear graph |
| M03_Charcoal | C01 chassis, C04 ring and surround, C06/C07 housings, joints, C09 recess, C10 blade, struts/shins/blades, C13 under-plate | Base (0.055, 0.040, 0.033), roughness 0.68, metallic 0 |
| M04_WarmHub | Knee, ankle, elbow, shoulder hubs; hip collars; C04 accent studs; C09 centre hub | Base (0.36, 0.11, 0.025), roughness 0.50, metallic 0 (bare metal unproven) |
| M05_Emitter | C05 plus observed front apertures | Opaque; radial generated-coordinate ramp yellow (1, 0.78, 0.05) → (1, 0.42, 0.01) → orange (1, 0.16, 0); emission strength 2.6 × falloff (1 → 0.45) × per-object scale; diffuse base dimmed ×0.12; no transmission |

- Wear is procedural and object-space, so it stays stable when legs are re-posed. Since rev 3 it is biased per object by the `oow_wear` property: legs 1.0, everything else 0. It is restricted to edges plus sparse specks; there is no full-surface noise and no exposed silver metal.
- No image textures, so `textures/` was not needed. `bpy.data.images` holds no file images, there are no linked libraries, and `report_missing_files` found none.
- **Lights** (area lights in `PRESENTATION`):

  | Light | Power | Position |
  |---|---|---|
  | Key | 320 W | upper front-left; azimuth −48°, elevation 36° |
  | Fill | 170 W | right-front, low |
  | Rim | 240 W | back-right |
  | Top | 40 W | overhead |

- **World.** Hero: dark grey (0.03). Inspection: grey (0.20).
- **Support surfaces.** Hero: matte dark sweep `PRES_Sweep`, albedo 0.06, roughness 0.85. Inspection: matte plane `PRES_InspectFloor`, albedo 0.16.
- **Measured pixels** (rev 2 hero; rev 3 and rev 4 heroes give core p99 219 vs ivory 220; rev 4 ivory mean is darker, (193, 171, 146), because of the heavier specks).
  - Core p99 luma 219 vs ivory highlight 220: **about equal**. Rev 1 had the core slightly brighter (225 vs 220), but its centre looked pale.
  - In rev 2 I lowered the emission gain to 2.6 so the core reads as saturated yellow-orange like the concept. Brightest core pixel: (251, 228, 107). Core mean: (206, 128, 46).
  - Visually the core is still the focal glow, but by luma it no longer clearly exceeds the ivory highlight. Restoring a clear margin would need a slightly dimmer key light or a higher gain at some cost to saturation.
  - Charcoal ring mean (69, 46, 30): not crushed.
  - Background (32, 33, 36).
  - No pure-white pixels in any image.

## 8. Final .blend reopen check (separate background process)

- `orange-orb-walker_final.blend` contains the scenes `OOW_Scene` and `Scene`; the original `Scene` still has Camera, Cube and Light on EEVEE.
- Render state:
  - scene camera `HERO`; Cycles/CPU, 256 spp, 1920×1080 at 100%
  - Khronos PBR Neutral, look None, exposure −0.45
- 280 objects in the asset collection, including 10 cameras and 4 lights. Cameras:
  - perspective: `REF_MATCH`, `HERO`, `UNDERSIDE`, `CORE_DETAIL`, `LEG_DETAIL`, `TOOLS_DETAIL`
  - true ortho: `FRONT`, `RIGHT`, `REAR`, `TOP`
- Materials M01–M05 present. 65 objects carry `oow_evidence` = `proposed` or `inferred`.
- Text datablocks:
  - `OOW_NOTES.txt` (evidence boundaries and the handedness decision)
  - reference copies of the build scripts: `OOW_src_lib.py`, `OOW_src_build.py`, `OOW_src_mat.py`, `OOW_src_cam.py`, `OOW_src_present.py`
- No external dependencies.
- **Limit of this check.** Settings were checked by script; no re-render was performed from the reopened file.

## 9. Fidelity against R01 — honest qualitative differences

- **Legs.** Rev 3 follows the concept sheet's symmetric layout and much more of the C11 detail. Still simpler than the reference:
  - fewer scratch marks and no painted-on chip shapes
  - no groove line cut into the blade face
  - the side plates are rounded boxes rather than the concept's hexagonal plates
- **Spread.** By user request the legs are symmetric. R01's asymmetric spread (far-left blade further out, right-rear leg hidden) is therefore no longer reproduced in REF_MATCH.
- **Tools.** C09's curled backing is a simplified pair of torus curls. C10's hanging blade is leaf-shaped where R01's is a broader paddle. Tool poses approximate R01 but are not exact.
- **Body detail.** Rev 4 adds the tapered band, 21 seamed panels, layered lower plates, bezelled slots and holes, rivets and heavier wear. Still simpler than the reference:
  - fewer distinct chip shapes; the procedural chips are noise-based, not hand-painted
  - no long scratch strokes
  - the panel seams are uniform-width gaps, not hand-placed bevelled lines
  - the roof aperture's glow pattern is simplified to three dark teeth
- **Colour.** The orange top band reads a little lighter than R01 where it faces the key light. Colours are approximate, not calibrated.
- **Matches.** Proportions of ring, core, roof and chin are within the brief's ratio guides (§6). The eye is centred, as in the concept front view. Ivory/orange zoning matches the front of R01. The clay reference-match image reads as the same robot.

## 10. Proposed / inferred items (retained uncertainty)

- **Leg count and C12.** Total original leg count is unresolved; R01 shows three clear tips. `C12_LR_PROPOSED` is a proposal, and its placement (+X rear, azimuth 126°) is a construction convention.
- **Quadrants.** Leg quadrant assignment and the symmetric azimuths (±54° front, ±126° rear) are an editable convention taken from the generated concept sheet at the user's request. They are not proven attachment points.
- **Eye.** The centred C04 axis and the layered bezel depth follow the generated concept C04+C05 panel, not a measurement.
- **Body depth.** Fore-aft depth is inferred near-spherical.
- **Rear and underside.** All rear/underside surfaces (C13) are inferred.
- **Hidden roof surfaces.** The hidden rear of C06 is simple and non-emissive (the concept sheet's rear roof light was omitted).
- **Hidden attachments.** The C07 neck and the C09/C10 mounts are inferred.
- **Pivots.** All pivots (hip, knee, ankle, elbow, wrist) are visual conventions. This is not a rig, no range of motion is certified, and the internal mechanisms are not modelled.
- **Material substrate.** Dielectric paint by default; substrate is unknown.
- **Physical scale.** Unknown; D = 1 is a scene unit.

## 11. Not done / out of scope

No rig, animation, FBX/GLB/STL export or print validation; none were required. Nothing in this run is blocked or incomplete. As of rev 4 there are no outstanding mesh-validity issues (no inverted normals, no duplicates, no non-manifold meshes, nothing below Z = 0).
