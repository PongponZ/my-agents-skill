import sys
from PIL import Image, ImageDraw, ImageFont
sp, out = sys.argv[1], sys.argv[2]
names = [('CORE_DETAIL', 'CORE_DETAIL  C04 ring lip + cavity, C05 core'),
         ('LEG_DETAIL', 'LEG_DETAIL  C11_RF knee / armour / ankle / blade'),
         ('TOOLS_DETAIL', 'TOOLS_DETAIL  C09 (robot-right) vs C10 (robot-left)'),
         ('UNDERSIDE', 'UNDERSIDE  C12_LR_PROPOSED root + C13 closure (inferred)')]
sheet = Image.new('RGB', (1920, 1080), (20, 20, 22))
try:
    font = ImageFont.truetype('arial.ttf', 22)
except Exception:
    font = ImageFont.load_default()
for i, (n, label) in enumerate(names):
    im = Image.open(f'{sp}/det_{n}.png').convert('RGB')
    assert im.size == (960, 540), im.size
    x, y = (i % 2) * 960, (i // 2) * 540
    sheet.paste(im, (x, y))
    d = ImageDraw.Draw(sheet)
    tw = d.textlength(label, font=font)
    d.rectangle([x + 10, y + 10, x + 26 + tw, y + 44], fill=(0, 0, 0))
    d.text((x + 18, y + 14), label, fill=(255, 220, 120), font=font)
d = ImageDraw.Draw(sheet)
d.line([(960, 0), (960, 1080)], fill=(20, 20, 22), width=4)
d.line([(0, 540), (1920, 540)], fill=(20, 20, 22), width=4)
sheet.save(out)
print(sheet.size)
