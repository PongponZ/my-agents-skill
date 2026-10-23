# Orange Orb Walker - procedural build (exec'd inside Blender after oow_lib.py)
# Scene convention: D = 1 (body diameter, arbitrary scene unit), +Z up, front -Y.
# Handedness note: R01 shows C09 on image-left of a front view. With front = -Y and +Z up,
# image-left of a front view is -X, i.e. the robot's anatomical right. Robot-right parts
# (C09, C11_RF, C11_RR) are therefore built on -X so the tools are not mirrored vs R01.

LEVEL = globals().get('LEVEL', 'blockout')   # 'blockout' | 'detailed'
DET = (LEVEL != 'blockout')

P = dict(
    H=1.00,                # body centre height above support plane (follows leg contacts)
    R_SHELL=0.505,         # outer armour radius (visible diameter ~1D)
    SHELL_T=0.025,         # armour thickness (presentation choice)
    R_CHASSIS=0.478,       # dark chassis radius under the armour
    Z_RING=0.0,            # C04 axis through the body centre
    RING_OUT=0.222, RING_IN=0.150, CORE_R=0.118,
    HS_OUT=0.315, HS_ANG=22.0, R_HS=0.545,
    Z_BELT=-0.03, XB=0.17, GAP=0.010, Z_BAND_REAR=0.40,
    Z_SHELL_BOTTOM=-0.28,
)
H = P['H']
BODY_C = Vector((0, 0, H))
BODY_M = Matrix.Translation(BODY_C)

# ------------------------------------------------------------------ collections
sc = get_scene()
root_coll = get_coll('ORANGE_ORB_WALKER', sc.collection)
C_BODY = get_coll('BODY', root_coll)
C_LEGS = get_coll('LEGS', root_coll)
C_TOOLS = get_coll('TOOLS', root_coll)
C_DET = get_coll('DETAILS', root_coll)
C_PRES = get_coll('PRESENTATION', root_coll)
for c in (C_BODY, C_LEGS, C_TOOLS, C_DET):
    clear_coll(c)
for ob in list(root_coll.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
WM.clear()

# ------------------------------------------------------------------ materials (shared IDs, filled later)
def mat(name, rgb):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.diffuse_color = (*rgb, 1.0)
    return m

M01 = mat('M01_Ivory', (0.80, 0.70, 0.58))
M02 = mat('M02_Orange', (0.95, 0.35, 0.05))
M03 = mat('M03_Charcoal', (0.09, 0.075, 0.07))
M04 = mat('M04_WarmHub', (0.55, 0.25, 0.08))
M05 = mat('M05_Emitter', (1.0, 0.7, 0.1))

def tag(ob, comp, evidence='observed', note=None):
    ob['oow_component'] = comp
    ob['oow_evidence'] = evidence
    if note:
        ob['oow_note'] = note

def mk(name, bm, coll, parent, world, mats, comp, evidence='observed', bevel=None, smooth_angle=35.0, note=None):
    """bm is in WORLD coordinates; converted to the local frame of `world`."""
    inv = world.inverted()
    for v in bm.verts:
        v.co = inv @ v.co
    me = finish_mesh(name, bm, smooth=True, sharp_angle=smooth_angle)
    ob = mesh_obj(name, me, coll, parent, world, mats)
    tag(ob, comp, evidence, note)
    if bevel and DET:
        mod_bevel(ob, *bevel)
    return ob

def bw(m):
    """body-local matrix -> world"""
    return BODY_M @ m

def bv(v):
    return BODY_C + Vector(v)

# ------------------------------------------------------------------ root + C01
ROOT = empty('OOW_ROOT', root_coll, None, Matrix.Identity(4), size=0.3, kind='ARROWS')
ROOT['oow_note'] = 'Ground projection of chassis centre. D=1 scene unit, not metres. Front -Y, +Z up.'
ROOT['oow_handedness'] = 'Robot-right (C09, C11_RF, C11_RR) on -X to match R01; brief text said +X (inconsistent with front -Y).'

def chassis_point(az, el, r=None):
    r = P['R_CHASSIS'] if r is None else r
    d = sph_dir(az, el)
    p = d * r
    if p.z < 0:   # tucked underside
        k = 1.0 - 0.07 * (p.z / -r) ** 2
        p.x *= k; p.y *= k
    return p

bm = bm_new()
if DET:
    bm_sphere(bm, P['R_CHASSIS'], 96, 48)
    for v in bm.verts:
        if v.co.z < 0:
            k = 1.0 - 0.07 * (v.co.z / -P['R_CHASSIS']) ** 2
            v.co.x *= k; v.co.y *= k
else:
    bm_sphere(bm, 0.5, 64, 32)
    for v in bm.verts:
        if v.co.z < 0:
            k = 1.0 - 0.05 * (v.co.z / -0.5) ** 2
            v.co.x *= k; v.co.y *= k
# open a pocket behind C04 so the recessed core is not hidden by the chassis skin
pr = P['RING_OUT'] - 0.012
kill = [f for f in bm.faces if all(v.co.y < -0.1 and v.co.x ** 2 + (v.co.z - P['Z_RING']) ** 2 < pr * pr for v in f.verts)]
bmesh.ops.delete(bm, geom=kill, context='FACES')
edges = [e for e in bm.edges if e.is_boundary]
ext = bmesh.ops.extrude_edge_only(bm, edges=edges)
nv = [g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)]
for v in nv:
    v.co.y = -0.345
ne = [g for g in ext['geom'] if isinstance(g, bmesh.types.BMEdge) and all(v in nv for v in g.verts)]
bmesh.ops.holes_fill(bm, edges=ne)
for v in bm.verts:
    v.co = BODY_C + v.co
C01 = mk('C01_Chassis', bm, C_BODY, ROOT, BODY_M, [M03], 'C01', 'observed',
         note='Body diameter D=1; fore-aft depth unmeasured (inferred near-spherical).')
C01['oow_depth_scale_y'] = 1.0

# ------------------------------------------------------------------ armour shell (detailed)
def box_cutter(name, coll, center, size, rot=Matrix.Identity(4)):
    bm = bm_new()
    bm_box(bm, *size)
    m = BODY_M @ Matrix.Translation(Vector(center)) @ rot
    for v in bm.verts:
        v.co = m @ v.co
    me = finish_mesh(name, bm, smooth=False)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob

def cyl_cutter(name, coll, center, axis, r, length, segs=64):
    bm = bm_new()
    bm_cyl(bm, r, length, segs)
    m = BODY_M @ frame_z(Vector(center), Vector(axis))
    for v in bm.verts:
        v.co = m @ v.co
    me = finish_mesh(name, bm, smooth=False)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob

def prism_cutter(name, coll, pts2d, y0, y1, zc):
    """convex polygon in body XZ plane (x, z) extruded along Y from y0 to y1."""
    bm = bm_new()
    a = [bm.verts.new(BODY_C + Vector((x, y0, z + zc))) for x, z in pts2d]
    b = [bm.verts.new(BODY_C + Vector((x, y1, z + zc))) for x, z in pts2d]
    n = len(pts2d)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], b[i], b[j], a[j]))
    me = finish_mesh(name, bm, smooth=False)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob

SHOULDER = {'R': (-86.0, 6.0), 'L': (86.0, 6.0)}

# Body surface detail after R01 / concept: (name, az, el, length, width, tilt, evidence).
# Dark rounded recess slots get a raised dark bezel; the dark chassis shows as the recess floor.
SLOTS = [
    ('C02_Slot_R', -48, 32, 0.140, 0.060, -32, 'observed'),        # diagonal slots beside the band
    ('C02_Slot_L', 48, 32, 0.140, 0.060, 32, 'observed'),
    ('C02_SideSlot_R', -75, 28, 0.115, 0.052, 0, 'observed'),       # above the shoulders
    ('C02_SideSlot_L', 75, 28, 0.115, 0.052, 0, 'observed'),
    ('C03_Hole_R', -36, -21, 0.062, 0.028, 90, 'observed'),         # small holes in lower orange plates
    ('C03_Hole_L', 36, -21, 0.062, 0.028, 90, 'observed'),
    ('C13_Vent', 180, -16, 0.080, 0.036, 90, 'inferred'),           # rear lower centre (concept rear)
]
LOWER_RAISE = 0.010      # lower orange plates stand proud of the ivory (layered armour)
BAND_RAISE = 0.004
XB_TOP, BAND_TAPER = 0.185, 0.20   # top band half-width at the crown, narrowing toward the ring
Z_CROWN = 0.360          # crown latitude seam (el ~45 deg) outside the band

