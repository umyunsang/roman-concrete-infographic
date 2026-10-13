"""Fresh saved v9/v11 validation; execute only after root says ready.
No data mutation, visibility toggles, render, save or UI writes.
"""
import hashlib,json,runpy
from collections import Counter
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
REPORT_PATH=ROOT/'out/construction-detail-v11.json'
REPORT=json.loads(REPORT_PATH.read_text())
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
RUNTIME={'rna_type','session_uid','is_updated','is_updated_data','is_updated_transform','is_runtime_data','is_evaluated','is_embedded_data'}

def plain(v):
    if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
    if isinstance(v,(str,bool,int,float)) or v is None:return v
    if hasattr(v,'__iter__'):return [plain(x) for x in v]
    raise TypeError(type(v).__name__)

def scalar(ob):
    out={}
    for p in ob.bl_rna.properties:
        if p.identifier in RUNTIME or p.type in {'POINTER','COLLECTION'}:continue
        try:
            v=getattr(ob,p.identifier)
            if p.type=='ENUM':v=str(v)
            if getattr(p,'is_array',False):v=list(v)
            if isinstance(v,(str,bool,int,float,list)):out[p.identifier]=plain(v)
        except (AttributeError,TypeError,RuntimeError):pass
    return out

def world(w):
    d={'properties':scalar(w),'nodes':{},'links':[]}
    if w.use_nodes:
        for n in w.node_tree.nodes:
            inputs={}
            for i in n.inputs:
                if not hasattr(i,'default_value'):continue
                v=i.default_value
                if hasattr(v,'__len__') and not isinstance(v,str):v=list(v)
                if isinstance(v,(str,bool,int,float,list)):inputs[i.name]=v
            d['nodes'][n.name]={'properties':scalar(n),'inputs':inputs}
        d['links']=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in w.node_tree.links]
    return d

def normalize(objs):
    for o in objs.values():
        if 'camera_data' in o:o['camera_data'].pop('session_uid',None)
    return objs

