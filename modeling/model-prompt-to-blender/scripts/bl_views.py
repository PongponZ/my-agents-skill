"""Cameras, inspection/presentation stages and renders.

    import bl_views as bv
    st = bv.Stage('MYASSET_Scene', pres_coll, mode='diagnostic')   # or 'presentation' if in scope
    cams = bv.standard_cameras(pres_coll, asset_coll, ref=dict(az=-7, el=13, dist=5.9, aim=-0.17, lens=55, target_z=1.0))
    st.render('FRONT', r'...\\front.png', (1920, 1080), kind='material', samples=128)

Modes
- diagnostic (default for v3 packages, presentation=false): plain grey world light, plain inspection
  floor, no key/fill/rim rig, no hero framing. kind='clay' uses Workbench (viewport-equivalent
  studio light, single colour, cavity) ; kind='material' uses Cycles with the grey world.
- presentation (only when the brief/scope asks for hero renders): dark sweep + key/fill/rim/top
  area lights + dark world. kind='hero' / 'clay' (Cycles + clay override) / 'material'.

Device: Stage(device='AUTO') enables the best Cycles GPU backend at runtime (OptiX > CUDA > HIP >
oneAPI > Metal, discrete GPUs preferred over integrated ones) and falls back to CPU. The choice is
in Stage.device_info -> report it in verification.md. Preferences are NOT saved unless
enable_gpu(save_prefs=True) is called explicitly.
"""
import math
import re
import bpy
from mathutils import Vector, Matrix


# ----------------------------------------------------------------------------- GPU
GPU_BACKENDS = ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL')
INTEGRATED_GPU = re.compile(r'Radeon\(TM\) Graphics|Radeon Graphics|Vega \d+ Graphics|Intel|UHD|Iris', re.I)


def enable_gpu(prefer=GPU_BACKENDS, allow_integrated=False, include_cpu=False, save_prefs=False):
    """Enable the first backend with a usable (discrete) GPU for Cycles.
    Returns {'backend': str|None, 'devices': [names], 'skipped': [names]}."""
    info = {'backend': None, 'devices': [], 'skipped': []}
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
    except KeyError:
        return info
    for backend in prefer:
        try:
            prefs.compute_device_type = backend
        except TypeError:
            continue                                  # backend not compiled in / not supported
        if hasattr(prefs, 'refresh_devices'):
            prefs.refresh_devices()
        try:
            devs = list(prefs.get_devices_for_type(backend))
        except Exception:
            continue
        gpus = [d for d in devs if d.type == backend]
        usable = [d for d in gpus if allow_integrated or not INTEGRATED_GPU.search(d.name)]
        if not usable:
            info['skipped'] += [d.name for d in gpus]
            continue
        for d in devs:
            d.use = (d in usable) or (include_cpu and d.type == 'CPU')
        info.update(backend=backend, devices=[d.name for d in usable])
        if save_prefs:
            bpy.ops.wm.save_userpref()
        return info
    prefs.compute_device_type = 'NONE'
    return info


def configure_device(scene, device='AUTO'):
    """device: 'AUTO' (GPU if available, else CPU) | 'GPU' | 'CPU'. Returns a report dict."""
    if device in ('AUTO', 'GPU'):
        info = enable_gpu()
        if info['backend']:
            scene.cycles.device = 'GPU'
            info['device'] = 'GPU'
            return info
        if device == 'GPU':
            print('WARNING: no usable GPU backend, falling back to CPU', info)
    scene.cycles.device = 'CPU'
    return {'backend': None, 'devices': ['CPU'], 'device': 'CPU', 'skipped': []}


# ----------------------------------------------------------------------------- cameras
def look_at_matrix(eye, target, roll_up=Vector((0, 0, 1))):
    eye, target = Vector(eye), Vector(target)
    f = (target - eye).normalized()
    r = f.cross(roll_up)
    if r.length < 1e-6:
        r = f.cross(Vector((0, 1, 0)))
    r.normalize()
    u = r.cross(f).normalized()
    m = Matrix((r, u, -f)).transposed().to_4x4()
    m.translation = eye
    return m