def capsule_frame(az, el, tilt_deg):
    d = sph_dir(az, el)
    t_az = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
    t_el = d.cross(t_az).normalized()
    if t_el.z < 0:
        t_el = -t_el
    ang = math.radians(tilt_deg)
    ax = (t_el * math.cos(ang) + t_az * math.sin(ang)).normalized()
    sd = d.cross(ax).normalized()
    return d, ax, sd

def capsule_pts(ax, sd, length, width, n=12):
    pts = []
    hl = max(length / 2 - width / 2, 0.0)
    for i in range(n):
        a = -math.pi / 2 + math.pi * i / (n - 1)
        pts.append(ax * (hl + math.cos(a) * width / 2) + sd * (math.sin(a) * width / 2))
    for i in range(n):
        a = math.pi / 2 + math.pi * i / (n - 1)
        pts.append(ax * (-hl + math.cos(a) * width / 2) + sd * (math.sin(a) * width / 2))
    return pts

def capsule_cutter(name, coll, az, el, length, width, tilt_deg):
    d, ax, sd = capsule_frame(az, el, tilt_deg)
    pts = capsule_pts(ax, sd, length, width)
    bm = bm_new()
    inner = [bm.verts.new(BODY_C + d * 0.40 + p) for p in pts]
    outer = [bm.verts.new(BODY_C + d * 0.70 + p) for p in pts]
    n = len(pts)
    bm.faces.new(list(reversed(inner)))
    bm.faces.new(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((inner[i], inner[j], outer[j], outer[i]))
    me = finish_mesh(name, bm, smooth=False)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob

def slot_bezel(name, az, el, length, width, tilt, r_top, comp, ev, rim=0.013, grow=0.012, depth=0.040):
    """raised dark frame around a cut slot, conformed to the sphere"""
    d, ax, sd = capsule_frame(az, el, tilt)
    R = P['R_SHELL']
    outer = capsule_pts(ax, sd, length + 2 * grow, width + 2 * grow, 14)
    inner = capsule_pts(ax, sd, length - 2 * rim, max(width - 2 * rim, 0.01), 14)
    def proj(p, r):
        return BODY_C + (d * R + p).normalized() * r
    bm = bm_new()
    loops = [[bm.verts.new(proj(p, r_top)) for p in outer],
             [bm.verts.new(proj(p, r_top)) for p in inner],
             [bm.verts.new(proj(p, r_top - depth)) for p in inner],
             [bm.verts.new(proj(p, r_top - depth)) for p in outer]]
    n = len(outer)
    for k in range(4):
        a_, b_ = loops[k], loops[(k + 1) % 4]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a_[i], a_[j], b_[j], b_[i]))
    return mk(name + '_Bezel', bm, C_DET, C01, BODY_M, [M03], comp, ev, bevel=(0.003, 2, 30.0), smooth_angle=35.0)

