# Orange Orb Walker - helper library (exec'd inside Blender)
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler, Quaternion

# ---------------------------------------------------------------- scene / collections
def get_scene():
    sc = bpy.data.scenes.get('OOW_Scene')
    if sc is None:
        sc = bpy.data.scenes.new('OOW_Scene')
    for w in bpy.context.window_manager.windows:
        if w.scene != sc:
            w.scene = sc
    return sc

def get_coll(name, parent):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    if c.name not in parent.children.keys():
        parent.children.link(c)
    return c

def clear_coll(c):
    for ob in list(c.objects):
        me = ob.data if ob.type == 'MESH' else None
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    for ch in c.children:
        clear_coll(ch)

# ---------------------------------------------------------------- transforms
WM = {}  # object name -> intended world matrix

def frame_matrix(origin, x_axis, z_hint=Vector((0, 0, 1))):
    """Orthonormal frame with local X along x_axis, Z as close as possible to z_hint."""
    x = Vector(x_axis).normalized()
    y = Vector(z_hint).cross(x)
    if y.length < 1e-6:
        y = Vector((0, 1, 0)).cross(x)
    y.normalize()
    z = x.cross(y).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m

def frame_z(origin, z_axis, x_hint=Vector((1, 0, 0))):
    """Frame with local Z along z_axis (for cylinders/discs)."""
    z = Vector(z_axis).normalized()
    x = Vector(x_hint) - z * Vector(x_hint).dot(z)
    if x.length < 1e-6:
        x = Vector((0, 1, 0)) - z * z.y
    x.normalize()
    y = z.cross(x).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m

def place(ob, parent, world):
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Identity(4)
    pw = WM[parent.name] if parent is not None else Matrix.Identity(4)
    ob.matrix_basis = pw.inverted() @ world
    WM[ob.name] = world.copy()

def empty(name, coll, parent, world, size=0.08, kind='PLAIN_AXES'):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    coll.objects.link(ob)
    place(ob, parent, world)
    return ob

# ---------------------------------------------------------------- mesh building
def bm_new():
    return bmesh.new()

def bm_cyl(bm, r, depth, segs=32, m=Matrix.Identity(4), r2=None):
    return bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                                 radius1=r, radius2=(r if r2 is None else r2), depth=depth, matrix=m)

def bm_sphere(bm, r, u=48, v=24, m=Matrix.Identity(4)):
    return bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r, matrix=m)

def bm_box(bm, sx, sy, sz, m=Matrix.Identity(4)):
    res = bmesh.ops.create_cube(bm, size=1.0, matrix=m @ Matrix.Diagonal((sx, sy, sz, 1.0)))
    return res

def bm_revolve(bm, profile, segs=64, m=Matrix.Identity(4)):
    """profile: closed list of (rho, h) around local Z axis (h along Z)."""
    n = len(profile)
    rings = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new(m @ Vector((rho * ca, rho * sa, h))) for (rho, h) in profile])
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % segs]
        for j in range(n):
            j1 = (j + 1) % n
            try:
                bm.faces.new((r0[j], r0[j1], r1[j1], r1[j]))
            except ValueError:
                pass
    return rings

def bm_loft(bm, sections, closed_section=True, cap_start=True, cap_end=True):
    """sections: list of lists of Vector with equal counts."""
    rings = [[bm.verts.new(p) for p in sec] for sec in sections]
    n = len(sections[0])
    rng = n if closed_section else n - 1
    for a, b in zip(rings[:-1], rings[1:]):
        for j in range(rng):
            j1 = (j + 1) % n
            bm.faces.new((a[j], a[j1], b[j1], b[j]))
    if closed_section:
        if cap_start:
            bm.faces.new(list(reversed(rings[0])))
        if cap_end:
            bm.faces.new(rings[-1])
    return rings

