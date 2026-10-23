"""Test the Blender-only (no Pillow / no shell) helpers on the smoke-test outputs.

  "<blender.exe>" -b --factory-startup --python no_shell_test.py -- <smoke_out_dir>
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bl_images as bi, bl_check as bc

d = sys.argv[sys.argv.index('--') + 1]
clay, mat, sil = (os.path.join(d, n) for n in ('smoke_clay.png', 'smoke_material.png', 'smoke_silhouette.png'))
res = bi.check([clay, mat], expect=(320, 180))
print('CHECK', res)
assert all(r['ok'] and r['opaque'] for r in res), res
print('MEASURE', json.dumps(bi.measure(mat, {'centre': (140, 60, 180, 100)})))
outs = [bi.sheet([(clay, ''), (mat, ''), (sil, '')], os.path.join(d, 'ns_sheet.png'), cols=3, tile=(320, 180)),
        bi.pair(clay, mat, os.path.join(d, 'ns_pair.png'), height=180),
        bi.overlay(clay, sil, os.path.join(d, 'ns_overlay.png'), scale=1.0),
        bi.crop(mat, os.path.join(d, 'ns_crop.png'), 100, 40, 220, 140, scale=2)]
print('SIZES', [r['size'] for r in bi.check(outs)])
info = bc.inspect_saved_blend(os.path.join(d, 'smoke.blend'))
print('SAVED', {k: (v if not isinstance(v, list) else len(v)) for k, v in info.items()})
assert info['exists'] and 'SMOKE_Scene' in info['scenes'], info
print('NO_SHELL_OK')
