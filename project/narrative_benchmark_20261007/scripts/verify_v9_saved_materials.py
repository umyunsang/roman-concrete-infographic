"""Fresh saved v8/v9 validation. No data mutation, visibility toggles, render or save."""
import hashlib,json,runpy
from collections import Counter
from pathlib import Path
import bpy
import numpy as np

ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/sea-volcano-copy')
REPORT=json.loads((ROOT/'out/poster-sea-volcano-v9.json').read_text())
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
        counts=dict(Counter(role_indices[int(i)] for i in indices)) if role_indices and valid else {}
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
        'custom_properties':{o.name:{k:o[k] for k in o.keys() if k.startswith('narrative_')} for o in bpy.data.objects}}

def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for k in sorted(set(a)|set(b)):
            p=path+'.'+k if path else k
            if k not in a or k not in b:out.append({'path':p,'before':a.get(k),'after':b.get(k)})
            else:out.extend(diff(a[k],b[k],p))
        return out
    return [] if a==b else [{'path':path,'before':a,'after':b}]

TARGETS={'L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','NB_marine_breakwater','L07_vesuvius'}
assert set(REPORT['applied'])==TARGETS
bpy.ops.wm.open_mainfile(filepath=REPORT['input']);v8=snap()
bpy.ops.wm.open_mainfile(filepath=REPORT['output']);v9=snap()
before_match=diff(normalize(json.loads(json.dumps(REPORT['before']))),v8['objects'])
after_match=diff(normalize(json.loads(json.dumps(REPORT['after']))),v9['objects'])
object_changes=diff(v8['objects'],v9['objects'])
allowed_material_changes=[x for x in object_changes if x['path'].endswith('.materials') and x['path'].rsplit('.',1)[0] in TARGETS]
unexpected_object_changes=[x for x in object_changes if x not in allowed_material_changes]
scene_changes=diff(v8['scene'],v9['scene'])
viewport_changes=diff(v8['viewports'],v9['viewports'])
extra_changes=diff({k:v for k,v in v8.items() if k in {'raw_world','hidden_world_calculated','parent_inverse','custom_properties'}},
 {k:v for k,v in v9.items() if k in {'raw_world','hidden_world_calculated','parent_inverse','custom_properties'}})
mesh_geometry_differences=[];mesh_data_name_changes=[];wrong_applied=[];nontarget_changes=[];index_report_mismatches=[]
for name,m8 in v8['meshes'].items():
 m9=v9['meshes'][name]
 for key in ['vertices','edges','loops','polygons','geometry_sha256','uv_layers','color_attributes','render_visible']:
  if m8[key]!=m9[key]:mesh_geometry_differences.append({'object':name,'field':key,'before':m8[key],'after':m9[key]})
 if m8['data_name']!=m9['data_name']:mesh_data_name_changes.append(name)
 if name in TARGETS:
  expected=REPORT['applied'][name]
  for key in ['material_roles','face_counts','assignment_sha256']:
   if m9[key]!=expected[key]:wrong_applied.append({'object':name,'field':key,'expected':expected[key],'actual':m9[key]})
  if m9['polygons']!=expected['polygon_count'] or not m9['valid_material_indices']:wrong_applied.append({'object':name,'field':'polygon_count/index validity'})
  expected_names=[REPORT['materials'][role]['name'] for role in expected['material_roles']]
  if m9['material_names']!=expected_names:wrong_applied.append({'object':name,'field':'material_slot_names','expected':expected_names,'actual':m9['material_names']})
 else:
  changed=diff(m8,m9)
  if changed:nontarget_changes.append({'object':name,'changes':changed})
 for source,reportkey,m in [('v8','indices_before',m8),('v9','indices_after',m9)]:
  if m['assignment_sha256']!=REPORT[reportkey][name]:index_report_mismatches.append({'object':name,'source':source})
