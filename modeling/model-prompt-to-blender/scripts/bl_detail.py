"""Reusable hard-surface DETAIL builders (import after bl_build).

    import bl_build as bl, bl_detail as dl

Builders take world-space inputs and return objects created through bl.mk().
Techniques (see ../references/detail-techniques.md for when to use each):
- ArmourProfile: faceted 'gable' armour shell along a spine (centre ridge + side skirts),
  panel splits along the spine, V-shaped colour splits, raised caps, chisel ends, surface points.
- stepped_disc / domed_hub: thick joint discs with raised rim, recessed face, domed hub + ring.
- faceted_wedge (+ keel_strip): blade/claw with keel, chamfers, flat inner face, inset strip.
- capsule_cutter / slot_bezel: recessed slots cut through a spherical shell + raised dark bezel.
- rivet_cluster: many small domes in ONE object (cheap, editable).
- side_plate: rounded plate with a warm dot (exposed mechanism).
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix
import bl_build as bl


# ----------------------------------------------------------------------------- spine along a limb
class Spine:
    """Cubic Bezier spine with a stable in-plane normal (side_axis = hinge/tangent axis)."""

    def __init__(self, p0, p1, p2, p3, side_axis, outward_hint):
        self.P = [Vector(p0), Vector(p1), Vector(p2), Vector(p3)]
        self.side = Vector(side_axis).normalized()
        self.out = Vector(outward_hint).normalized()

    def point(self, t):
        return bl.bezier3(*self.P, t)

    def frame(self, t, e=1e-3):
        tg = (self.point(min(t + e, 1.3)) - self.point(max(t - e, -0.3))).normalized()
        nn = self.side.cross(tg).normalized()
        if nn.dot(self.out) < 0:
            nn = -nn
        return self.point(t), tg, nn


def tube_along(name, spine, size_fn, mat, coll, parent, pivot, comp, ev, steps=16, segs=16, exp=0.6,
               smooth_angle=50.0):
    """Rounded-rect tube (shin core / inner mechanism). size_fn(t) -> (half_n, half_side)."""
    secs = []
    for i in range(steps + 1):
        t = i / steps
        p, tg, nn = spine.frame(t)
        an, ay = size_fn(t)
        sec = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            c, s = math.cos(a), math.sin(a)
            sec.append(p + nn * (an * math.copysign(abs(c) ** exp, c)) + spine.side * (ay * math.copysign(abs(s) ** exp, s)))
        secs.append(sec)
    bm = bl.bm_new()
    bl.bm_loft(bm, secs, True, True, True)
    return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, smooth_angle=smooth_angle)


class ArmourProfile:
    """Armour plate wrapping the outer side of a spine.

    size_fn(t) -> (an, ay): half extents along the outward normal and the side axis.
    profile 'gable': centre ridge (slope `ridge`) + near-vertical skirts beyond |f| > 0.8.
    profile 'round': superellipse arc (blockout look).
    chisel=(t_start, t_len, side_scale, normal_scale): pointed end.
    f in [-1, 1] runs across the plate (side to side); t along the spine.
    """

    def __init__(self, spine, size_fn, thick=0.034, wrap_deg=96.0, profile='gable', ridge=0.30, skirt=2.6,
                 chisel=None):
        self.s, self.size_fn, self.thick = spine, size_fn, thick
        self.PH = math.radians(wrap_deg)
        self.profile, self.ridge, self.skirt, self.chisel = profile, ridge, skirt, chisel

    def point(self, t, f, inner=False, lift=0.0):
        p, tg, nn = self.s.frame(t)
        an, ay = self.size_fn(t)
        an += lift
        ay += lift * 0.5
        if self.chisel and t > self.chisel[0]:
            q = min((t - self.chisel[0]) / self.chisel[1], 1.0)
            ay *= 1.0 - self.chisel[2] * q
            an *= 1.0 - self.chisel[3] * q
        if inner:
            an -= self.thick
            ay -= self.thick
        fa = f * self.PH
        if self.profile == 'round':
            sp = lambda v: math.copysign(abs(v) ** 0.62, v)
            return p + nn * (an * sp(math.cos(fa))) + self.s.side * (ay * sp(math.sin(fa)))
        af = abs(f)
        rn = an * (1.0 - self.ridge * min(af, 0.8))
        if af > 0.8:
            rn -= an * (af - 0.8) * self.skirt
        ry = ay * math.copysign(min(abs(math.sin(fa)) / math.sin(self.PH * 0.8), 1.0), f)
        return p + nn * rn + self.s.side * ry

    def surface(self, t, f, lift=0.0, e=0.01):
        """Outer surface point and outward normal (for bolts, latches, decals)."""
        p0 = self.point(t, f, False, lift)
        dt = self.point(t + e, f, False, lift) - self.point(t - e, f, False, lift)
        df = self.point(t, f + e, False, lift) - self.point(t, f - e, False, lift)
        n = df.cross(dt).normalized()
        if n.dot(p0 - self.s.point(t)) < 0:
            n = -n
        return p0, n

    def build(self, name, tlo, thi, mat, coll, parent, pivot, comp, ev, steps=16, N=16, lift=0.0,
              frange=(-1.0, 1.0), bevel=(0.004, 2, 25.0), smooth_angle=18.0):
        """tlo/thi: callables f -> t. A t-range varying with f gives V-shaped colour splits;
        frange splits a plate lengthwise (panel seam). Build adjacent pieces with a small t/f gap."""
        f0, f1 = frange
        fs = [f0 + (f1 - f0) * j / N for j in range(N + 1)]
        secs = []
        for i in range(steps + 1):
            u = i / steps
            sec = [self.point(tlo(f) + u * (thi(f) - tlo(f)), f, False, lift) for f in fs]
            sec += [self.point(tlo(f) + u * (thi(f) - tlo(f)), f, True, lift) for f in reversed(fs)]
            secs.append(sec)
        bm = bl.bm_new()
        bl.bm_loft(bm, secs, True, True, True)
        return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=bevel, smooth_angle=smooth_angle)


def surface_dot(name, prof, t, f, r, mat, coll, parent, pivot, comp, ev, lift=0.0, depth=0.012, proud=0.002):
    """Bolt head / dark bolt hole seated on an ArmourProfile surface."""
    p0, n = prof.surface(t, f, lift)
    M = bl.frame_z(p0 + n * (proud - depth / 2), n)
    bm = bl.bm_new()
    bl.bm_cyl(bm, r, depth, 20, M)
    return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=(min(0.003, r * 0.3), 1, 30.0),
                 smooth_angle=40.0)


# ----------------------------------------------------------------------------- joints
def stepped_disc(name, c, axis, r, w, mat, coll, parent, pivot, comp, ev, step=0.013, segs=64):
    """Thick disc: raised outer rim + recessed face on both sides. Returns face-to-face width."""
    M = bl.frame_z(Vector(c), Vector(axis))
    h, hr = w / 2 - step, w / 2
    prof = [(0.02, -h), (r * 0.78, -h), (r * 0.85, -hr), (r, -hr), (r, hr), (r * 0.85, hr), (r * 0.78, h), (0.02, h)]
    bm = bl.bm_new()
    bl.bm_revolve(bm, prof, segs, M)
    bl.mk(name + 'Housing', bm, coll, parent, pivot, [mat], comp, ev, bevel=(0.004, 2, 30.0), smooth_angle=30.0)
    return 2 * h


def domed_hub(name, c, axis, w, rd, hub_mat, ring_mat, coll, parent, pivot, comp, ev):
    """Domed hub on both faces of a disc (face-to-face width w) with a raised ring around each."""
    bmh, bmr = bl.bm_new(), bl.bm_new()
    axis = Vector(axis).normalized()
    for s in (-1, 1):
        M = bl.frame_z(Vector(c) + axis * s * (w / 2), axis * s)
        bl.bm_sphere(bmh, 1.0, 32, 16, M @ Matrix.Diagonal((rd, rd, rd * 0.55, 1)))
        bl.bm_torus(bmr, rd + 0.012, 0.007, 48, 10, M @ Matrix.Translation((0, 0, 0.002)))
    bl.mk(name + 'Hub', bmh, coll, parent, pivot, [hub_mat], comp, ev, smooth_angle=None)
    bl.mk(name + 'HubRing', bmr, coll, parent, pivot, [ring_mat], comp, ev, smooth_angle=None)


# ----------------------------------------------------------------------------- blades / claws
WEDGE_SECTION = [(1.15, 0.0), (0.80, 0.30), (0.45, 0.80), (0.20, 1.0), (-0.45, 1.0), (-0.85, 0.75),
                 (-1.0, 0.30), (-1.0, -0.30), (-0.85, -0.75), (-0.45, -1.0), (0.20, -1.0), (0.45, -0.80),
                 (0.80, -0.30)]   # (normal, side) units: keel at +normal, flat inner face at -normal


def faceted_wedge(name, path, side_axis, outward_hint, wt_fn, mat, coll, parent, pivot, comp, ev,
                  steps=18, section=WEDGE_SECTION, ground_z=None, bevel=(0.003, 2, 25.0), bevel_tip_comp=0.00023):
    """Blade along path(t) (t 0..1). wt_fn(t) -> (half_width_side, half_thickness_normal).
    ground_z: shift so the lowest point (after the Bevel tip shrink) sits exactly on ground_z."""
    side = Vector(side_axis).normalized()
    pts = [path(i / steps) for i in range(steps + 1)]
    secs = []
    for i, p in enumerate(pts):
        tg = (pts[min(i + 1, steps)] - pts[max(i - 1, 0)]).normalized()
        nn = side.cross(tg).normalized()
        if nn.dot(Vector(outward_hint)) < 0:
            nn = -nn
        w, th = wt_fn(i / steps)
        secs.append([p + nn * (th * a) + side * (w * b) for a, b in section])
    dz = 0.0
    if ground_z is not None:
        dz = min(p.z for sec in secs for p in sec) - ground_z + (bevel_tip_comp if bevel else 0.0)
        secs = [[p - Vector((0, 0, dz)) for p in sec] for sec in secs]
    bm = bl.bm_new()
    bl.bm_loft(bm, secs, True, True, True)
    ob = bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=bevel, smooth_angle=22.0)
    return ob, dz


def keel_strip(name, path, side_axis, outward_hint, wt_fn, mat, coll, parent, pivot, comp, ev, t0=0.04, t1=0.60,
               dz=0.0, steps=12):
    """Raised inset strip following the keel facets of faceted_wedge (same path/wt_fn/dz)."""
    side = Vector(side_axis).normalized()
    outer_u = [(1.15, 0.0), (0.80, 0.30), (0.62, 0.55)]
    secs = []
    for i in range(steps):
        t = t0 + (t1 - t0) * i / (steps - 1)
        p = path(t) - Vector((0, 0, dz))
        tg = (path(t + 0.01) - path(t - 0.01)).normalized()
        nn = side.cross(tg).normalized()
        if nn.dot(Vector(outward_hint)) < 0:
            nn = -nn
        w, th = wt_fn(t)
        outer = [(a * th + 0.006, b * w * 1.02) for a, b in outer_u]
        loop_o = [(a, -b) for a, b in reversed(outer[1:])] + outer
        loop_i = [(a - 0.008, b * 0.93) for a, b in loop_o]
        loop = loop_o + list(reversed(loop_i))
        secs.append([p + nn * a + side * b for a, b in loop])
    bm = bl.bm_new()
    bl.bm_loft(bm, secs, True, True, True)
    return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=(0.002, 1, 25.0), smooth_angle=22.0)


# ----------------------------------------------------------------------------- spherical shells
def capsule_frame(az, el, tilt_deg):
    d = bl.sph_dir(az, el)
    t_el, t_az = bl.tangent_frame(d, az)
    a = math.radians(tilt_deg)
    ax = (t_el * math.cos(a) + t_az * math.sin(a)).normalized()
    return d, ax, d.cross(ax).normalized()


def capsule_pts(ax, sd, length, width, n=12):
    hl = max(length / 2 - width / 2, 0.0)
    pts = []
    for i in range(n):
        a = -math.pi / 2 + math.pi * i / (n - 1)
        pts.append(ax * (hl + math.cos(a) * width / 2) + sd * (math.sin(a) * width / 2))
    for i in range(n):
        a = math.pi / 2 + math.pi * i / (n - 1)
        pts.append(ax * (-hl + math.cos(a) * width / 2) + sd * (math.sin(a) * width / 2))
    return pts


def capsule_cutter(name, coll, center, az, el, length, width, tilt, r0, r1):
    """Rounded slot prism along the radial direction from distance r0 to r1 (world units)."""
    d, ax, sd = capsule_frame(az, el, tilt)
    pts = capsule_pts(ax, sd, length, width)
    bm = bl.bm_new()
    c = Vector(center)
    inner = [bm.verts.new(c + d * r0 + p) for p in pts]
    outer = [bm.verts.new(c + d * r1 + p) for p in pts]
    n = len(pts)
    bm.faces.new(list(reversed(inner)))
    bm.faces.new(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((inner[i], inner[j], outer[j], outer[i]))
    return bl._cutter(name, coll, bm)


def slot_bezel(name, center, R, az, el, length, width, tilt, r_top, mat, coll, parent, pivot, comp, ev,
               rim=0.013, grow=0.012, depth=0.040):
    """Raised dark frame around a capsule slot cut in a sphere of radius R, conformed to it."""
    d, ax, sd = capsule_frame(az, el, tilt)
    outer = capsule_pts(ax, sd, length + 2 * grow, width + 2 * grow, 14)
    inner = capsule_pts(ax, sd, length - 2 * rim, max(width - 2 * rim, 0.01), 14)
    c = Vector(center)
    proj = lambda p, r: c + (d * R + p).normalized() * r
    loops = [[proj(p, r_top) for p in outer], [proj(p, r_top) for p in inner],
             [proj(p, r_top - depth) for p in inner], [proj(p, r_top - depth) for p in outer]]
    bm = bl.bm_new()
    bl.bm_ring_loops(bm, loops)
    return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=(0.003, 2, 30.0), smooth_angle=35.0)


def rivet_cluster(name, center, items, mat, coll, parent, pivot, comp, ev, r=0.0085, h=0.004):
    """items: [(unit_direction, radius_from_center)] -> one mesh of flattened domes."""
    bm = bl.bm_new()
    c = Vector(center)
    for dv, rad in items:
        dv = Vector(dv).normalized()
        bl.bm_sphere(bm, 1.0, 16, 8, bl.frame_z(c + dv * rad, dv) @ Matrix.Diagonal((r, r, h, 1)))
    return bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, smooth_angle=None)


def side_plate(name, c, long_axis, normal_axis, size, mat, dot_mat, coll, parent, pivot, comp, ev, dot_r=0.013):
    """Rounded mechanical plate (size = long, across, thick) with a warm dot near one end."""
    PM = bl.frame_matrix(Vector(c), Vector(long_axis), Vector(normal_axis))
    bm = bl.bm_new()
    bl.bm_box(bm, *size, PM)
    # bevel wider than ~half the thickness collapses edges (zero-length edges): keep <= 0.45 * thickness
    plate = bl.mk(name, bm, coll, parent, pivot, [mat], comp, ev, bevel=(min(0.016, size[2] * 0.45), 2, 30.0))
    bm = bl.bm_new()
    # offset only along local X/Z: local Y flips between mirrored right-handed frames (breaks symmetry)
    bl.bm_cyl(bm, dot_r, 0.012, 20, PM @ Matrix.Translation((size[0] * 0.22, 0.0, size[2] / 2)))
    dot = bl.mk(name + 'Dot', bm, coll, parent, pivot, [dot_mat], comp, ev, smooth_angle=40.0)
    return plate, dot


def panelize_sphere_shell(center, R, thick, z_bottom, cutters, classify, coll, parent, pivot, segs=(160, 80)):
    """Spherical armour shell split into separate panels by thin cutters.

    cutters: list of cutter objects (slabs, cylinders, prisms, capsules) - applied sequentially.
    classify(centroid_local, island_bmesh) -> (name, material, comp, evidence, raise_amount) or None.
    raise_amount scales a panel radially (layered armour). Poles are rotated onto +-X so they can
    hide inside side holes (e.g. shoulder cut-outs).
    Returns the created panel objects.
    """
    c = Vector(center)
    bm = bl.bm_new()
    bl.bm_sphere(bm, R, segs[0], segs[1], m=Matrix.Rotation(math.radians(90), 4, 'Y'))
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                           plane_co=Vector((0, 0, z_bottom)), plane_no=Vector((0, 0, 1)), clear_inner=True)
    for v in bm.verts:
        v.co = c + v.co
    me = bl.finish_mesh('TMP_Shell', bm, smooth=True, sharp_angle=None)
    shell = bpy.data.objects.new('TMP_Shell', me)
    coll.objects.link(shell)
    bl.mod_solidify(shell, thick, -1.0)
    bl.apply_modifiers(shell)
    bl.bool_sequential(shell, cutters)
    islands = bl.split_islands(shell)
    bpy.data.objects.remove(shell, do_unlink=True)
    made, counts = [], {}
    for cen, ibm, nv in islands:
        res = classify(cen - c, ibm) if nv >= 40 else None
        if res is None:
            ibm.free()
            continue
        name, mat, comp, ev, raise_ = res
        if raise_:
            k = 1.0 + raise_ / R
            for v in ibm.verts:
                v.co = c + (v.co - c) * k
        n = counts.get(name, 0)
        counts[name] = n + 1
        if n:
            name = '%s_%d' % (name, n + 1)
        made.append(bl.mk(name, ibm, coll, parent, pivot, [mat], comp, ev, bevel=(0.0055, 3, 40.0), smooth_angle=40.0))
    return made
