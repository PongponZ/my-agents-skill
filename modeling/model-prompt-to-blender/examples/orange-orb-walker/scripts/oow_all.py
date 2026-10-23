# full pipeline runner (exec'd in Blender). Optional overrides via globals: REBUILD, PARAMS
SP = r"C:/Users/User/AppData/Local/Temp/claude/C--Users-User-Desktop-projects-ai-model/32cfdf74-c199-4cf5-85df-42a56ccb635f/scratchpad/"
DEFAULTS = dict(
    LIGHT_POWER=dict(key=320, fill=170, rim=240, top=40),
    REF_CAM=dict(az=-7.0, el=13.0, dist=5.9, aim=-0.17, lens=55.0),
    HERO_CAM=dict(az=-6.0, el=14.0, dist=6.5, lens=65.0),
    ORTHO_SCALE=2.6, VIEW_TRANSFORM='Khronos PBR Neutral', VIEW_LOOK='None', EXPOSURE=-0.45, EMIT_GAIN=2.6,
)
P_ = dict(DEFAULTS); P_.update(globals().get('PARAMS', {}))
G = {'__name__': 'oow', 'LEVEL': 'detailed'}
G.update(P_)
exec(open(SP + 'oow_lib.py', encoding='utf-8').read(), G)
if globals().get('REBUILD', True):
    exec(open(SP + 'oow_build.py', encoding='utf-8').read(), G)
exec(open(SP + 'oow_mat.py', encoding='utf-8').read(), G)
exec(open(SP + 'oow_cam.py', encoding='utf-8').read(), G)
exec(open(SP + 'oow_present.py', encoding='utf-8').read(), G)
render = G['render']
