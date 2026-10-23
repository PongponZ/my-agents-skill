"""<ASSET> build script (template). Copy to the work folder, rename, fill the TODOs.

Exec inside Blender (see references/workflow.md §1):
    g = {'__name__': 'asset', 'LEVEL': 'detailed'}     # or 'blockout'
    exec(open(r'<work>/<asset>_build.py', encoding='utf-8').read(), g)

Rules: world-space geometry -> bl.mk(pivot); tag evidence; only clear OUR collections; every
required feature ID from feature_plan appears in a comment next to the code that builds it.
"""
import sys, math, importlib
SKILL_SCRIPTS = r"<skill>/model-prompt-to-blender/scripts"          # TODO path
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)
import bpy
from mathutils import Vector, Matrix
import bl_build as bl, bl_detail as dl, bl_materials as bm_
for _m in (bl, dl, bm_):
    importlib.reload(_m)

LEVEL = globals().get('LEVEL', 'detailed')
NAME = 'ASSET'                                                       # TODO collection / prefix
bl.CTX.update(scene=NAME + '_Scene', detailed=(LEVEL != 'blockout'))

# ------------------------------------------------------------------ parameters (D = 1 working unit)
P = dict(
    H=1.0,            # body centre height; follows ground contacts (never stretch limbs to reach Z=0)
    R=0.505,          # outer armour radius
    LIMB_AZ=(54.0, 126.0),   # symmetric families: front +-54, rear +-126 (decision Dxx)
)
H = P['H']
C = Vector((0, 0, H))
BODY_M = Matrix.Translation(C)

# ------------------------------------------------------------------ scene, collections, materials
sc = bl.get_scene()
root_coll = bl.get_coll(NAME, sc.collection)
CB, CL, CT, CD, CP = (bl.get_coll(n, root_coll) for n in ('BODY', 'LEGS', 'TOOLS', 'DETAILS', 'PRESENTATION'))
for c in (CB, CL, CT, CD):
    bl.clear_coll(c)
for ob in list(root_coll.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
bl.WM.clear()

M01 = bm_.painted('M01_Main', (0.64, 0.51, 0.37), 0.64, (0.09, 0.065, 0.05), (0.2, 0.14, 0.1))   # TODO palette
M02 = bm_.painted('M02_Accent', (0.86, 0.17, 0.014), 0.58, (0.12, 0.05, 0.025), (0.3, 0.08, 0.02))
M03 = bm_.plain('M03_Dark', (0.055, 0.04, 0.033), 0.68)
M04 = bm_.plain('M04_Hub', (0.36, 0.11, 0.025), 0.5)
M05 = bm_.emitter('M05_Emitter', gain=2.6)

ROOT = bl.empty(NAME + '_ROOT', root_coll, None, Matrix.Identity(4), 0.3, 'ARROWS')
ROOT['oow_note'] = 'Ground projection of body centre. D=1 scene unit. Front -Y, +Z up. Robot-right side = TODO (+X/-X).'

# ------------------------------------------------------------------ C01 body (+ shell panels when detailed)
bm = bl.bm_new()
bl.bm_sphere(bm, 0.478 if bl.CTX['detailed'] else 0.5, 96, 48, BODY_M)
BODY = bl.mk('C01_Body', bm, CB, ROOT, BODY_M, [M03], 'C01', note='TODO depth evidence')

if bl.CTX['detailed']:
    cut = bl.get_coll(NAME + '_CUTTERS', root_coll)
    cutters = [
        bl.slab_cutter('cut_belt', cut, C + Vector((0, 0, -0.03)), (1, 0, 0), (0, 0, 1), 1.4, 0.01, 1.4),
        bl.slab_cutter('cut_crown', cut, C + Vector((0, 0, 0.36)), (1, 0, 0), (0, 0, 1), 1.4, 0.01, 1.4),
        # TODO meridians / band / holes / slots from the detail inventory
    ]

    def classify(c, ibm):                      # -> (name, material, comp, evidence, raise) or None
        if c.z > 0.34:
            return ('C02_Crown', M01, 'C02', 'observed', 0.0)
        if c.z > -0.03:
            return ('C02_Upper', M01, 'C02', 'observed', 0.0)
        return ('C03_Lower', M02, 'C03', 'observed', 0.010)

    for ob in dl.panelize_sphere_shell(C, P['R'], 0.025, -0.28, cutters, classify, CB, BODY, BODY_M):
        ob['oow_wear'] = 1.0
    bl.clear_coll(cut)
    bpy.data.collections.remove(cut)


# ------------------------------------------------------------------ repeated family prototype (legs)
def build_leg(name, az, evidence='observed'):
    """Prototype once, then call for every member. Off-centre details use mf (mirror factor)."""
    a = math.radians(az)
    rad, tan, up = Vector((math.sin(a), -math.cos(a), 0)), Vector((math.cos(a), math.sin(a), 0)), Vector((0, 0, 1))
    mf = bl.mirror_factor(az)
    lp = lambda r, z: C + rad * r + up * z
    K, A, T = lp(0.56, -0.30), lp(0.86, -0.68), lp(0.97, -H)          # TODO from measurements
    LM = bl.frame_matrix(K, rad, up)
    leg = bl.empty(name, CL, BODY, LM, 0.1)
    bl.tag(leg, name[:3], evidence)
    if bl.CTX['detailed']:
        w = dl.stepped_disc(name + '_Knee', K, tan, 0.12, 0.134, M03, CL, leg, LM, name[:3], evidence)
        dl.domed_hub(name + '_Knee', K, tan, w, 0.046, M04, M03, CL, leg, LM, name[:3], evidence)
    sp = dl.Spine(K, K + rad * 0.22 + up * 0.05, A + rad * 0.04 + up * 0.26, A, tan, rad + up)
    prof = dl.ArmourProfile(sp, lambda t: (0.10, 0.108 - 0.014 * t),
                            profile='gable' if bl.CTX['detailed'] else 'round', chisel=(0.92, 0.20, 0.55, 0.25))
    prof.build(name + '_Armour', lambda f: 0.06, lambda f: 1.10, M02, CL, leg, LM, name[:3], evidence)
    path = lambda t: bl.bezier(A + up * 0.03, (A + T) / 2 + rad * 0.03, T, t)
    wt = lambda t: (max(0.086 * (1 - t ** 2) ** 0.75, 0.006), max(0.056 * (1 - t ** 1.8) ** 0.7, 0.005))
    dl.faceted_wedge(name + '_Blade', path, tan, rad, wt, M03, CL, leg, LM, name[:3], evidence, ground_z=0.0)
    # TODO: remaining required features (seams, latch, bolts, side plates, keel strip ...)
    return leg


front, rear = P['LIMB_AZ']
for nm, az, ev in (('C11_RF', -front, 'observed'), ('C11_LF', front, 'observed'),
                   ('C11_RR', -rear, 'observed'), ('C12_LR', rear, 'proposed')):    # TODO names/evidence
    build_leg(nm, az, ev)
for ob in CL.all_objects:
    ob['oow_wear'] = 1.0

sc.view_layers[0].update()
print('LEVEL', LEVEL, 'objects:', len(root_coll.all_objects))
