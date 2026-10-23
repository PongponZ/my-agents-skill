"""Structural symmetry measurements for paired components (run inside Blender).

    import bl_symmetry as bs
    rows = bs.measure_pairs([('C11_RF', 'C11_LF'), ('C11_RR', 'C12_LR')], plane='X',
                            origin=(0, 0, 0), tolerance=0.002, scene='MYASSET_Scene')
    print(bs.table(rows))

For each pair of hierarchy roots (empties or meshes), member B is mirrored across the plane and
compared with member A, part by part. Parts are matched by role = name with the root name removed
(e.g. 'C11_RF_KneeHub' and 'C11_LF_KneeHub' -> '_KneeHub'):
- pivot delta: |A.root - mirror(B.root)|
- per part: centroid delta and axis-aligned extent delta (both invariant to tessellation phase)
- vertex-count mismatches and parts present on one side only
- informational: nearest-vertex distance mirror(B) -> A (max/mean; sensitive to tessellation phase)
Status uses pivot, centroid and extent deltas against `tolerance`.
Measure the NEUTRAL construction before intentional posing; report posed checks separately.
plane: 'X' (left/right about x = origin.x) or 'Y' (front/rear about y = origin.y).
"""
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree


def _mirror(p, plane, origin):
    p = Vector(p)
    if plane == 'X':
        p.x = 2 * origin[0] - p.x
    elif plane == 'Y':
        p.y = 2 * origin[1] - p.y
    else:
        raise ValueError(plane)
    return p


def _parts(root, dg):
    out = {}
    for o in [root] + list(root.children_recursive):
        if o.type != 'MESH':
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        pts = [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
        role = o.name[len(root.name):] if o.name.startswith(root.name) else o.name
        out[role] = pts
    return out


def _stats(pts):
    c = sum(pts, Vector()) / len(pts)
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return c, mx - mn


def measure_pairs(pairs, plane='X', origin=(0, 0, 0), tolerance=0.002, scene=None):
    sc = bpy.data.scenes[scene] if scene else bpy.context.scene
    dg = sc.view_layers[0].depsgraph
    dg.update()
    rows = []
    for a_name, b_name in pairs:
        A, B = bpy.data.objects[a_name], bpy.data.objects[b_name]
        pa, pb = _parts(A, dg), _parts(B, dg)
        pivot = (A.matrix_world.translation - _mirror(B.matrix_world.translation, plane, origin)).length
        only = sorted(set(pa) ^ set(pb))
        count_mm, worst = [], (0.0, None)
        for role in sorted(set(pa) & set(pb)):
            va = pa[role]
            vb = [_mirror(p, plane, origin) for p in pb[role]]
            if len(va) != len(vb):
                count_mm.append(role)
            if not va or not vb:
                continue
            ca, ea = _stats(va)
            cb, eb = _stats(vb)
            d = max((ca - cb).length, max(abs(x) for x in (ea - eb)))
            if d > worst[0]:
                worst = (d, role)
        allA = [p for v in pa.values() for p in v]
        allB = [_mirror(p, plane, origin) for v in pb.values() for p in v]
        vmax = vmean = None
        if allA and allB:
            kd = KDTree(len(allA))
            for i, p in enumerate(allA):
                kd.insert(p, i)
            kd.balance()
            ds = [kd.find(p)[2] for p in allB]
            vmax, vmean = max(ds), sum(ds) / len(ds)
        ok = pivot <= tolerance and worst[0] <= tolerance and not only and not count_mm
        rows.append(dict(pair=(a_name, b_name), plane=plane, pivot_delta=round(pivot, 6),
                         part_delta_max=round(worst[0], 6), worst_part=worst[1],
                         vertex_nn_max=None if vmax is None else round(vmax, 6),
                         vertex_nn_mean=None if vmean is None else round(vmean, 6),
                         parts=(len(pa), len(pb)), unmatched_parts=only, count_mismatch=count_mm,
                         tolerance=tolerance, status='pass' if ok else 'fail'))
    return rows


def table(rows):
    lines = ['| Pair | Plane | Pivot delta | Worst part delta (part) | Vertex NN max / mean | Parts | Unmatched / count mismatch | Tolerance | Status |',
             '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        lines.append('| %s / %s | %s | %.6f | %.6f (%s) | %s / %s | %d / %d | %s / %s | %g | %s |' % (
            r['pair'][0], r['pair'][1], r['plane'], r['pivot_delta'], r['part_delta_max'], r['worst_part'],
            r['vertex_nn_max'], r['vertex_nn_mean'], r['parts'][0], r['parts'][1],
            ', '.join(r['unmatched_parts']) or '-', ', '.join(r['count_mismatch']) or '-', r['tolerance'], r['status']))
    return '\n'.join(lines)
