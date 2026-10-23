# M01-M05 shader graphs (procedural, editable; no external images). Exec'd in Blender.
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

def L(nt, a, b):
    nt.links.new(a, b)

def math_node(nt, op, loc, a=None, b=None, clamp=False, c=None):
    n = node(nt, 'ShaderNodeMath', loc)
    n.operation = op
    n.use_clamp = clamp
    if a is not None and not hasattr(a, 'is_linked'):
        n.inputs[0].default_value = a
    elif a is not None:
        L(nt, a, n.inputs[0])
    if b is not None and not hasattr(b, 'is_linked'):
        n.inputs[1].default_value = b
    elif b is not None:
        L(nt, b, n.inputs[1])
    if c is not None:
        n.inputs[2].default_value = c
    return n

def map_range(nt, src, loc, fmin, fmax, tmin=0.0, tmax=1.0):
    n = node(nt, 'ShaderNodeMapRange', loc)
    n.clamp = True
    L(nt, src, n.inputs['Value'])
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
    fa = n.inputs[0]
    if hasattr(fac, 'is_linked'):
        L(nt, fac, fa)
    else:
        fa.default_value = fac
    ia = [s for s in n.inputs if s.type == 'RGBA'][0]
    ib = [s for s in n.inputs if s.type == 'RGBA'][1]
    if hasattr(a, 'is_linked'): L(nt, a, ia)
    else: ia.default_value = a
    if hasattr(b, 'is_linked'): L(nt, b, ib)
    else: ib.default_value = b
    oc = [s for s in n.outputs if s.type == 'RGBA'][0]
    return n, oc

def painted(name, base, rough, chip_col, speck_col, chip_amt=0.62, speck_amt=0.735, var=0.06, edge_light=0.0, spec=0.5,
            fleck_col=None, fleck_amt=0.79):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    o = node(nt, 'ShaderNodeOutputMaterial', (1400, 0))
    bsdf = node(nt, 'ShaderNodeBsdfPrincipled', (1100, 0))
    L(nt, out(bsdf, 'BSDF'), inp(o, 'Surface'))
    inp(bsdf, 'Metallic').default_value = 0.0
    inp(bsdf, 'Roughness').default_value = rough
    try:
        inp(bsdf, 'Coat Weight').default_value = 0.0
    except KeyError:
        pass
    inp(bsdf, 'Specular IOR Level').default_value = spec
    tc = node(nt, 'ShaderNodeTexCoord', (-1200, 0))
    # broad, low-frequency value variation (painted look, no high-frequency noise)
    nb = node(nt, 'ShaderNodeTexNoise', (-900, 300))
    nb.inputs['Scale'].default_value = 2.2
    nb.inputs['Detail'].default_value = 2.0
    L(nt, out(tc, 'Object'), nb.inputs['Vector'])
    vr = map_range(nt, out(nb, 'Fac'), (-650, 300), 0.3, 0.7, 1.0 - var, 1.0 + var)
    bc = node(nt, 'ShaderNodeRGB', (-650, 520))
    bc.outputs[0].default_value = (*base, 1.0)
    bc.label = 'Base colour'
    m1, c1 = mix_rgb(nt, (-400, 400), 1.0, out(bc, 'Color'), (1, 1, 1, 1), 'MULTIPLY')
    # feed variation as grey multiplier
    cv = node(nt, 'ShaderNodeCombineColor', (-650, 150))
    for i in range(3):
        L(nt, out(vr, 'Result'), cv.inputs[i])
    L(nt, out(cv, 'Color'), [s for s in m1.inputs if s.type == 'RGBA'][1])
    # edge mask from bevel normal vs true normal (Cycles)
    bev = node(nt, 'ShaderNodeBevel', (-900, -200))
    bev.samples = 8
    bev.inputs['Radius'].default_value = 0.012
    geo = node(nt, 'ShaderNodeNewGeometry', (-900, -400))
    dot = node(nt, 'ShaderNodeVectorMath', (-700, -280))
    dot.operation = 'DOT_PRODUCT'
    L(nt, out(bev, 'Normal'), dot.inputs[0])
    L(nt, out(geo, 'Normal'), dot.inputs[1])
    edge = map_range(nt, out(dot, 'Value'), (-500, -280), 0.985, 0.90)
    # sparse chip pattern restricted to edges
    nc = node(nt, 'ShaderNodeTexNoise', (-700, -560))
    nc.inputs['Scale'].default_value = 16.0
    nc.inputs['Detail'].default_value = 6.0
    nc.inputs['Roughness'].default_value = 0.6
    L(nt, out(tc, 'Object'), nc.inputs['Vector'])
    chip_n = map_range(nt, out(nc, 'Fac'), (-500, -560), chip_amt, chip_amt + 0.03)
    chips = math_node(nt, 'MULTIPLY', (-300, -400), out(edge, 'Result'), out(chip_n, 'Result'), clamp=True)
    chips.label = 'Edge chips'
    # tiny sparse specks / scuffs anywhere (restrained)
    ns = node(nt, 'ShaderNodeTexNoise', (-700, -800))
    ns.inputs['Scale'].default_value = 55.0
    ns.inputs['Detail'].default_value = 2.0
    L(nt, out(tc, 'Object'), ns.inputs['Vector'])
    specks = map_range(nt, out(ns, 'Fac'), (-500, -800), speck_amt, speck_amt + 0.015)
    specks.label = 'Specks'
    # per-object wear bias (object property oow_wear, 0..1): lowers chip/speck thresholds
    wear = node(nt, 'ShaderNodeAttribute', (-1100, -680))
    wear.attribute_type = 'OBJECT'
    wear.attribute_name = 'oow_wear'
    wear.label = 'Wear bias (oow_wear)'
    for mr, base, k in ((chip_n, chip_amt, -0.075), (specks, speck_amt, -0.022)):
        lo = math_node(nt, 'MULTIPLY_ADD', (-760, -900), out(wear, 'Fac'), k, c=base)
        hi = math_node(nt, 'MULTIPLY_ADD', (-760, -960), out(wear, 'Fac'), k, c=base + (0.03 if mr is chip_n else 0.015))
        L(nt, out(lo, 'Value'), mr.inputs['From Min'])
        L(nt, out(hi, 'Value'), mr.inputs['From Max'])
    m2, c2 = mix_rgb(nt, (-100, 200), out(chips, 'Value'), c1, (*chip_col, 1.0))
    m3, c3 = mix_rgb(nt, (150, 200), out(specks, 'Result'), c2, (*speck_col, 1.0))
    if fleck_col is not None:
        # sparse paint flecks of the neighbouring colour (R01 shows orange flecks on the ivory)
        nf = node(nt, 'ShaderNodeTexNoise', (-700, -1050))
        nf.inputs['Scale'].default_value = 34.0
        nf.inputs['Detail'].default_value = 3.0
        L(nt, out(tc, 'Object'), nf.inputs['Vector'])
        fl = map_range(nt, out(nf, 'Fac'), (-500, -1050), fleck_amt, fleck_amt + 0.012)
        lo = math_node(nt, 'MULTIPLY_ADD', (-760, -1150), out(wear, 'Fac'), -0.02, c=fleck_amt)
        hi = math_node(nt, 'MULTIPLY_ADD', (-760, -1210), out(wear, 'Fac'), -0.02, c=fleck_amt + 0.012)
        L(nt, out(lo, 'Value'), fl.inputs['From Min']); L(nt, out(hi, 'Value'), fl.inputs['From Max'])
        fl.label = 'Paint flecks'
        m4, c3 = mix_rgb(nt, (350, 200), out(fl, 'Result'), c3, (*fleck_col, 1.0))
    L(nt, c3, inp(bsdf, 'Base Color'))
    # chips are slightly rougher
    rr = math_node(nt, 'MULTIPLY_ADD', (600, -300), out(chips, 'Value'), 0.15, c=rough)
    L(nt, out(rr, 'Value'), inp(bsdf, 'Roughness'))
    mat['oow_role'] = 'opaque painted dielectric; procedural sparse edge wear (Cycles bevel mask)'
    return mat