def build_shell():
    g = P['GAP']; XB = XB_TOP; ZB = P['Z_BELT']; ZR = P['Z_RING']
    cut = bpy.data.collections.get('OOW_CUTTERS') or bpy.data.collections.new('OOW_CUTTERS')
    if cut.name not in root_coll.children.keys():
        root_coll.children.link(cut)
    clear_coll(cut)
    # band seams: one tapered plane x = +-(XB_TOP - BAND_TAPER * (top - z)) shared by the front and the
    # rear over the crown (so the two halves meet without a gap), and vertical seams continuing down
    # the back below the band end (rear centre panel keeps a constant width)
    th = math.atan(BAND_TAPER)
    ztop = P['R_SHELL']
    edge = lambda z: XB - BAND_TAPER * (ztop - z)
    zr = P['Z_BAND_REAR']
    for s in (-1, 1):
        for y0, y1, z0, z1 in ((-0.7, 0.0, ZB - 0.01, 0.70), (0.0, 0.7, zr - 0.01, 0.70)):
            zc = (z0 + z1) / 2
            box_cutter('cut_band_t', cut, (s * edge(zc), (y0 + y1) / 2, zc), (g, y1 - y0, (z1 - z0) / math.cos(th)),
                       Matrix.Rotation(s * th, 4, 'Y'))
        box_cutter('cut_band_r', cut, (s * edge(zr), 0.35, (zr - 0.7) / 2), (g, 0.7, zr + 0.7))
    box_cutter('cut_band_end', cut, (0, 0.35, zr), (2 * edge(zr) + g, 0.7, g))
    box_cutter('cut_belt', cut, (0, 0, ZB), (1.4, 1.4, g))
    # crown latitude seam outside the band: starts inside the band seam slab so it fully separates
    # the panels without entering the band (front band edge is tapered, rear edge at XB_TOP)
    x_front = edge(Z_CROWN)
    for s in (-1, 1):
        x0f, x0r = x_front, edge(zr)
        box_cutter('cut_crown_f', cut, (s * (x0f + 0.75) / 2 + s * 0.0, -0.35, Z_CROWN), (0.75 - x0f, 0.7, g))
        box_cutter('cut_crown_r', cut, (s * (x0r + 0.75) / 2, 0.35, Z_CROWN), (0.75 - x0r, 0.7, g))
    # upper meridian seams (stop short of the band)
    for az in (62, -62, 118, -118):
        a = math.radians(az)
        rot = Matrix.Rotation(a, 4, 'Z')   # local Y along the meridian direction (-dv)
        dv = Vector((math.sin(a), -math.cos(a), 0))
        c = dv * 0.449
        box_cutter('cut_mer_up', cut, (c.x, c.y, (ZB + 0.7) / 2), (g, 0.502, 0.7 - ZB), rot)
    # lower meridian seams: sides at +-90, and a front split at +-56
    for s in (-1, 1):
        box_cutter('cut_mer_lo', cut, (s * 0.425, 0.0, (ZB - 0.7) / 2), (0.55, g, 0.7 + ZB))
    for az in (56, -56):
        a = math.radians(az)
        rot = Matrix.Rotation(a, 4, 'Z')   # local Y along the meridian direction (-dv)
        dv = Vector((math.sin(a), -math.cos(a), 0))
        c = dv * 0.43
        box_cutter('cut_mer_lof', cut, (c.x, c.y, (ZB - 0.7) / 2), (g, 0.54, 0.7 + ZB), rot)
    # lower front centre strip (chin area exposes dark chassis)
    box_cutter('cut_strip', cut, (0, -0.375, (ZR - 0.7) / 2), (0.22 + g, 0.65, 0.7 + ZR))
    # ring hole + horseshoe region (circle segment, convex)
    cyl_cutter('cut_ring', cut, (0, -0.45, ZR), (0, 1, 0), P['RING_OUT'] + 0.006, 0.7)
    pts = []
    a0, a1 = math.radians(-P['HS_ANG']), math.radians(180 + P['HS_ANG'])
    ro = P['HS_OUT'] + 0.006
    for i in range(41):
        a = a0 + (a1 - a0) * i / 40
        pts.append((ro * math.cos(a), ro * math.sin(a)))
    prism_cutter('cut_horseshoe', cut, list(reversed(pts)), -0.8, -0.1, ZR)
    # shoulder holes
    for side, (az, el) in SHOULDER.items():
        d = sph_dir(az, el)
        cyl_cutter('cut_shoulder', cut, d * 0.55, d, 0.095, 0.4)
    # recess slots / holes / vent
    for nm, az, el, ln, wd, tilt, ev_ in SLOTS:
        capsule_cutter('cut_' + nm, cut, az, el, ln, wd, tilt)
    for ob in cut.objects:
        ob.hide_render = True
        ob.display_type = 'WIRE'

    # shell base
    bm = bm_new()
    bm_sphere(bm, P['R_SHELL'], 160, 80, m=Matrix.Rotation(math.radians(90), 4, 'Y'))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                           plane_co=Vector((0, 0, P['Z_SHELL_BOTTOM'])), plane_no=Vector((0, 0, 1)),
                           clear_inner=True)
    for v in bm.verts:
        v.co = BODY_C + v.co
    me = finish_mesh('OOW_ShellTmp', bm, smooth=True, sharp_angle=None)
    shell = bpy.data.objects.new('OOW_ShellTmp', me)
    C_BODY.objects.link(shell)
    mod_solidify(shell, P['SHELL_T'], -1.0)
    apply_modifiers(shell)
    # one cutter at a time: the exact solver mis-handled the combined overlapping cutter set
    for co in list(cut.objects):
        m_ = shell.modifiers.new('Bool', 'BOOLEAN')
        m_.operation = 'DIFFERENCE'
        m_.operand_type = 'OBJECT'
        m_.object = co
        m_.solver = 'EXACT'
        apply_modifiers(shell)
    isl = split_islands(shell)
    bpy.data.objects.remove(shell, do_unlink=True)
    clear_coll(cut)
    bpy.data.collections.remove(cut)
    counts = {}
    made = []
    for cen_w, ibm, nv in isl:
        c = cen_w - BODY_C
        if nv < 40:
            print('drop sliver', nv, tuple(round(x, 3) for x in c))
            ibm.free()
            continue
        # clean boolean degeneracies (zero-length edges at seam/rim junctions)
        bmesh.ops.remove_doubles(ibm, verts=ibm.verts[:], dist=2e-5)
        bmesh.ops.dissolve_degenerate(ibm, dist=2e-5, edges=ibm.edges[:])
        side = 'R' if c.x < 0 else 'L'
        az = math.degrees(math.atan2(c.x, -c.y))
        ev = 'observed'
        raise_ = 0.0
        if abs(c.x) < 0.12 and c.z > 0.22:
            name, m_, comp = 'C03_TopBand', M02, 'C03'
            raise_ = BAND_RAISE
        elif abs(c.x) < 0.12 and c.y > 0 and c.z > ZB:
            name, m_, comp, ev = 'C13_RearUpper_C', M01, 'C13', 'inferred'
        elif abs(c.x) < 0.12 and c.y > 0:
            name, m_, comp, ev = 'C13_RearLower_C', M02, 'C13', 'inferred'
            raise_ = LOWER_RAISE
        elif c.z > Z_CROWN - 0.03:
            if abs(az) < 118:
                name, m_, comp = 'C02_Crown_' + side + ('F' if abs(az) < 62 else 'S'), M01, 'C02'
                ev = 'observed-partial'
            else:
                name, m_, comp, ev = 'C13_Crown_' + side, M01, 'C13', 'inferred'
        elif c.z > ZB:
            if abs(az) < 62:
                name, m_, comp = 'C02_FrontUpper_' + side, M01, 'C02'
            elif abs(az) < 118:
                name, m_, comp = 'C02_Side_' + side, M01, 'C02'
                ev = 'observed-partial'
            else:
                name, m_, comp, ev = 'C13_RearUpper_' + side, M01, 'C13', 'inferred'
        else:
            raise_ = LOWER_RAISE
            if abs(az) < 56:
                name, m_, comp = 'C03_LowerFront_' + side, M02, 'C03'
            elif abs(az) < 90:
                name, m_, comp = 'C03_LowerSide_' + side, M02, 'C03'
            else:
                name, m_, comp, ev = 'C13_RearLower_' + side, M02, 'C13', 'inferred'
        if raise_:
            k_ = 1.0 + raise_ / P['R_SHELL']
            for v in ibm.verts:
                v.co = BODY_C + (v.co - BODY_C) * k_
        k = counts.get(name, 0)
        counts[name] = k + 1
        if k:
            name = '%s_%d' % (name, k + 1)
        ob = mk(name, ibm, C_BODY, C01, BODY_M, [m_], comp, ev, bevel=(0.0055, 3, 40.0), smooth_angle=40.0)
        ob['oow_wear'] = 1.0
        made.append((name, nv))
    print('shell panels:', made)
    # raised dark bezels around the recess slots
    for nm, az, el, ln, wd, tilt, ev_ in SLOTS:
        lower = el < P['Z_BELT']
        r_top = P['R_SHELL'] + (LOWER_RAISE if lower else 0.0) + 0.006
        b = slot_bezel(nm, az, el, ln, wd, tilt, r_top, nm[:3], ev_)
        b['oow_wear'] = 0.5
    # rivets / small dark bolt heads near panel edges (sparse; rear ones inferred)
    riv = []
    for s in (-1, 1):
        for z in (0.36, 0.45):          # along both band edges, just inside the band
            xe = XB_TOP - BAND_TAPER * (P['R_SHELL'] - z) - 0.026
            y = -math.sqrt(max(P['R_SHELL'] ** 2 - xe * xe - z * z, 1e-6))
            dv = Vector((s * xe, y, z)).normalized()
            riv.append((dv, BAND_RAISE, 'C03', 'observed'))
        for az, el, lift, comp_, ev_ in ((56, 8, 0, 'C02', 'observed'), (52, 47, 0, 'C02', 'observed'),
                                         (100, 14, 0, 'C02', 'observed-partial'), (100, 42, 0, 'C02', 'observed-partial'),
                                         (78, 54, 0, 'C02', 'observed-partial'),
                                         (24, -27, LOWER_RAISE, 'C03', 'observed'), (50, -12, LOWER_RAISE, 'C03', 'observed'),
                                         (74, -8, LOWER_RAISE, 'C03', 'observed'), (74, -24, LOWER_RAISE, 'C03', 'observed'),
                                         (140, 16, 0, 'C13', 'inferred'), (140, -16, LOWER_RAISE, 'C13', 'inferred')):
            riv.append((sph_dir(s * az, el), lift, comp_, ev_))
    bmr = bm_new()
    for dv, lift, comp_, ev_ in riv:
        p = BODY_C + dv * (P['R_SHELL'] + lift + 0.0005)
        bm_sphere(bmr, 1.0, 16, 8, frame_z(p, dv) @ Matrix.Diagonal((0.0085, 0.0085, 0.0040, 1)))
    o = mk('C02_C03_Rivets', bmr, C_DET, C01, BODY_M, [M03], 'C02', 'observed-partial', smooth_angle=None,
           note='Sparse rivet heads near panel edges; rear ones inferred.')
    # dark mechanical skirt under the armour rim (R01 shows dark mechanism between body and legs)
    zb = P['Z_SHELL_BOTTOM']
    prof = [(0.330, zb - 0.075), (0.372, zb - 0.075), (0.392, zb - 0.040), (0.398, zb + 0.012),
            (0.380, zb + 0.012), (0.352, zb - 0.030)]
    bm = bm_new(); bm_revolve(bm, prof, 96, BODY_M)
    sk = mk('C13_UnderSkirt', bm, C_BODY, C01, BODY_M, [M03], 'C13', 'inferred', bevel=(0.004, 2, 30.0), smooth_angle=30.0,
            note='Dark lip under the armour rim; underside inferred.')
    bmb = bm_new()
    for i in range(16):
        a_ = 2 * math.pi * (i + 0.5) / 16
        dv = Vector((math.cos(a_), math.sin(a_), -0.62)).normalized()
        p = BODY_C + Vector((0.389 * math.cos(a_), 0.389 * math.sin(a_), zb - 0.045))
        bm_cyl(bmb, 0.010, 0.012, 16, frame_z(p, dv))
    mk('C13_UnderSkirtBolts', bmb, C_DET, C01, BODY_M, [M04], 'C13', 'inferred', smooth_angle=40.0)

if DET:
    build_shell()

# ------------------------------------------------------------------ C04 / C05
# Layered bezel after the concept C04+C05 detail: raised outer rim, groove, inner lip, funnel face,
# ribbed deep barrel, dark collar, deeply recessed domed core. Axis through the body centre (Z_RING = 0).
RING_M = bw(frame_z(Vector((0, 0, P['Z_RING'])), Vector((0, -1, 0)), Vector((1, 0, 0))))
C04 = empty('C04_RingAssembly', C_BODY, C01, RING_M, size=0.25, kind='CIRCLE')
tag(C04, 'C04', 'observed', 'Axis along -Y through body centre. One functional assembly.')
RO = P['RING_OUT']
prof = [(0.100, 0.36), (RO, 0.36), (RO, 0.505), (RO - 0.008, 0.530), (0.200, 0.541), (0.188, 0.540),
        (0.181, 0.532), (0.176, 0.532), (0.170, 0.537), (0.160, 0.535), (0.150, 0.522), (0.142, 0.500),
        (0.138, 0.470), (0.132, 0.462), (0.132, 0.452), (0.136, 0.445), (0.133, 0.425), (0.126, 0.410),
        (0.100, 0.405)]
bm = bm_new()
bm_revolve(bm, prof, 128, RING_M)
o_ = mk('C04_CoreRing', bm, C_BODY, C04, RING_M, [M03], 'C04', bevel=(0.0025, 2, 30.0), smooth_angle=30.0)
if DET:
    o_.modifiers['Bevel'].use_clamp_overlap = True
    bm = bm_new(); bm_torus(bm, 0.125, 0.0075, 96, 12, RING_M @ Matrix.Translation((0, 0, 0.412)))
    mk('C04_InnerCollar', bm, C_BODY, C04, RING_M, [M03], 'C04', smooth_angle=None)

