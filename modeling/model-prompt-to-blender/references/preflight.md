# Preflight: read the package before modeling

Run this before the blockout. Record every resolution in the build script header and in `verification.md` under "Decisions". Ask the user only when identity or scope would change. Resolve the rest with the documented precedence: user constraints → primary reference identity → selected concept panels for assigned details → other evidence.

## 1. Inventory the inputs

- Read every file the prompt lists: analysis/build_spec JSON, details, QA, handoff and usage. Note the schema version.
  - v3: use `feature_plan`, `phases`, `detail_crops` and `measurements` directly.
  - v1/v2: build your own feature list from the components and their details/inspection criteria.
- Open the actual pixels of the primary reference and the concept sheet. Crop and zoom every identity-critical region:

  ```
  python img_tools.py crop <ref> <out> x0 y0 x1 y1 --scale 2
  python img_tools.py cropn <sheet> <out> x y w h
  ```

- List the concept panels that carry detail (for example `C04+C05`, `C11`, tool panels). For a v3 package, check `design_source` to see which panels are binding.

## 2. Conflicts to check explicitly

| Check | What went wrong before | Resolution |
|---|---|---|
| **Handedness** | The brief said "+X = robot right, source-left tool on +X" with front = −Y. In a front view +X is on the image right, so following that literally mirrors the tools. | Pick an asymmetric landmark (a unique tool or emblem) and verify that the planned axes put it on the same image side as the primary reference. Record which side is robot-right. |
| **Symmetry intent** | The brief said "preserve the original spread rather than a centred symmetric pose". The asymmetric legs that resulted did not match the concept sheet, and the user wanted symmetry. | Decide per family: a symmetric neutral build (default for intended pairs) versus a source pose. Note which one the user or concept prefers. |
| **Centred parts** | The ring/core height was unspecified. Reading it from the perspective reference placed it low, and the user wanted it centred. | When the concept front view shows a feature centred, build it centred, and say so. |
| **Numeric ranges vs concept** | The 1.8–2.1D leg span disagreed with the concept front view (≈1.7D). | Measure the concept views. Follow the higher-priority source, and report the deviation from the other range. |
| **Competing goals** | "Core is the brightest landmark" competed with "yellow centre, not a white hole" under the display transform. | Choose one priority and report the measured luma of both. |
| **Detail inventory** | "Small dark recesses" and similar wording gave no count, size or position. | Turn every vague phrase into a concrete inventory row (count, size, position, mesh or texture) taken from the crops. If the crops cannot answer, mark it inferred. |
| **Scope** | Presentation lighting and hero renders were in some briefs and excluded in v3. | Follow `build_spec.scope` exactly. |
| **Restrictive wording** | "Restrained", "do not transfer generated variations" and similar phrases led to under-detailed geometry. | Still implement every required feature at the density the crops show. "Restrained" constrains wear intensity, not geometry. |

## 3. Detail inventory table (write it before modeling)

| Feature ID | Component | Source crop | What must exist (count, size, layers) | Mesh / texture | Technique | Check view |
|---|---|---|---|---|---|---|

Fill in one row per required feature. For v3 packages copy `feature_plan` and add the technique column. This table becomes the coverage table in `verification.md`.

## 4. Scale and axes

- Working unit: D = 1, the main-body diameter, unless the brief gives one. It is not metres.
- Axes: +Z up, front −Y, ground Z = 0. Root empty at the ground projection of the body centre.
- Body height follows the foot/ground contacts. Never stretch limbs to reach the floor.
