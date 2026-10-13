"""Fresh saved v7/v8 validation. No data mutation, visibility toggles, render or save."""
import hashlib,json,runpy
from collections import Counter
from pathlib import Path
import bpy
import numpy as np

ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/part-color')
REPORT=json.loads((ROOT/'out/poster-part-materials-v8.json').read_text())
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
            'principled_roughness':bsdf.inputs['Roughness'].default_value if bsdf else None,'users':m.users}
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

bpy.ops.wm.open_mainfile(filepath=REPORT['input']);v7=snap()
bpy.ops.wm.open_mainfile(filepath=REPORT['output']);v8=snap()
before_match=diff(normalize(json.loads(json.dumps(REPORT['before']))),v7['objects'])
after_match=diff(normalize(json.loads(json.dumps(REPORT['after']))),v8['objects'])
object_changes=diff(v7['objects'],v8['objects'])
allowed_material_changes=[x for x in object_changes if x['path'].endswith('.materials') and x['path'].rsplit('.',1)[0] in REPORT['applied']]
unexpected_object_changes=[x for x in object_changes if x not in allowed_material_changes]
scene_changes=diff(v7['scene'],v8['scene'])
unexpected_scene_changes=[x for x in scene_changes if not (x['path']=='shading.color_type' and x['before']=='OBJECT' and x['after']=='MATERIAL')]
viewport_changes=diff(v7['viewports'],v8['viewports'])
unexpected_viewport_changes=[x for x in viewport_changes if not (x['path'].endswith('.shading.color_type') and x['after']=='MATERIAL')]
extra_changes=diff({k:v for k,v in v7.items() if k in {'raw_world','hidden_world_calculated','parent_inverse','custom_properties'}},
    {k:v for k,v in v8.items() if k in {'raw_world','hidden_world_calculated','parent_inverse','custom_properties'}})

mesh_geometry_differences=[];mesh_data_name_changes=[];wrong_applied=[];unapplied_mesh_changes=[]
for name,m7 in v7['meshes'].items():
    m8=v8['meshes'][name]
    for k in ['vertices','edges','loops','polygons','geometry_sha256','uv_layers','color_attributes','render_visible']:
        if m7[k]!=m8[k]:mesh_geometry_differences.append({'object':name,'field':k,'before':m7[k],'after':m8[k]})
    if m7['data_name']!=m8['data_name']:mesh_data_name_changes.append(name)
    if name in REPORT['applied']:
        expected=REPORT['applied'][name]
        for k in ['material_roles','face_counts','assignment_sha256']:
            if m8[k]!=expected[k]:wrong_applied.append({'object':name,'field':k,'expected':expected[k],'actual':m8[k]})
        if m8['polygons']!=expected['polygon_count'] or not m8['valid_material_indices']:wrong_applied.append({'object':name,'field':'polygon_count/index validity'})
        expected_names=[REPORT['materials'][r]['name'] for r in expected['material_roles']]
        if m8['material_names']!=expected_names:wrong_applied.append({'object':name,'field':'material_slot_names','expected':expected_names,'actual':m8['material_names']})
    elif any(m7[k]!=m8[k] for k in ['material_names','assignment_sha256']):unapplied_mesh_changes.append(name)

material_errors=[]
for role,expected in REPORT['materials'].items():
    name=expected['name'];m=v8['materials'].get(name)
    if not m:material_errors.append({'material':name,'error':'missing'});continue
    hex=expected['hex'];s=[int(hex[i:i+2],16)/255 for i in (1,3,5)]
    rgba=[float(np.float32(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)) for x in s]+[1.0]
    for k,val in [('role',role),('hex',hex),('diffuse_color',rgba),('principled_base_color',rgba),('use_nodes',True),('roughness',float(np.float32(.85))),('principled_roughness',float(np.float32(.85)))]:
        if m[k]!=val:material_errors.append({'material':name,'field':k,'expected':val,'actual':m[k]})
    if m['diffuse_color']!=expected['linear_color']:material_errors.append({'material':name,'field':'reported linear_color'})