# upper horseshoe surround, conformed to sphere R_HS (projected along Y), chamfered front edges
def hs_pt(rho, th, R):
    x = rho * math.cos(th)
    z = P['Z_RING'] + rho * math.sin(th)
    y = -math.sqrt(max(R * R - x * x - z * z, 1e-6))
    return BODY_C + Vector((x, y, z))
secs = []
a0, a1 = math.radians(-P['HS_ANG'] + 1.5), math.radians(180 + P['HS_ANG'] - 1.5)
r_in, r_out = RO + 0.012, P['HS_OUT']
Rf, Rb = P['R_HS'], P['R_HS'] - 0.09
ch = 0.014
for i in range(97):
    th = a0 + (a1 - a0) * i / 96
    front = [(r_in, Rf - ch), (r_in + ch, Rf)] + \
            [(r_in + ch + (r_out - r_in - 2 * ch) * k / 3, Rf) for k in (1, 2)] + \
            [(r_out - ch, Rf), (r_out, Rf - ch)]
    sec = [hs_pt(r, th, R) for r, R in front]
    sec += [hs_pt(r_out - (r_out - r_in) * k / 3, th, Rb) for k in range(4)]
    secs.append(sec)
bm = bm_new()
bm_loft(bm, secs, True, True, True)
mk('C04_UpperSurround', bm, C_BODY, C04, RING_M, [M03], 'C04', bevel=(0.005, 2, 30.0), smooth_angle=30.0)

bm = bm_new()
bm_sphere(bm, 1.0, 64, 32, m=RING_M @ Matrix.Translation((0, 0, 0.405)) @ Matrix.Diagonal((P['CORE_R'], P['CORE_R'], 0.045, 1)))
C05 = mk('C05_Core', bm, C_BODY, C04, RING_M, [M05], 'C05', smooth_angle=None,
         note='Single dominant front emitter; shallow dome recessed ~0.09 behind the bezel; no transmission.')

if DET:
    # warm accent bolts along the surround (ends + shoulders of the arch)
    for nm, deg in (('R', 180 + P['HS_ANG'] - 8), ('UR', 128), ('UL', 52), ('L', -P['HS_ANG'] + 8)):
        p = hs_pt((r_in + r_out) / 2, math.radians(deg), Rf + 0.003)
        n = (p - BODY_C).normalized()
        bm = bm_new()
        bm_cyl(bm, 0.014, 0.018, 24, frame_z(p, n))
        mk('C04_AccentStud_' + nm, bm, C_DET, C04, RING_M, [M04], 'C04',
           bevel=(0.004, 2, 30.0), smooth_angle=40.0)

# ------------------------------------------------------------------ C06 roof
ROOF_M = bw(Matrix.Translation((0, -0.06, 0.535)) @ Matrix.Rotation(math.radians(-8), 4, 'X'))
C06 = empty('C06_RoofAssembly', C_BODY, C01, ROOF_M, size=0.15)
tag(C06, 'C06', 'observed', 'Two visible masses; unseen rear kept simple and non-emissive (inferred).')
housing_sz = (0.27, 0.20, 0.21)
if DET:
    cut = bpy.data.collections.new('OOW_TMP_CUT')
    root_coll.children.link(cut)
    def lbox(name, c, s, M):
        bm = bm_new(); bm_box(bm, *s, M @ Matrix.Translation(c))
        me = finish_mesh(name, bm, smooth=False)
        o = bpy.data.objects.new(name, me); cut.objects.link(o); return o
    lbox('cut_ap', (0, -0.10, 0.02), (0.175, 0.05, 0.075), ROOF_M)
    lbox('cut_top', (0, -0.005, 0.105), (0.17, 0.10, 0.05), ROOF_M)
    bm = bm_new(); bm_box(bm, *housing_sz, ROOF_M)
    me = finish_mesh('C06_Housing', bm, smooth=False)
    hs = bpy.data.objects.new('C06_Housing', me); C_BODY.objects.link(hs)
    bool_apply(hs, cut, 'DIFFERENCE', 'EXACT')
    clear_coll(cut); bpy.data.collections.remove(cut)
    me = hs.data
    me.transform(ROOF_M.inverted())
    set_smooth(me, 30.0)
    place(hs, C06, ROOF_M)
    me.materials.clear()
    me.materials.append(M03)
    tag(hs, 'C06', 'observed', 'Recessed front aperture and top recess; rear simple (inferred).')
    bv_ = mod_bevel(hs, 0.018, 4, 30.0)
    bv_.use_clamp_overlap = True
    # emissive aperture insert (observed front aperture)
    bm = bm_new(); bm_box(bm, 0.168, 0.006, 0.068, ROOF_M @ Matrix.Translation((0, -0.078, 0.02)))
    mk('C06_FrontAperture', bm, C_BODY, C06, ROOF_M, [M05], 'C06', smooth_angle=None)
    # dark crenellation teeth in front of the glow (R01 pattern, simplified)
    for i, x in enumerate((-0.05, 0.0, 0.05)):
        bm = bm_new(); bm_box(bm, 0.018, 0.012, 0.03, ROOF_M @ Matrix.Translation((x, -0.084, -0.002)))
        mk('C06_ApertureTooth_%d' % i, bm, C_DET, C06, ROOF_M, [M03], 'C06', bevel=(0.003, 2, 30.0))
    for s in (-1, 1):
        bm = bm_new(); bm_box(bm, 0.022, 0.012, 0.12, ROOF_M @ Matrix.Translation((s * 0.122, -0.101, 0.02)))
        mk('C06_SideAccent_' + ('L' if s > 0 else 'R'), bm, C_BODY, C06, ROOF_M, [M02], 'C06', bevel=(0.005, 3, 30.0))
else:
    bm = bm_new(); bm_box(bm, *housing_sz, ROOF_M)
    mk('C06_Housing', bm, C_BODY, C06, ROOF_M, [M03], 'C06', smooth_angle=30.0)

RM_M = ROOF_M @ Matrix.Translation((0, 0.085, 0.155))
bm = bm_new(); bm_box(bm, 0.21, 0.12, 0.10, RM_M)
mk('C06_RearMass', bm, C_BODY, C06, RM_M, [M02], 'C06', bevel=(0.035, 4, 30.0), smooth_angle=30.0,
   note='Smaller rounded mass behind and above housing; rear surface inferred, non-emissive.')
if DET:
    bm = bm_new(); bm_box(bm, 0.12, 0.03, 0.082, RM_M @ Matrix.Translation((0, -0.055, 0.0)))
    mk('C06_RearMassFrame', bm, C_BODY, C06, RM_M, [M03], 'C06', bevel=(0.01, 3, 30.0))
    bm = bm_new(); bm_box(bm, 0.075, 0.006, 0.03, RM_M @ Matrix.Translation((0, -0.0705, 0.0)))
    mk('C06_RearMassAperture', bm, C_BODY, C06, RM_M, [M05], 'C06', smooth_angle=None)

# ------------------------------------------------------------------ C07 chin
CHIN_M = bw(Matrix.Translation((0, -0.395, P['Z_RING'] - P['RING_OUT'] - 0.094)))
C07 = empty('C07_ChinAssembly', C_BODY, C01, CHIN_M, size=0.12)
tag(C07, 'C07', 'observed', 'Hidden attachment into lower chassis inferred.')
bm = bm_new(); bm_box(bm, 0.20, 0.15, 0.19, CHIN_M)
if DET:
    cut = bpy.data.collections.new('OOW_TMP_CUT'); root_coll.children.link(cut)
    bmc = bm_new(); bm_box(bmc, 0.125, 0.05, 0.045, CHIN_M @ Matrix.Translation((0, -0.075, 0.05)))
    mec = finish_mesh('cut_chin', bmc, smooth=False)
    oc = bpy.data.objects.new('cut_chin', mec); cut.objects.link(oc)
    me = finish_mesh('C07_ChinPod', bm, smooth=False)
    pod = bpy.data.objects.new('C07_ChinPod', me); C_BODY.objects.link(pod)
    bool_apply(pod, cut, 'DIFFERENCE', 'EXACT')
    clear_coll(cut); bpy.data.collections.remove(cut)
    pod.data.transform(CHIN_M.inverted()); set_smooth(pod.data, 30.0)
    place(pod, C07, CHIN_M); pod.data.materials.clear(); pod.data.materials.append(M03); tag(pod, 'C07')
    b_ = mod_bevel(pod, 0.035, 4, 30.0); b_.use_clamp_overlap = True
    bm = bm_new(); bm_box(bm, 0.118, 0.006, 0.04, CHIN_M @ Matrix.Translation((0, -0.053, 0.05)))
    mk('C07_Aperture', bm, C_BODY, C07, CHIN_M, [M05], 'C07', smooth_angle=None)
    for s in (-1, 1):
        bm = bm_new(); bm_box(bm, 0.04, 0.05, 0.04, CHIN_M @ Matrix.Translation((s * 0.075, -0.05, -0.083)))
        mk('C07_Accent_' + ('L' if s > 0 else 'R'), bm, C_BODY, C07, CHIN_M, [M02], 'C07', bevel=(0.01, 3, 30.0))
