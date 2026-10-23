# rebuild detailed, save detailed checkpoint, render every deliverable, save final (exec'd in Blender)
import bpy, time, json
SP = r"C:/Users/User/AppData/Local/Temp/claude/C--Users-User-Desktop-projects-ai-model/32cfdf74-c199-4cf5-85df-42a56ccb635f/scratchpad/"
OUTDIR = r"C:/Users/User/Desktop/projects/playground/orange-orb-walker/model_output/"
REBUILD = True
PARAMS = {}
exec(open(SP + 'oow_all.py', encoding='utf-8').read())
sc = bpy.data.scenes['OOW_Scene']
G['setup']('hero'); sc.camera = bpy.data.objects['HERO']
bpy.ops.wm.save_as_mainfile(filepath=OUTDIR + 'orange-orb-walker_detailed.blend', copy=True)
T = {}
def R(key, *a, **k):
    t0 = time.time(); render(*a, **k); T[key] = round(time.time() - t0, 1)
R('preview', 'HERO', OUTDIR + 'orange-orb-walker_preview.png', (960, 540), 'hero', samples=96)
R('hero', 'HERO', OUTDIR + 'orange-orb-walker_hero.png', (1920, 1080), 'hero', samples=256)
R('clay', 'REF_MATCH', OUTDIR + 'orange-orb-walker_clay.png', (1920, 1080), 'clay', samples=160, surface='sweep')
for cam in ('FRONT', 'RIGHT', 'REAR', 'TOP'):
    R(cam, cam, OUTDIR + 'orange-orb-walker_%s.png' % cam.lower(), (1920, 1080), 'inspect', samples=128)
for cam, hf in (('CORE_DETAIL', False), ('LEG_DETAIL', False), ('TOOLS_DETAIL', False), ('UNDERSIDE', True)):
    R(cam, cam, SP + 'det_%s.png' % cam, (960, 540), 'inspect', samples=128, hide_floor=hf)
# restore hero state and save final
G['setup']('hero')
sc.camera = bpy.data.objects['HERO']
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.cycles.samples = 256
sc.render.filepath = '//orange-orb-walker_hero.png'
def put_text(name, path):
    t = bpy.data.texts.get(name) or bpy.data.texts.new(name)
    t.clear(); t.write(open(path, encoding='utf-8').read())
put_text('OOW_NOTES.txt', SP + 'oow_notes.txt')
for nm in ('lib', 'build', 'mat', 'cam', 'present'):
    put_text('OOW_src_%s.py' % nm, SP + 'oow_%s.py' % nm)
bpy.ops.wm.save_as_mainfile(filepath=OUTDIR + 'orange-orb-walker_final.blend')
json.dump(T, open(SP + 'final_pass_times.json', 'w'))
open(SP + 'final_pass_done.txt', 'w').write('done')
print('FINAL PASS DONE', T)