visible_meshes=[n for n,m in v8['meshes'].items() if m['render_visible']]
multi=[n for n,m in v8['meshes'].items() if sum(x>0 for x in m['face_counts'].values())>1]
checks={
    'fresh_v7_v8_files_opened':True,
    'exact_317_objects_255_meshes_preserved':len(v7['objects'])==len(v8['objects'])==317 and set(v7['objects'])==set(v8['objects']) and len(v7['meshes'])==len(v8['meshes'])==255,
    'all_geometry_basis_parent_inverse_transforms_collections_constraints_camera_visibility_object_colors_preserved':not unexpected_object_changes and not mesh_geometry_differences and not extra_changes,
    'only_applied_material_slots_changed':len(allowed_material_changes)==227 and not unapplied_mesh_changes,
    'saved_before_report_exact_match':not before_match,
    'saved_after_report_exact_match':not after_match,
    'exact_51_materials_227_assigned_visible_meshes_36_multicolor_meshes':len(v8['materials'])==51 and set(visible_meshes)==set(REPORT['applied']) and len(visible_meshes)==227 and len(multi)==36,
    'all_reported_face_counts_slot_roles_and_assignment_sha_exact':not wrong_applied,
    'all_diffuse_and_principled_colors_match_srgb_linear_float32_palette':not material_errors,
    'only_18_reported_shared_mesh_data_isolations':set(mesh_data_name_changes)==set(REPORT['shared_data_isolated']) and len(mesh_data_name_changes)==18,
    'only_workbench_material_scene_shading_change':not unexpected_scene_changes and scene_changes==[{'path':'shading.color_type','before':'OBJECT','after':'MATERIAL'}],
    'only_existing_view3d_material_color_changes':not unexpected_viewport_changes and all(v['shading']['color_type']=='MATERIAL' for v in v8['viewports'].values()),
    'v7_source_sha_preserved':H['sha256_file'](Path(REPORT['input']))==REPORT['source_sha256'],
    'canonical_sha_preserved':H['sha256_file'](H['SOURCE'])==REPORT['canonical_sha256'],
}
result={'pass':all(checks.values()),'checks':checks,'object_count':len(v8['objects']),'mesh_count':len(v8['meshes']),
    'material_count':len(v8['materials']),'visible_assigned_mesh_count':len(visible_meshes),'multicolor_mesh_count':len(multi),
    'shared_data_isolated_count':len(mesh_data_name_changes),'shared_data_isolated':mesh_data_name_changes,
    'v7_sha256':H['sha256_file'](Path(REPORT['input'])),'v8_sha256':H['sha256_file'](Path(REPORT['output'])),'canonical_sha256':H['sha256_file'](H['SOURCE']),
    'scene_changes':scene_changes,'viewport_changes':viewport_changes,'unexpected_object_changes':unexpected_object_changes,
    'unexpected_scene_changes':unexpected_scene_changes,'unexpected_viewport_changes':unexpected_viewport_changes,
    'unexpected_extra_changes':extra_changes,'geometry_differences':mesh_geometry_differences,
    'report_before_mismatches':before_match,'report_after_mismatches':after_match,'wrong_applied_materials':wrong_applied,
    'unapplied_mesh_changes':unapplied_mesh_changes,'material_errors':material_errors,
    'saved_materials':v8['materials'],'saved_object_material_assignments':{n:v8['meshes'][n] for n in REPORT['applied']},
    'hidden_world_calculated':v8['hidden_world_calculated'],
    'method':'Two fresh background file opens. Exact vertices/edges/loops/poly topology mesh hashes, matrices and persisted settings; hidden world matrices calculated read-only from basis and parent inverse. No scene/visibility/material/UI changes, save or render.'}
(OUT/'v8-saved-material-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# v8 부위 재질 저장본 검증','',f"결과: {'PASS' if result['pass'] else 'FAIL'}",'',
    'v7와 v8를 fresh background open으로 각각 읽고 비교했다. 씬·가시성·재질·UI를 수정하지 않았고 저장·렌더하지 않았다.','',
    f"317객체/255메시, 실제 재질 {len(v8['materials'])}개, 렌더 표시 메시 {len(visible_meshes)}개, 2개 이상 색을 쓰는 메시 {len(multi)}개.",
    f"공유 mesh data 분리는 실제 {len(mesh_data_name_changes)}개이며 production 리포트 목록과 대조했다.",'','## 체크','']
lines.extend(f"- {'PASS' if b else 'FAIL'}: {k}" for k,b in checks.items())
lines.extend(['','## 검증 범위','',
    '- vertices/edges/loops/polygon topology 해시, basis/world/parent inverse, 부모·컬렉션·제약·카메라·가시성·object color를 비교했다.',
    '- material slots와 polygon material_index만 메시별 허용 변경이다. 분리된 공유 mesh data도 이름 변경 외 geometry가 같은지 확인했다.',
    '- 모든 227메시의 material role 순서, 슬롯 이름, role별 면 수, 원본 순서의 uint16 material_index SHA를 적용 리포트와 대조했다.',
    '- 모든 51재질의 HEX를 독립적으로 linear float32로 변환하여 diffuse_color와 Principled Base Color 및 메타데이터를 대조했다.',
    '- Studio/shadow/cavity/outline/exposure/world/background/resolution은 보존 비교 대상이다. Scene Workbench OBJECT→MATERIAL 및 기존 VIEW_3D color_type→MATERIAL만 표시 방식의 허용 변경이다.',
    '- 숨김 원본 16개의 identity world cache는 basis/parent inverse에서 읽기 계산했다. raw cache와 persistent parent inverse도 v7/v8 사이에서 비교했다.',
    '', '## SHA256','',f"- v7: `{result['v7_sha256']}`",f"- v8: `{result['v8_sha256']}`",f"- canonical: `{result['canonical_sha256']}`"])
lines.extend(['','## 검증 스크립트 점검 기록','',
    '첫 실행의 JSON 출력에서 VIEW_3D clip_planes의 중첩 bpy_prop_array 직렬화가 실패했다. RNA 배열을 재귀적으로 일반 목록으로 변환한 뒤 다시 비교했다. 제작 파일이나 UI를 변경하지 않았다.',
    'World/Material.use_nodes 제거 예정과 wireframe_color_type enum0 경고는 읽기 중 출력됐으며 허용 변경과 구분했다.'])
if not result['pass']:lines.extend(['','상세 불일치는 JSON에 남겼고 제작 파일을 자동 수정하지 않았다.'])
(OUT/'v8-saved-material-validation.md').write_text('\n'.join(lines)+'\n')
print('V8_SAVED_MATERIAL_VALIDATION',json.dumps({'pass':result['pass'],'checks':checks,'material_count':len(v8['materials']),
    'unexpected_object_changes':len(unexpected_object_changes),'unexpected_scene_changes':len(unexpected_scene_changes),
    'unexpected_viewport_changes':len(unexpected_viewport_changes),'geometry_differences':len(mesh_geometry_differences),
    'report_before_mismatches':len(before_match),'report_after_mismatches':len(after_match),'material_errors':len(material_errors)},ensure_ascii=False))
