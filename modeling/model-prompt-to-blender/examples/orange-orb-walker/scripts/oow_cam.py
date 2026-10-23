# cameras + quick render helpers (exec'd after oow_lib.py)
import bpy, math
from mathutils import Vector, Matrix

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

def camera(name, eye, target, lens=50.0, ortho=None, coll=None, up=Vector((0, 0, 1)), sensor_fit='VERTICAL'):
    sc = bpy.data.scenes['OOW_Scene']
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        (coll or sc.collection).objects.link(cam)
    cd = cam.data
    cd.sensor_fit = sensor_fit
    cd.sensor_width = 36.0
    cd.sensor_height = 24.0
    cd.clip_start = 0.05
    cd.clip_end = 200.0
    if ortho:
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho
    else:
        cd.type = 'PERSP'
        cd.lens = lens
    cam.matrix_world = look_at_matrix(eye, target, up)
    return cam

def orbit_eye(target, az_deg, el_deg, dist):
    a, e = math.radians(az_deg), math.radians(el_deg)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    return Vector(target) + d * dist