def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def snap():
    bpy.context.view_layer.update()
    objs=normalize(H['source_fingerprints'](list(bpy.data.objects)))
    raw_world={k:v['matrix_world'] for k,v in objs.items()}
    calculated=[];cache={}
    def persistent_world(ob):
        if ob.name in cache:return cache[ob.name]
        m=ob.matrix_world.copy() if not ob.hide_viewport else ob.matrix_basis.copy()
        if ob.hide_viewport:
            if ob.constraints:raise RuntimeError(('Hidden constrained object',ob.name))
            if ob.parent:
                if ob.parent_type!='OBJECT':raise RuntimeError(('Parent type',ob.name))
                m=persistent_world(ob.parent)@ob.matrix_parent_inverse@m
        cache[ob.name]=m
        return m
    for ob in bpy.data.objects:
        if ob.hide_viewport:
            m=[list(row) for row in persistent_world(ob)]
            if m!=objs[ob.name]['matrix_world']:calculated.append(ob.name)
            objs[ob.name]['matrix_world']=m
    meshes={}
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        m=ob.data;indices=np.array([p.material_index for p in m.polygons],dtype='<u2')
        material_names=[x.name if x else None for x in m.materials]
        role_indices=[x.get('semantic_role') if x else None for x in m.materials]
        valid=all(int(i)<len(role_indices) for i in indices) if len(role_indices) else bool(np.all(indices==0))
        counter=Counter(role_indices[int(i)] for i in indices) if role_indices and valid else Counter()
        counts={role:counter[role] for role in role_indices} if role_indices and valid else {}
        meshes[ob.name]={'data_name':m.name,'vertices':len(m.vertices),'edges':len(m.edges),'loops':len(m.loops),'polygons':len(m.polygons),
            'geometry_sha256':H['mesh_fingerprint'](m),'material_names':material_names,'material_roles':role_indices,
            'valid_material_indices':valid,'face_counts':counts,'assignment_sha256':hashlib.sha256(indices.tobytes()).hexdigest(),
            'uv_layers':[x.name for x in m.uv_layers],'color_attributes':[(x.name,x.domain,x.data_type) for x in m.color_attributes],
            'render_visible':not ob.hide_render and any(not c.hide_render for c in ob.users_collection)}
    viewports={}
    for screen in bpy.data.screens:
        for ai,area in enumerate(screen.areas):
            if area.type!='VIEW_3D':continue
            for si,space in enumerate(area.spaces):
                if space.type=='VIEW_3D':
                    viewports[f'{screen.name}/{ai}/{si}']={'shading':scalar(space.shading),'properties':scalar(space),
                        'region3d':scalar(space.region_3d) if space.region_3d else None}
    materials={}
    for m in bpy.data.materials:
        bsdf=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        materials[m.name]={'role':m.get('semantic_role'),'hex':m.get('sRGB_hex'),'diffuse_color':list(m.diffuse_color),
            'use_nodes':m.use_nodes,'roughness':m.roughness,'principled_base_color':list(bsdf.inputs['Base Color'].default_value) if bsdf else None,
            'principled_roughness':bsdf.inputs['Roughness'].default_value if bsdf else None,'users':m.users,
            'nodes':world(m)['nodes'],'links':world(m)['links']}
    scene=bpy.context.scene
    return {'objects':objs,'meshes':meshes,'materials':materials,'viewports':viewports,
        'scene':{'render':scalar(scene.render),'display':scalar(scene.display),'shading':scalar(scene.display.shading),
            'view':scalar(scene.view_settings),'display_settings':scalar(scene.display_settings),'world':world(scene.world),
            'basic':H['scene_fingerprint'](scene)},
        'raw_world':raw_world,'hidden_world_calculated':sorted(calculated),
        'parent_inverse':{o.name:[list(row) for row in o.matrix_parent_inverse] for o in bpy.data.objects},
        'custom_properties':{o.name:{k:plain(o[k]) for k in o.keys() if k.startswith('narrative_')} for o in bpy.data.objects},
        'overlay_vertices':{o.name:[list(v.co) for v in o.data.vertices] for o in bpy.data.objects if o.name in {'S_core2_badge','S_core2_underline'}},
        'scene_extra':{'frame_current':scene.frame_current,'frame_subframe':scene.frame_subframe,'frame_start':scene.frame_start,'frame_end':scene.frame_end,'unit_settings':scalar(scene.unit_settings)}}

def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for k in sorted(set(a)|set(b)):
            p=path+'.'+k if path else k
            if k not in a or k not in b:out.append({'path':p,'before':a.get(k),'after':b.get(k)})
            else:out.extend(diff(a[k],b[k],p))
        return out
    return [] if a==b else [{'path':path,'before':a,'after':b}]

SOURCE=ROOT/'out/roman_concrete_narrative_v9.blend'
TARGET=ROOT/'out/roman_concrete_narrative_v11.blend'
EXPECTED_V9_SHA='8125d6cf8ec2da6cf09125472aa603afd1debcd88910ff8ed0893b174a2288fe'
EXPECTED_CANONICAL_SHA='28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3'
LAYOUT=json.loads((OUT/'construction-layout-proposal.json').read_text())
RETIRE=set(n for group in LAYOUT['retireGroups'].values() for n in group)-{'L03_forum_vesta','L03_forum_temple'}
MOVERS={'COL_ruined','C2_hot_mixing','D2_lime_kiln','L04_palatine'}
WORLD_CHILDREN={'L04_palatine_arch'}
OVERLAY={'S_core2_badge','S_core2_underline'}
KNOWN_SCOPE=RETIRE|MOVERS|WORLD_CHILDREN|OVERLAY


def names(value):
    if isinstance(value,dict):return set(value)
    result=set()
    for item in value:
        if isinstance(item,str):result.add(item)
        elif isinstance(item,dict):result.add(item.get('name') or item.get('object'))
        else:raise TypeError('Unsupported object-name report entry')
    if None in result:raise ValueError('Report object entry lacks a name')
    return result


