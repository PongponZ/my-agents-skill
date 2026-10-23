"""Procedural, editable material graphs (no image files -> nothing to pack).

    import bl_materials as bm_
    ivory = bm_.painted('M01_Ivory', (0.64, 0.51, 0.37), 0.64, chip_col=(0.09, 0.065, 0.05),
                        speck_col=(0.20, 0.14, 0.10), fleck_col=(0.80, 0.20, 0.02))
    core = bm_.emitter('M05_Emitter', gain=2.6)

- Node lookups use socket identifiers/types, never localized node names.
- Wear is object-space (stable when parts are re-posed) and biased per object through an object
  custom property (default 'oow_wear', 0..1) read by an Attribute node: set it on objects that
  should carry heavier chips/specks (legs, exposed body panels).
- painted(): Bevel-node edge mask x noise -> sparse edge chips; small specks; optional flecks.
  The Bevel node only works in Cycles (EEVEE shows no chips).
- emitter(): opaque emissive look, radial yellow->orange ramp from Generated coords, emission
  strength = falloff x per-object scale (object property 'oow_emit_scale') x gain. The diffuse base
  is dimmed so scene lights do not wash the emitter to white.
"""
import bpy


def inp(node, *names):
    for n in names:
        for s in node.inputs:
            if s.identifier == n or s.name == n:
                return s
    raise KeyError((node.type, names))


def out(node, *names):
    for n in names:
        for s in node.outputs:
            if s.identifier == n or s.name == n:
                return s
    return node.outputs[0]


def reset(mat):
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return nt


def node(nt, typ, loc, **kw):
    n = nt.nodes.new(typ)
    n.location = loc
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def link(nt, a, b):
    nt.links.new(a, b)


def _is_socket(x):
    return hasattr(x, 'is_linked')


def math_node(nt, op, loc, a=None, b=None, c=None, clamp=False):
    n = node(nt, 'ShaderNodeMath', loc)
    n.operation = op
    n.use_clamp = clamp
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if _is_socket(x):
            link(nt, x, n.inputs[i])
        else:
            n.inputs[i].default_value = x
    return n


def map_range(nt, src, loc, fmin, fmax, tmin=0.0, tmax=1.0):
    n = node(nt, 'ShaderNodeMapRange', loc)
    n.clamp = True
    link(nt, src, n.inputs['Value'])
    n.inputs['From Min'].default_value = fmin
    n.inputs['From Max'].default_value = fmax
    n.inputs['To Min'].default_value = tmin
    n.inputs['To Max'].default_value = tmax
    return n


def mix_rgb(nt, loc, fac, a, b, blend='MIX'):
    n = node(nt, 'ShaderNodeMix', loc)
    n.data_type = 'RGBA'
    n.blend_type = blend
    n.clamp_factor = True
    if _is_socket(fac):
        link(nt, fac, n.inputs[0])
    else:
        n.inputs[0].default_value = fac
    ia, ib = [s for s in n.inputs if s.type == 'RGBA'][:2]
    for sock, val in ((ia, a), (ib, b)):
        if _is_socket(val):
            link(nt, val, sock)
        else:
            sock.default_value = val
    return n, [s for s in n.outputs if s.type == 'RGBA'][0]


def obj_attr(nt, loc, name):
    a = node(nt, 'ShaderNodeAttribute', loc)
    a.attribute_type = 'OBJECT'
    a.attribute_name = name
    return a


def _bsdf(nt, loc):
    b = node(nt, 'ShaderNodeBsdfPrincipled', loc)
    o = node(nt, 'ShaderNodeOutputMaterial', (loc[0] + 300, loc[1]))
    link(nt, out(b, 'BSDF'), inp(o, 'Surface'))
    inp(b, 'Metallic').default_value = 0.0
    return b


