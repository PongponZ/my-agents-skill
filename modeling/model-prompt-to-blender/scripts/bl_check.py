"""Targeted mesh / scene validation (run inside Blender).

    import bl_check as bc
    res = bc.check(asset_coll_name='MYASSET', scene_name='MYASSET_Scene', ground_z=0.0,
                   counts={'walking_legs': r'^C1[12]_(?!.*_).*$'})
    print(bc.summary(res))

Per evaluated mesh: non-manifold / boundary edges, inconsistent winding across manifold edges,
degenerate faces, zero-length edges, loose verts, duplicate faces, signed volume when closed.
Across meshes: exact duplicate objects (same rounded world-vertex set), lowest point vs ground.
Signed volume or centroids alone are NOT evidence of correct normals / no duplicates; this
module checks winding and vertex sets explicitly. Open boundaries can be intentional: report,
do not auto-fail them; decide per object in verification.md.
'issues' = defects in the authored (base) mesh -> fix them. 'modifier_artifacts' = extra defects
that only appear after modifiers (typically zero-area Bevel miter triangles where seams meet) ->
inspect visually and report as advisory if invisible.
"""
import re, json, hashlib
import bpy, bmesh
from mathutils import Vector


def _mesh_stats(bm):
    st = {}
    st['nonmanifold_edges'] = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    st['boundary_edges'] = sum(1 for e in bm.edges if e.is_boundary)
    bad_wind = 0
    for e in bm.edges:
        if len(e.link_loops) == 2:
            l1, l2 = e.link_loops
            if l1.vert == l2.vert:          # both faces traverse the edge in the same direction
                bad_wind += 1
    st['inconsistent_winding_edges'] = bad_wind
    st['degenerate_faces'] = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
    st['zero_length_edges'] = sum(1 for e in bm.edges if e.calc_length() < 1e-9)
    st['loose_verts'] = sum(1 for v in bm.verts if not v.link_edges)
    keys = {}
    dup = 0
    for f in bm.faces:
        k = tuple(sorted(v.index for v in f.verts))
        if k in keys:
            dup += 1
        keys[k] = 1
    st['duplicate_faces'] = dup
    closed = st['boundary_edges'] == 0 and st['nonmanifold_edges'] == 0
    st['closed'] = closed
    st['signed_volume'] = round(bm.calc_volume(signed=True), 8) if closed else None
    return st


def check(asset_coll_name, scene_name, ground_z=0.0, exclude_prefix='PRES_', counts=None, tag_prefix='oow'):
    col = bpy.data.collections[asset_coll_name]
    sc = bpy.data.scenes[scene_name]
    dg = sc.view_layers[0].depsgraph
    dg.update()
    res = {'meshes': 0, 'faces': 0, 'issues': {}, 'open_boundaries': {}, 'inverted_closed': [],
           'duplicate_objects': [], 'lowest': [], 'below_ground': []}
    hashes = {}
    lows = []
    for o in col.all_objects:
        if o.type != 'MESH' or o.name.startswith(exclude_prefix) or o.get('oow_support'):
            continue
        res['meshes'] += 1
        keys = ('nonmanifold_edges', 'inconsistent_winding_edges', 'degenerate_faces', 'zero_length_edges',
                'loose_verts', 'duplicate_faces')
        # base mesh = authored geometry; evaluated = after modifiers (Bevel can add zero-area miter tris)
        bb = bmesh.new()
        bb.from_mesh(o.data)
        base = _mesh_stats(bb)
        bb.free()
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.ensure_lookup_table()
        res['faces'] += len(bm.faces)
        st = _mesh_stats(bm)
        bad = {k: base[k] for k in keys if base[k]}
        if bad:
            res['issues'][o.name] = bad
        mod_only = {k: st[k] - base[k] for k in keys if st[k] > base[k]}
        if mod_only:
            res.setdefault('modifier_artifacts', {})[o.name] = mod_only
        if st['boundary_edges']:
            res['open_boundaries'][o.name] = st['boundary_edges']
        if st['closed'] and st['signed_volume'] is not None and st['signed_volume'] < 0:
            res['inverted_closed'].append(o.name)
        mw = o.matrix_world
        wv = [mw @ v.co for v in bm.verts]
        if wv:
            lows.append((min(p.z for p in wv), o.name))
            h = hashlib.md5(json.dumps(sorted((round(p.x, 4), round(p.y, 4), round(p.z, 4)) for p in wv)).encode()).hexdigest()
            if h in hashes:
                res['duplicate_objects'].append((o.name, hashes[h]))
            hashes[h] = o.name
        bm.free()
        ev.to_mesh_clear()
    lows.sort()
    res['lowest'] = [(round(z, 5), n) for z, n in lows[:6]]
    res['below_ground'] = [(round(z, 5), n) for z, n in lows if z < ground_z - 1e-4]
    objs = list(col.all_objects)
    if counts:
        res['counts'] = {k: sorted(o.name for o in objs if re.search(p, o.name)) for k, p in counts.items()}
    asset = [o for o in objs if not o.name.startswith(exclude_prefix) and not o.get('oow_support')]
    res['materials_used'] = sorted({m.name for o in asset if o.type == 'MESH' for m in o.data.materials if m})
    res['empty_material_slots'] = sorted(o.name for o in objs if o.type == 'MESH' and any(m is None for m in o.data.materials))
    res['hidden'] = sorted(o.name for o in objs if o.hide_render or o.hide_get())
    res['images'] = [(i.name, i.filepath, i.packed_file is not None) for i in bpy.data.images if i.source == 'FILE']
    res['tagged_inferred_or_proposed'] = sum(1 for o in objs if o.get(tag_prefix + '_evidence') in ('inferred', 'proposed'))
    return res


def inspect_saved_blend(path):
    """Read-only look into a saved .blend from INSIDE the live session (no shell needed):
    lists datablock names without opening or appending anything. Weaker than a background
    reopen (verify_blend.py) - use it when no local shell is available and say so in the report."""
    import os
    info = {'path': path, 'exists': os.path.exists(path), 'bytes': os.path.getsize(path) if os.path.exists(path) else 0}
    if not info['exists']:
        return info
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        info.update(scenes=list(src.scenes), objects=len(src.objects), meshes=len(src.meshes),
                    materials=list(src.materials), cameras=list(src.cameras), lights=list(src.lights),
                    collections=list(src.collections), images=list(src.images), texts=list(src.texts))
    return info


def summary(res):
    keys = ('meshes', 'faces', 'issues', 'modifier_artifacts', 'inverted_closed', 'duplicate_objects', 'below_ground', 'lowest',
            'empty_material_slots', 'counts', 'materials_used', 'hidden', 'images', 'open_boundaries')
    return json.dumps({k: res.get(k) for k in keys if k in res}, indent=1, default=str)
