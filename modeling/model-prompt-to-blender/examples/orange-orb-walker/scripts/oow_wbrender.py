# Workbench clay render of a named camera at given size (exec'd in Blender); vars: CAMNAME, OUTPATH, RES, CLAY, BG
import bpy
sc = bpy.data.scenes['OOW_Scene']
w = bpy.data.worlds.get('OOW_World') or bpy.data.worlds.new('OOW_World')
sc.world = w
sc.camera = bpy.data.objects[CAMNAME]
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'
sh.color_type = 'SINGLE' if CLAY else 'MATERIAL'
sh.single_color = (0.62, 0.60, 0.57)
sh.show_cavity = True
sh.cavity_type = 'BOTH'
sh.show_shadows = True
sh.shadow_intensity = 0.35
sh.background_type = 'WORLD' if hasattr(sh, 'background_type') else sh.background_type
w.color = BG
sc.render.film_transparent = False
sc.render.resolution_x, sc.render.resolution_y = RES
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGB'
sc.render.filepath = OUTPATH
bpy.ops.render.render(write_still=True, scene=sc.name)
print('wrote', OUTPATH)
