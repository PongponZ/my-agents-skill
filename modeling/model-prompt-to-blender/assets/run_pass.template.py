"""Final pass runner (template): rebuild -> detailed checkpoint -> diagnostic renders -> final save.

Launch through execute_blender_code. It will outlive the ~120 s MCP timeout; wait for DONE in a
background shell:  until [ -f "<work>/done.txt" ]; do sleep 5; done
"""
import sys, os, json, time, importlib
SKILL_SCRIPTS = r"<skill>/model-prompt-to-blender/scripts"          # TODO
WORK = r"<work>"                                                     # TODO scratch/work folder
OUT = r"<output_dir>"                                                # TODO model_output
NAME, ASSET = 'ASSET', 'asset-slug'                                  # TODO
sys.path.insert(0, SKILL_SCRIPTS)
import bpy
import bl_build as bl, bl_views as bv, bl_materials as bm_
for _m in (bl, bv, bm_):
    importlib.reload(_m)
DONE = os.path.join(WORK, 'done.txt')
if os.path.exists(DONE):
    os.remove(DONE)

g = {'__name__': 'asset', 'LEVEL': 'detailed'}
exec(open(os.path.join(WORK, ASSET + '_build.py'), encoding='utf-8').read(), g)
sc = bpy.data.scenes[NAME + '_Scene']
root = bpy.data.collections[NAME]
pres = bpy.data.collections['PRESENTATION']
st = bv.Stage(sc.name, pres, mode='diagnostic', device='AUTO')       # GPU if available; 'presentation' only if in scope
cams = bv.standard_cameras(pres, root, ref=None,                      # TODO REF_MATCH dict from blockout
                           details={})                               # TODO feature close-up cameras
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, ASSET + '_detailed.blend'), copy=True)

T = {}
def R(key, *a, **k):
    t0 = time.time(); st.render(*a, **k); T[key] = round(time.time() - t0, 1)

R('clay', 'DIAG_34', os.path.join(OUT, ASSET + '_clay.png'), (1920, 1080), kind='clay')
for cam in ('FRONT', 'RIGHT', 'REAR', 'TOP'):
    R(cam, cam, os.path.join(OUT, '%s_%s.png' % (ASSET, cam.lower())), (1920, 1080), kind='material', samples=128)
R('underside', 'UNDERSIDE', os.path.join(WORK, 'det_UNDERSIDE.png'), (960, 540), kind='material', samples=96, surface='none')
# TODO: one render per feature close-up camera -> WORK/det_<CAM>.png (pair with crops later)

sc.camera = bpy.data.objects['DIAG_34']
for t_name, path in (('NOTES.txt', os.path.join(WORK, 'notes.txt')),
                     ('src_build.py', os.path.join(WORK, ASSET + '_build.py'))):
    if os.path.exists(path):
        t = bpy.data.texts.get(t_name) or bpy.data.texts.new(t_name)
        t.clear(); t.write(open(path, encoding='utf-8').read())
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, ASSET + '_final.blend'))
T['device'] = st.device_info                                          # report backend/devices
json.dump(T, open(os.path.join(WORK, 'render_times.json'), 'w'))
open(DONE, 'w').write('done')
print('FINAL PASS DONE', T)