else:
    mk('C07_ChinPod', bm, C_BODY, C07, CHIN_M, [M03], 'C07', smooth_angle=30.0)
bm = bm_new(); bm_box(bm, 0.12, 0.14, 0.12, CHIN_M @ Matrix.Translation((0, 0.09, 0.04)))
mk('C07_Neck', bm, C_BODY, C07, CHIN_M, [M03], 'C07', 'inferred', bevel=(0.012, 2, 30.0))

# ------------------------------------------------------------------ C13 underside
if DET:
    UM = bw(Matrix.Translation((0, 0.0, -0.455)))
    bm = bm_new(); bm_cyl(bm, 0.24, 0.07, 64, UM)
    mk('C13_UnderPlate', bm, C_BODY, C01, UM, [M03], 'C13', 'inferred', bevel=(0.015, 3, 30.0))

# ------------------------------------------------------------------ C08 arms + C09/C10 tools
def seg_cyl(name, a, b, r, coll, parent, mats, comp, t0=0.0, t1=1.0, bevel=(0.006, 2, 30.0), segs=32, ev='observed'):
    a, b = Vector(a), Vector(b)
    d = b - a
    p0 = a + d * t0; p1 = a + d * t1
    mid = (p0 + p1) / 2
    M = frame_z(mid, d)
    bm = bm_new(); bm_cyl(bm, r, (p1 - p0).length, segs, M)
    return mk(name, bm, coll, parent, M, mats, comp, ev, bevel=bevel)

def joint(name, c, axis, r, depth, coll, parent, comp, hub_r=None, ev='observed'):
    M = frame_z(Vector(c), Vector(axis))
    bm = bm_new(); bm_cyl(bm, r, depth, 40, M)
    o = mk(name + 'Housing', bm, coll, parent, M, [M03], comp, ev, bevel=(min(0.012, r * 0.25), 3, 30.0))
    if hub_r and DET:
        bm = bm_new(); bm_cyl(bm, hub_r, depth + 0.022, 32, M)
        mk(name + 'Hub', bm, coll, parent, M, [M04], comp, ev, bevel=(0.004, 2, 30.0))
    return o

ARMS = {
    'R': dict(E=(-0.66, -0.06, 0.05), W=(-0.70, -0.115, 0.205)),
    'L': dict(E=(0.665, -0.05, 0.085), W=(0.765, -0.07, 0.215)),
}
for side, (az, el) in SHOULDER.items():
    d = sph_dir(az, el)
    S0 = BODY_C + d * 0.505
    S = BODY_C + d * 0.545
    E = bv(ARMS[side]['E']); W = bv(ARMS[side]['W'])
    SH_M = frame_x = frame_matrix(S0, d)
    arm = empty('C08_Arm_' + side, C_TOOLS, C01, SH_M, size=0.1)
    tag(arm, 'C08', 'observed', 'Visual pivot convention only; no range of motion certified.')
    arm['oow_tool'] = 'C09' if side == 'R' else 'C10'
    # shoulder base ring (seated in shell hole)
    M = frame_z(S0, d)
    prof = [(0.045, -0.035), (0.088, -0.035), (0.088, 0.022), (0.075, 0.034), (0.045, 0.034)]
    bm = bm_new(); bm_revolve(bm, prof, 48, M)
    mk('C08_%s_ShoulderBase' % side, bm, C_TOOLS, arm, M, [M03], 'C08', bevel=(0.006, 2, 30.0))
    if DET:
        bm = bm_new(); bm_cyl(bm, 0.047, 0.05, 32, M @ Matrix.Translation((0, 0, 0.005)))
        mk('C08_%s_ShoulderHub' % side, bm, C_TOOLS, arm, M, [M04], 'C08', bevel=(0.005, 2, 30.0))
    bm = bm_new(); bm_sphere(bm, 0.04, 32, 16, Matrix.Translation(S))
    mk('C08_%s_ShoulderBall' % side, bm, C_TOOLS, arm, M, [M03], 'C08', smooth_angle=None)
    # upper arm
    seg_cyl('C08_%s_UpperStrut' % side, S, E, 0.034, C_TOOLS, arm, [M03], 'C08')
    seg_cyl('C08_%s_UpperSleeve' % side, S, E, 0.058, C_TOOLS, arm, [M02], 'C08', 0.28, 0.78, (0.01, 3, 30.0))
    # elbow
    ax = (S - E).cross(W - E)
    if ax.length < 1e-4:
        ax = Vector((0, 1, 0))
    elbow = empty('C08_%s_Elbow' % side, C_TOOLS, arm, frame_matrix(E, (W - E), ax), size=0.06)
    tag(elbow, 'C08', 'proposed', 'Elbow pivot; visual convention.')
    joint('C08_%s_Elbow' % side, E, ax, 0.060, 0.095, C_TOOLS, elbow, 'C08', hub_r=0.029)
    seg_cyl('C08_%s_ForeStrut' % side, E, W, 0.032, C_TOOLS, elbow, [M03], 'C08')
    seg_cyl('C08_%s_ForeSleeveA' % side, E, W, 0.058, C_TOOLS, elbow, [M02], 'C08', 0.22, 0.52, (0.01, 3, 30.0))
    seg_cyl('C08_%s_ForeSleeveB' % side, E, W, 0.058, C_TOOLS, elbow, [M02], 'C08', 0.58, 0.86, (0.01, 3, 30.0))
    # wrist pivot
    WR_M = frame_matrix(W, (W - E))
    wrist = empty('C08_%s_Wrist' % side, C_TOOLS, elbow, WR_M, size=0.06)
    tag(wrist, 'C08', 'proposed', 'Editable wrist pivot (presentation convention).')
    bm = bm_new(); bm_sphere(bm, 0.048, 32, 16, Matrix.Translation(W))
    mk('C08_%s_WristBall' % side, bm, C_TOOLS, wrist, WR_M, [M03], 'C08', smooth_angle=None)

    if side == 'R':
        # ---------------- C09: source-left tool (robot right, -X)
        n9 = Vector((-0.42, -0.86, -0.12)).normalized()
        TC = bv((-0.735, -0.165, 0.30))
        TM = frame_z(TC, n9, Vector((0, 0, 1)))
        tool = empty('C09_Tool', C_TOOLS, wrist, TM, size=0.08)
        tag(tool, 'C09', 'observed', 'Concealed grip/mount minimal and inferred. Not a hand or cannon.')
        seg_cyl('C09_Mount', W, TM @ Vector((0, 0, -0.07)), 0.026, C_TOOLS, tool, [M03], 'C09', ev='inferred')
        prof = [(0.054, -0.05), (0.108, -0.05), (0.110, 0.020), (0.099, 0.040), (0.070, 0.042), (0.057, 0.024)]
        bm = bm_new(); bm_revolve(bm, prof, 64, TM)
        mk('C09_Rim', bm, C_TOOLS, tool, TM, [M02], 'C09', bevel=(0.008, 3, 30.0), smooth_angle=30.0)
        bm = bm_new(); bm_cyl(bm, 0.058, 0.05, 48, TM @ Matrix.Translation((0, 0, -0.024)))
        mk('C09_Recess', bm, C_TOOLS, tool, TM, [M03], 'C09', bevel=(0.004, 2, 30.0))
        if DET:
            bm = bm_new(); bm_cyl(bm, 0.019, 0.012, 32, TM @ Matrix.Translation((0, 0, 0.004)))
            mk('C09_CenterHub', bm, C_TOOLS, tool, TM, [M04], 'C09', bevel=(0.004, 2, 30.0))
        bm = bm_new(); bm_cyl(bm, 0.09, 0.065, 48, TM @ Matrix.Translation((0, 0, -0.08)))
        mk('C09_BackDrum', bm, C_TOOLS, tool, TM, [M03], 'C09', bevel=(0.01, 3, 30.0))
        # curled backing forms: arc over the top curling forward, plus a smaller side curl
        # torus plane spanned by tool X (up) and tool Z (face normal); a=0 up, a=90 behind, a=-90 front
        CM = TM @ Matrix.Translation((0.035, 0.0, -0.055)) @ Matrix.Rotation(math.radians(-90), 4, 'X')
        bm = bm_new(); bm_torus(bm, 0.088, 0.034, 32, 16, CM @ Matrix.Diagonal((1.0, 1.0, 1.5, 1.0)), arc=(math.radians(-38), math.radians(165)))
        mk('C09_CurlTop', bm, C_TOOLS, tool, TM, [M02], 'C09', smooth_angle=None)
        # side curl wrapping the outer (+tool Y) side: a=0 behind, a=90 outer side, a=180 front
        CM2 = TM @ Matrix.Translation((-0.035, 0.045, -0.065)) @ Matrix.Rotation(math.radians(90), 4, 'Y')
        bm = bm_new(); bm_torus(bm, 0.07, 0.027, 26, 14, CM2, arc=(math.radians(15), math.radians(150)))
        mk('C09_CurlSide', bm, C_TOOLS, tool, TM, [M02], 'C09', smooth_angle=None)
    else:
        # ---------------- C10: source-right tool (robot left, +X)
        x10 = Vector((1.0, -0.05, -0.38)).normalized()
        HC = bv((0.855, -0.075, 0.255))
        HM = frame_matrix(HC, x10, Vector((0, 0, 1)))
        tool = empty('C10_Tool', C_TOOLS, wrist, HM, size=0.08)
        tag(tool, 'C10', 'observed', 'Hanging blade is a tool, not a floor support.')
        seg_cyl('C10_Mount', W, HM @ Vector((-0.075, 0, 0)), 0.026, C_TOOLS, tool, [M03], 'C10', ev='inferred')
        bm = bm_new(); bm_sphere(bm, 1.0, 48, 24, HM @ Matrix.Diagonal((0.112, 0.078, 0.07, 1)))
        mk('C10_Head', bm, C_TOOLS, tool, HM, [M02], 'C10', smooth_angle=None)
        bm = bm_new(); bm_sphere(bm, 1.0, 32, 16, HM @ Matrix.Translation((0.005, -0.052, 0.004)) @ Matrix.Diagonal((0.034, 0.016, 0.026, 1)))
        mk('C10_FrontDetail', bm, C_TOOLS, tool, HM, [M03], 'C10', smooth_angle=None)
        if DET:
            bm = bm_new(); bm_box(bm, 0.03, 0.026, 0.012, HM @ Matrix.Translation((-0.01, 0.0, 0.056)))
            mk('C10_TopDetail', bm, C_DET, tool, HM, [M03], 'C10', bevel=(0.003, 2, 30.0))
        JC = HM @ Vector((0.095, 0, -0.012))
        joint('C10_TipJoint', JC, HM.to_3x3() @ Vector((0, 1, 0)), 0.033, 0.08, C_TOOLS, tool, 'C10')
        # flattened hanging blade (finite thickness), broad faces toward +-local Y
        b0 = HM @ Vector((0.10, 0, -0.02))
        b1 = HM @ Vector((0.16, 0, -0.09))
        b2 = b0 + Vector((0.065, 0.0, -0.235))
        pts = [bezier(b0, b1, b2, i / 14) for i in range(15)]
        yax = (HM.to_3x3() @ Vector((0, 1, 0))).normalized()
        secs = []
        for i, p in enumerate(pts):
            t = i / 14
            if i == 0: tg = pts[1] - pts[0]
            elif i == 14: tg = pts[14] - pts[13]
            else: tg = pts[i + 1] - pts[i - 1]
            tg.normalize()
            nn = yax.cross(tg).normalized()
            w = max(0.046 * (1 - t ** 2.2) ** 0.8, 0.005)
            th = max(0.016 * (1 - t ** 1.5) ** 0.6, 0.004)
            sec = []
            for k in range(16):
                a = 2 * math.pi * k / 16
                ca, sa = math.cos(a), math.sin(a)
                sec.append(p + nn * (w * ca + 0.25 * w * ca * abs(ca)) + yax * (th * sa))
            secs.append(sec)
        bm = bm_new(); bm_loft(bm, secs, True, True, True)
        mk('C10_HangingBlade', bm, C_TOOLS, tool, HM, [M03], 'C10', smooth_angle=50.0)

