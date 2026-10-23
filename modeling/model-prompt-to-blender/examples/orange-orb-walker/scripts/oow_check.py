# geometry / scene checks (exec'd in Blender); prints a JSON-ish summary
import bpy, bmesh, json
from mathutils import Vector
root = bpy.data.collections['ORANGE_ORB_WALKER']
sc = bpy.data.scenes['OOW_Scene']
dg = sc.view_layers[0].depsgraph
dg.update()
res = dict(neg=[], nonmanifold=[], dups=[], meshes=0, faces=0)
minz = []
sigs = {}
for o in root.all_objects:
    if o.type != 'MESH' or o.name.startswith('PRES_'):
        continue
    res['meshes'] += 1
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    res['faces'] += len(bm.faces)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    if nonman:
        res['nonmanifold'].append((o.name, nonman))
    elif bm.calc_volume(signed=True) < 0:
        res['neg'].append(o.name)
    mw = o.matrix_world
    minz.append((min((mw @ v.co).z for v in bm.verts), o.name))
    cen = sum(((mw @ v.co) for v in bm.verts), Vector()) / len(bm.verts)
    key = (len(bm.verts), tuple(round(c, 3) for c in cen))
    if key in sigs:
        res['dups'].append((o.name, sigs[key]))
    sigs[key] = o.name
    bm.free(); ev.to_mesh_clear()
minz.sort()
res['lowest'] = [(round(z, 5), n) for z, n in minz[:6]]
res['chin_min_z'] = round(next(z for z, n in minz if n == 'C07_ChinPod'), 4)
res['c10_blade_min_z'] = round(next(z for z, n in minz if n == 'C10_HangingBlade'), 4)
res['below_floor'] = [(round(z, 5), n) for z, n in minz if z < -1e-4]
# counts
objs = root.all_objects
res['walking_legs'] = sorted(o.name for o in objs if o.type == 'EMPTY' and o.parent and o.parent.name == 'C01_Chassis'
                            and (o.name.startswith('C11_') or o.name.startswith('C12_')))
res['arms'] = sorted(o.name for o in objs if o.name.startswith('C08_Arm_'))
res['tools'] = sorted(o.name for o in objs if o.name in ('C09_Tool', 'C10_Tool'))
res['core_emitters'] = sorted(o.name for o in objs if o.name.startswith('C05'))
res['roof_masses'] = sorted(o.name for o in objs if o.name in ('C06_Housing', 'C06_RearMass'))
res['chin'] = sorted(o.name for o in objs if o.name == 'C07_ChinPod')
emitters = [o.name for o in objs if o.type == 'MESH' and o.data.materials and o.data.materials[0] and o.data.materials[0].name == 'M05_Emitter']
res['emissive_objects'] = emitters
res['materials_used'] = sorted({m.name for o in objs if o.type == 'MESH' and not o.name.startswith('PRES_') for m in o.data.materials if m})
res['hidden'] = [o.name for o in objs if o.hide_render or o.hide_get()]
res['images'] = [(i.name, i.filepath, i.packed_file is not None) for i in bpy.data.images if i.source == 'FILE']
res['missing_files'] = []
try:
    bpy.ops.file.report_missing_files()
except Exception as e:
    res['missing_files'] = str(e)
c = sum(1 for o in objs if o.get('oow_evidence') in ('inferred', 'proposed'))
res['tagged_inferred_or_proposed'] = c
print(json.dumps(res, indent=1))
CHECK = res
