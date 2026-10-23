"""End-to-end smoke test of the shared libraries in an isolated background Blender.

  "<blender.exe>" -b --factory-startup --python smoke_test.py -- <out_dir>

Builds a tiny symmetric orb-walker-like asset (panelized shell, slot bezel, rivets, layered ring +
emitter, two mirrored legs with armour/discs/hubs/wedge blades), assigns materials, renders a
clay + material diagnostic image, runs topology and symmetry checks and saves a .blend.
Exit code 0 and 'SMOKE_OK' when everything ran; check results are printed as JSON.
"""
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bpy
from mathutils import Vector, Matrix
import bl_build as bl, bl_detail as dl, bl_materials as bm_, bl_views as bv, bl_check as bc, bl_symmetry as bs

out_dir = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else os.path.join(HERE, '_smoke_out')
os.makedirs(out_dir, exist_ok=True)

bl.CTX.update(scene='SMOKE_Scene', detailed=True)
sc = bl.get_scene()
root = bl.get_coll('SMOKE', sc.collection)
BODY, LEGS, DET, PRES = (bl.get_coll(n, root) for n in ('SMOKE_BODY', 'SMOKE_LEGS', 'SMOKE_DETAILS', 'SMOKE_PRES'))
TMP = bl.get_coll('SMOKE_CUTTERS', root)

M01 = bm_.painted('S_M01_Ivory', (0.64, 0.51, 0.37), 0.64, (0.09, 0.065, 0.05), (0.2, 0.14, 0.1), fleck_col=(0.8, 0.2, 0.02))
M02 = bm_.painted('S_M02_Orange', (0.86, 0.17, 0.014), 0.58, (0.12, 0.05, 0.025), (0.3, 0.08, 0.02))
M03 = bm_.plain('S_M03_Charcoal', (0.055, 0.04, 0.033), 0.68)
M04 = bm_.plain('S_M04_Warm', (0.36, 0.11, 0.025), 0.5)
M05 = bm_.emitter('S_M05_Emitter', gain=2.6)
CLAY = bm_.clay('S_Clay')

H = 1.0
C = Vector((0, 0, H))
BODY_M = Matrix.Translation(C)
ROOT = bl.empty('S_ROOT', root, None, Matrix.Identity(4), 0.3, 'ARROWS')
bm = bl.bm_new(); bl.bm_sphere(bm, 0.478, 64, 32, BODY_M)
CH = bl.mk('S_Chassis', bm, BODY, ROOT, BODY_M, [M03], 'C01')

# --- panelized shell: belt, two meridians, ring hole, one capsule slot
R, g = 0.505, 0.01
cut = [bl.slab_cutter('cut_belt', TMP, C + Vector((0, 0, -0.03)), (1, 0, 0), (0, 0, 1), 1.4, g, 1.4)]
for az in (62, -62):
    dv = bl.sph_dir(az, 0)
    t = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
    cut.append(bl.slab_cutter('cut_mer', TMP, C + dv * 0.45 + Vector((0, 0, 0.33)), dv, t, 0.5, g, 0.72))
# crown latitude seam closes the top so the meridians actually separate front and back panels
cut.append(bl.slab_cutter('cut_crown', TMP, C + Vector((0, 0, 0.437)), (1, 0, 0), (0, 0, 1), 1.4, g, 1.4))
cut.append(bl.cyl_cutter('cut_ring', TMP, C + Vector((0, -0.45, 0)), (0, 1, 0), 0.228, 0.7))
cut.append(dl.capsule_cutter('cut_slot', TMP, C, 46, 33, 0.12, 0.05, 30, 0.40, 0.70))


def classify(c, ibm):
    if c.z > 0.42:
        return ('S_Crown', M01, 'C02', 'observed', 0.0)
    if c.z > -0.03:
        side = 'F' if c.y < 0 and abs(math.degrees(math.atan2(c.x, -c.y))) < 62 else 'S'
        return ('S_Upper_' + side + ('R' if c.x < 0 else 'L'), M01, 'C02', 'observed', 0.0)
    return ('S_Lower', M02, 'C03', 'observed', 0.01)


panels = dl.panelize_sphere_shell(C, R, 0.025, -0.28, cut, classify, BODY, CH, BODY_M)
bl.clear_coll(TMP)
dl.slot_bezel('S_SlotBezel', C, R, 46, 33, 0.12, 0.05, 30, R + 0.006, M03, DET, CH, BODY_M, 'C02', 'observed')
dl.rivet_cluster('S_Rivets', C, [(bl.sph_dir(a, 10), R + 0.0005) for a in (-70, -40, 40, 70)], M03, DET, CH, BODY_M, 'C02', 'observed')

# --- layered ring + emitter
RM = BODY_M @ bl.frame_z(Vector((0, 0, 0)), Vector((0, -1, 0)))
prof = [(0.1, 0.36), (0.222, 0.36), (0.222, 0.505), (0.2, 0.541), (0.17, 0.537), (0.15, 0.522), (0.138, 0.47), (0.126, 0.41), (0.1, 0.405)]
bm = bl.bm_new(); bl.bm_revolve(bm, prof, 96, RM)
bl.mk('S_Ring', bm, BODY, CH, RM, [M03], 'C04', bevel=(0.0025, 2, 30.0), smooth_angle=30.0)
bm = bl.bm_new(); bl.bm_sphere(bm, 1.0, 48, 24, RM @ Matrix.Translation((0, 0, 0.405)) @ Matrix.Diagonal((0.118, 0.118, 0.045, 1)))
core = bl.mk('S_Core', bm, BODY, CH, RM, [M05], 'C05', smooth_angle=None)
core['oow_emit_scale'] = 1.0