# ------------------------------------------------------------------ C11 / C12 legs
# Symmetric four-leg layout after the concept sheet (front/rear views): mirrored left/right and
# fore/aft, identical reach. Profile: knee beside the lower body, armour goes out then turns
# down, near-vertical blade. Detail after R01 legs and the concept C11 panel: faceted ridged
# armour plates with seams, bolt holes, latch, joint block, stepped knee/ankle discs, exposed
# dark side plates with warm dots, faceted wedge blade with keel inset.
LEG_FRONT_AZ, LEG_REAR_AZ = 54.0, 126.0
LEG_COMMON = dict(kr=0.56, reach=1.10, split=0.60)
LEGS = {
    # name: azimuth (deg, 0=front -Y, + toward +X), knee radius, reach scale, cowl V-split, evidence
    'C11_RF': dict(az=-LEG_FRONT_AZ, ev='observed', **LEG_COMMON),
    'C11_RR': dict(az=-LEG_REAR_AZ, ev='observed', **LEG_COMMON),
    'C11_LF': dict(az=LEG_FRONT_AZ, ev='observed', **LEG_COMMON),
    'C12_LR_PROPOSED': dict(az=LEG_REAR_AZ, ev='proposed', **LEG_COMMON),
}
HIP_EL = -46.0
KNEE_Z = -0.30
ANKLE = (0.27, -0.38)     # ankle offset from knee (radial scaled by reach, dz)
TIP_DR = 0.37             # tip radial offset from knee (scaled by reach); tip z = -H

def domed_hub(name, c, axis, w, rd, coll, parent, comp, ev):
    """M04 domes on both faces of a disc (axis), each with a dark raised ring around it."""
    bmh = bm_new(); bmr = bm_new()
    for s in (-1, 1):
        f = c + axis * s * (w / 2)
        M = frame_z(f, axis * s)
        bm_sphere(bmh, 1.0, 32, 16, M @ Matrix.Diagonal((rd, rd, rd * 0.55, 1)))
        bm_torus(bmr, rd + 0.012, 0.007, 48, 10, M @ Matrix.Translation((0, 0, 0.002)))
    M = frame_z(c, axis)
    mk(name + 'Hub', bmh, coll, parent, M, [M04], comp, ev, smooth_angle=None)
    mk(name + 'HubRing', bmr, coll, parent, M, [M03], comp, ev, smooth_angle=None)

def stepped_disc(name, c, axis, r, w, coll, parent, comp, ev):
    """Thick dark disc with a raised outer rim and a recessed face on both sides."""
    M = frame_z(c, axis)
    h, hr = w / 2 - 0.013, w / 2
    prof = [(0.02, -h), (r * 0.78, -h), (r * 0.85, -hr), (r, -hr), (r, hr), (r * 0.85, hr), (r * 0.78, h), (0.02, h)]
    bm = bm_new(); bm_revolve(bm, prof, 64, M)
    o = mk(name + 'Housing', bm, coll, parent, M, [M03], comp, ev, bevel=(0.004, 2, 30.0), smooth_angle=30.0)
    return h * 2

