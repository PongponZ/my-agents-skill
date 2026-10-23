"""Core procedural-modeling helpers for Blender (bpy + bmesh).

Import inside Blender (e.g. through the Blender MCP execute tool):

    import sys, importlib
    sys.path.insert(0, r"<skills>/model-prompt-to-blender/scripts")
    import bl_build as bl; importlib.reload(bl)
    bl.CTX.update(scene='MYASSET_Scene', detailed=True)

Conventions
- Build bmesh geometry in WORLD coordinates, then call mk(): it converts the mesh into the
  local frame of the object's pivot matrix and parents it without parent-inverse tricks.
- Every object gets oow-style tags (component id, evidence, note) as custom properties.
- Keep useful modifiers live (Bevel etc.); apply only what must be applied (shell Booleans).
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

CTX = {'scene': 'MODEL_Scene', 'detailed': True, 'tag_prefix': 'oow'}
WM = {}   # object name -> intended world matrix (used by place())


# ----------------------------------------------------------------------------- scene / collections
def get_scene(name=None, activate=True):
    """Dedicated scene for the asset: keeps the user's existing scenes and settings untouched."""
    name = name or CTX['scene']
    sc = bpy.data.scenes.get(name) or bpy.data.scenes.new(name)
    if activate:
        for w in bpy.context.window_manager.windows:
            if w.scene != sc:
                w.scene = sc
    return sc


def get_coll(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children.keys():
        parent.children.link(c)
    return c


def clear_coll(c, recursive=True):
    """Delete objects (and orphaned meshes) in a collection. Only call on collections you own."""
    for ob in list(c.objects):
        me = ob.data if ob.type == 'MESH' else None
        bpy.data.objects.remove(ob, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    if recursive:
        for ch in c.children:
            clear_coll(ch)


def get_dg():
    sc = bpy.data.scenes.get(CTX['scene'])
    if sc is None or bpy.context.scene == sc:
        return bpy.context.evaluated_depsgraph_get()
    dg = sc.view_layers[0].depsgraph
    dg.update()
    return dg


# ----------------------------------------------------------------------------- frames / placement
def frame_matrix(origin, x_axis, z_hint=Vector((0, 0, 1))):
    """Right-handed frame: local X along x_axis, local Z as close as possible to z_hint."""
    x = Vector(x_axis).normalized()
    y = Vector(z_hint).cross(x)
    if y.length < 1e-6:
        y = Vector((0, 1, 0)).cross(x)
    y.normalize()
    z = x.cross(y).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m


def frame_z(origin, z_axis, x_hint=None):
    """Right-handed frame with local Z along z_axis (cylinders, discs, revolves).
    Default x_hint = world up for non-vertical axes: tessellation of revolves then starts at the
    top on both members of a mirrored pair, so paired meshes mirror vertex-for-vertex."""
    z = Vector(z_axis).normalized()
    if x_hint is None:
        x_hint = Vector((0, 0, 1)) if abs(z.z) < 0.9 else Vector((1, 0, 0))
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


# ----------------------------------------------------------------------------- bmesh primitives
def bm_new():
    return bmesh.new()


def bm_cyl(bm, r, depth, segs=32, m=Matrix.Identity(4), r2=None):
    return bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                                 radius1=r, radius2=(r if r2 is None else r2), depth=depth, matrix=m)


def bm_sphere(bm, r, u=48, v=24, m=Matrix.Identity(4)):
    return bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r, matrix=m)


def bm_box(bm, sx, sy, sz, m=Matrix.Identity(4)):
    return bmesh.ops.create_cube(bm, size=1.0, matrix=m @ Matrix.Diagonal((sx, sy, sz, 1.0)))


def bm_revolve(bm, profile, segs=64, m=Matrix.Identity(4)):
    """Closed (rho, h) profile revolved around local Z of m -> closed ring/solid."""
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
    """Loft equal-count sections (lists of Vector). Closed sections + caps -> closed solid."""
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


def bm_ring_loops(bm, loops):
    """Connect N closed loops cyclically (loop k -> k+1 -> ... -> 0): e.g. a bezel frame from
    [outer_top, inner_top, inner_bottom, outer_bottom]."""
    vs = [[bm.verts.new(p) for p in lp] for lp in loops]
    n = len(loops[0])
    for k in range(len(vs)):
        a, b = vs[k], vs[(k + 1) % len(vs)]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    return vs