old_material_errors=[]
for name,m8 in v8['materials'].items():
 m9=v9['materials'].get(name)
 if m9 is None:old_material_errors.append({'material':name,'field':'missing'});continue
 state8={k:v for k,v in m8.items() if k!='users'};state9={k:v for k,v in m9.items() if k!='users'}
 for mismatch in diff(state8,state9):old_material_errors.append({'material':name,'mismatch':mismatch})
material_errors=[]
for role,expected in REPORT['materials'].items():
 name=expected['name'];m=v9['materials'].get(name)
 if not m:material_errors.append({'material':name,'error':'missing'});continue
 hex=expected['hex'];srgb=[int(hex[i:i+2],16)/255 for i in (1,3,5)]
 rgba=[float(np.float32(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)) for x in srgb]+[1.0]
 for key,value in [('role',role),('hex',hex),('diffuse_color',rgba),('principled_base_color',rgba),('use_nodes',True),('roughness',float(np.float32(.85))),('principled_roughness',float(np.float32(.85)))]:
  if m[key]!=value:material_errors.append({'material':name,'field':key,'expected':value,'actual':m[key]})
 if m['diffuse_color']!=expected['linear_color']:material_errors.append({'material':name,'field':'reported linear_color'})
new_names=set(v9['materials'])-set(v8['materials'])
expected_names={m['name'] for m in REPORT['materials'].values()}
checks={
 'fresh_v8_v9_files_opened':True,
 'exact_317_objects_255_meshes_preserved':len(v8['objects'])==len(v9['objects'])==317 and set(v8['objects'])==set(v9['objects']) and len(v8['meshes'])==len(v9['meshes'])==255 and set(v8['meshes'])==set(v9['meshes']),
 'all_geometry_transforms_camera_visibility_object_colors_parent_inverse_custom_properties_preserved':not unexpected_object_changes and not mesh_geometry_differences and not extra_changes,
 'only_exact_five_target_object_material_slots_changed':len(allowed_material_changes)==5 and {x['path'].rsplit('.',1)[0] for x in allowed_material_changes}==TARGETS,
 'exact_250_nontarget_mesh_data_names_material_slots_roles_indices_counts_preserved':len(set(v8['meshes'])-TARGETS)==250 and not nontarget_changes,
 'all_scene_render_display_shading_world_exposure_settings_exact':not scene_changes,
 'all_saved_viewport_settings_exact':not viewport_changes,
 'existing_51_materials_colors_principled_nodes_links_metadata_exact_except_users':len(v8['materials'])==51 and not old_material_errors,
 'exact_10_new_61_total_reported_materials':len(v9['materials'])==61 and len(REPORT['materials'])==10 and new_names==expected_names and REPORT['new_material_count']==10 and REPORT['total_material_count']==61,
 'all_five_target_slot_roles_face_counts_uint16_assignment_shas_exact':not wrong_applied,
 'all_255_reported_before_after_index_shas_exact':not index_report_mismatches,
 'new_10_material_hex_linear_float32_diffuse_principled_roughness_correct':not material_errors,
 'only_reported_shared_mesh_data_isolations':set(mesh_data_name_changes)==set(REPORT['shared_data_isolated']) and set(mesh_data_name_changes)<=TARGETS,
 'production_before_report_matches_fresh_v8':not before_match,
 'production_after_report_matches_fresh_v9':not after_match,
 'v8_source_sha_preserved':H['sha256_file'](Path(REPORT['input']))==REPORT['source_sha256'],
 'canonical_sha_preserved':H['sha256_file'](H['SOURCE'])==REPORT['canonical_sha256'],
}
result={'pass':all(checks.values()),'checks':checks,'object_count':len(v9['objects']),'mesh_count':len(v9['meshes']),
 'material_count':len(v9['materials']),'existing_material_count':len(v8['materials']),'new_material_count':len(new_names),
 'target_count':len(TARGETS),'nontarget_mesh_count':len(set(v8['meshes'])-TARGETS),
 'v8_sha256':H['sha256_file'](Path(REPORT['input'])),'v9_sha256':H['sha256_file'](Path(REPORT['output'])),'canonical_sha256':H['sha256_file'](H['SOURCE']),
 'unexpected_object_changes':unexpected_object_changes,'geometry_differences':mesh_geometry_differences,
 'scene_changes':scene_changes,'viewport_changes':viewport_changes,'extra_changes':extra_changes,
 'nontarget_mesh_changes':nontarget_changes,'old_material_errors':old_material_errors,'new_material_errors':material_errors,
 'wrong_applied_materials':wrong_applied,'index_report_mismatches':index_report_mismatches,
 'before_report_mismatches':before_match,'after_report_mismatches':after_match,'shared_mesh_data_isolated':mesh_data_name_changes,
 'target_saved_assignments':{n:v9['meshes'][n] for n in sorted(TARGETS)},
 'old_material_user_changes':{n:{'v8':v8['materials'][n]['users'],'v9':v9['materials'][n]['users']} for n in v8['materials'] if v8['materials'][n]['users']!=v9['materials'][n]['users']},
 'hidden_world_calculated':v9['hidden_world_calculated'],
 'method':'Two fresh background file opens, no save/render/visibility/material/UI mutation. Hidden cached matrix_world is normalized read-only using matrix_basis and parent inverse. Exact geometry hashes, persisted scene and viewport RNA, slots and uint16 face-index hashes. Existing material Principled node inputs/properties and links compared except material users.'}