# --- one leg builder used for a mirrored pair
def leg(name, az):
    a = math.radians(az)
    rad, tan, up = Vector((math.sin(a), -math.cos(a), 0)), Vector((math.cos(a), math.sin(a), 0)), Vector((0, 0, 1))
    mf = bl.mirror_factor(az)
    lp = lambda r, z: C + rad * r + up * z
    K, A, T = lp(0.56, -0.30), lp(0.86, -0.68), lp(0.97, -H)
    LM = bl.frame_matrix(K, rad, up)
    root_ = bl.empty(name, LEGS, CH, LM, 0.1)
    bl.tag(root_, 'C11', 'observed')
    w = dl.stepped_disc(name + '_Knee', K, tan, 0.12, 0.134, M03, LEGS, root_, LM, 'C11', 'observed')
    dl.domed_hub(name + '_Knee', K, tan, w, 0.046, M04, M03, LEGS, root_, LM, 'C11', 'observed')
    sp = dl.Spine(K, K + rad * 0.22 + up * 0.05, A + rad * 0.04 + up * 0.26, A, tan, rad + up)
    dl.tube_along(name + '_Shin', sp, lambda t: (0.056 - 0.01 * t, 0.058 - 0.008 * t), M03, LEGS, root_, LM, 'C11', 'observed')
    prof_ = dl.ArmourProfile(sp, lambda t: (0.100 + 0.016 * math.sin(math.pi * min(max((t - 0.06) / 1.06, 0), 1)),
                                           0.108 - 0.014 * (t - 0.06) / 1.06), chisel=(0.92, 0.20, 0.55, 0.25))
    vs = lambda f: 0.60 + 0.20 * (1 - abs(f)) - 0.06
    prof_.build(name + '_Cap', lambda f: 0.05, lambda f: 0.19, M02, LEGS, root_, LM, 'C11', 'observed', lift=0.010)
    prof_.build(name + '_Upper', lambda f: 0.205, vs, M02, LEGS, root_, LM, 'C11', 'observed')
    prof_.build(name + '_Lower', lambda f: vs(f) + 0.022, lambda f: 1.10, M01, LEGS, root_, LM, 'C11', 'observed')
    dl.surface_dot(name + '_BoltHole', prof_, 0.84, 0.45 * mf, 0.019, M03, DET, root_, LM, 'C11', 'observed', depth=0.01, proud=0.0015)
    p, tg, nn = sp.frame(0.8)
    for s in (-1, 1):
        role = 'P' if s * mf > 0 else 'N'      # mirror-consistent role name for symmetry matching
        dl.side_plate(name + '_Plate' + role, p + tan * s * 0.066 - nn * 0.045, tg, tan * s, (0.14, 0.09, 0.024),
                      M03, M04, LEGS, root_, LM, 'C11', 'observed')
    path = lambda t: bl.bezier(A + up * 0.03, (A + T) / 2 + rad * 0.03, T, t)
    wt = lambda t: (max(0.086 * (1 - t ** 2.0) ** 0.75, 0.006), max(0.056 * (1 - t ** 1.8) ** 0.7, 0.005))
    blade, dz = dl.faceted_wedge(name + '_Blade', path, tan, rad, wt, M03, LEGS, root_, LM, 'C11', 'observed', ground_z=0.0)
    dl.keel_strip(name + '_Keel', path, tan, rad, wt, M02, LEGS, root_, LM, 'C11', 'observed', dz=dz)
    for o in LEGS.all_objects:
        o['oow_wear'] = 1.0
    return root_


leg('S_LegRF', -54)
leg('S_LegLF', 54)

# --- views, renders, checks
st = bv.Stage('SMOKE_Scene', PRES, mode='diagnostic', prefix='S_PRES_', clay_mat=CLAY)
cams = bv.standard_cameras(PRES, root, ref=dict(az=-7, el=13, dist=5.9, aim=-0.17, lens=55, target_z=H),
                           details={'S_CORE': dict(target=C + Vector((0, -0.5, 0)), az=-24, el=9, dist=1.6, lens=70)})
st.render('REF_MATCH', os.path.join(out_dir, 'smoke_clay.png'), (320, 180), kind='clay')
import time
t0 = time.time()
st.render('DIAG_34', os.path.join(out_dir, 'smoke_material.png'), (320, 180), kind='material', samples=8)
print('CYCLES_DEVICE', st.device_info, 'render %.2fs' % (time.time() - t0))
bv.workbench_silhouette('SMOKE_Scene', 'REF_MATCH', os.path.join(out_dir, 'smoke_silhouette.png'), (320, 222))
res = bc.check('SMOKE', 'SMOKE_Scene', ground_z=0.0, counts={'legs': r'^S_Leg(RF|LF)$'}, exclude_prefix='S_PRES_')
sym = bs.measure_pairs([('S_LegRF', 'S_LegLF')], plane='X', tolerance=1e-4, scene='SMOKE_Scene')
legs_only = [o for o in bpy.data.collections['SMOKE_LEGS'].all_objects]
print(bc.summary(res))
print(bs.table(sym))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, 'smoke.blend'))
assert len(panels) >= 4, panels
assert not res['inverted_closed'] and not res['below_ground'] and not res['duplicate_objects'], res
assert not res['issues'], res['issues']     # base-mesh defects only
assert sym[0]['status'] == 'pass', sym
print('SMOKE_OK', len(panels), 'panels')
