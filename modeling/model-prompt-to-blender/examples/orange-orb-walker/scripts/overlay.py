import sys
from PIL import Image, ImageChops, ImageFilter, ImageDraw
ref_p, rend_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
ref = Image.open(ref_p).convert('RGB')
r = Image.open(rend_p).convert('RGBA').resize(ref.size)
alpha = r.split()[3]
# side by side + overlay with model silhouette edge drawn on the reference
edge = alpha.point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
ov = ref.copy()
cyan = Image.new('RGB', ref.size, (0, 255, 255))
ov.paste(cyan, (0, 0), edge)
bg = Image.new('RGB', ref.size, (70, 72, 76))
bg.paste(r, (0, 0), r)
blend = Image.blend(ref, bg, 0.5)
W, Hh = ref.size
out = Image.new('RGB', (W * 2, Hh * 2), (0, 0, 0))
out.paste(ref, (0, 0)); out.paste(bg, (W, 0)); out.paste(ov, (0, Hh)); out.paste(blend, (W, Hh))
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
out = out.resize((int(out.width * scale), int(out.height * scale)))
out.save(out_p)
print(out.size)
