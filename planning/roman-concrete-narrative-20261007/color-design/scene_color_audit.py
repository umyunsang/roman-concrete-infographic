"""Read-only inventory. Does not save, render, mutate Blender data or use UI."""
import json
import hashlib
from collections import Counter
from pathlib import Path
import bpy
import numpy as np

OUT = Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/color-design')
SOURCE = Path(bpy.data.filepath)

def rna_values(obj):
    result = {}
    for p in obj.bl_rna.properties:
        if p.identifier == 'rna_type' or p.type in {'POINTER','COLLECTION'}:
            continue
        try:
            value = getattr(obj, p.identifier)
            if p.is_array: value = list(value)
            if isinstance(value, (str, bool, int, float, list)): result[p.identifier] = value
        except (AttributeError, TypeError, RuntimeError): pass
    return result

def category(ob):
    n = ob.name
    c = {x.name for x in ob.users_collection}
    if ob.type == 'CAMERA': return 'camera'
    if ob.type == 'LIGHT': return 'light'
    if ob.type == 'FONT' or '70_LABELS_TEST' in c: return 'legacy_text'
    if '85_HEADER' in c: return 'header_graphic'
    if n.startswith(('S_core','S_detail')): return 'core_detail_badge_or_underline'
    if n.startswith('S_pin'): return 'support_leader'
    if n.startswith('S_d4'): return 'mechanism_annotation'
    if n.startswith('NB_core4_sequence'): return 'core4_crack_sequence'
    if n.startswith('NB_lime_clast_specimen'): return 'core3_lime_clast_specimen'
    if n.startswith('NB_modern_building'): return 'core1_modern_reinforced_building'
    if n.startswith('NB_marine_breakwater'): return 'support_roman_breakwater'
    if n.startswith('D4_'): return 'legacy_crack_sequence_hidden'
    if n.startswith('D1_'): return 'detail1_marine_chemistry'
    if n.startswith('D2_'): return 'detail2_hot_mixing'
    if n.startswith('D3_'): return 'detail3_structure'
    if n.startswith(('COL_', 'CI_')) or '25_COL_INNER' in c: return 'hero_colosseum'
    if n.startswith(('T_pine','T_cypress')): return 'vegetation_tree'
    if n.startswith('T_land'): return 'terrain_plain'
    if n.startswith('T_'): return 'terrain_other'
    if n.startswith('F_centuriatio'): return 'agricultural_fields'
    if n.startswith('B_pons'): return 'bridge'
    if n.startswith(('R_', 'ROAD_', 'road_')): return 'roads'
    if '35_FIELDS_ROADS' in c: return 'road_or_field_other'
    if n.startswith(('L10_sea', 'L02_tiber')): return 'water'
    if n == 'W_water_marks': return 'water_surface_marks'
    if n.startswith('L01'): return 'mountains'
    if n.startswith('L03'): return 'support_roman_forum'
    if n.startswith('L04'): return 'support_palatine'
    if n.startswith('L05'): return 'support_aqueduct'
    if n.startswith('L06'): return 'support_appian_way'
    if n.startswith('L07'): return 'support_vesuvius'
    if n.startswith('L08'): return 'support_pompeii'
    if n.startswith(('L09', 'L12', 'L13')): return 'support_port_harbor'
    if n.startswith('L11'): return 'support_privernum'
    if n.startswith('S_lab'): return 'core5_modern_experiment_laboratory'
    if n == 'C5_researchers': return 'support_generic_ruin_observation'
    if n.startswith('C2_'): return 'core2_hot_mixing'
    if n.startswith('C'): return 'legacy_core_model'
    if n.startswith('B'): return 'basic_icon'
    if '80_SHAPES' in c or '81_NOSHADOW' in c: return 'overlay_other'
    if '10_PROXY' in c or '00_REF' in c: return 'legacy_proxy_reference_hidden'
    return 'unclassified'

