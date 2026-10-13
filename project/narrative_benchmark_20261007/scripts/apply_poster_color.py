"""Color-only v6 -> v7. Exact geometry, positions, camera, and visibility are retained."""
import json, runpy
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'copy/color_system_v11.json').read_text())
h=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
source=(ROOT/P['sourceScene']).resolve();output=(ROOT/P['outputScene']).resolve()
assert Path(bpy.data.filepath).resolve()==source
inventory=json.loads(Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/color-design/scene-color-inventory.json').read_text())
assert h['sha256_file'](source)==inventory['source_sha256']
source_sha=h['sha256_file'](source);original_sha=h['sha256_file'](h['SOURCE'])
states={o.name:o.hide_viewport for o in bpy.data.objects}
def snap():
    for o in bpy.data.objects:o.hide_viewport=False
    bpy.context.view_layer.update()
    result=h['source_fingerprints'](list(bpy.data.objects))
    for name,ob in result.items():
        ob['hide_viewport']=states[name]
        if 'camera_data' in ob:ob['camera_data'].pop('session_uid',None)
    for o in bpy.data.objects:o.hide_viewport=states[o.name]
    bpy.context.view_layer.update()
    return result
before=snap();scene_before=h['scene_fingerprint'](bpy.context.scene)
colors=P['tokens'];assignments={}
def linear_hex(v):
    c=[int(v[i:i+2],16)/255 for i in (1,3,5)]
    return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]
def token_for(ob):
    name=ob['name'];category=ob['category']
    if not ob['render_visible_in_saved_scene'] or ob['type'] not in {'MESH','CURVE'}:return None
    if name=='COL_ruined':return 'colosseum'
    if name=='NB_modern_building':return 'modern_concrete'
    if name=='NB_lime_clast_specimen':return 'lime_specimen_matrix'
    if name.startswith('NB_lime_clast_specimen_LIME'):return 'lime_calcium_crystal'
    if name.startswith('NB_core4_sequence_GRAY'):
        return {'00':'type_secondary_on_light_ground','01':'type_heading','02':'lime_calcium_crystal',
                '03':'lime_specimen_matrix','04':'water_process'}[name[-2:]]
    if name=='S_lab_island':return 'laboratory'
    if name=='C2_hot_mixing':return 'hot_mixing'
    if name=='C5_researchers':return 'roman_support_stone'
    if category=='terrain_plain':return 'terrain'
    if category=='water':return 'sea_river'
    if category=='water_surface_marks':return 'water_wave'
    if category=='vegetation_tree':return 'foliage'
    if category=='mountains':return 'mountain_volcano'
    if category=='agricultural_fields':return 'field'
    if category in {'roads','bridge'}:return 'road_foundation'
    if category.startswith('support_') and category not in {'support_leader'}:
        return 'mountain_volcano' if category=='support_vesuvius' else 'roman_support_stone'
    if name.startswith('S_core'):
        number=int(name[6]);return {1:'badge_1_5',2:'badge_2',3:'badge_3',4:'badge_4',5:'badge_1_5'}[number]
    if name.startswith('D1_crystal'):return 'lime_calcium_crystal'
    if name in {'D1_concrete','D1_material'}:return 'lime_specimen_matrix'
    if name=='D1_seawater':return 'water_process'
    if name.startswith('D1_tank'):return 'modern_concrete'
    if name.startswith('D2_lime') and name!='D2_lime_kiln':return 'lime_calcium_crystal'
    if name=='D2_cube':return 'lime_specimen_matrix'
    if name.startswith('D2_heat'):return 'hot_mixing'
    if name.startswith('D2_'):return 'roman_support_stone'
    if name.startswith('D3_press'):return 'type_secondary_on_light_ground'
    if name=='D3_foundation':return 'concrete_dense'
    if name=='D3_heavy':return 'road_foundation'
    if name=='D3_middle':return 'stone_middle'
    if name=='D3_light':return 'stone_light'
    if name.startswith('D3_brick'):return 'pozzolan'
    if name.startswith('D3_'):return 'roman_support_stone'
    if name.startswith('H_lime') or name.startswith('H_mold_lime'):return 'lime_calcium_crystal'
    if name.startswith('H_ash'):return 'pozzolan'
    if name.startswith('H_stone'):return 'stone_middle'
    if name.startswith('H_mold_plank'):return 'road_foundation'
    if name.startswith('H_mold'):return 'lime_specimen_matrix'
    if name.startswith('H_book'):
        return 'stone_light' if 'pages' in name else 'laboratory'
    if name.startswith('H_core_band'):return 'steel_if_separate'
    if name.startswith('H_core') or name=='H_research':return 'modern_concrete'
    if name.startswith('H_lens'):return 'badge_1_5'
    if name.startswith('H_colosseum'):return 'colosseum'
    if name.startswith('H_gate'):
        return 'header_surface' if name in {'H_gate','H_gate_body'} else 'header_trim'
    if name.startswith('S_sect'):
        if name=='S_sect0':return 'stone_light'
        if name=='S_sect1':return 'stone_middle'
        if name=='S_sect2':return 'road_foundation'
        if name=='S_sect3':return 'concrete_dense'
        return 'line'
    if name.startswith('S_time'):return 'line'
    if name.startswith('S_lead') or name.startswith('S_pin'):return 'line'
    raise RuntimeError(('Unclassified visible color object',name,category))

for ob in inventory['inventory']:
    token=token_for(ob)
    if token:
        bpy.data.objects[ob['name']].color=(*linear_hex(colors[token]),1.)
        assignments[ob['name']]={'token':token,'hex':colors[token],
            'linear_rgb':linear_hex(colors[token])}
scene=bpy.context.scene
settings_before={'exposure':scene.view_settings.exposure,'background_type':scene.display.shading.background_type,
 'background_color':list(scene.display.shading.background_color)}
scene.view_settings.exposure=P['colorManagement']['exposure']
scene.display.shading.background_type='WORLD'
scene.world.color=linear_hex(colors['background'])
if scene.world.use_nodes:
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(*linear_hex(colors['background']),1.)
after=snap()
changed={n:[k for k in before[n] if before[n][k]!=after[n][k]] for n in before if before[n]!=after[n]}
assert all(keys==['color'] for keys in changed.values()),changed
assert set(changed)<=set(assignments)
assert scene_before==h['scene_fingerprint'](scene)
assert h['sha256_file'](source)==source_sha and h['sha256_file'](h['SOURCE'])==original_sha
assert scene.display.shading.color_type=='OBJECT' and scene.view_settings.view_transform=='Standard'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report={'input':str(source),'output':str(output),'input_sha256':source_sha,'original_source_sha256':original_sha,
        'geometry_camera_transforms_visibility_preserved':True,'object_count':len(before),
        'color_assignments':assignments,'changed_objects':changed,'before':before,'after':after,
        'color_settings_before':settings_before,'color_settings_after':{'exposure':scene.view_settings.exposure,'background_type':'WORLD',
         'world_color_linear':list(scene.world.color),'view_transform':'Standard'},
        'render_passes':h['render_two_pass'](ROOT/'renders/narrative_v7_color.png')}
(ROOT/'out/poster-color-v7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('COLOR_V7_COMPLETE',json.dumps({'output':str(output),'changed_color_objects':len(changed),
      'preserved_geometry_objects':len(before),'renders':report['render_passes']},ensure_ascii=False))
