# Compact prompt artifact contract

The deliverable has two kinds of content: a main prompt and part reference/prompt pairs. Authoring evidence may remain in the project, but the archive includes only this structure:

```text
<name>/
  main_prompt.md
  parts/
    00-overview/
      prompt.md
      reference.png
    body/
      prompt.md
      reference.png
      detail.png
    legs/
      prompt.md
      reference.png
```

Use only as many meaningful parts and images as necessary. Overview owns the overall silhouette, assembly and whole-subject reference; other parts own local detail. A small asset may use just the overview part. Paired/repeated components normally share a part prompt with explicit exceptions.

## Reference layout and generation

Image 1 is `parts/00-overview/reference.png`: the whole assembled asset in labeled FRONT, TOP and SIDE orthographic views, in that reading order, with consistent pose, scale, axes and design. Specify the side direction. All three views must exist in the pixels; labels alone do not satisfy this requirement. Reuse a compliant existing image or generate a new one conditioned on the supplied source.

For a source containing multiple parts, generate a new standalone image for each modeled part from the full source and the reviewed overview. Do not crop, split, mask, upscale or copy a sheet panel to serve as that part's reference. Each new image shows the complete part and its attachment interfaces, with the views needed to explain its construction. Check it against the overview before accepting it. Supplementary detail images follow the same generate-new rule.

Each part prompt links `reference.png` first. Identify generated interpretations and uncertain/unseen surfaces in that prompt; selected generated details are design targets, not source observations. Keep original images and analytical crops as working evidence outside the ZIP. Image generation or saving failure blocks final delivery; do not fall back to a crop. This does not add generation-brief or QA files to the compact artifact.

## Main prompt

Include the goal and intended use; scope; scale, axes and handedness; final pose; global proportions and locked decisions; an ordered index of **every** part prompt with its role and dependencies; phase gates; expected model outputs. Preserve user-specified execution constraints. Keep local feature inventories out of main.

The executor reads main and overview first. Load only the active part and relevant dependencies thereafter, including when returning for materials or verification. Read all parts eventually, not all at once. Maintain per-part/feature status in the model output's verification report; after context loss reload main, progress and active part. All required parts must pass before completion.

## Part prompt

Use the headings `## Reference`, `## Build`, `## Check`, each with substantive content. The body may use the requested language.

- **Reference:** link `reference.png` first, then any necessary newly generated detail images. Describe original/generated provenance, view directions, the aspects each image controls, and observed/inferred/proposed labels. The overview names FRONT/TOP/SIDE; part references state their source conditioning and selected design targets. Generated interpretations remain labeled even when binding. PNG conversion preserves pixels but cannot substitute for required generation.
- **Build:** owned component/feature IDs; affirmative geometry inventory (location, supported count, profile, depth, layers, cross-section); interfaces and dependencies; geometry versus texture; symmetry/shared parameters and exceptions; material zones and texture placement; allowed simplifications and hidden-geometry choices. Carry measured values with units, frame, datum, basis and tolerance when justified. Qualitative checks are valid when source evidence cannot support numbers.
- **Check:** feature IDs, matching model views, selected reference links and observable acceptance; topology/attachment checks relevant to this part, surface checks and explicit failure conditions. Preserve required close-up and prototype comparisons. Do not copy global workflow boilerplate into every part.

Record part-to-part interfaces with a single owner and link that owner's prompt from dependent parts. Carry the dependency order in main so reading one part does not require searching the entire project. If a critical source is missing or decisions conflict, resolve them before declaring the package ready.

## Links and packaging

Use plain inline Markdown links with ASCII lowercase paths and no spaces, titles, queries or fragments. Main indexes `parts/00-overview/prompt.md` first, followed by the part prompts; part prompts link images in their own folder, e.g. `![Reference](reference.png)`, and may link another indexed part, e.g. `[Body interface](../body/prompt.md)`. Link main as `../../main_prompt.md` only when useful. Part IDs and PNG stems use lowercase alphanumeric words separated by hyphens. Use forward slashes. Reference-style links and HTML image tags are not supported.

Each part must link at least one PNG and be directly indexed in main. Dependencies must point to indexed prompts; do not rely on implicit recursive discovery. Only linked images are shipped. The packager rejects missing/empty files, paths escaping the project, unsupported targets, unfilled template slots and malformed PNG containers. It verifies archived bytes and CRCs but does not certify image decoding, visual fidelity, semantic QA or feature coverage. The author visually inspects sources and reviews every required feature before running it.

Do not ship analysis JSON/Markdown, build specs, concept-generation prompts, QA reports, handoff/usage documents, duplicate language versions, manifests or unused images. Important content from those documents must be distilled into the owning main/part prompt, not simply dropped. No packaged instruction may depend on an excluded file.

## Existing handoffs

Use existing `analysis.json`, `details.md`, `build_spec.json`, selected concept panels and QA as authoring inputs when present. Reuse IDs and decisions, but replace old multi-part panels/crops with newly generated focused references. Review old unresolved decisions and stale generators before conversion; preserve originals and outputs. New archives use this compact layout and need no legacy schema files at runtime. Hand the result to a separate modeling workflow; this skill set ends at prompt delivery.