def report_objects(value, actual):
    result=normalize(json.loads(json.dumps(value)))
    # Production snapshots may materialize hidden cache matrices before save.
    # Basis and inverse are independently compared; normalize only hidden cache.
    for name,record in result.items():
        if name in actual and record.get('hide_viewport'):
            record['matrix_world']=actual[name]['matrix_world']
    return result


EXPECTED_NEW=set(['NB_vault_construction','NB_vault_complete','NB_worker_carrier','NB_worker_builder','NB_worker_pair','NB_carrier_human_head','NB_carrier_bucket','NB_carrier_mortar','NB_carrier_handle0','NB_carrier_handle1','NB_pair_mortar','NB_build_wall_mortar','NB_build_formpost0','NB_build_formpost1','NB_build_formboard0','NB_build_formboard1','NB_build_formbrace','NB_detail_calcium_clast','NB_detail4_micro','NB_detail4_matrix','NB_detail4_crack','NB_detail4_crystal'])
EXPECTED_NEW|={f'NB_vault_timber_{part}{i}' for i in range(2) for part in ['rib','sill']}
EXPECTED_NEW|={f'NB_vault_timber_post{i}_{j}' for i in range(2) for j in range(2)}
EXPECTED_NEW|={f'NB_build_stone_{i}_{j}' for i in range(3) for j in range(4 if i<2 else 2)}

bpy.ops.wm.open_mainfile(filepath=str(SOURCE));v9=snap()
source_overlay_bboxes={n:H['screen_bbox'](bpy.data.objects[n]) for n in OVERLAY}
bpy.ops.wm.open_mainfile(filepath=str(TARGET));v11=snap()
old_names=set(v9['objects']);new_names=set(v11['objects'])-old_names
reported_new=names(REPORT['new_objects'])
allowed=names(REPORT['allowed_existing_changes'])
reported_hidden=names(REPORT['hidden_objects'])
existing10={n:v11['objects'][n] for n in old_names if n in v11['objects']}
object_changes=diff(v9['objects'],existing10)
changed_names={x['path'].split('.',1)[0] for x in object_changes}
field_allow={n:{'hide_render','hide_viewport'} for n in RETIRE}
field_allow.update({n:{'matrix_basis','matrix_world'} for n in MOVERS})
field_allow['D2_lime_kiln'].add('materials')
field_allow.update({n:{'matrix_world'} for n in WORLD_CHILDREN})
field_allow.update({n:{'matrix_basis','matrix_world'} for n in OVERLAY})
unexpected_object_changes=[]
for change in object_changes:
    name,field=change['path'].split('.',1)
    if name not in allowed or field not in field_allow.get(name,set()):unexpected_object_changes.append(change)
report_allowed_field_errors=[]
if isinstance(REPORT['allowed_existing_changes'],dict):
    for name,fields in REPORT['allowed_existing_changes'].items():
        if not isinstance(fields,list):continue
        actual={x['path'].split('.',1)[1] for x in object_changes if x['path'].startswith(name+'.')}
        if not actual<=set(fields):report_allowed_field_errors.append({'object':name,'actual':sorted(actual),'allowed':fields})
newly_hidden={n for n in old_names if not v9['objects'][n]['hide_render'] and v11['objects'][n]['hide_render']}
mesh_errors=[];geometry_errors=[];data_name_changes=[];translation_errors=[]
for name,m9 in v9['meshes'].items():
    m10=v11['meshes'].get(name)
    if not m10:geometry_errors.append({'object':name,'error':'missing original mesh'});continue
    keys=['vertices','edges','loops','polygons','uv_layers','color_attributes']
    for key in keys:
        if m9[key]!=m10[key]:geometry_errors.append({'object':name,'field':key})
    if m9['geometry_sha256']!=m10['geometry_sha256']:
        if True:geometry_errors.append({'object':name,'field':'geometry_sha256'})
        else:
            a=np.asarray(v9['overlay_vertices'][name]);b=np.asarray(v11['overlay_vertices'][name]);delta=b-a
            if a.shape!=b.shape or np.max(np.abs(delta-delta.mean(axis=0)))>2e-5:
                translation_errors.append({'object':name,'error':'baked vertices are not one rigid translation'})
    if m9['data_name']!=m10['data_name']:data_name_changes.append(name)
    permitted={'render_visible'} if name in RETIRE else set()
    if name=='D2_lime_kiln':permitted|={'data_name','material_names','material_roles','face_counts','assignment_sha256'}
    # Overlay geometry remains exact in v11; only its object transform is moved.
    for change in diff(m9,m10):
        if change['path'].split('.',1)[0] not in permitted:mesh_errors.append({'object':name,**change})
    if not m10['valid_material_indices']:mesh_errors.append({'object':name,'error':'invalid material indices'})