def bm_torus(bm, R, r, segs=48, rsegs=16, m=Matrix.Identity(4), arc=(0.0, 2 * math.pi), closed=True):
    a0, a1 = arc
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    nseg = segs if full else segs + 1
    secs = []
    for i in range(nseg):
        a = a0 + (a1 - a0) * i / segs
        c = Vector((math.cos(a), math.sin(a), 0))
        sec = []
        for k in range(rsegs):
            b = 2 * math.pi * k / rsegs
            p = c * (R + r * math.cos(b)) + Vector((0, 0, r * math.sin(b)))
            sec.append(m @ p)
        secs.append(sec)
    if full:
        secs.append(secs[0])
        rings = [[bm.verts.new(p) for p in sec] for sec in secs[:-1]]
        rings.append(rings[0])
        for a, b in zip(rings[:-1], rings[1:]):
            for j in range(rsegs):
                j1 = (j + 1) % rsegs
                bm.faces.new((a[j], a[j1], b[j1], b[j]))
        return rings
    return bm_loft(bm, secs, True, True, True)

def finish_mesh(name, bm, smooth=True, sharp_angle=35.0, recalc=True):
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        # recalc can pick the inside for some closed primitives: enforce positive signed volume
        if bm.faces and all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True) < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        set_smooth(me, sharp_angle)
    return me

def set_smooth(me, sharp_angle=35.0):
    me.shade_smooth()
    if sharp_angle is None:
        return
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.radians(sharp_angle)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            try:
                ang = e.calc_face_angle()
            except ValueError:
                ang = 0.0
            e.smooth = ang < lim
        else:
            e.smooth = True
    bm.to_mesh(me)
    bm.free()

def mesh_obj(name, me, coll, parent, world, mats=None):
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    place(ob, parent, world)
    if mats:
        for m in mats:
            me.materials.append(m)
    return ob

# ---------------------------------------------------------------- modifiers
def mod_bevel(ob, width=0.006, segs=3, angle=35.0, harden=False, limit='ANGLE'):
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width = width
    m.segments = segs
    m.limit_method = limit
    if limit == 'ANGLE':
        m.angle_limit = math.radians(angle)
    m.harden_normals = harden
    m.miter_outer = 'MITER_ARC'
    return m

def mod_solidify(ob, thick, offset=-1.0):
    m = ob.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = thick
    m.offset = offset
    m.use_even_offset = True
    m.use_quality_normals = True
    return m

def mod_subsurf(ob, levels=1, render=None):
    m = ob.modifiers.new('Subdivision', 'SUBSURF')
    m.levels = levels
    m.render_levels = levels if render is None else render
    return m

def get_dg():
    sc = bpy.data.scenes.get('OOW_Scene')
    if sc is None or bpy.context.scene == sc:
        return bpy.context.evaluated_depsgraph_get()
    dg = sc.view_layers[0].depsgraph
    dg.update()
    return dg

def apply_modifiers(ob):
    dg = get_dg()
    ev = ob.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ob

def bool_apply(ob, cutter_coll, op='DIFFERENCE', solver='EXACT'):
    m = ob.modifiers.new('Bool', 'BOOLEAN')
    m.operation = op
    m.operand_type = 'COLLECTION'
    m.collection = cutter_coll
    m.solver = solver
    try:
        m.use_self = True
        m.use_hole_tolerant = True
    except Exception:
        pass
    apply_modifiers(ob)
    return ob

def split_islands(ob):
    """Return list of (centroid_world, bmesh) for each connected component of ob.data (object-local coords)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    seen = set()
    islands = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]
        comp = []
        seen.add(v.index)
        while stack:
            cur = stack.pop()
            comp.append(cur.index)
            for e in cur.link_edges:
                o = e.other_vert(cur)
                if o.index not in seen:
                    seen.add(o.index)
                    stack.append(o)
        islands.append(comp)
    out = []
    for comp in islands:
        cs = set(comp)
        nb = bm.copy()
        nb.verts.ensure_lookup_table()
        kill = [vv for vv in nb.verts if vv.index not in cs]
        bmesh.ops.delete(nb, geom=kill, context='VERTS')
        cen = Vector()
        for vv in nb.verts:
            cen += vv.co
        cen /= max(1, len(nb.verts))
        out.append((cen, nb, len(nb.verts)))
    bm.free()
    return out

# ---------------------------------------------------------------- sphere helpers
def sph_dir(az_deg, el_deg):
    a, e = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))

def bezier(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t

def bezier3(p0, p1, p2, p3, t):
    u = 1 - t
    return p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3

def path_frames(pts, up_hint):
    """Parallel-ish frames along polyline: returns list of (p, tangent, side, normal)."""
    out = []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t.normalize()
        side = t.cross(up_hint)
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        nrm = side.cross(t).normalized()
        out.append((p, t, side, nrm))
    return out
