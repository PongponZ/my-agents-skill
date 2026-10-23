"""Image checks and comparison sheets INSIDE Blender (numpy + bpy only, no Pillow).

Use this when the agent has no local shell/Python with Pillow (e.g. Claude desktop/web chat with a
Blender MCP connection): every call runs through execute_blender_code.

    import bl_images as bi
    print(bi.check([r'...\\hero.png'], expect=(1920, 1080)))
    print(bi.measure(r'...\\hero.png', {'core': (900, 465, 1010, 575)}))
    bi.sheet([(p1, ''), (p2, '')], r'...\\details.png', cols=2, tile=(960, 540))
    bi.pair(crop_png, render_png, r'...\\pair.png', height=540)
    bi.overlay(ref_png, silhouette_rgba_png, r'...\\overlay.png')
    bi.crop(src, out, x0, y0, x1, y1, scale=2)

Coordinates are pixels with a top-left origin (like Pillow). No text labels are drawn: put the
captions in verification.md, or use img_tools.py where Pillow is available.
"""
import os
import bpy
import numpy as np


def load(path):
    """-> float32 array (H, W, 4) in 0..1, top-down rows."""
    img = bpy.data.images.load(path, check_existing=False)
    try:
        w, h = img.size
        a = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        return a.reshape(h, w, 4)[::-1].copy()
    finally:
        bpy.data.images.remove(img)


def save(arr, path):
    """float array (H, W, 3|4) 0..1 top-down -> PNG (8-bit RGB)."""
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1), np.float32)], 2)
    img = bpy.data.images.new('tmp_bl_images', w, h, alpha=False)
    try:
        img.pixels.foreach_set(np.ascontiguousarray(arr[::-1], dtype=np.float32).ravel())
        img.filepath_raw = path
        img.file_format = 'PNG'
        img.save()
    finally:
        bpy.data.images.remove(img)
    return path


def _resize(arr, w, h):
    """Nearest-neighbour resize (enough for review sheets)."""
    H, W = arr.shape[:2]
    ys = (np.arange(h) * H / h).astype(int)
    xs = (np.arange(w) * W / w).astype(int)
    return arr[ys][:, xs]


def _luma(rgb255):
    return 0.2126 * rgb255[..., 0] + 0.7152 * rgb255[..., 1] + 0.0722 * rgb255[..., 2]


def check(paths, expect=None):
    """Decode, size, opaque and fully white-clipped pixel count for each PNG."""
    out = []
    for p in paths:
        try:
            a = load(p)
        except Exception as e:
            out.append(dict(path=p, ok=False, error=str(e)))
            continue
        h, w = a.shape[:2]
        rgb = np.round(a[..., :3] * 255)
        out.append(dict(path=p, size=(w, h), ok=(expect is None or (w, h) == tuple(expect)),
                        opaque=bool((a[..., 3] >= 0.999).all()),
                        white_clipped=int((rgb >= 255).all(2).sum())))
    return out


def measure(path, regions):
    """regions: {name: (x0, y0, x1, y1)} -> mean RGB (0-255), p99 luma, brightest pixel."""
    a = np.round(load(path)[..., :3] * 255)
    res = {}
    for name, (x0, y0, x1, y1) in regions.items():
        r = a[y0:y1, x0:x1].reshape(-1, 3)
        l = _luma(r)
        res[name] = dict(mean=r.mean(0).round(0).tolist(), p99_luma=float(np.percentile(l, 99)),
                         brightest=r[int(l.argmax())].tolist())
    res['_image'] = dict(white_clipped=int((a >= 255).all(2).sum()), max_luma=float(_luma(a).max()))
    return res


def crop(src, out, x0, y0, x1, y1, scale=2.0):
    a = load(src)[y0:y1, x0:x1]
    return save(_resize(a, int(a.shape[1] * scale), int(a.shape[0] * scale)), out)


def sheet(items, out, cols=2, tile=(960, 540), bg=(0.08, 0.08, 0.09)):
    """items: [(path, caption_unused)] -> grid PNG; each image fitted into its tile."""
    tw, th = tile
    rows = (len(items) + cols - 1) // cols
    canvas = np.empty((th * rows, tw * cols, 4), np.float32)
    canvas[...] = (*bg, 1.0)
    for i, it in enumerate(items):
        p = it[0] if isinstance(it, (tuple, list)) else it
        a = load(p)
        s = min(tw / a.shape[1], th / a.shape[0])
        w, h = max(1, int(a.shape[1] * s)), max(1, int(a.shape[0] * s))
        a = _resize(a, w, h)
        x = (i % cols) * tw + (tw - w) // 2
        y = (i // cols) * th + (th - h) // 2
        canvas[y:y + h, x:x + w] = a
    return save(canvas, out)


def pair(left, right, out, height=540, gap=8):
    ims = []
    for p in (left, right):
        a = load(p)
        ims.append(_resize(a, max(1, int(a.shape[1] * height / a.shape[0])), height))
    canvas = np.zeros((height, ims[0].shape[1] + ims[1].shape[1] + gap, 4), np.float32)
    canvas[..., 3] = 1.0
    canvas[:, :ims[0].shape[1]] = ims[0]
    canvas[:, ims[0].shape[1] + gap:] = ims[1]
    return save(canvas, out)


def overlay(ref, render_rgba, out, scale=0.6):
    """2x2: reference | render on grey | silhouette edges (cyan) on reference | 50% blend."""
    R = load(ref)
    h, w = R.shape[:2]
    S = _resize(load(render_rgba), w, h)
    m = S[..., 3] > 0.5
    er = m.copy()
    er[1:] &= m[:-1]; er[:-1] &= m[1:]; er[:, 1:] &= m[:, :-1]; er[:, :-1] &= m[:, 1:]
    edge = m & ~er
    for _ in range(1):                                     # thicken edges by 1 px
        e2 = edge.copy()
        e2[1:] |= edge[:-1]; e2[:-1] |= edge[1:]; e2[:, 1:] |= edge[:, :-1]; e2[:, :-1] |= edge[:, 1:]
        edge = e2
    grey = np.zeros_like(R); grey[...] = (0.275, 0.282, 0.298, 1.0)
    rend = grey * (1 - S[..., 3:4]) + np.concatenate([S[..., :3], np.ones((h, w, 1), np.float32)], 2) * S[..., 3:4]
    ov = R.copy(); ov[edge] = (0.0, 1.0, 1.0, 1.0)
    blend = (R + rend) / 2
    top = np.concatenate([R, rend], 1)
    bot = np.concatenate([ov, blend], 1)
    full = np.concatenate([top, bot], 0)
    full = _resize(full, int(full.shape[1] * scale), int(full.shape[0] * scale))
    return save(full, out)