def bm_torus(bm, R, r, segs=48, rsegs=16, m=Matrix.Identity(4), arc=(0.0, 2 * math.pi)):
    """Torus in local XY plane of m; a partial arc gets capped ends."""
    a0, a1 = arc
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    secs = []
    for i in range(segs if full else segs + 1):
        a = a0 + (a1 - a0) * i / segs
        c = Vector((math.cos(a), math.sin(a), 0))
        secs.append([m @ (c * (R + r * math.cos(2 * math.pi * k / rsegs)) +
                          Vector((0, 0, r * math.sin(2 * math.pi * k / rsegs)))) for k in range(rsegs)])
    if full:
        rings = [[bm.verts.new(p) for p in sec] for sec in secs]
        for i in range(segs):
            a_, b_ = rings[i], rings[(i + 1) % segs]
            for j in range(rsegs):
                j1 = (j + 1) % rsegs
                bm.faces.new((a_[j], a_[j1], b_[j1], b_[j]))
        return rings
    return bm_loft(bm, secs, True, True, True)


# ----------------------------------------------------------------------------- mesh objects
def finish_mesh(name, bm, smooth=True, sharp_angle=35.0, recalc=True):
    if recalc and bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        # recalc_face_normals can choose the inside for some closed primitives: enforce outward
        if all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True) < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        set_smooth(me, sharp_angle)
    return me


def set_smooth(me, sharp_angle=35.0):
    """Smooth shading + sharp edges above an angle (data-level 'smooth by angle')."""
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


def tag(ob, comp, evidence='observed', note=None, **extra):
    p = CTX['tag_prefix']
    ob[p + '_component'] = comp
    ob[p + '_evidence'] = evidence
    if note:
        ob[p + '_note'] = note
    for k, v in extra.items():
        ob[p + '_' + k] = v


def mk(name, bm, coll, parent, world, mats, comp, evidence='observed', bevel=None, smooth_angle=35.0,
       note=None, bevel_always=False):
    """bm in WORLD coordinates -> mesh object with pivot `world`, parented to `parent`.
    bevel = (width, segments, angle_deg) is added only for detailed builds unless bevel_always."""
    inv = world.inverted()
    for v in bm.verts:
        v.co = inv @ v.co
    me = finish_mesh(name, bm, smooth=True, sharp_angle=smooth_angle)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    place(ob, parent, world)
    for m in (mats or []):
        me.materials.append(m)
    tag(ob, comp, evidence, note)
    if bevel and (CTX['detailed'] or bevel_always):
        mod_bevel(ob, *bevel)
    return ob


def seg_cyl(name, a, b, r, coll, parent, mats, comp, t0=0.0, t1=1.0, bevel=(0.006, 2, 30.0), segs=32,
            evidence='observed'):
    """Cylinder covering the [t0, t1] part of segment a->b (struts, sleeves, rods)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    p0, p1 = a + d * t0, a + d * t1
    M = frame_z((p0 + p1) / 2, d)
    bm = bm_new()
    bm_cyl(bm, r, (p1 - p0).length, segs, M)
    return mk(name, bm, coll, parent, M, mats, comp, evidence, bevel=bevel)


# ----------------------------------------------------------------------------- modifiers / booleans
def mod_bevel(ob, width=0.006, segs=3, angle=35.0, harden=False, clamp=True):
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width = width
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = harden
    m.use_clamp_overlap = clamp
    m.miter_outer = 'MITER_ARC'
    return m


def mod_solidify(ob, thick, offset=-1.0):
    m = ob.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness = thick
    m.offset = offset
    m.use_even_offset = True
    m.use_quality_normals = True
    return m


def apply_modifiers(ob):
    """Apply the whole stack via the evaluated mesh (no operator/context needed)."""
    ev = ob.evaluated_get(get_dg())
    me = bpy.data.meshes.new_from_object(ev)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ob


def bool_sequential(ob, cutters, op='DIFFERENCE', solver='EXACT'):
    """Apply Boolean cutters ONE AT A TIME. A single collection operand with many overlapping
    cutters silently failed to separate panels; sequential application is robust."""
    for co in cutters:
        m = ob.modifiers.new('Bool', 'BOOLEAN')
        m.operation = op
        m.operand_type = 'OBJECT'
        m.object = co
        m.solver = solver
        apply_modifiers(ob)
    # Boolean results carry an empty material slot from the operand: clear before assigning
    ob.data.materials.clear()
    return ob


def split_islands(ob):
    """Connected components of ob.data -> [(centroid_local, bmesh, vert_count)]."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    seen, islands = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
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
        bmesh.ops.delete(nb, geom=[vv for vv in nb.verts if vv.index not in cs], context='VERTS')
        cen = sum((vv.co for vv in nb.verts), Vector()) / max(1, len(nb.verts))
        bmesh.ops.remove_doubles(nb, verts=nb.verts[:], dist=5e-5)      # Boolean degeneracies
        bmesh.ops.dissolve_degenerate(nb, dist=1e-4, edges=nb.edges[:])
        # zero-area slivers with long collinear edges survive dissolve_degenerate: merge only
        # (near-)coplanar neighbours; curved tessellation (>0.1 deg) is kept
        bmesh.ops.dissolve_limit(nb, angle_limit=math.radians(0.1), verts=nb.verts[:], edges=nb.edges[:])
        out.append((cen, nb, len(nb.verts)))
    bm.free()
    return out


