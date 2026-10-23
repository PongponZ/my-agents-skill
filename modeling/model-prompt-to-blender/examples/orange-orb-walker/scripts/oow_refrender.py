# rebuild + REF_MATCH camera + quick workbench render for overlay (exec'd in Blender)
import bpy
from mathutils import Vector
SP = r"C:/Users/User/AppData/Local/Temp/claude/C--Users-User-Desktop-projects-ai-model/32cfdf74-c199-4cf5-85df-42a56ccb635f/scratchpad/"
g = {'__name__': 'oow', 'LEVEL': LEVEL}
exec(open(SP + 'oow_lib.py', encoding='utf-8').read(), g)
if REBUILD:
    exec(open(SP + 'oow_build.py', encoding='utf-8').read(), g)
exec(open(SP + 'oow_cam.py', encoding='utf-8').read(), g)
sc = bpy.data.scenes['OOW_Scene']
pres = bpy.data.collections['PRESENTATION']
H = bpy.data.objects['C01_Chassis'].matrix_world.translation.z
tgt = Vector((0, 0, H + CAM['aim']))
eye = g['orbit_eye'](tgt, CAM['az'], CAM['el'], CAM['dist'])
cam = g['camera']('REF_MATCH', eye, tgt, lens=CAM['lens'], coll=pres)
cam['oow_note'] = 'Reference-match camera fitted visually to R01 (1131x784, vertical sensor fit).'
sc.camera = cam
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1131, 784, 100
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
sc.render.filepath = SP + OUT
bpy.ops.render.render(write_still=True, scene=sc.name)
print('rendered', OUT, 'H', H)
