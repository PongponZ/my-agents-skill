# Run with: blender -b <file.blend> --python verify_blend.py -- <out.json>
import bpy, sys, json
out = sys.argv[sys.argv.index('--') + 1]
r = {}
r['file'] = bpy.data.filepath
r['version_file'] = list(bpy.data.version)
r['scenes'] = [s.name for s in bpy.data.scenes]
sc = bpy.data.scenes.get('OOW_Scene')
r['active_scene_window'] = bpy.context.window.scene.name if bpy.context.window else None
r['oow_scene_present'] = sc is not None
if sc:
    col = bpy.data.collections.get('ORANGE_ORB_WALKER')
    r['subcollections'] = [c.name for c in col.children] if col else None
    objs = list(col.all_objects) if col else []
    r['n_objects'] = len(objs)
    r['n_mesh'] = sum(o.type == 'MESH' for o in objs)
    r['cameras'] = sorted(o.name for o in objs if o.type == 'CAMERA')
    r['camera_types'] = {o.name: o.data.type for o in objs if o.type == 'CAMERA'}
    r['lights'] = sorted(o.name for o in objs if o.type == 'LIGHT')
    r['scene_camera'] = sc.camera.name if sc.camera else None
    r['engine'] = sc.render.engine
    r['device'] = sc.cycles.device
    r['samples'] = sc.cycles.samples
    r['resolution'] = [sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage]
    r['view_transform'] = sc.view_settings.view_transform
    r['look'] = sc.view_settings.look
    r['exposure'] = sc.view_settings.exposure
    r['legs'] = sorted(o.name for o in objs if o.type == 'EMPTY' and o.parent and o.parent.name == 'C01_Chassis' and o.name[:4] in ('C11_', 'C12_'))
    r['arms'] = sorted(o.name for o in objs if o.name.startswith('C08_Arm_'))
    r['materials'] = sorted({m.name for o in objs if o.type == 'MESH' and not o.name.startswith('PRES_') for m in o.data.materials if m})
    r['hidden_render'] = sorted(o.name for o in objs if o.hide_render)
    r['proposed_or_inferred'] = sorted(o.name for o in objs if o.get('oow_evidence') in ('proposed', 'inferred'))
    r['root_note'] = col.objects['OOW_ROOT'].get('oow_note') if col and 'OOW_ROOT' in col.objects else None
    r['texts'] = [t.name for t in bpy.data.texts]
    r['modifiers_live'] = sum(len(o.modifiers) for o in objs)
orig = bpy.data.scenes.get('Scene')
if orig:
    r['original_scene_objects'] = sorted(o.name for o in orig.objects)
    r['original_scene_engine'] = orig.render.engine
r['images'] = [(i.name, i.filepath, bool(i.packed_file)) for i in bpy.data.images if i.source == 'FILE']
r['libraries'] = [l.filepath for l in bpy.data.libraries]
json.dump(r, open(out, 'w'), indent=1)
print('VERIFY_OK')