def project_bbox(ob):
    if ob.type != 'MESH' or not ob.data.vertices: return None
    cam = bpy.context.scene.camera
    values = np.empty(len(ob.data.vertices)*3, dtype=np.float64)
    ob.data.vertices.foreach_get('co', values)
    matrix = np.array(ob.matrix_world)
    points = values.reshape(-1,3) @ matrix[:3,:3].T + matrix[:3,3]
    tr, br, bl, tl = [np.array(x) for x in cam.data.view_frame(scene=bpy.context.scene)]
    inv = np.linalg.inv(np.array(cam.matrix_world))
    pc = points @ inv[:3,:3].T + inv[:3,3]
    scale = np.ones(len(pc)) if cam.data.type == 'ORTHO' else tr[2] / pc[:,2]
    x,y = pc[:,0]*scale, pc[:,1]*scale
    uv = np.stack([(x-bl[0])/(tr[0]-bl[0])*1191,(tr[1]-y)/(tr[1]-bl[1])*1684],1)
    return [float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]

scene = bpy.context.scene
inventory = []
for ob in sorted(bpy.data.objects, key=lambda x:x.name):
    record = {'name': ob.name,'type':ob.type,'category':category(ob),'color':list(ob.color),
        'collections': sorted(x.name for x in ob.users_collection),'parent':ob.parent.name if ob.parent else None,
        'children':sorted(x.name for x in ob.children),'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,
        'display_type':ob.display_type,'materials':[m.name if m else None for m in getattr(ob.data,'materials',[])],
        'projected_bbox': project_bbox(ob),
        'narrative_custom_properties':{k:ob[k] for k in ob.keys() if k.startswith('narrative_')}}
    record['render_visible_in_saved_scene'] = not ob.hide_render and any(not x.hide_render for x in ob.users_collection)
    if ob.type == 'MESH':
        record.update({'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),
            'material_indices':dict(Counter(p.material_index for p in ob.data.polygons)),
            'color_attributes':[{'name':a.name,'domain':a.domain,'data_type':a.data_type} for a in ob.data.color_attributes]})
    if ob.type == 'FONT':record['body']=ob.data.body
    inventory.append(record)

materials = []
for m in bpy.data.materials:
    d={'name':m.name,'users':m.users,'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes}
    if m.use_nodes:
        d['nodes']=[{'name':n.name,'type':n.type,
          'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(str,bool,int,float)) or hasattr(i,'default_value') and i.name in {'Base Color','Color'}}}
          for n in m.node_tree.nodes if n.type in {'BSDF_PRINCIPLED','RGB','EMISSION'}]
    materials.append(d)

world = None
if scene.world:
    world = {'name':scene.world.name,'color':list(scene.world.color),'use_nodes':scene.world.use_nodes,
        'nodes':[{'name':n.name,'type':n.type,'inputs':{i.name:list(i.default_value) if i.type=='RGBA' else i.default_value for i in n.inputs if i.type in {'RGBA','VALUE'}}} for n in scene.world.node_tree.nodes] if scene.world.use_nodes else []}

report={'source_file':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'blender_version':bpy.app.version_string,'scene':scene.name,'object_count':len(inventory),
    'render':rna_values(scene.render),'shading':rna_values(scene.display.shading),
    'scene_display':rna_values(scene.display),'view_settings':rna_values(scene.view_settings),
    'display_settings':rna_values(scene.display_settings),'world':world,
    'camera':scene.camera.name if scene.camera else None,
    'collections':[{'name':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport,'objects':len(c.objects)} for c in bpy.data.collections],
    'materials':materials,'inventory':inventory,
    'categories':dict(Counter(x['category'] for x in inventory)),
    'method':'Read-only background file open; no render, save, data mutation or UI calls.'}
report['critical_shading']={k:str(getattr(scene.display.shading,k)) for k in ['type','light','studio_light','color_type','background_type','cavity_type','render_pass']}
report['critical_color_management']={k:str(getattr(scene.view_settings,k)) for k in ['view_transform','look','exposure','gamma']}
report['display_device']=str(scene.display_settings.display_device)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'scene-color-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'objects':len(inventory),'categories':report['categories'],'engine':scene.render.engine,
    'color_type':scene.display.shading.color_type,'view_transform':scene.view_settings.view_transform,
    'source_sha256':report['source_sha256'],'output':str(OUT/'scene-color-inventory.json')},ensure_ascii=False))