# ----------------------------------------------------------------------------- cutters (temporary)
def _cutter(name, coll, bm):
    me = finish_mesh(name, bm, smooth=False)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob['oow_support'] = True
    ob.hide_render = True
    ob.display_type = 'WIRE'
    return ob


def box_cutter(name, coll, world):
    """world: 4x4 matrix whose basis columns carry the box size (use M @ Matrix.Diagonal(size))."""
    bm = bm_new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=world)
    return _cutter(name, coll, bm)


def slab_cutter(name, coll, center, axis_long, axis_thin, size_long, size_thin, size_third):
    """Thin seam slab: long along axis_long, thin along axis_thin (in world space)."""
    x = Vector(axis_thin).normalized()
    y = Vector(axis_long).normalized()
    z = x.cross(y).normalized()
    y = z.cross(x).normalized()
    M = Matrix((x, y, z)).transposed().to_4x4()
    M.translation = Vector(center)
    return box_cutter(name, coll, M @ Matrix.Diagonal((size_thin, size_long, size_third, 1)))


def cyl_cutter(name, coll, center, axis, r, length, segs=64):
    bm = bm_new()
    bm_cyl(bm, r, length, segs, frame_z(Vector(center), Vector(axis)))
    return _cutter(name, coll, bm)


def prism_cutter(name, coll, pts2d, origin, u_axis, v_axis, d0, d1):
    """Convex 2D polygon (u, v) in the plane spanned by u_axis/v_axis at origin, extruded
    along the plane normal from d0 to d1."""
    u, v = Vector(u_axis).normalized(), Vector(v_axis).normalized()
    n = u.cross(v).normalized()
    bm = bm_new()
    a = [bm.verts.new(Vector(origin) + u * x + v * y + n * d0) for x, y in pts2d]
    b = [bm.verts.new(Vector(origin) + u * x + v * y + n * d1) for x, y in pts2d]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    k = len(pts2d)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((a[i], b[i], b[j], a[j]))
    return _cutter(name, coll, bm)


# ----------------------------------------------------------------------------- sphere / curve maths
def sph_dir(az_deg, el_deg):
    """Unit direction: az 0 = front (-Y), + toward +X; el up from the horizontal."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))


def tangent_frame(d, az_deg):
    """(t_el, t_az) tangent axes on a sphere at direction d (meridian-up, east)."""
    t_az = Vector((math.cos(math.radians(az_deg)), math.sin(math.radians(az_deg)), 0))
    t_el = d.cross(t_az).normalized()
    if t_el.z < 0:
        t_el = -t_el
    return t_el, t_az


def bezier(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t


def bezier3(p0, p1, p2, p3, t):
    u = 1 - t
    return p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3


def meridian_rotation(az_deg):
    """Rotation about Z whose local Y lies along the meridian direction of azimuth az.
    NOTE: Matrix.Rotation(-a) is WRONG here (it mirrors the direction); this bug once made
    seam cutters run off-meridian."""
    return Matrix.Rotation(math.radians(az_deg), 4, 'Z')


def mirror_factor(az_deg):
    """+1/-1 so off-centre details on four mirrored limbs (front/rear x left/right) land as
    mirror images: +1 for (az<0, front) and (az>0, rear), -1 otherwise."""
    return 1.0 if ((az_deg < 0) == (abs(az_deg) < 90)) else -1.0
