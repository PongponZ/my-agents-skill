# Detail techniques catalogue (hard-surface / stylized robots and props)

Pick a technique by reference cue. Functions are in `scripts/bl_detail.py` (D = body diameter = 1). Keep every detail a separate, named, tagged object (or one cluster object for many tiny repeats), parented to the right pivot so poses stay editable.

## Armour plates on limbs

| Reference cue | Technique | Code |
|---|---|---|
| Plate with a centre ridge, flat facets, vertical side skirts | Gable section along a spine (`ridge` ≈ 0.30, skirts beyond \|f\| > 0.8, wrap ≈ 96°) | `ArmourProfile(spine, size_fn, profile='gable').build(...)` |
| Panel seam along the plate | Build two pieces with `frange=(-1, 0.36)` and `(0.42, 1)`; the gap is the seam | `build(..., frange=...)` |
| Seam across the plate | Adjacent t-ranges with a ≈0.02 gap | `tlo` / `thi` |
| Colour split with a V tongue (orange pointing into ivory) | Make the split t depend on f: `vs = lambda f: s0 + 0.20*(1-abs(f)) - 0.06`. Orange piece `[t0, vs(f)]`, ivory piece `[vs(f)+0.022, t1]` | `tlo` / `thi` callables |
| Raised cap / overlapping plate | Separate piece with `lift=0.010` | `build(..., lift=...)` |
| Pointed chisel end over the blade | `chisel=(t_start, t_len, side_scale, normal_scale)` | `ArmourProfile(..., chisel=...)` |
| Latch, clip, bolt, bolt hole | Read the surface point and normal, then seat a small box or cylinder there (a dark hole is a short proud dark disc; add a rim disc beneath it) | `prof.surface(t, f)`, `surface_dot(...)` |

## Joints and mechanisms

| Cue | Technique | Code |
|---|---|---|
| Thick disc with a raised rim and recessed face | Revolve a stepped profile | `stepped_disc(...)` returns the face-to-face width |
| Domed warm hub with a dark ring | Flattened spheres on both faces plus tori | `domed_hub(name, c, axis, w, rd, ...)` |
| Dark mechanism visible under the armour edge | Rounded side plates with a warm dot; reduce the armour wrap (106° → 96°) so they show | `side_plate(...)` |
| Inner shin, strut, rod | Rounded-rect tube along the spine; struts as bevelled boxes; rods with `bl.seg_cyl` | `tube_along`, `bl.seg_cyl` |
| Joint block bridging a disc and the armour | Bevelled box at `spine.frame(0.06)`, offset along the normal | `bl.bm_box` + `bl.mk` |

## Blades, claws, tool tips

| Cue | Technique | Code |
|---|---|---|
| Faceted wedge (keel, shoulders, chamfers, flat inner face) | Loft of `WEDGE_SECTION` along a Bezier path, tapering with `wt_fn`; sharp shading at 22° | `faceted_wedge(..., ground_z=0)` |
| Colour inset along the keel | Thin shell following the keel facets | `keel_strip(...)`, same path, `wt_fn` and `dz` |
| Exact floor contact | `ground_z` shifts the blade so its lowest point after the Bevel tip shrink is Z = 0 | built in |

## Spherical or round bodies

| Cue | Technique | Code |
|---|---|---|
| Many armour panels with dark seams | Solidified shell cut by seam slabs (meridians, latitude / crown / belt, a tapered band) applied sequentially, then split into islands and classified | `panelize_sphere_shell(..., classify)` |
| Wedge-shaped centre band | ONE tapered plane per side (x = ±(XB − k·(top − z))), shared by front and rear above the band end; vertical seams below the band end | `bl.slab_cutter` rotated about Y |
| Layered plates (lower plates proud of upper) | In `classify`, return a radial raise amount (+0.010) | `raise_amount` |
| Dark rounded slots / vents with frames | Capsule cutter through the shell plus a raised dark bezel conformed to the sphere (`grow` ≈ 0.012, `rim` ≈ 0.013) | `capsule_cutter`, `slot_bezel` |
| Rivets near panel edges | One object of flattened domes (r ≈ 0.0085) | `rivet_cluster` |
| Deep layered eye / lens | Revolve: outer wall → rim → groove → inner lip → funnel → ribbed barrel → seat. Dark torus collar, domed emitter about 0.09 deep. Pocket the chassis behind it | `bl.bm_revolve`, `bl.bm_torus` |
| Horseshoe or arch surround | Annulus sector projected onto a sphere of radius R + δ, chamfered front edges, bolts on the arch | loft of projected sections |
| Dark skirt under an armour rim | Revolve profile with bolts around it | `bl.bm_revolve` + `bl.bm_cyl` |

## Surface (texture, not geometry)

- **Edge chips, specks, flecks.** Use `bl_materials.painted(...)` and set `obj['oow_wear']`: about 1.0 on exposed legs and body panels, 0.5 on bezels and surrounds, 0 elsewhere.
- **Emissive apertures.** Use `bl_materials.emitter(...)`. Secondary apertures get `obj['oow_emit_scale'] = 0.3`.
- **Geometry first.** Never use wear to stand in for missing geometry. Openings, deep grooves, layered edges and silhouette changes are mesh.

## Symmetry checklist for any repeated family

- Build the prototype once and derive the others from parameters (azimuth, mirror factor).
- Apply `mirror_factor(az)` to every off-centre detail coordinate (f, side offsets, seam side).
- Give side-specific parts mirror-consistent role names (`P`/`N`).
- Run `bl_symmetry.measure_pairs([...], plane='X')` for left/right, and `plane='Y'` when front and rear mirror each other. Paste the table into the report.
