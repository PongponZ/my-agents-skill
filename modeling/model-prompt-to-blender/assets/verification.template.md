# <Display name> — verification report

Executed from `<prompt file>` on <date>. All paths are absolute. Statements are what was produced and checked, not a claim of pixel-perfect or engineering accuracy.

Output directory: `<path>`

## 0. Revisions
<!-- newest first: "## 0b. Revision N (user request: ...)": what changed, why, re-done outputs, new deviations -->

## 1. Delivered files (existence and decode verified)
| File | Status | Check |
|---|---|---|
| `<asset>_blockout.blend` / `.png` | | reopened in background Blender (`verify_blend.py`) |
| `<asset>_detailed.blend` | | |
| `<asset>_final.blend` | | |
| `<images>` | WxH PNG | `img_tools.py check` (decode, size, opaque, white clipping) |
| `verification.md` | this file | |

## 2. Environment and settings
Blender version and connection, engine and device (`Stage.device_info`: GPU backend + device names, or the CPU fallback and why), samples/denoiser, colour management (view transform, look, exposure), measured render times, MCP timeouts and how completion was confirmed.

## 3. Scene organisation and decisions
- Dedicated scene, collections, hierarchy (pivots), modifiers kept live, D=1 convention, body height.
- Decisions table: ID, issue, selected, reason, evidence status (handedness, symmetry, centred parts, ranges...).

## 4. Gates
| Gate | Result | Evidence |
|---|---|---|
| Blockout / reference match | | overlay sheets |
| Symmetry (neutral) | | §6 table |
| Phase A detailed mesh (close-up review) | | rounds, repairs |
| Topology (`bl_check`) | | base issues, modifier artifacts |
| Phase B materials/textures | | clay vs material, emission off |
| Delivery (reopen, images) | | |

## 5. Feature coverage
| Feature ID | Source region / crop | Expected | Implementation (objects) | Evidence image | Status (pass / fail / not_verified / allowed_simplification) | Correction |
|---|---|---|---|---|---|---|

## 6. Symmetry
<!-- paste bl_symmetry.table(rows); members, plane, tolerance, exceptions; neutral vs posed kept separate -->

## 7. View-by-view inspection
| View | Method | Finding | Status |
|---|---|---|---|

## 8. Geometry checks
Counts, measured proportions vs brief guides (with deviations), contacts and clearances, base-mesh issues, modifier artifacts, open boundaries (intended?), duplicates, hidden objects, size.

## 9. Materials and lighting
Material table (ID, assignment, settings), wear/emission object properties, diagnostic or presentation stage, measured luma/clipping and trade-offs.

## 10. Reopen check (separate background process)
Scenes, collections, objects, cameras, materials, render state, texts, images/libraries, limits of the check.

## 11. Fidelity — honest qualitative differences

## 12. Proposed / inferred items (retained uncertainty)

## 13. Not done / out of scope