# All old material colors, nodes, links and metadata remain exact; users can vary.
old_material_errors=[];retired_unused_materials=[]
for name,m9 in v9['materials'].items():
    m10=v11['materials'].get(name)
    if m10 is None:
        consumers={obj for obj,mesh in v9['meshes'].items() if name in mesh['material_names']}
        if consumers=={'D2_lime_kiln'} and m9['users']==1:
            retired_unused_materials.append({'material':name,'original_consumers':sorted(consumers),'original_users':m9['users'],'reason':'old kiln slot replaced by authorized four-part material assignment; resulting unused datablock omitted from saved file'})
        else:old_material_errors.append({'material':name,'error':'missing','original_consumers':sorted(consumers),'original_users':m9['users']})
        continue
    for change in diff({k:v for k,v in m9.items() if k!='users'}, {k:v for k,v in m10.items() if k!='users'}):
        old_material_errors.append({'material':name,**change})
new_materials=set(v11['materials'])-set(v9['materials'])
new_material_errors=[]
for name in sorted(new_materials):
    m=v11['materials'][name]
    hx=m['hex']
    if not isinstance(hx,str) or len(hx)!=7 or not m['role']:
        new_material_errors.append({'material':name,'error':'missing semantic role/HEX metadata'});continue
    rgb=[int(hx[i:i+2],16)/255 for i in (1,3,5)]
    rgba=[float(np.float32(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)) for x in rgb]+[1.0]
    for key,expected in [('diffuse_color',rgba),('principled_base_color',rgba),('use_nodes',True)]:
        if m[key]!=expected:new_material_errors.append({'material':name,'field':key,'expected':expected,'actual':m[key]})

# Recompute original kiln face roles independently from the delivered pure helper.
kiln_helper=runpy.run_path(str(OUT/'hearth_object_parts.py'),run_name='read_only_hearth')
kiln_spec=kiln_helper['build_assignments'](bpy)['D2_lime_kiln']
kiln=bpy.data.objects['D2_lime_kiln'];expected_roles=[kiln_spec['default']]*len(kiln.data.polygons)
for role,inds in kiln_spec['faces'].items():
    for i in inds:expected_roles[i]=role
actual_roles=[kiln.data.materials[p.material_index].get('semantic_role') for p in kiln.data.polygons]
kiln_errors=[]
if actual_roles!=expected_roles:kiln_errors.append({'error':'actual polygon semantic roles differ from independent helper'})
for role,hx in kiln_helper['PALETTE'].items():
    mats=[m for m in kiln.data.materials if m.get('semantic_role')==role]
    if len(mats)!=1 or mats[0].get('sRGB_hex')!=hx:kiln_errors.append({'role':role,'error':'missing or wrong kiln palette material'})

scene_errors=[]
scene9=json.loads(json.dumps(v9['scene']));scene10=json.loads(json.dumps(v11['scene']))
old_collections=scene9['basic']['collections'];new_collections=scene10['basic']['collections']
for name,record in old_collections.items():
    if new_collections.get(name)!=record:scene_errors.append({'collection':name,'error':'existing collection visibility changed'})
scene10['basic']['collections']={n:new_collections[n] for n in old_collections if n in new_collections}
scene_errors+=diff(scene9,scene10)
scene_errors+=diff(v9['scene_extra'],v11['scene_extra'])
viewport_errors=diff(v9['viewports'],v11['viewports'])
extra_errors=[]
for key in ['parent_inverse','custom_properties']:
    fresh={n:v11[key][n] for n in old_names if n in v11[key]}
    extra_errors.extend({'section':key,**x} for x in diff(v9[key],fresh))
