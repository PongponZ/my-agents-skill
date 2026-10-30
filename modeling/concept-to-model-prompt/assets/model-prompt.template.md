# {{display_name}} — Main modeling prompt

{{goal_intended_use_and_scope}}
{{scale_axes_handedness_final_pose_global_proportions_and_locked_decisions}}
{{tool_constraints_scene_preservation_and_output_directory}}

## Parts and reading order

Read this file and the overview first. Load only the active part's prompt, images and necessary dependencies. Revisit that part for materials and verification. Do not preload the entire package.

Image 1, linked inside the overview prompt, shows the assembled asset from FRONT, TOP and SIDE. The following part prompts pair focused reference images with their own construction instructions. Generated views are selected design targets; their provenance and uncertainties are stated in each part.

| Order | Part prompt | Role | Depends on |
|---|---|---|---|
{{ordered_links_to_every_parts_part_id_prompt_md_including_overview}}

## Build and verification gates

{{blockout_and_overall_proportions_gate}}
{{prototype_symmetry_and_interface_gate}}

Phase A: implement each part's required geometry and compare close-ups against its selected references. Record missing/wrong features, repair failures and recheck. Pass all required mesh and topology checks before Phase B; a correct first pass needs no artificial edit.

Phase B: load each part's material/texture instructions and check its surfaces. Return to Phase A for geometry defects or shape-changing displacement. Use diagnostic views within the declared scope.

Keep part/feature IDs, pass/fail/pending/not_verified, evidence paths and next actions in the model output's verification report. After context loss, read this main prompt, that progress record and the active part. Finish only when every indexed part and required feature passes; unavailable verification remains not_verified.

## Delivery

{{editable_blend_checkpoints_texture_resources_diagnostic_comparisons_and_verification_outputs}}
{{save_resource_and_reopen_checks_with_tool_limitations}}