def build_leg(name, L):
    a = math.radians(L['az'])
    rad = Vector((math.sin(a), -math.cos(a), 0))
    tan = Vector((math.cos(a), math.sin(a), 0))
    up = Vector((0, 0, 1))
    k = L['reach']
    def lp(r, z, t=0.0):
        return BODY_C + rad * r + up * z + tan * t
    ev = L['ev']
    comp = 'C12' if name.startswith('C12') else 'C11'
    # mirror factor for off-centre details so all four legs are mirror images (L/R and front/rear)
    mf = 1.0 if ((L['az'] < 0) == (abs(L['az']) < 90)) else -1.0
    hipc = chassis_point(L['az'], HIP_EL)
    hip = BODY_C + hipc
    hip_n = hipc.normalized()
    LEG_M = frame_matrix(hip, rad, up)
    leg = empty(name, C_LEGS, C01, LEG_M, size=0.12)
    tag(leg, comp, ev, 'Quadrant assignment is an editable construction convention, not proof of attachment.')
    leg['oow_azimuth_deg'] = L['az']
    kr = L['kr']
    K = lp(kr, KNEE_Z)
    A = lp(kr + ANKLE[0] * k, KNEE_Z + ANKLE[1])
    T = lp(kr + TIP_DR * k, -H + 0.0045)
    # socket
    M = frame_z(hip + hip_n * 0.012, hip_n)
    bm = bm_new(); bm_cyl(bm, 0.080, 0.10, 40, M)
    mk(name + '_HipSocket', bm, C_LEGS, leg, LEG_M, [M03], comp, ev, bevel=(0.01, 3, 30.0))
    if DET:
        bm = bm_new(); bm_cyl(bm, 0.05, 0.11, 32, M)
        mk(name + '_HipCollar', bm, C_LEGS, leg, LEG_M, [M04], comp, ev, bevel=(0.004, 2, 30.0))
    # proximal strut
    s0 = hip + hip_n * 0.045
    d = K - s0
    SM = frame_matrix((s0 + K) / 2, d, up)
    bm = bm_new(); bm_box(bm, d.length + 0.02, 0.075, 0.080, SM)
    mk(name + '_Strut', bm, C_LEGS, leg, SM, [M03], comp, ev, bevel=(0.012, 3, 30.0))
    if DET:
        # orange accent collar near the hip (R01) and a lower secondary rod into the knee
        seg_cyl(name + '_StrutCollar', s0, K, 0.052, C_LEGS, leg, [M02], comp, 0.18, 0.34, (0.008, 2, 30.0), ev=ev)
        ra, rb = s0 - up * 0.05 + tan * 0.0, K - up * 0.075
        seg_cyl(name + '_StrutRod', ra, rb, 0.017, C_LEGS, leg, [M03], comp, 0.0, 1.0, (0.004, 2, 30.0), ev=ev)
        seg_cyl(name + '_StrutRodChrome', ra, rb, 0.011, C_LEGS, leg, [M04], comp, 0.30, 0.80, (0.002, 1, 30.0), ev=ev)
    # knee pivot: thick stepped disc with domed warm hubs
    KM = frame_matrix(K, rad, up)
    knee = empty(name + '_Knee', C_LEGS, leg, KM, size=0.08)
    tag(knee, comp, 'proposed', 'Knee pivot at hinge centre; visual convention.')
    if DET:
        wf = stepped_disc(name + '_Knee', K, tan, 0.120, 0.134, C_LEGS, knee, comp, ev)
        domed_hub(name + '_Knee', K, tan, wf, 0.046, C_LEGS, knee, comp, ev)
    else:
        joint(name + '_Knee', K, tan, 0.118, 0.13, C_LEGS, knee, comp, hub_r=None, ev=ev)
    # spine K -> A: out from the knee, then turning down (concept front view)
    P0, P1 = K, K + rad * 0.20 * k + up * 0.05
    P2, P3 = A + rad * 0.04 + up * 0.26, A
    def spine(t):
        return bezier3(P0, P1, P2, P3, t)
    def frame_at(t):
        e = 1e-3
        tg = (spine(min(t + e, 1.25)) - spine(max(t - e, -0.3))).normalized()
        nn = tan.cross(tg).normalized()      # in-plane normal
        if nn.dot(rad + up) < 0:
            nn = -nn
        return spine(t), tg, nn
    # shin core (dark)
    secs = []
    for i in range(17):
        t = i / 16
        p, tg, nn = frame_at(t)
        an, ay = 0.056 - 0.010 * t, 0.058 - 0.008 * t
        sec = []
        for j in range(16):
            ang = 2 * math.pi * j / 16
            c, s = math.cos(ang), math.sin(ang)
            sec.append(p + nn * (an * math.copysign(abs(c) ** 0.6, c)) + tan * (ay * math.copysign(abs(s) ** 0.6, s)))
        secs.append(sec)
    bm = bm_new(); bm_loft(bm, secs, True, True, True)
    mk(name + '_Shin', bm, C_LEGS, knee, KM, [M03], comp, ev, smooth_angle=50.0)
    # cowl armour: faceted shield with a centre ridge (gable section, chamfered sides). The t-range
    # may vary across the section (f), giving the concept's V-shaped orange/ivory boundary.
    PH = math.radians(96)
    def sp_(v, e=0.62):
        return math.copysign(abs(v) ** e, v)
    def cowl_pt(t, f, inner, lift=0.0):
        p, tg, nn = frame_at(t)
        u = (t - 0.06) / 1.06
        an = 0.100 + 0.016 * math.sin(math.pi * min(max(u, 0), 1)) + lift
        ay = 0.108 - 0.014 * u + lift * 0.5
        if t > 0.92:   # chisel-pointed lower end overhanging the blade
            q = min((t - 0.92) / 0.20, 1.0)
            ay *= 1.0 - 0.55 * q
            an *= 1.0 - 0.25 * q
        if inner:
            an -= 0.034; ay -= 0.034
        fa = f * PH
        if not DET:
            return p + nn * (an * sp_(math.cos(fa))) + tan * (ay * sp_(math.sin(fa)))
        # gable section: centre ridge with two sloped facets (|f| <= 0.8), then near-vertical
        # side skirts (|f| > 0.8) -- reads as an angular armour plate instead of a tube
        af = abs(f)
        rn = an * (1.0 - 0.30 * min(af, 0.8))
        if af > 0.8:
            rn -= an * (af - 0.8) * 2.6
        ry = ay * math.copysign(min(abs(math.sin(fa)) / math.sin(PH * 0.8), 1.0), f)
        return p + nn * rn + tan * ry
    def cowl(nm, tlo, thi, material, steps=16, N=16, lift=0.0, coll=None, frange=(-1.0, 1.0)):
        f0, f1 = frange
        fs = [f0 + (f1 - f0) * j / N for j in range(N + 1)]
        secs = []
        for i in range(steps + 1):
            u = i / steps
            sec = [cowl_pt(tlo(f) + u * (thi(f) - tlo(f)), f, False, lift) for f in fs]
            sec += [cowl_pt(tlo(f) + u * (thi(f) - tlo(f)), f, True, lift) for f in reversed(fs)]
            secs.append(sec)
        bm = bm_new(); bm_loft(bm, secs, True, True, True)
        return mk(nm, bm, coll or C_LEGS, knee, KM, [material], comp, ev, bevel=(0.004, 2, 25.0), smooth_angle=18.0)
    def surf(t, f, lift=0.0):
        """point and outward normal on the cowl outer surface"""
        e = 0.01
        p0 = cowl_pt(t, f, False, lift)
        pt_ = cowl_pt(t + e, f, False, lift) - cowl_pt(t - e, f, False, lift)
        pf = cowl_pt(t, f + e, False, lift) - cowl_pt(t, f - e, False, lift)
        n = pf.cross(pt_).normalized()
        if n.dot(p0 - spine(t)) < 0:
            n = -n
        return p0, n
    def dot(nm, t, f, r, mat, lift=0.0, depth=0.012, proud=0.002):
        p0, n = surf(t, f * mf, lift)
        Md = frame_z(p0 + n * (proud - depth / 2), n)
        bm = bm_new(); bm_cyl(bm, r, depth, 20, Md)
        mk(nm, bm, C_DET, knee, KM, [mat], comp, ev, bevel=(min(0.003, r * 0.3), 1, 30.0), smooth_angle=40.0)
    sp = L['split']
    vsplit = lambda f: sp + 0.20 * (1 - abs(f)) - 0.06      # orange tongue pointing down the ridge
    if DET:
        cowl(name + '_CowlCap', lambda f: 0.05, lambda f: 0.19, M02, lift=0.010)
        # main orange plate split along its length by a seam (concept C11 panel line)
        fr_main, fr_side = ((-1.0, 0.36), (0.42, 1.0)) if mf > 0 else ((-0.36, 1.0), (-1.0, -0.42))
        cowl(name + '_CowlUpper', lambda f: 0.205, vsplit, M02, N=14, frange=fr_main)
        cowl(name + '_CowlUpperSide', lambda f: 0.205, vsplit, M02, N=6, frange=fr_side)
        cowl(name + '_CowlLower', lambda f: vsplit(f) + 0.022, lambda f: 0.93, M01)
        cowl(name + '_CowlTip', lambda f: 0.955, lambda f: 1.10, M01, lift=0.006)
    else:
        cowl(name + '_CowlUpper', lambda f: 0.06, vsplit, M02)
        cowl(name + '_CowlLower', lambda f: vsplit(f) + 0.022, lambda f: 1.10, M02)
    if DET:
        # small ivory latch with a dark slot on the cap crown (concept C11)
        p0, n = surf(0.13, 0.0, 0.010)
        p, tg, nn = frame_at(0.13)
        CM_ = frame_matrix(p0 + n * 0.008, tg, n)
        bm = bm_new(); bm_box(bm, 0.075, 0.052, 0.022, CM_)
        mk(name + '_CowlLatch', bm, C_DET, knee, KM, [M01], comp, ev, bevel=(0.006, 2, 30.0))
        bm = bm_new(); bm_box(bm, 0.03, 0.022, 0.012, CM_ @ Matrix.Translation((0.012, 0, 0.011)))
        mk(name + '_CowlLatchSlot', bm, C_DET, knee, KM, [M03], comp, ev, bevel=(0.002, 1, 30.0))
        # bolt heads on the orange plate and a dark bolt hole on the ivory panel (R01 / C11)
        dot(name + '_BoltA', 0.33, -0.55, 0.010, M03)
        dot(name + '_BoltB', 0.33, 0.55, 0.010, M03)
        dot(name + '_BoltHole', 0.84, 0.45, 0.019, M03, depth=0.010, proud=0.0015)
        dot(name + '_BoltHoleRim', 0.84, 0.45, 0.026, M01, depth=0.006, proud=0.0010)
        dot(name + '_BoltC', 0.50, -0.30, 0.009, M03)
        # dark joint block bridging the knee disc and the armour cap (concept front view)
        p, tg, nn = frame_at(0.06)
        JB = frame_matrix(p + nn * 0.075, tg, nn)
        bm = bm_new(); bm_box(bm, 0.10, 0.118, 0.07, JB)
        mk(name + '_JointBlock', bm, C_LEGS, knee, KM, [M03], comp, ev, bevel=(0.014, 2, 30.0))
        # exposed dark side plates under the armour edge with warm dots (inner mechanism)
        for tt, sz, tag_ in ((0.52, (0.12, 0.075, 0.022), 'U'), (0.82, (0.14, 0.09, 0.024), 'L')):
            p, tg, nn = frame_at(tt)
            for s, sn in ((-1, 'A'), (1, 'B')):
                c = p + tan * s * 0.066 - nn * 0.045
                PM = frame_matrix(c, tg, tan * s)
                bm = bm_new(); bm_box(bm, *sz, PM)
                mk(name + '_ShinPlate' + tag_ + sn, bm, C_LEGS, knee, KM, [M03], comp, ev, bevel=(0.016, 2, 30.0))
                bm = bm_new(); bm_cyl(bm, 0.013, 0.012, 20, PM @ Matrix.Translation((sz[0] * 0.22, -sz[1] * 0.12, sz[2] / 2)))
                mk(name + '_ShinDot' + tag_ + sn, bm, C_DET, knee, KM, [M04], comp, ev, smooth_angle=40.0)
        # dark under-lip plate between the chisel armour end and the blade root
        p, tg, nn = frame_at(1.04)
        UL = frame_matrix(p + nn * 0.015, tg, nn)
        bm = bm_new(); bm_box(bm, 0.09, 0.115, 0.04, UL)
        mk(name + '_UnderLip', bm, C_LEGS, knee, KM, [M03], comp, ev, bevel=(0.012, 2, 30.0))
    # ankle pivot
    ank = empty(name + '_Ankle', C_LEGS, knee, frame_matrix(A, rad, up), size=0.06)
    tag(ank, comp, 'proposed', 'Ankle pivot; visual convention.')
    if DET:
        wf = stepped_disc(name + '_Ankle', A, tan, 0.072, 0.19, C_LEGS, ank, comp, ev)
        domed_hub(name + '_Ankle', A, tan, wf, 0.028, C_LEGS, ank, comp, ev)
    else:
        joint(name + '_Ankle', A, tan, 0.068, 0.165, C_LEGS, ank, comp, hub_r=None, ev=ev)
    # blade foot: faceted wedge (outer keel, flat broad faces, chamfered edges), finite thickness
    b0 = A + up * 0.03 - rad * 0.005
    b1 = (A + T) / 2 + rad * 0.03
    b2 = T
    def blade_wt(t):
        return (max(0.086 * (1 - t ** 2.0) ** 0.75, 0.006), max(0.056 * (1 - t ** 1.8) ** 0.7, 0.005))
    # section outline in (n, y) units: keel, shoulders, chamfers, flat inner face (closed loop)
    SEC = [(1.15, 0.0), (0.80, 0.30), (0.45, 0.80), (0.20, 1.0), (-0.45, 1.0), (-0.85, 0.75),
           (-1.0, 0.30), (-1.0, -0.30), (-0.85, -0.75), (-0.45, -1.0), (0.20, -1.0), (0.45, -0.80), (0.80, -0.30)]
    if not DET:
        SEC = [(math.cos(2 * math.pi * j / 16) * (1.15 if math.cos(2 * math.pi * j / 16) > 0 else 1.0),
                math.sin(2 * math.pi * j / 16)) for j in range(16)]
    pts = [bezier(b0, b1, b2, i / 18) for i in range(19)]
    secs = []
    for i, p in enumerate(pts):
        t = i / 18
        if i == 0: tg = pts[1] - pts[0]
        elif i == 18: tg = pts[18] - pts[17]
        else: tg = pts[i + 1] - pts[i - 1]
        tg.normalize()
        nn = tan.cross(tg).normalized()
        if nn.dot(rad) < 0:
            nn = -nn
        w, th = blade_wt(t)
        secs.append([p + nn * (th * a_) + tan * (w * b_) for a_, b_ in SEC])
    # exact contact: lowest blade point on Z=0 (detailed: offset for the tip shrink of the Bevel modifier)
    dz = min(p.z for sec in secs for p in sec) + (0.00023 if DET else 0.0)
    secs = [[p - Vector((0, 0, dz)) for p in sec] for sec in secs]
    bm = bm_new(); bm_loft(bm, secs, True, True, True)
    ob_ = mk(name + '_Blade', bm, C_LEGS, ank, frame_matrix(A, rad, up), [M03], comp, ev,
             bevel=(0.003, 2, 25.0), smooth_angle=22.0)
    if DET:
        # orange inset strip along the outer keel (concept C11), following the facets
        secs = []
        for i in range(12):
            t = 0.04 + 0.56 * i / 11
            p = bezier(b0, b1, b2, t) - Vector((0, 0, dz))
            tg = (bezier(b0, b1, b2, t + 0.01) - bezier(b0, b1, b2, t - 0.01)).normalized()
            nn = tan.cross(tg).normalized()
            if nn.dot(rad) < 0: nn = -nn
            w, th = blade_wt(t)
            o_ = [(1.15, 0.0), (0.80, 0.30), (0.62, 0.55)]
            outer = [(a_ * th + 0.006, b_ * w * 1.02) for a_, b_ in o_]
            sec_n = [(a_, -b_) for a_, b_ in reversed(outer[1:])] + outer
            inner = [(a_ - 0.008, b_ * 0.93) for a_, b_ in sec_n]
            loop = sec_n + list(reversed(inner))
            secs.append([p + nn * a_ + tan * b_ for a_, b_ in loop])
        bm = bm_new(); bm_loft(bm, secs, True, True, True)
        mk(name + '_BladePlate', bm, C_LEGS, ank, frame_matrix(A, rad, up), [M02], comp, ev,
           bevel=(0.002, 1, 25.0), smooth_angle=22.0)
    return leg