before_report_errors=diff(report_objects(REPORT['before'],v9['objects']),v9['objects'])
after_report=report_objects(REPORT['after'],v11['objects'])
after_expected=v11['objects'] if set(after_report)==set(v11['objects']) else existing10
after_report_errors=diff(after_report,after_expected)

new_object_errors=[]
for name in new_names:
    obj=bpy.data.objects[name]
    if obj.type!='MESH':continue
    m=v11['meshes'][name]
    if not m['valid_material_indices'] or not m['material_names']:new_object_errors.append({'object':name,'error':'missing/invalid mesh materials'})
    if obj.hide_render:new_object_errors.append({'object':name,'error':'new mesh is hidden from render'})
    box=H['screen_bbox'](obj)
    if box[0]<8 or box[1]<8 or box[2]>1183 or box[3]>1676:new_object_errors.append({'object':name,'error':'outside poster safe bounds','bbox':box})

bbox_errors=[];checked_bboxes={}
# v11 operations supersede abandoned upper-row layout. Check the actual
# production operation targets, independently comparing the saved geometry.

# Explicit fresh projected bbox entries in the production report, if present.
def bbox_records(value,context=None):
    found=[]
    if isinstance(value,dict):
        candidate=value.get('object') or value.get('name') or context
        if candidate in v11['objects'] and bpy.data.objects[candidate].type in {'MESH','EMPTY'}:
            for key in ['projected_bbox','actual_bbox','got_bbox','after_bbox']:
                box=value.get(key)
                if isinstance(box,list) and len(box)==4 and all(isinstance(x,(int,float)) for x in box):found.append((candidate,key,box))
        for key,child in value.items():
            if key in {'before','after'}:continue
            found+=bbox_records(child,key if key in v11['objects'] else context)
    elif isinstance(value,list):
        for child in value:found+=bbox_records(child,context)
    return found
def object_bbox(name):
    ob=bpy.data.objects[name]
    meshes=([ob] if ob.type=='MESH' else [])+[x for x in ob.children_recursive if x.type=='MESH']
    uv=H['project_pts'](np.concatenate([H['world_coords'](x) for x in meshes]))
    return [float(uv[:,0].min()),float(uv[:,1].min()),float(uv[:,0].max()),float(uv[:,1].max())]
for operation in REPORT['operations']:
    if 'target_bbox' not in operation:continue
    name=operation['name'];box=object_bbox(name);target=operation['target_bbox']
    checked_bboxes[name]={'actual':box,'target':target}
    if box[0]<target[0]-.6 or box[1]<target[1]-.6 or box[2]>target[2]+.6 or box[3]>target[3]+.6:
        bbox_errors.append({'object':name,'actual':box,'target':target,'error':'outside production target slot'})
for name,key,reported in bbox_records(REPORT):
    actual=object_bbox(name)
    if max(abs(x-y) for x,y in zip(actual,reported))>.25:bbox_errors.append({'object':name,'field':key,'reported':reported,'actual':actual})

index_report_errors=[]
for key,state in [('indices_before',v9),('indices_after',v11)]:
    actual={name:mesh['assignment_sha256'] for name,mesh in state['meshes'].items()}
    for mismatch in diff(REPORT[key],actual):index_report_errors.append({'report_field':key,**mismatch})
applied_report_errors=[]
for name,record in REPORT['applied'].items():
    actual=v11['meshes'][name]
    for key in ['material_roles','face_counts','assignment_sha256']:
        if actual[key]!=record[key]:applied_report_errors.append({'object':name,'field':key,'reported':record[key],'actual':actual[key]})
    if actual['polygons']!=record['polygon_count']:applied_report_errors.append({'object':name,'field':'polygon_count'})
    expected_names=[REPORT['materials'][role]['name'] for role in record['material_roles']]
    if actual['material_names']!=expected_names:applied_report_errors.append({'object':name,'field':'material_slot_names'})