(OUT/'v9-saved-material-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# v9 바다·화산 부위 재질 저장본 검증','',f"결과: {'PASS' if result['pass'] else 'FAIL'}",'',
 'v8/v9 저장본을 각각 fresh background open으로 읽었다. 씬·가시성·재질·UI를 수정하지 않았고 저장·렌더하지 않았다.','',
 f"317객체/255메시, 기존51재질 유지 + 새10재질 =61재질. target5개, nontarget250메시.",'','## 체크','']
lines.extend(f"- {'PASS' if good else 'FAIL'}: {name}" for name,good in checks.items())
lines.extend(['','## 범위','',
 '- 모든317객체의 geometry/basis/world/parent/constraint/collection/camera/visibility/object color와255메시의 topology/UV/color attribute를 비교했다.',
 '- 기존51재질의 diffuse/Principled base color/roughness와 node properties/inputs/links/role/HEX를 대조했다. material users만 허용한다.',
 '- nontarget250메시는 mesh data name, material slot order/role/face count/material_index uint16 SHA를 포함해 전체 snapshot이 같아야 한다.',
 '- 다섯 target은 production report의 role 순서, polygon count, 실제 role별 face count, material slot 이름, index SHA를 대조했다.',
 '- 새10재질의 HEX를 독립 linear float32로 변환해 diffuse_color/Principled Base Color와 roughness .85를 확인했다.',
 '- 숨김 객체의 identity world cache는 basis/parent inverse를 읽어 계산하며 viewport를 일시 켜지 않는다. raw cache와 parent inverse도 별도로 보존 비교한다.',
 '', '## SHA256','',f"- v8: `{result['v8_sha256']}`",f"- v9: `{result['v9_sha256']}`",f"- canonical: `{result['canonical_sha256']}`"])
if not result['pass']:lines.extend(['','상세 차이는 JSON에 기록했으며 생산 파일을 자동 수정하지 않았다.'])
(OUT/'v9-saved-material-validation.md').write_text('\n'.join(lines)+'\n')
print('V9_SAVED_MATERIAL_VALIDATION',json.dumps({'pass':result['pass'],'checks':checks,
 'objects':len(v9['objects']),'meshes':len(v9['meshes']),'materials':len(v9['materials']),
 'unexpected_object_changes':len(unexpected_object_changes),'geometry_differences':len(mesh_geometry_differences),
 'scene_changes':len(scene_changes),'viewport_changes':len(viewport_changes),'nontarget_mesh_changes':len(nontarget_changes),
 'old_material_errors':len(old_material_errors),'new_material_errors':len(material_errors),
 'before_report_mismatches':len(before_match),'after_report_mismatches':len(after_match)},ensure_ascii=False))