def orbit_eye(target, az_deg, el_deg, dist):
    """az 0 = in front (-Y side), + toward +X; el above the horizon."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    return Vector(target) + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist


def camera(name, eye, target, lens=50.0, ortho=None, coll=None, up=Vector((0, 0, 1)), sensor_fit='VERTICAL'):
    """Vertical sensor fit keeps the vertical framing of a reference when the aspect changes."""
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        (coll or bpy.context.scene.collection).objects.link(cam)
    cd = cam.data
    cd.sensor_fit, cd.sensor_width, cd.sensor_height = sensor_fit, 36.0, 24.0
    cd.clip_start, cd.clip_end = 0.05, 200.0
    if ortho:
        cd.type, cd.ortho_scale = 'ORTHO', ortho
    else:
        cd.type, cd.lens = 'PERSP', lens
    cam.matrix_world = look_at_matrix(eye, target, up)
    return cam


def asset_bbox(asset_coll, exclude_prefix='PRES_'):
    mn, mx = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in asset_coll.all_objects:
        if o.type == 'MESH' and not o.name.startswith(exclude_prefix) and not o.get('oow_support') and not o.hide_render:
            for c in o.bound_box:
                p = o.matrix_world @ Vector(c)
                mn, mx = Vector(map(min, mn, p)), Vector(map(max, mx, p))
    return mn, mx


def standard_cameras(pres_coll, asset_coll, ortho_scale=None, ref=None, three_quarter=(-35, 18), details=None,
                     underside=True):
    """FRONT (looks +Y), RIGHT (from +X looking -X = Blender Right view), REAR, TOP (front at image
    bottom) as true orthographic views with ONE shared scale; optional REF_MATCH, DIAG_34, UNDERSIDE
    and detail close-ups: details = {name: dict(target=(x,y,z), az=, el=, dist=, lens=)}."""
    mn, mx = asset_bbox(asset_coll)
    ctr, ext = (mn + mx) / 2, mx - mn
    os_ = ortho_scale or max(ext.x, ext.y, ext.z) * 1.25
    cams = {
        'FRONT': camera('FRONT', (ctr.x, ctr.y - 30, ctr.z), (ctr.x, ctr.y, ctr.z), ortho=os_, coll=pres_coll),
        'RIGHT': camera('RIGHT', (ctr.x + 30, ctr.y, ctr.z), (ctr.x, ctr.y, ctr.z), ortho=os_, coll=pres_coll),
        'REAR': camera('REAR', (ctr.x, ctr.y + 30, ctr.z), (ctr.x, ctr.y, ctr.z), ortho=os_, coll=pres_coll),
        'TOP': camera('TOP', (ctr.x, ctr.y, ctr.z + 30), (ctr.x, ctr.y, ctr.z), ortho=os_, coll=pres_coll,
                      up=Vector((0, 1, 0))),
    }
    diag = max(ext.x, ext.y, ext.z)
    if three_quarter:
        cams['DIAG_34'] = camera('DIAG_34', orbit_eye(ctr, three_quarter[0], three_quarter[1], diag * 2.6), ctr,
                                 lens=50, coll=pres_coll)
    if underside:
        cams['UNDERSIDE'] = camera('UNDERSIDE', orbit_eye(ctr, 145, -38, diag * 2.2), ctr, lens=45, coll=pres_coll)
    if ref:
        t = Vector((0, 0, ref.get('target_z', ctr.z) + ref.get('aim', 0.0)))
        cams['REF_MATCH'] = camera('REF_MATCH', orbit_eye(t, ref['az'], ref['el'], ref['dist']), t,
                                   lens=ref['lens'], coll=pres_coll)
    for name, d in (details or {}).items():
        cams[name] = camera(name, orbit_eye(d['target'], d['az'], d['el'], d['dist']), d['target'],
                            lens=d.get('lens', 60), coll=pres_coll)
    for n, c in cams.items():
        c['oow_view'] = n
    cams['RIGHT']['oow_note'] = 'Ortho from +X looking -X (Blender Right view); which subject side this shows depends on the asset handedness.'
    return cams


# ----------------------------------------------------------------------------- stage
def _flat_mat(name, col, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    m.diffuse_color = (*col, 1)
    return m


class Stage:
    def __init__(self, scene_name, pres_coll, mode='diagnostic', world_grey=None, hero_world=0.03,
                 view_transform='Khronos PBR Neutral', look='None', exposure=0.0, prefix='PRES_',
                 lights=None, clay_mat=None, light_target=(0, 0, 1.0), device='AUTO'):
        self.sc = bpy.data.scenes[scene_name]
        self.device_info = configure_device(self.sc, device)
        print('Cycles device:', self.device_info)
        self.pres = pres_coll
        self.mode = mode
        # diagnostic: the grey world is the only light -> pale grey; presentation: dimmer inspect bg
        self.world_grey = world_grey if world_grey is not None else (0.55 if mode == 'diagnostic' else 0.20)
        self.hero_world = hero_world
        self.prefix = prefix
        self.clay_mat = clay_mat
        w = bpy.data.worlds.get(prefix + 'World') or bpy.data.worlds.new(prefix + 'World')
        try:
            w.use_nodes = True
        except Exception:
            pass
        self.sc.world = w
        nt = w.node_tree
        self.bg = next((n for n in nt.nodes if n.type == 'BACKGROUND'), None)
        if self.bg is None:
            self.bg = nt.nodes.new('ShaderNodeBackground')
            wo = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
            nt.links.new(self.bg.outputs[0], wo.inputs[0])
        self.floor = self._plane(prefix + 'InspectFloor', _flat_mat(prefix + 'InspectFloorMat', (0.16, 0.16, 0.16)))
        self.sweep = None
        self.lights = []
        if mode == 'presentation':
            self.sweep = self._sweep(prefix + 'Sweep', _flat_mat(prefix + 'SweepMat', (0.060, 0.062, 0.066)))
            self.lights = self._light_rig(lights or {}, Vector(light_target))
        vs = self.sc.view_settings
        try:
            vs.view_transform = view_transform
        except TypeError as e:     # message lists the valid transforms
            print('view transform fallback:', e)
            vs.view_transform = 'AgX'
        vs.look, vs.exposure, vs.gamma = look, exposure, 1.0
        self.sc.display_settings.display_device = 'sRGB'
        self.cycles(samples=128)

    # -- support surfaces / lights
    def _plane(self, name, mat, size=15.0):
        ob = bpy.data.objects.get(name)
        if ob is None:
            import bmesh
            bm = bmesh.new()
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size)
            me = bpy.data.meshes.new(name)
            bm.to_mesh(me)
            bm.free()
            me.materials.append(mat)
            ob = bpy.data.objects.new(name, me)
            self.pres.objects.link(ob)
        ob['oow_note'] = 'Inspection support surface (not part of the asset).'
        ob['oow_support'] = True
        return ob

    def _sweep(self, name, mat):
        ob = bpy.data.objects.get(name)
        if ob is None:
            import bmesh
            bm = bmesh.new()
            prof = [(y, 0.0) for y in (-9.0, -4.0, -1.0, 1.0, 2.5)]
            R = 2.0
            for i in range(1, 13):
                a = math.radians(90 * i / 12)
                prof.append((2.5 + R * math.sin(a), R - R * math.cos(a)))
            prof.append((2.5 + R, 9.0))
            rows = [[bm.verts.new((x, y, z)) for y, z in prof] for x in (-12.0, 12.0)]
            for i in range(len(prof) - 1):
                bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            me = bpy.data.meshes.new(name)
            bm.to_mesh(me)
            bm.free()
            me.shade_smooth()
            me.materials.append(mat)
            ob = bpy.data.objects.new(name, me)
            self.pres.objects.link(ob)
            if ob.data.polygons[0].normal.z < 0:
                ob.data.flip_normals()
        ob['oow_note'] = 'Presentation sweep (presentation scope only).'
        ob['oow_support'] = True
        return ob

    def _light_rig(self, cfg, tgt):
        """Key/fill/rim/top area lights (presentation scope only). cfg overrides e.g. {'Key': {'power': 280}}."""
        rig = dict(Key=dict(az=-48, el=36, dist=4.2, size=2.6, power=320, color=(1.0, 0.97, 0.93)),
                   Fill=dict(az=62, el=14, dist=4.5, size=3.2, power=170, color=(0.93, 0.96, 1.0)),
                   Rim=dict(az=150, el=38, dist=4.0, size=2.2, power=240, color=(1, 1, 1)),
                   Top=dict(az=0, el=82, dist=3.6, size=2.4, power=40, color=(1.0, 0.99, 0.97)))
        for k, v in cfg.items():
            rig.setdefault(k, {}).update(v)
        out = []
        for nm, d in rig.items():
            name = self.prefix + nm
            ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, 'AREA')
            ld.type, ld.shape, ld.size, ld.energy, ld.color = 'AREA', 'SQUARE', d['size'], d['power'], d['color']
            ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, ld)
            if ob.name not in self.pres.objects:
                self.pres.objects.link(ob)
            ob.matrix_world = look_at_matrix(orbit_eye(tgt, d['az'], d['el'], d['dist']), tgt)
            out.append(ob)
        return out

    # -- engine settings
    def cycles(self, samples=128, threshold=0.015):
        sc = self.sc
        try:
            sc.render.engine = 'CYCLES'
        except TypeError as e:
            print('engine error:', e)
        cy = sc.cycles
        cy.device = self.device_info.get('device', 'CPU')
        cy.samples = samples
        cy.use_adaptive_sampling = True
        cy.adaptive_threshold = threshold
        cy.use_denoising = True
        try:
            cy.denoiser = 'OPENIMAGEDENOISE'
        except TypeError:
            pass
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 8, 3, 3
        cy.caustics_reflective = cy.caustics_refractive = False
        r = sc.render
        r.film_transparent = False
        r.image_settings.file_format = 'PNG'
        r.image_settings.color_mode = 'RGB'
        r.image_settings.color_depth = '8'

    def setup(self, kind='material', surface=None):
        """kind: 'material' | 'clay' | 'hero'. surface: 'plane' | 'sweep' | None (auto) | 'none'."""
        vl = self.sc.view_layers[0]
        if surface is None:
            surface = 'sweep' if (kind == 'hero' and self.sweep) else 'plane'
        self.floor.hide_render = self.floor.hide_viewport = surface != 'plane'
        if self.sweep:
            self.sweep.hide_render = self.sweep.hide_viewport = surface != 'sweep'
        if kind == 'hero':
            self.bg.inputs['Color'].default_value = (self.hero_world,) * 3 + (1,)
        else:
            g = self.world_grey
            self.bg.inputs['Color'].default_value = (g, g, g, 1)
        self.bg.inputs['Strength'].default_value = 1.0
        vl.material_override = self.clay_mat if (kind == 'clay' and self.mode == 'presentation') else None

    def render(self, cam, path, res, kind='material', samples=None, surface=None):
        """Render one image. kind='clay' in diagnostic mode uses Workbench (viewport-like)."""
        sc = self.sc
        self.setup(kind, surface)
        sc.camera = bpy.data.objects[cam]
        r = sc.render
        r.resolution_x, r.resolution_y = res
        r.resolution_percentage = 100
        if kind == 'clay' and self.mode != 'presentation':
            prev = r.engine
            r.engine = 'BLENDER_WORKBENCH'
            sh = sc.display.shading
            sh.light, sh.color_type = 'STUDIO', 'SINGLE'
            sh.single_color = (0.62, 0.60, 0.57)
            sh.show_cavity, sh.cavity_type = True, 'BOTH'
            sh.show_shadows, sh.shadow_intensity = True, 0.35
            r.filepath = path
            bpy.ops.render.render(write_still=True, scene=sc.name)
            r.engine = prev
            return path
        self.cycles(samples=samples or sc.cycles.samples)
        r.filepath = path
        bpy.ops.render.render(write_still=True, scene=sc.name)
        return path


def workbench_silhouette(scene_name, cam, path, res, color_type='MATERIAL'):
    """Transparent Workbench render used for silhouette overlays against a reference image."""
    sc = bpy.data.scenes[scene_name]
    r = sc.render
    prev = (r.engine, r.film_transparent, r.image_settings.color_mode)
    r.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light, sc.display.shading.color_type = 'STUDIO', color_type
    r.film_transparent = True
    r.image_settings.file_format, r.image_settings.color_mode = 'PNG', 'RGBA'
    r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], 100
    sc.camera = bpy.data.objects[cam]
    support = [o for o in sc.objects if o.get('oow_support') and not o.hide_render]
    for o in support:                     # floors/sweeps must not enter the silhouette
        o.hide_render = True
    r.filepath = path
    try:
        bpy.ops.render.render(write_still=True, scene=sc.name)
    finally:
        for o in support:
            o.hide_render = False
        r.engine, r.film_transparent, r.image_settings.color_mode = prev
    return path