material_report_errors=[]
for role,record in REPORT['materials'].items():
    m=v11['materials'].get(record['name'])
    if not m:material_report_errors.append({'role':role,'error':'missing reported material'});continue
    for key,expected in [('role',role),('hex',record['hex']),('diffuse_color',record['linear_color'])]:
        if m[key]!=expected:material_report_errors.append({'role':role,'field':key})
mesh_source_errors=[]
for name in new_names:
    ob=bpy.data.objects[name]
    if ob.get('narrative_source_file'):
        path=Path(ob['narrative_source_file'])
        if H['sha256_file'](path)!=ob.get('narrative_model_sha256'):mesh_source_errors.append({'object':name,'error':'input GLB SHA changed'})
        if not ob.get('narrative_meshy_task_id'):mesh_source_errors.append({'object':name,'error':'missing Meshy task provenance'})

# Supplemental physical geometry checks; classifications and contact constraints
# are independent of projection rectangles and do not mutate scene evaluation.
physical=runpy.run_path(str(OUT/'v11_physical_geometry.py'),run_name='read_only_geometry')['audit'](bpy,H)
overlay_shift_errors=[]
for n in OVERLAY:
    now=H['screen_bbox'](bpy.data.objects[n]);delta=np.asarray(now)-np.asarray(source_overlay_bboxes[n])
    if np.max(np.abs(delta-[-39.5,-22,-39.5,-22]))>.015:overlay_shift_errors.append({'object':n,'actual_delta':delta.tolist()})

