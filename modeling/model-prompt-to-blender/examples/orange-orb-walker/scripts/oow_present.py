# Presentation: world, support surfaces, lights, cameras, render settings, setups. Exec'd after oow_lib + oow_cam.
import bpy, math
from mathutils import Vector, Matrix

sc = bpy.data.scenes['OOW_Scene']
root = bpy.data.collections['ORANGE_ORB_WALKER']
PRES = bpy.data.collections['PRESENTATION']
H = bpy.data.objects['C01_Chassis'].matrix_world.translation.z
BC = Vector((0, 0, H))

def obj_in(name, data):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, data)
        PRES.objects.link(ob)
    return ob

# ---------------------------------------------------------------- world
w = bpy.data.worlds.get('OOW_World') or bpy.data.worlds.new('OOW_World')
sc.world = w
try:
    w.use_nodes = True
except Exception:
    pass
nt = w.node_tree
bgn = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
if bgn is None:
    bgn = nt.nodes.new('ShaderNodeBackground')
    wo = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    nt.links.new(bgn.outputs[0], wo.inputs[0])

# ---------------------------------------------------------------- materials for support surfaces
def flat_mat(name, col, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    for s in b.inputs:
        if s.identifier in ('Specular IOR Level',):
            s.default_value = 0.25
    m.diffuse_color = (*col, 1)
    return m

MF = flat_mat('OOW_FloorMatte', (0.060, 0.062, 0.066))
MI = flat_mat('OOW_InspectFloor', (0.16, 0.16, 0.16))

# ---------------------------------------------------------------- sweep (hero) and plain plane (inspection)
import bmesh
if bpy.data.objects.get('PRES_Sweep') is None:
    bm = bmesh.new()
    prof = []
    for y in (-9.0, -4.0, -1.0, 1.0, 2.5):
        prof.append((y, 0.0))
    R = 2.0
    for i in range(1, 13):
        a = math.radians(90 * i / 12)
        prof.append((2.5 + R * math.sin(a), R - R * math.cos(a)))
    prof.append((2.5 + R, 9.0))
    rows = []
    for x in (-12.0, 12.0):
        rows.append([bm.verts.new((x, y, z)) for y, z in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('PRES_Sweep'); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    for p in me.polygons:   # make normals face up/forward
        pass
    sw = obj_in('PRES_Sweep', me)
    me.materials.append(MF)
sw = bpy.data.objects['PRES_Sweep']
if sw.data.polygons[0].normal.z < 0:
    sw.data.flip_normals()
if bpy.data.objects.get('PRES_InspectFloor') is None:
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=15.0)
    me = bpy.data.meshes.new('PRES_InspectFloor'); bm.to_mesh(me); bm.free()
    fl = obj_in('PRES_InspectFloor', me); me.materials.append(MI)
fl = bpy.data.objects['PRES_InspectFloor']
for o in (sw, fl):
    o['oow_note'] = 'Presentation support surface (not part of the asset).'

# ---------------------------------------------------------------- lights
def area(name, az, el, dist, size, power, color=(1, 1, 1), size_y=None, target=BC):
    ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'AREA')
    ld.type = 'AREA'
    ld.shape = 'RECTANGLE' if size_y else 'SQUARE'
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.energy = power
    ld.color = color
    ob = obj_in(name, ld)
    eye = orbit_eye(target, az, el, dist)
    ob.matrix_world = look_at_matrix(eye, target)
    return ob

LIGHTS = dict(
    PRES_Key=dict(az=-48, el=36, dist=4.2, size=2.6, power=LIGHT_POWER['key'], color=(1.0, 0.97, 0.93)),
    PRES_Fill=dict(az=62, el=14, dist=4.5, size=3.2, power=LIGHT_POWER['fill'], color=(0.93, 0.96, 1.0)),
    PRES_Rim=dict(az=150, el=38, dist=4.0, size=2.2, power=LIGHT_POWER['rim'], color=(1.0, 1.0, 1.0)),
    PRES_Top=dict(az=0, el=82, dist=3.6, size=2.4, power=LIGHT_POWER['top'], color=(1.0, 0.99, 0.97)),
)
for nm, d in LIGHTS.items():
    area(nm, d['az'], d['el'], d['dist'], d['size'], d['power'], d['color'])

# ---------------------------------------------------------------- cameras
CAMS = {}
bbmin = Vector((1e9,) * 3); bbmax = Vector((-1e9,) * 3)
for o in root.all_objects:
    if o.type == 'MESH' and o.name not in ('PRES_Sweep', 'PRES_InspectFloor') and not o.hide_render:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            bbmin = Vector(map(min, bbmin, p)); bbmax = Vector(map(max, bbmax, p))
ctr = (bbmin + bbmax) / 2
print('asset bbox', tuple(round(v, 3) for v in bbmin), tuple(round(v, 3) for v in bbmax))
tgt = Vector((0, 0, H + REF_CAM['aim']))
CAMS['REF_MATCH'] = camera('REF_MATCH', orbit_eye(tgt, REF_CAM['az'], REF_CAM['el'], REF_CAM['dist']), tgt, lens=REF_CAM['lens'], coll=PRES)
ht = Vector((ctr.x * 0.5, 0.0, ctr.z - 0.02))
CAMS['HERO'] = camera('HERO', orbit_eye(ht, HERO_CAM['az'], HERO_CAM['el'], HERO_CAM['dist']), ht, lens=HERO_CAM['lens'], coll=PRES)
OS = ORTHO_SCALE
CAMS['FRONT'] = camera('FRONT', (ctr.x, -12, ctr.z), (ctr.x, 0, ctr.z), ortho=OS, coll=PRES)
CAMS['RIGHT'] = camera('RIGHT', (12, ctr.y, ctr.z), (0, ctr.y, ctr.z), ortho=OS, coll=PRES)
CAMS['REAR'] = camera('REAR', (ctr.x, 12, ctr.z), (ctr.x, 0, ctr.z), ortho=OS, coll=PRES)
CAMS['TOP'] = camera('TOP', (ctr.x, ctr.y, 12), (ctr.x, ctr.y, 0), ortho=OS, coll=PRES, up=Vector((0, 1, 0)))
ut = BC + Vector((0.05, 0.1, -0.35))
CAMS['UNDERSIDE'] = camera('UNDERSIDE', ut + Vector((1.25, 1.75, -1.25)) * 1.45, ut, lens=45, coll=PRES)
ct = BC + Vector((0, -0.5, -0.06))
CAMS['CORE_DETAIL'] = camera('CORE_DETAIL', orbit_eye(ct, -24, 9, 1.55), ct, lens=70, coll=PRES)
rf = bpy.data.objects['C11_RF_Knee'].matrix_world.translation
an = bpy.data.objects['C11_RF_Ankle'].matrix_world.translation
lt = (rf + an) / 2 + Vector((-0.03, 0, -0.17))
CAMS['LEG_DETAIL'] = camera('LEG_DETAIL', orbit_eye(lt, -34, 12, 2.45), lt, lens=60, coll=PRES)
tt = BC + Vector((0.0, -0.1, 0.12))
CAMS['TOOLS_DETAIL'] = camera('TOOLS_DETAIL', orbit_eye(tt, -4, 20, 3.9), tt, lens=55, coll=PRES)
for n, c in CAMS.items():
    c['oow_view'] = n
CAMS['FRONT']['oow_note'] = 'True orthographic, looks along +Y.'
CAMS['RIGHT']['oow_note'] = 'True orthographic from +X looking along -X (Blender Right view). Under the R01-consistent handedness this shows the robot-left side (C10, C11_LF, C12).'
CAMS['REAR']['oow_note'] = 'True orthographic from +Y looking along -Y; inferred C13 surfaces.'
CAMS['TOP']['oow_note'] = 'True orthographic from +Z looking along -Z; front (-Y) at image bottom.'

# ---------------------------------------------------------------- render settings
r = sc.render
try:
    r.engine = 'CYCLES'
except TypeError as e:
    print('engine error', e)
cy = sc.cycles
# GPU first (OptiX > CUDA > HIP > oneAPI > Metal, discrete GPUs only), CPU fallback
cy.device = 'CPU'
try:
    _pr = bpy.context.preferences.addons['cycles'].preferences
    for _b in ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL'):
        try:
            _pr.compute_device_type = _b
        except TypeError:
            continue
        _all = list(_pr.get_devices_for_type(_b))
        _ds = [d for d in _all if d.type == _b and not any(k in d.name for k in ('Radeon(TM) Graphics', 'Intel', 'UHD', 'Iris'))]
        if _ds:
            for d in _all:
                d.use = d in _ds
            cy.device = 'GPU'
            print('Cycles GPU:', _b, [d.name for d in _ds])
            break
except Exception as _e:
    print('GPU setup failed, using CPU:', _e)
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.015
cy.samples = 256
cy.use_denoising = True
try:
    cy.denoiser = 'OPENIMAGEDENOISE'
except TypeError:
    pass
cy.max_bounces = 8
cy.diffuse_bounces = 3
cy.glossy_bounces = 3
cy.transmission_bounces = 2
cy.caustics_reflective = False
cy.caustics_refractive = False
r.film_transparent = False
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGB'
r.image_settings.color_depth = '8'
sc.view_settings.view_transform = VIEW_TRANSFORM
sc.view_settings.look = VIEW_LOOK
sc.view_settings.exposure = EXPOSURE
sc.view_settings.gamma = 1.0
sc.display_settings.display_device = 'sRGB'

def setup(kind, surface=None):
    """kind: 'hero' | 'clay' | 'inspect' (materials, pale bg). surface: 'sweep' | 'plane' | None (auto)."""
    vl = sc.view_layers[0]
    if surface is None:
        surface = 'sweep' if kind == 'hero' else 'plane'
    sw.hide_render = surface != 'sweep'
    fl.hide_render = surface != 'plane'
    if kind == 'hero':
        bgn.inputs['Color'].default_value = (0.030, 0.032, 0.036, 1)
        vl.material_override = None
    else:
        bgn.inputs['Color'].default_value = (0.20, 0.20, 0.21, 1)
        vl.material_override = bpy.data.materials['OOW_Clay'] if kind == 'clay' else None
    bgn.inputs['Strength'].default_value = 1.0
    sw.hide_viewport = sw.hide_render; fl.hide_viewport = fl.hide_render

def render(cam, path, res, kind, samples=None, hide_floor=False, surface=None):
    setup(kind, surface)
    if hide_floor:
        fl.hide_render = True; sw.hide_render = True
    sc.camera = bpy.data.objects[cam]
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    if samples:
        cy.samples = samples
    r.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    return path
print('presentation ok')
