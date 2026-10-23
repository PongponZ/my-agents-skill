"""Reopen a saved .blend in a SEPARATE background Blender and dump what it contains.

    "<blender.exe>" -b "<file.blend>" --factory-startup --python verify_blend.py -- <out.json> <ASSET_COLLECTION> [<SCENE>]

Never reopen in the user's live session (that would replace their open file). Prints VERIFY_OK.
"""
import sys, json
import bpy

argv = sys.argv[sys.argv.index('--') + 1:]
out, coll_name = argv[0], argv[1]
scene_name = argv[2] if len(argv) > 2 else None
r = {'file': bpy.data.filepath, 'file_version': list(bpy.data.version), 'scenes': {}}
for s in bpy.data.scenes:
    r['scenes'][s.name] = {'objects': len(s.objects), 'engine': s.render.engine}
sc = bpy.data.scenes.get(scene_name) if scene_name else bpy.context.scene
col = bpy.data.collections.get(coll_name)
r['collection_found'] = col is not None
if col:
    objs = list(col.all_objects)
    r['subcollections'] = [c.name for c in col.children]
    r['n_objects'] = len(objs)
    r['n_mesh'] = sum(o.type == 'MESH' for o in objs)
    r['cameras'] = {o.name: o.data.type for o in objs if o.type == 'CAMERA'}
    r['lights'] = sorted(o.name for o in objs if o.type == 'LIGHT')
    r['materials'] = sorted({m.name for o in objs if o.type == 'MESH' for m in o.data.materials if m})
    r['hidden_render'] = sorted(o.name for o in objs if o.hide_render)
    r['modifiers_live'] = sum(len(o.modifiers) for o in objs)
    r['evidence_tags'] = {}
    for o in objs:
        e = o.get('oow_evidence')
        if e:
            r['evidence_tags'][e] = r['evidence_tags'].get(e, 0) + 1
if sc:
    r['scene'] = sc.name
    r['scene_camera'] = sc.camera.name if sc.camera else None
    r['render'] = dict(engine=sc.render.engine, res=[sc.render.resolution_x, sc.render.resolution_y,
                       sc.render.resolution_percentage], view_transform=sc.view_settings.view_transform,
                       look=sc.view_settings.look, exposure=sc.view_settings.exposure)
r['texts'] = [t.name for t in bpy.data.texts]
r['images'] = [(i.name, i.filepath, bool(i.packed_file)) for i in bpy.data.images if i.source == 'FILE']
r['missing_images'] = [i.name for i in bpy.data.images if i.source == 'FILE' and not i.packed_file and not i.has_data]
r['libraries'] = [l.filepath for l in bpy.data.libraries]
json.dump(r, open(out, 'w', encoding='utf-8'), indent=1)
print('VERIFY_OK')
