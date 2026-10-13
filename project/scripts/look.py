"""'미니어처 디오라마 + 약간 플랫' 룩: 3단 툰 셰이더 묶음, 재질, 조명, 색 관리.

EEVEE 전용(Shader to RGB). 받은 빛(그림자·주변광 포함)을 3단으로 끊고 단계 경계만 살짝 부드럽게,
어두운 단계엔 라벤더를 섞어 클레이 모형 같은 차가운 그늘을 만든다.
"""
import bpy, math, sys, os
from mathutils import Vector

P = os.path.expanduser('~/Documents/로마콘크리트_3D/scripts')
if P not in sys.path:
    sys.path.insert(0, P)
import importlib, palette
importlib.reload(palette)
LIN, PAL = palette.LINEAR, palette.PALETTE

STEPS = [(0.00, 0.70), (0.40, 0.70), (0.46, 0.87), (0.82, 0.87), (0.90, 1.00), (1.00, 1.00)]
SHADOW_TINT = palette.oklch_to_linear_srgb(0.62, 0.055, 285)


def clay_group():
    ng = bpy.data.node_groups.get('CLAY_FLAT')
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new('CLAY_FLAT', 'ShaderNodeTree')
    ng.interface.new_socket('Base Color', in_out='INPUT', socket_type='NodeSocketColor')
    ng.interface.new_socket('Shadow Tint', in_out='INPUT', socket_type='NodeSocketColor')
    s = ng.interface.new_socket('Softness', in_out='INPUT', socket_type='NodeSocketFloat')
    s.default_value = 0.15; s.min_value = 0; s.max_value = 1
    ng.interface.new_socket('Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
    N, L = ng.nodes, ng.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    dif = N.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N.new('ShaderNodeShaderToRGB')
    bw = N.new('ShaderNodeRGBToBW')
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cr.interpolation = 'EASE'
    while len(cr.elements) < len(STEPS):
        cr.elements.new(0.5)
    for el, (pos, val) in zip(cr.elements, STEPS):
        el.position = pos; el.color = (val, val, val, 1)
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    amt = N.new('ShaderNodeMath'); amt.operation = 'MULTIPLY'; amt.inputs[1].default_value = 1.6; amt.use_clamp = True
    tint = N.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MIX'
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    emi = N.new('ShaderNodeEmission'); emi.inputs['Strength'].default_value = 1.0
    soft = N.new('ShaderNodeBsdfDiffuse')
    mix = N.new('ShaderNodeMixShader')
    L.new(dif.outputs['BSDF'], s2r.inputs['Shader'])
    L.new(s2r.outputs['Color'], bw.inputs['Color'])
    L.new(bw.outputs['Val'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], inv.inputs[1])
    L.new(inv.outputs['Value'], amt.inputs[0])
    L.new(amt.outputs['Value'], tint.inputs['Factor'])
    L.new(gi.outputs['Base Color'], tint.inputs['A'])
    L.new(gi.outputs['Shadow Tint'], tint.inputs['B'])
    L.new(tint.outputs['Result'], mul.inputs['A'])
    L.new(ramp.outputs['Color'], mul.inputs['B'])
    L.new(mul.outputs['Result'], emi.inputs['Color'])
    L.new(gi.outputs['Base Color'], soft.inputs['Color'])
    L.new(gi.outputs['Softness'], mix.inputs['Fac'])
    L.new(emi.outputs['Emission'], mix.inputs[1])
    L.new(soft.outputs['BSDF'], mix.inputs[2])
    L.new(mix.outputs['Shader'], go.inputs['Shader'])
    return ng


def material(key, softness=0.15):
    name = f'M_{key}'
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    g = nt.nodes.new('ShaderNodeGroup'); g.node_tree = bpy.data.node_groups['CLAY_FLAT']
    g.inputs['Base Color'].default_value = (*LIN[key], 1)
    g.inputs['Shadow Tint'].default_value = (*SHADOW_TINT, 1)
    g.inputs['Softness'].default_value = softness
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(g.outputs['Shader'], out.inputs['Surface'])
    m.diffuse_color = (*LIN[key], 1)
    return m


def lighting():
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new('World'); sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (*LIN['sky_ambient'], 1)
    bg.inputs['Strength'].default_value = 0.35
    sun = bpy.data.objects.get('SUN_key')
    if not sun:
        ld = bpy.data.lights.new('SUN_key', 'SUN'); sun = bpy.data.objects.new('SUN_key', ld)
        sc.collection.objects.link(sun)
    sun.data.energy = 4.6
    sun.data.color = palette.oklch_to_linear_srgb(0.985, 0.022, 85)
    sun.data.angle = math.radians(7)
    # 화면 왼쪽 위·관찰자 쪽에서 비치는 빛(오른쪽 면이 어두워지는 인포그래픽 관례)
    bpy.context.view_layer.update()
    cam = bpy.data.objects['CAM_iso']; m = cam.matrix_world.to_3x3()
    right, up, fwd = m @ Vector((1, 0, 0)), m @ Vector((0, 1, 0)), m @ Vector((0, 0, -1))
    travel = (right * 0.55 - up * 0.75 + fwd * 0.55).normalized()
    sun.rotation_euler = travel.to_track_quat('-Z', 'Y').to_euler()
    # 색 관리: 지정한 파스텔 그대로
    vs = sc.view_settings
    for attr, val in (('view_transform', 'Standard'), ('look', 'None')):
        try:
            setattr(vs, attr, val)
        except TypeError as e:
            print('color mgmt', attr, e)
    vs.exposure = 0; vs.gamma = 1


def assign():
    rules = [('COL_colosseum', 'travertine'), ('PX_wall_ring', 'tuff_stone'), ('PX_ground', 'ground_meadow'),
             ('PX_tiber', 'water_river'), ('PX_sea', 'water_sea'), ('PX_mtn', 'mountain'),
             ('PX_hill', 'ochre_field'), ('PX_houses', 'house_wall'), ('PX_aqueduct', 'tuff_stone'),
             ('PX_kiln', 'terracotta'), ('PX_breakwater', 'tuff_stone'), ('PX_harbor', 'tuff_stone'),
             ('PX_pompeii', 'house_wall'), ('PX_vesuvius', 'volcano_ash'), ('PX_lab', 'house_wall')]
    done = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        for prefix, key in rules:
            if ob.name.startswith(prefix):
                ob.data.materials.clear(); ob.data.materials.append(bpy.data.materials[f'M_{key}'])
                done += 1
                break
    return done


def bevel_proxies():
    for ob in bpy.data.collections['10_PROXY'].objects:
        if ob.type == 'MESH' and ob.name not in ('PX_ground', 'PX_tiber', 'PX_sea_band') and not ob.modifiers.get('클레이 모서리'):
            b = ob.modifiers.new('클레이 모서리', 'BEVEL')
            b.width = min(0.35, 0.12 * min(ob.dimensions)); b.segments = 3; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(40)
            b.use_clamp_overlap = True


def eevee():
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError as e:
        print('engine', e)
    ee = sc.eevee
    for attr, val in (('use_raytracing', True), ('use_shadows', True), ('shadow_ray_count', 2),
                      ('shadow_step_count', 8), ('use_fast_gi', True), ('taa_render_samples', 32)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception as e:
                print('eevee', attr, e)


clay_group()
for k in PAL:
    if k != 'sky_ambient':
        material(k)
lighting(); bevel_proxies(); eevee()
print('materials assigned', assign())


def outline(thickness=0.9, alpha=0.55):
    """얇은 따뜻한 갈색 외곽선(Freestyle): 실루엣·경계·각진 모서리만."""
    sc = bpy.context.scene
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = 'ABSOLUTE'
    sc.render.line_thickness = thickness
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(135)
    ls = fs.linesets.get('CLAY_LINE') or fs.linesets.new('CLAY_LINE')
    for i in list(fs.linesets):
        if i.name != 'CLAY_LINE':
            i.show_render = False
    ls.select_by_visibility = True
    ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
    ls.select_contour = False; ls.select_external_contour = False
    st = ls.linestyle
    st.color = palette.oklch_to_linear_srgb(0.42, 0.035, 50)
    st.alpha = alpha
    st.thickness = 1.0


outline()