checks={
    'fresh_v9_v11_opened_read_only':True,
    'source_v9_original317_objects_all_retained':len(old_names)==317 and old_names<=set(v11['objects']),
    'new_objects_exactly40_match_production_report':len(new_names)==40 and new_names==reported_new and new_names==EXPECTED_NEW,
    'allowed_existing_names_within_independent_user_scope':allowed<=KNOWN_SCOPE and changed_names<=allowed,
    'existing_object_changes_only_authorized_fields':not unexpected_object_changes and not report_allowed_field_errors,
    'newly_hidden_objects_exactly_reported_and_scoped':newly_hidden==reported_hidden and reported_hidden<=RETIRE,
    'all_original_geometry_topology_exact_including_overlays':not geometry_errors and not translation_errors,
    'existing_slots_and_indices_exact_except_kiln':not mesh_errors,
    'original_mesh_datablock_names_exact_except_optional_kiln_isolation':set(data_name_changes)<={'D2_lime_kiln'},
    'all_original_materials_preserved_except_unused_replaced_kiln_slot':len(v9['materials'])==61 and not old_material_errors,
    'new_material_HEX_linear_diffuse_and_principled_match':not new_material_errors,
    'kiln_exact_original_faces_match_independent_helper_and_palette':not kiln_errors,
    'new_meshes_visible_material_indices_valid_inside_safe_poster_bounds':not new_object_errors,
    'scene_camera_render_world_exposure_studio_and_old_collections_preserved':not scene_errors,
    'all_saved_viewport_settings_preserved':not viewport_errors,
    'all_original_parent_inverse_and_narrative_properties_preserved':not extra_errors,
    'production_before_matches_fresh_v9':not before_report_errors,
    'production_after_matches_fresh_v11':not after_report_errors,
    'fresh_mover_bboxes_and_reported_bboxes_valid':not bbox_errors,
    'all_original_and_new_face_index_SHAs_match_report':not index_report_errors,
    'applied_roles_face_counts_material_slot_order_polygon_count_match_report':not applied_report_errors,
    'material_roles_HEX_and_linear_values_match_report':not material_report_errors,
    'downloaded_Meshy_GLB_provenance_SHA_preserved':not mesh_source_errors,
    'report_object_material_totals_match_fresh_saved':len(v11['objects'])==REPORT['total_objects'] and len(v11['materials'])==REPORT['total_materials'],
    'CORE2_overlay_screen_translation_exact':not overlay_shift_errors,
    'upper_temples_exact_original_source_restored':all(v9['objects'][n]==v11['objects'][n] for n in ['L03_forum_vesta','L03_forum_temple']),
    'white_micro_fill_matches_crack_geometry_and_camera_front':physical['micro_fill']['pass'],
    'actual_stage_and_hero_BVH_surfaces_do_not_intersect':not any(x['surface_triangle_overlap_pair_count'] for x in physical['collisions']),
    'sampled_low_vertices_have_no_ground_penetration_beyond_0_002':not any(x['ground_penetration_beyond_0_002'] for x in physical['contacts']),
    'source_v9_SHA_exact_preserved':H['sha256_file'](SOURCE)==EXPECTED_V9_SHA,
    'canonical_SHA_exact_preserved':H['sha256_file'](H['SOURCE'])==EXPECTED_CANONICAL_SHA,
}
result={'pass':all(checks.values()),'checks':checks,'source':str(SOURCE),'output':str(TARGET),
 'source_sha256':H['sha256_file'](SOURCE),'output_sha256':H['sha256_file'](TARGET),'canonical_sha256':H['sha256_file'](H['SOURCE']),
 'original_object_count':len(old_names),'output_object_count':len(v11['objects']),'output_mesh_count':len(v11['meshes']),
 'new_objects':sorted(new_names),'new_materials':sorted(new_materials),'actual_material_count':len(v11['materials']),'reported_material_count':REPORT['total_materials'],'retired_unused_materials':retired_unused_materials,'changed_original_objects':sorted(changed_names),'hidden_original_objects':sorted(newly_hidden),
 'unexpected_object_changes':unexpected_object_changes,'report_allowed_field_errors':report_allowed_field_errors,'geometry_errors':geometry_errors,'translation_errors':translation_errors,
 'mesh_errors':mesh_errors,'old_material_errors':old_material_errors,'new_material_errors':new_material_errors,'kiln_errors':kiln_errors,'new_object_errors':new_object_errors,
 'scene_errors':scene_errors,'viewport_errors':viewport_errors,'extra_errors':extra_errors,'before_report_errors':before_report_errors,'after_report_errors':after_report_errors,'bbox_errors':bbox_errors,'checked_mover_bboxes':checked_bboxes,
 'index_report_errors':index_report_errors,'applied_report_errors':applied_report_errors,'material_report_errors':material_report_errors,'mesh_source_errors':mesh_source_errors,
 'physical_geometry':physical,'overlay_shift_errors':overlay_shift_errors,
 'hero_transform':{'basis_before':v9['objects']['COL_ruined']['matrix_basis'],'basis_after':v11['objects']['COL_ruined']['matrix_basis'],'relative_linear_transform':(np.asarray(v11['objects']['COL_ruined']['matrix_basis'])[:3,:3]@np.linalg.inv(np.asarray(v9['objects']['COL_ruined']['matrix_basis'])[:3,:3])).tolist()},
 'method':'Two fresh background file opens. No save, render, object/material/visibility/UI writes. Hidden matrix_world cache normalized read-only from persistent basis/parent inverse. Existing geometry/slots/indices/property and material-node snapshots compared outside independent authorized scope.'}
(OUT/'v11-saved-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Saved v11 independent read-only validation','',f"Result: {'PASS' if result['pass'] else 'FAIL'}",'',f"Original objects {len(old_names)}; output objects {len(v11['objects'])}; new objects {len(new_names)}; changed originals {len(changed_names)}.",'']
lines.extend(f"- {'PASS' if good else 'FAIL'}: {name}" for name,good in checks.items())
lines.extend(['',f"Source v9 SHA `{result['source_sha256']}`",f"Output v11 SHA `{result['output_sha256']}`",f"Canonical SHA `{result['canonical_sha256']}`",'',result['method']])
(OUT/'v11-saved-validation.md').write_text('\n'.join(lines)+'\n')
print('V11_SAVED_VALIDATION '+json.dumps({'pass':result['pass'],'checks':checks,'new_objects':len(new_names),'changed_originals':len(changed_names),'output_objects':len(v11['objects']),'error_counts':{k:len(v) for k,v in result.items() if k.endswith('_errors') or k=='unexpected_object_changes'}},ensure_ascii=False))
