"""Image utilities for comparisons and delivery checks (system Python 3.10+ with Pillow + numpy).

  python img_tools.py crop SRC OUT x0 y0 x1 y1 [--scale 2]            # zoom a reference region (px)
  python img_tools.py cropn SRC OUT x y w h [--scale 2]               # normalized bbox (detail_crops style)
  python img_tools.py overlay REF RENDER_RGBA OUT [--scale 0.6]       # 2x2: ref | render | edges on ref | 50% blend
  python img_tools.py pair OUT LEFT RIGHT [--labels A B] [--height 540]   # side-by-side feature comparison
  python img_tools.py sheet OUT --cols 2 --tile 960x540 IMG[::LABEL] ...  # contact sheet with labels
  python img_tools.py measure IMG NAME:x0,y0,x1,y1 ...                # mean RGB, p99 luma, clipped px
  python img_tools.py check IMG[@WxH] ...                             # decode, size, mode, opaque, white-clip
"""
import argparse, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np


def _font(sz=22):
    for f in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def _label(img, text, xy=(10, 10)):
    d = ImageDraw.Draw(img)
    f = _font()
    w = d.textlength(text, font=f)
    d.rectangle([xy[0], xy[1], xy[0] + w + 16, xy[1] + 34], fill=(0, 0, 0))
    d.text((xy[0] + 8, xy[1] + 4), text, fill=(255, 220, 120), font=f)


def crop(a):
    im = Image.open(a.src).convert('RGB').crop((a.x0, a.y0, a.x1, a.y1))
    im = im.resize((int(im.width * a.scale), int(im.height * a.scale)), Image.LANCZOS)
    im.save(a.out)
    print(im.size)


def cropn(a):
    im = Image.open(a.src).convert('RGB')
    W, H = im.size
    box = (int(a.x * W), int(a.y * H), int((a.x + a.w) * W), int((a.y + a.h) * H))
    im = im.crop(box)
    im = im.resize((int(im.width * a.scale), int(im.height * a.scale)), Image.LANCZOS)
    im.save(a.out)
    print(box, im.size)


def overlay(a):
    ref = Image.open(a.ref).convert('RGB')
    r = Image.open(a.render).convert('RGBA').resize(ref.size)
    alpha = r.split()[3]
    edge = alpha.point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    ov = ref.copy()
    ov.paste(Image.new('RGB', ref.size, (0, 255, 255)), (0, 0), edge)
    bg = Image.new('RGB', ref.size, (70, 72, 76))
    bg.paste(r, (0, 0), r)
    blend = Image.blend(ref, bg, 0.5)
    W, H = ref.size
    o = Image.new('RGB', (W * 2, H * 2))
    for i, im in enumerate((ref, bg, ov, blend)):
        o.paste(im, ((i % 2) * W, (i // 2) * H))
    o = o.resize((int(o.width * a.scale), int(o.height * a.scale)))
    o.save(a.out)
    print(o.size)


def pair(a):
    ims = [Image.open(p).convert('RGB') for p in (a.left, a.right)]
    ims = [im.resize((int(im.width * a.height / im.height), a.height), Image.LANCZOS) for im in ims]
    o = Image.new('RGB', (ims[0].width + ims[1].width + 8, a.height), (20, 20, 22))
    o.paste(ims[0], (0, 0))
    o.paste(ims[1], (ims[0].width + 8, 0))
    labels = a.labels or ['reference', 'model']
    _label(o, labels[0])
    _label(o, labels[1], (ims[0].width + 18, 10))
    o.save(a.out)
    print(o.size)


def sheet(a):
    tw, th = map(int, a.tile.split('x'))
    items = [(s.split('::', 1) + [''])[:2] for s in a.images]      # IMG::LABEL (Windows-path safe)
    rows = (len(items) + a.cols - 1) // a.cols
    o = Image.new('RGB', (tw * a.cols, th * rows), (20, 20, 22))
    for i, (p, lab) in enumerate(items):
        im = Image.open(p).convert('RGB')
        im.thumbnail((tw, th), Image.LANCZOS)
        x, y = (i % a.cols) * tw + (tw - im.width) // 2, (i // a.cols) * th + (th - im.height) // 2
        o.paste(im, (x, y))
        if lab:
            _label(o, lab, ((i % a.cols) * tw + 10, (i // a.cols) * th + 10))
    o.save(a.out)
    print(o.size)


def measure(a):
    im = np.asarray(Image.open(a.img).convert('RGB')).astype(int)
    luma = lambda c: 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    for spec in a.regions:
        name, box = spec.split(':')
        x0, y0, x1, y1 = map(int, box.split(','))
        r = im[y0:y1, x0:x1].reshape(-1, 3)
        l = luma(r)
        print(name, 'mean', r.mean(0).round(0).tolist(), 'p99_luma', round(float(np.percentile(l, 99))),
              'brightest', r[l.argmax()].tolist())
    print('white_clipped_px', int((im == 255).all(2).sum()), 'global_max_luma', round(float(luma(im).max())))


def check(a):
    ok = True
    for spec in a.images:
        p, exp = (spec.rsplit('@', 1) + [None])[:2] if '@' in spec else (spec, None)   # IMG@1920x1080
        try:
            im = Image.open(p)
            im.load()
        except Exception as e:
            print('FAIL decode', p, e)
            ok = False
            continue
        arr = np.asarray(im.convert('RGBA'))
        opaque = bool((arr[..., 3] == 255).all())
        clipped = int((arr[..., :3] == 255).all(2).sum())
        good = True
        if exp:
            w, h = map(int, exp.split('x'))
            good = im.size == (w, h)
        ok &= good
        print('OK ' if good else 'BAD', p, im.format, im.size, im.mode, 'opaque=%s' % opaque, 'white_clipped=%d' % clipped)
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    c = sp.add_parser('crop'); c.add_argument('src'); c.add_argument('out')
    for k in ('x0', 'y0', 'x1', 'y1'):
        c.add_argument(k, type=int)
    c.add_argument('--scale', type=float, default=2.0); c.set_defaults(fn=crop)
    c = sp.add_parser('cropn'); c.add_argument('src'); c.add_argument('out')
    for k in ('x', 'y', 'w', 'h'):
        c.add_argument(k, type=float)
    c.add_argument('--scale', type=float, default=2.0); c.set_defaults(fn=cropn)
    c = sp.add_parser('overlay'); c.add_argument('ref'); c.add_argument('render'); c.add_argument('out')
    c.add_argument('--scale', type=float, default=0.6); c.set_defaults(fn=overlay)
    c = sp.add_parser('pair'); c.add_argument('out'); c.add_argument('left'); c.add_argument('right')
    c.add_argument('--labels', nargs=2); c.add_argument('--height', type=int, default=540); c.set_defaults(fn=pair)
    c = sp.add_parser('sheet'); c.add_argument('out'); c.add_argument('--cols', type=int, default=2)
    c.add_argument('--tile', default='960x540'); c.add_argument('images', nargs='+'); c.set_defaults(fn=sheet)
    c = sp.add_parser('measure'); c.add_argument('img'); c.add_argument('regions', nargs='+'); c.set_defaults(fn=measure)
    c = sp.add_parser('check'); c.add_argument('images', nargs='+'); c.set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