def plain(name, base, rough, var=0.04):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    o = node(nt, 'ShaderNodeOutputMaterial', (900, 0))
    bsdf = node(nt, 'ShaderNodeBsdfPrincipled', (600, 0))
    L(nt, out(bsdf, 'BSDF'), inp(o, 'Surface'))
    inp(bsdf, 'Metallic').default_value = 0.0
    tc = node(nt, 'ShaderNodeTexCoord', (-700, 0))
    nb = node(nt, 'ShaderNodeTexNoise', (-450, 100))
    nb.inputs['Scale'].default_value = 3.0
    L(nt, out(tc, 'Object'), nb.inputs['Vector'])
    vr = map_range(nt, out(nb, 'Fac'), (-200, 100), 0.3, 0.7, 1.0 - var, 1.0 + var)
    bc = node(nt, 'ShaderNodeRGB', (-200, 300)); bc.outputs[0].default_value = (*base, 1.0)
    cv = node(nt, 'ShaderNodeCombineColor', (0, 100))
    for i in range(3):
        L(nt, out(vr, 'Result'), cv.inputs[i])
    m, c = mix_rgb(nt, (250, 200), 1.0, out(bc, 'Color'), out(cv, 'Color'), 'MULTIPLY')
    L(nt, c, inp(bsdf, 'Base Color'))
    inp(bsdf, 'Roughness').default_value = rough
    return mat