def _variation(nt, tc, base, var, loc=(-900, 300), scale=2.2):
    nb = node(nt, 'ShaderNodeTexNoise', loc)
    nb.inputs['Scale'].default_value = scale
    nb.inputs['Detail'].default_value = 2.0
    link(nt, out(tc, 'Object'), nb.inputs['Vector'])
    vr = map_range(nt, out(nb, 'Fac'), (loc[0] + 250, loc[1]), 0.3, 0.7, 1.0 - var, 1.0 + var)
    bc = node(nt, 'ShaderNodeRGB', (loc[0] + 250, loc[1] + 220))
    bc.outputs[0].default_value = (*base, 1.0)
    bc.label = 'Base colour'
    cv = node(nt, 'ShaderNodeCombineColor', (loc[0] + 250, loc[1] - 150))
    for i in range(3):
        link(nt, out(vr, 'Result'), cv.inputs[i])
    _, c = mix_rgb(nt, (loc[0] + 500, loc[1]), 1.0, out(bc, 'Color'), out(cv, 'Color'), 'MULTIPLY')
    return c


def painted(name, base, rough, chip_col, speck_col, chip_amt=0.60, speck_amt=0.725, var=0.06, spec=0.35,
            fleck_col=None, fleck_amt=0.755, wear_attr='oow_wear', chip_scale=16.0, speck_scale=55.0):
    """Opaque painted dielectric with sparse wear (edge chips, specks, optional colour flecks)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    b = _bsdf(nt, (1100, 0))
    inp(b, 'Specular IOR Level').default_value = spec
    tc = node(nt, 'ShaderNodeTexCoord', (-1200, 0))
    c1 = _variation(nt, tc, base, var)
    wear = obj_attr(nt, (-1150, -700), wear_attr)
    wear.label = 'Wear bias (%s)' % wear_attr
    # edge mask: bevel normal vs true normal (Cycles)
    bev = node(nt, 'ShaderNodeBevel', (-900, -200))
    bev.samples = 8
    bev.inputs['Radius'].default_value = 0.012
    geo = node(nt, 'ShaderNodeNewGeometry', (-900, -400))
    dot = node(nt, 'ShaderNodeVectorMath', (-700, -280))
    dot.operation = 'DOT_PRODUCT'
    link(nt, out(bev, 'Normal'), dot.inputs[0])
    link(nt, out(geo, 'Normal'), dot.inputs[1])
    edge = map_range(nt, out(dot, 'Value'), (-500, -280), 0.985, 0.90)

    def thresholded(scale, detail, amt, k, width, loc):
        nz = node(nt, 'ShaderNodeTexNoise', loc)
        nz.inputs['Scale'].default_value = scale
        nz.inputs['Detail'].default_value = detail
        link(nt, out(tc, 'Object'), nz.inputs['Vector'])
        mr = map_range(nt, out(nz, 'Fac'), (loc[0] + 200, loc[1]), amt, amt + width)
        lo = math_node(nt, 'MULTIPLY_ADD', (loc[0] - 60, loc[1] - 120), out(wear, 'Fac'), k, amt)
        hi = math_node(nt, 'MULTIPLY_ADD', (loc[0] - 60, loc[1] - 180), out(wear, 'Fac'), k, amt + width)
        link(nt, out(lo, 'Value'), mr.inputs['From Min'])
        link(nt, out(hi, 'Value'), mr.inputs['From Max'])
        return mr

    chip_n = thresholded(chip_scale, 6.0, chip_amt, -0.075, 0.03, (-700, -560))
    chips = math_node(nt, 'MULTIPLY', (-300, -400), out(edge, 'Result'), out(chip_n, 'Result'), clamp=True)
    chips.label = 'Edge chips'
    specks = thresholded(speck_scale, 2.0, speck_amt, -0.022, 0.015, (-700, -850))
    specks.label = 'Specks'
    _, c2 = mix_rgb(nt, (-100, 200), out(chips, 'Value'), c1, (*chip_col, 1.0))
    _, c3 = mix_rgb(nt, (150, 200), out(specks, 'Result'), c2, (*speck_col, 1.0))
    if fleck_col is not None:
        fl = thresholded(34.0, 3.0, fleck_amt, -0.02, 0.012, (-700, -1100))
        fl.label = 'Paint flecks'
        _, c3 = mix_rgb(nt, (350, 200), out(fl, 'Result'), c3, (*fleck_col, 1.0))
    link(nt, c3, inp(b, 'Base Color'))
    rr = math_node(nt, 'MULTIPLY_ADD', (600, -300), out(chips, 'Value'), 0.15, rough)
    link(nt, out(rr, 'Value'), inp(b, 'Roughness'))
    mat.diffuse_color = (*base, 1.0)
    mat['oow_role'] = 'painted dielectric; procedural sparse wear biased by object property %s' % wear_attr
    return mat


def plain(name, base, rough, var=0.04, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    b = _bsdf(nt, (600, 0))
    tc = node(nt, 'ShaderNodeTexCoord', (-700, 0))
    link(nt, _variation(nt, tc, base, var, (-450, 100), 3.0), inp(b, 'Base Color'))
    inp(b, 'Roughness').default_value = rough
    inp(b, 'Metallic').default_value = metallic
    mat.diffuse_color = (*base, 1.0)
    return mat


def emitter(name, stops=((0.0, (1.0, 0.78, 0.05)), (0.5, (1.0, 0.42, 0.01)), (1.0, (1.0, 0.16, 0.0))),
            gain=2.6, scale_attr='oow_emit_scale', rim_falloff=0.45, base_dim=0.12):
    """Radial emitter for discs/domes/slots. Set obj[scale_attr] (e.g. 1.0 main, 0.3 secondary)."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    b = _bsdf(nt, (800, 0))
    inp(b, 'Roughness').default_value = 0.35
    tc = node(nt, 'ShaderNodeTexCoord', (-900, 0))
    sep = node(nt, 'ShaderNodeSeparateXYZ', (-700, 0))
    link(nt, out(tc, 'Generated'), sep.inputs[0])
    cx = math_node(nt, 'SUBTRACT', (-500, 100), out(sep, 'X'), 0.5)
    cy = math_node(nt, 'SUBTRACT', (-500, -60), out(sep, 'Y'), 0.5)
    vv = node(nt, 'ShaderNodeCombineXYZ', (-320, 0))
    link(nt, out(cx, 'Value'), vv.inputs[0])
    link(nt, out(cy, 'Value'), vv.inputs[1])
    ln = node(nt, 'ShaderNodeVectorMath', (-150, 0))
    ln.operation = 'LENGTH'
    link(nt, out(vv, 'Vector'), ln.inputs[0])
    r = math_node(nt, 'MULTIPLY', (20, 0), out(ln, 'Value'), 2.0, clamp=True)
    ramp = node(nt, 'ShaderNodeValToRGB', (200, 150))
    cr = ramp.color_ramp
    cr.interpolation = 'EASE'
    cr.elements[0].position, cr.elements[0].color = stops[0][0], (*stops[0][1], 1)
    cr.elements[1].position, cr.elements[1].color = stops[-1][0], (*stops[-1][1], 1)
    for pos, col in stops[1:-1]:
        e = cr.elements.new(pos)
        e.color = (*col, 1)
    link(nt, out(r, 'Value'), ramp.inputs['Fac'])
    _, dimc = mix_rgb(nt, (520, 300), 1.0, out(ramp, 'Color'), (base_dim, base_dim, base_dim, 1.0), 'MULTIPLY')
    link(nt, dimc, inp(b, 'Base Color'))
    link(nt, out(ramp, 'Color'), inp(b, 'Emission Color'))
    fall = map_range(nt, out(r, 'Value'), (200, -150), 0.0, 1.0, 1.0, rim_falloff)
    sc = obj_attr(nt, (200, -350), scale_attr)
    st = math_node(nt, 'MULTIPLY', (420, -200), out(fall, 'Result'), out(sc, 'Fac'))
    g = node(nt, 'ShaderNodeValue', (420, -400))
    g.label = 'Emission gain'
    g.outputs[0].default_value = gain
    st2 = math_node(nt, 'MULTIPLY', (600, -250), out(st, 'Value'), out(g, 'Value'))
    link(nt, out(st2, 'Value'), inp(b, 'Emission Strength'))
    mat.diffuse_color = (*stops[0][1], 1.0)
    mat['oow_role'] = 'opaque emissive look; no transmission; radial ramp; per-object scale %s' % scale_attr
    return mat


def set_emission_gain(mat, gain):
    next(n for n in mat.node_tree.nodes if n.type == 'VALUE').outputs[0].default_value = gain


def clay(name='CLAY_Override', grey=0.26, rough=0.6):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    b = _bsdf(nt, (0, 0))
    inp(b, 'Base Color').default_value = (grey, grey, grey, 1)
    inp(b, 'Roughness').default_value = rough
    mat.diffuse_color = (0.6, 0.6, 0.6, 1)
    return mat