for nm, L in LEGS.items():
    build_leg(nm, L)
# heavier painted wear on the legs (read by the shared M01/M02 graphs via object property)
for ob in C_LEGS.all_objects:
    ob['oow_wear'] = 1.0
for ob in C_DET.all_objects:
    if ob.get('oow_component') in ('C11', 'C12'):
        ob['oow_wear'] = 1.0

# ------------------------------------------------------------------ C02/C03 small details
if DET:
    # simple emblem mark on top band (house-like outline, no lettering)
    phi = math.radians(52)
    n = Vector((0, -math.cos(phi), math.sin(phi)))
    c = BODY_C + n * (P['R_SHELL'] + BAND_RAISE + 0.0005)
    xax = Vector((1, 0, 0)); yax = n.cross(xax).normalized()   # yax points 'up the band'
    s = 0.024
    outline = [(-1, -1), (1, -1), (1, 0.45), (0, 1.2), (-1, 0.45)]
    segsl = list(zip(outline, outline[1:] + outline[:1])) + [((0.0, -0.75), (0.0, 0.35))]
    bm = bm_new()
    for (x0, y0), (x1, y1) in segsl:
        p0 = c + xax * x0 * s + yax * y0 * s
        p1 = c + xax * x1 * s + yax * y1 * s
        mid = (p0 + p1) / 2
        dd = p1 - p0
        M = frame_matrix(mid, dd, n)
        bm_box(bm, dd.length + 0.005, 0.005, 0.003, M)
    mk('C03_EmblemMark', bm, C_DET, C01, BODY_M, [M03], 'C03', smooth_angle=None,
       note='Simple reference-matched mark; no lettering.')

sc.view_layers[0].update()
print('LEVEL', LEVEL, 'objects:', len(root_coll.all_objects))