def emitter(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt = reset(mat)
    o = node(nt, 'ShaderNodeOutputMaterial', (1100, 0))
    bsdf = node(nt, 'ShaderNodeBsdfPrincipled', (800, 0))
    L(nt, out(bsdf, 'BSDF'), inp(o, 'Surface'))
    inp(bsdf, 'Roughness').default_value = 0.35
    tc = node(nt, 'ShaderNodeTexCoord', (-900, 0))
    sep = node(nt, 'ShaderNodeSeparateXYZ', (-700, 0))
    L(nt, out(tc, 'Generated'), sep.inputs[0])
    # radial distance from the object's bbox centre in local X/Y (0 centre .. 1 edge)
    cx = math_node(nt, 'SUBTRACT', (-500, 100), out(sep, 'X'), 0.5)
    cy = math_node(nt, 'SUBTRACT', (-500, -60), out(sep, 'Y'), 0.5)
    vv = node(nt, 'ShaderNodeCombineXYZ', (-320, 0))
    L(nt, out(cx, 'Value'), vv.inputs[0]); L(nt, out(cy, 'Value'), vv.inputs[1])
    ln = node(nt, 'ShaderNodeVectorMath', (-150, 0)); ln.operation = 'LENGTH'
    L(nt, out(vv, 'Vector'), ln.inputs[0])
    r = math_node(nt, 'MULTIPLY', (20, 0), out(ln, 'Value'), 2.0, clamp=True)
    ramp = node(nt, 'ShaderNodeValToRGB', (200, 150))
    cr = ramp.color_ramp
    cr.interpolation = 'EASE'
    cr.elements[0].position = 0.0
    cr.elements[0].color = (1.0, 0.78, 0.05, 1.0)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (1.0, 0.16, 0.0, 1.0)
    mid = cr.elements.new(0.50)
    mid.color = (1.0, 0.42, 0.01, 1.0)
    L(nt, out(r, 'Value'), ramp.inputs['Fac'])
    # dim diffuse base so the visible colour comes from emission, not from scene lights
    dim, dimc = mix_rgb(nt, (520, 300), 1.0, out(ramp, 'Color'), (0.12, 0.12, 0.12, 1.0), 'MULTIPLY')
    L(nt, dimc, inp(bsdf, 'Base Color'))
    L(nt, out(ramp, 'Color'), inp(bsdf, 'Emission Color'))
    # strength: falls off toward the rim; per-object scale via custom property oow_emit_scale
    fall = map_range(nt, out(r, 'Value'), (200, -150), 0.0, 1.0, 1.0, 0.45)
    attr = node(nt, 'ShaderNodeAttribute', (200, -350))
    attr.attribute_type = 'OBJECT'
    attr.attribute_name = 'oow_emit_scale'
    st = math_node(nt, 'MULTIPLY', (420, -200), out(fall, 'Result'), out(attr, 'Fac'))
    gain = node(nt, 'ShaderNodeValue', (420, -400)); gain.label = 'Emission gain'
    gain.outputs[0].default_value = EMIT_GAIN
    st2 = math_node(nt, 'MULTIPLY', (600, -250), out(st, 'Value'), out(gain, 'Value'))
    L(nt, out(st2, 'Value'), inp(bsdf, 'Emission Strength'))
    mat['oow_role'] = 'opaque emissive appearance; no transmission; radial yellow->orange'
    return mat

EMIT_GAIN = globals().get('EMIT_GAIN', 9.0)
M01 = painted('M01_Ivory', (0.64, 0.51, 0.37), 0.64, spec=0.38, fleck_col=(0.80, 0.20, 0.02), fleck_amt=0.755, chip_col=(0.09, 0.065, 0.05), speck_col=(0.20, 0.14, 0.10),
              chip_amt=0.57, speck_amt=0.712)
M02 = painted('M02_Orange', (0.86, 0.17, 0.014), 0.58, spec=0.32, chip_col=(0.12, 0.05, 0.025), speck_col=(0.30, 0.08, 0.02),
              chip_amt=0.59, speck_amt=0.725)
M03 = plain('M03_Charcoal', (0.055, 0.040, 0.033), 0.68)
M04 = plain('M04_WarmHub', (0.36, 0.11, 0.025), 0.50)
M05 = emitter('M05_Emitter')
for m, c in ((M01, (0.80, 0.70, 0.58)), (M02, (0.95, 0.35, 0.05)), (M03, (0.09, 0.075, 0.07)),
             (M04, (0.55, 0.25, 0.08)), (M05, (1.0, 0.7, 0.1))):
    m.diffuse_color = (*c, 1.0)
# per-object emitter scale: core dominant, apertures secondary
for ob in bpy.data.collections['ORANGE_ORB_WALKER'].all_objects:
    if ob.type == 'MESH' and ob.data.materials and ob.data.materials[0] == M05:
        ob['oow_emit_scale'] = 1.0 if ob.name.startswith('C05') else 0.32

clay = bpy.data.materials.get('OOW_Clay') or bpy.data.materials.new('OOW_Clay')
nt = reset(clay)
o = node(nt, 'ShaderNodeOutputMaterial', (300, 0)); b = node(nt, 'ShaderNodeBsdfPrincipled', (0, 0))
L(nt, out(b, 'BSDF'), inp(o, 'Surface'))
inp(b, 'Base Color').default_value = (0.26, 0.26, 0.26, 1); inp(b, 'Roughness').default_value = 0.6
clay.diffuse_color = (0.6, 0.6, 0.6, 1)
print('materials ok')
