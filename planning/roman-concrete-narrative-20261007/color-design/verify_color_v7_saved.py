"""Fresh v6/v7 audit; no save, render, UI or scene-data mutations."""
import hashlib
import json
import runpy
from pathlib import Path
import bpy
import numpy as np

ROOT=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/color-design')
report=json.loads((ROOT/'out/poster-color-v7.json').read_text())
palette=json.loads((ROOT/'copy/color_system_v11.json').read_text())
h=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
RUNTIME={'rna_type','session_uid','is_updated','is_updated_data','is_updated_transform','is_runtime_data','is_evaluated','is_embedded_data'}

def scalar(obj):
    out={}
    for p in obj.bl_rna.properties:
        if p.identifier in RUNTIME or p.type in {'POINTER','COLLECTION'}:continue
        try:
            v=getattr(obj,p.identifier)
            if p.type=='ENUM':v=str(v)
            if getattr(p,'is_array',False):v=list(v)
            if isinstance(v,(str,bool,int,float,list)):out[p.identifier]=v
        except (TypeError,AttributeError,RuntimeError):pass
    return out

def world_state(w):
    if not w:return None
    result={'properties':scalar(w),'nodes':{},'links':[]}
    if w.use_nodes:
        for n in w.node_tree.nodes:
            inputs={}
            for i in n.inputs:
                if not hasattr(i,'default_value'):continue
                v=i.default_value
                if hasattr(v,'__len__') and not isinstance(v,str):v=list(v)
                if isinstance(v,(str,bool,int,float,list)):inputs[i.name]=v
            result['nodes'][n.name]={'properties':scalar(n),'inputs':inputs}
        result['links']=[(x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name) for x in w.node_tree.links]
    return result

def normalize_snapshot(snapshot):
    for x in snapshot.values():
        if 'camera_data' in x:x['camera_data'].pop('session_uid',None)
    return snapshot

def snap():
    # Updating the dependency graph reads and computes current transforms; no visibility toggling.
    bpy.context.view_layer.update()
    objects=normalize_snapshot(h['source_fingerprints'](list(bpy.data.objects)))
    raw_world={n:x['matrix_world'] for n,x in objects.items()}
    computed_hidden=[]
    world_cache={}
    def persistent_world(ob):
        if ob.name in world_cache:return world_cache[ob.name]
        if not ob.hide_viewport:
            matrix=ob.matrix_world.copy()
        else:
            if ob.constraints:raise RuntimeError(('Hidden constrained object needs another read-only method',ob.name))
            matrix=ob.matrix_basis.copy()
            if ob.parent:
                if ob.parent_type!='OBJECT':raise RuntimeError(('Non-object parent',ob.name))
                matrix=persistent_world(ob.parent) @ ob.matrix_parent_inverse @ matrix
        world_cache[ob.name]=matrix
        return matrix
    for ob in bpy.data.objects:
        if ob.hide_viewport:
            calculated=[list(row) for row in persistent_world(ob)]
            if calculated!=objects[ob.name]['matrix_world']:computed_hidden.append(ob.name)
            objects[ob.name]['matrix_world']=calculated
    scene=bpy.context.scene
    return {'objects':objects,'render':scalar(scene.render),'display':scalar(scene.display),
        'shading':scalar(scene.display.shading),'view':scalar(scene.view_settings),
        'display_settings':scalar(scene.display_settings),'world':world_state(scene.world),
        'scene_basic':h['scene_fingerprint'](scene),
        'raw_world_cache':raw_world,'computed_hidden_world_names':sorted(computed_hidden),
        'persistent_parent_inverse':{o.name:[list(row) for row in o.matrix_parent_inverse] for o in bpy.data.objects},
        'custom_properties':{o.name:{k:o[k] for k in o.keys() if k.startswith('narrative_')} for o in bpy.data.objects},
        'mesh_attributes':{o.name:{'color_attributes':[(x.name,x.domain,x.data_type) for x in o.data.color_attributes],
            'uv_layers':[x.name for x in o.data.uv_layers],
            'poly_material_index_sha256':hashlib.sha256(np.array([x.material_index for x in o.data.polygons],dtype=np.int32).tobytes()).hexdigest()}
            for o in bpy.data.objects if o.type=='MESH'}}

def nested_diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            p=path+'.'+key if path else key
            if key not in a or key not in b:out.append({'path':p,'before':a.get(key),'after':b.get(key)})
            else:out.extend(nested_diff(a[key],b[key],p))
        return out
    return [] if a==b else [{'path':path,'before':a,'after':b}]

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=report['input'])
v6=snap()
bpy.ops.wm.open_mainfile(filepath=report['output'])
v7=snap()
before_report=normalize_snapshot(json.loads(json.dumps(report['before'])))
after_report=normalize_snapshot(json.loads(json.dumps(report['after'])))

object_diff=nested_diff(v6['objects'],v7['objects'])
changed={x['path'].rsplit('.',1)[0] for x in object_diff if x['path'].endswith('.color')}
allowed_object_diff=[x for x in object_diff if x['path'].endswith('.color') and x['path'].rsplit('.',1)[0] in report['color_assignments']]
unexpected_object_diff=[x for x in object_diff if x not in allowed_object_diff]
other_diff=nested_diff({k:v for k,v in v6.items() if k!='objects'},{k:v for k,v in v7.items() if k!='objects'})
allowed_scene_paths={'view.exposure','shading.background_type','world.properties.color','world.nodes.Background.inputs.Color'}
unexpected_scene_diff=[x for x in other_diff if x['path'] not in allowed_scene_paths]
before_match=nested_diff(before_report,v6['objects'])
after_match=nested_diff(after_report,v7['objects'])
expected_assignments={name:[float(np.float32(v)) for v in assignment['linear_rgb']]+[1.0] for name,assignment in report['color_assignments'].items()}
wrong_colors=[name for name,rgba in expected_assignments.items() if rgba!=v7['objects'][name]['color']]
hex_background=palette['tokens']['background'].lstrip('#')
srgb=[int(hex_background[i:i+2],16)/255 for i in (0,2,4)]
linear=[float(np.float32(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)) for x in srgb]
checks={
 'fresh_v6_and_v7_opened':True,
 'all_317_object_names_and_types_preserved':set(v6['objects'])==set(v7['objects']) and len(v6['objects'])==317 and all(v6['objects'][n]['type']==v7['objects'][n]['type'] for n in v6['objects']),
 'geometry_transforms_camera_visibility_modifiers_constraints_materials_preserved':not unexpected_object_diff,
 'exact_227_only_color_changes':len(allowed_object_diff)==227 and changed==set(report['color_assignments']),
 'saved_colors_exactly_match_declared_linear_rgb_float32':not wrong_colors,
 'source_report_before_matches_fresh_v6':not before_match,
 'source_report_after_matches_fresh_v7':not after_match,
 'all_other_render_shading_color_management_world_settings_preserved':not unexpected_scene_diff,
 'saved_exposure_matches_palette_float32':v7['view']['exposure']==float(np.float32(palette['colorManagement']['exposure'])),
 'saved_background_type_world':v7['shading']['background_type']=='WORLD',
 'world_color_matches_background_palette':v7['world']['properties']['color']==linear,
 'world_background_node_color_matches_background_palette':v7['world']['nodes']['Background']['inputs']['Color']==linear+[1.0],
 'v6_source_bytes_unchanged':h['sha256_file'](Path(report['input']))==report['input_sha256'],
 'canonical_original_bytes_unchanged':h['sha256_file'](h['SOURCE'])==report['original_source_sha256'],
}
result={'pass':all(checks.values()),'checks':checks,'v6_sha256':h['sha256_file'](Path(report['input'])),
    'v7_sha256':h['sha256_file'](Path(report['output'])),'canonical_original_sha256':h['sha256_file'](h['SOURCE']),
    'object_count':len(v6['objects']),'mesh_count':len(v6['mesh_attributes']),
    'color_changed_count':len(allowed_object_diff),'unchanged_color_count':len(v6['objects'])-len(allowed_object_diff),
    'object_snapshot_v6_sha256':digest(v6['objects']),'object_snapshot_v7_sha256':digest(v7['objects']),
    'allowed_scene_changes':other_diff,'unexpected_object_changes':unexpected_object_diff,
    'unexpected_scene_changes':unexpected_scene_diff,'report_before_mismatches':before_match,
    'report_after_mismatches':after_match,'wrong_saved_palette_colors':wrong_colors,
    'saved_shading':v7['shading'],'saved_render':v7['render'],'saved_view':v7['view'],
    'hidden_world_matrix_computed_from_persistent_basis_and_parent_inverse':v7['computed_hidden_world_names'],
    'correction_D4_crack':{'type':v7['objects']['D4_crack']['type'],'message':'Earlier prose called this a MESH. Actual inventory and fresh files show EMPTY parent; no geometry is rendered by this parent.'},
    'method':'Two fresh file opens within background Blender, scalar snapshots and exact mesh/transform comparison. Hidden object runtime world caches can remain identity after opening, so report matching uses world matrices calculated from persistent basis/parent inverse; raw caches and parent inverses are also compared. No visibility toggles, save, render, UI or scene mutation.'}
OUT.mkdir(exist_ok=True)
(OUT/'v7-saved-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# 컬러 v7 저장본 검증','',f"결과: {'PASS' if result['pass'] else 'FAIL'}",'',
 'v6와 v7를 별도로 새로 열어 비교했다. Blender 파일·UI·씬·가시성 변경과 저장·렌더를 수행하지 않았다.','',
 '## 체크','']
lines.extend(f"- {'PASS' if passed else 'FAIL'}: {name}" for name,passed in checks.items())
lines.extend(['','## 저장본 비교','',f"- 객체 {result['object_count']}개와 메시 {result['mesh_count']}개.",
 f"- 색만 변경된 객체 {result['color_changed_count']}개; 다른 {result['unchanged_color_count']}개 객체의 색은 동일.",
 '- 카메라·지형·콜로세움과 모든 객체의 메시·변환·가시성·부모·컬렉션·모디파이어·제약·재질을 비교했다.',
 '- 예외로 허용한 설정: view.exposure(+0.7), shading.background_type(WORLD), World.color와 World.Background node의 Color(동일 팔레트 배경색).',
 '- Studio light, 그림자, cavity, outline, 해상도 및 기타 렌더 설정은 비교 대상이다.',
 '- 숨김 원본 16개의 matrix_world는 새 로드에서 identity 캐시로 남는다. 씬을 수정하지 않고 persistent matrix_basis와 parent inverse로 world를 계산해 before/after 리포트와 비교했다. 이 16개의 raw 캐시도 v6/v7 사이에서 동일하고 basis·parent inverse·부모·실제 메시는 정확히 동일하다.',
 '', '## 정정','',
 '`D4_crack`는 EMPTY 부모이며 메시가 아니다. 앞선 scene-color-inventory.md와 메시 전달에서 이를 visible MESH라고 쓴 부분을 정정한다. 기존 JSON의 type=EMPTY는 정확했다. 원본 균열 모델 자식 13개의 부모이며, 이번 배색 객체 227개 목록에 이 EMPTY는 포함되지 않는다.',
 '', '## SHA256','',f"- v6: `{result['v6_sha256']}`",f"- v7: `{result['v7_sha256']}`",f"- canonical original: `{result['canonical_original_sha256']}`"])
lines.extend(['','## 검증 스크립트 점검 기록','',
 '첫 실행에서 enum RNA에는 is_array가 없어서 background_type 추출이 누락되어 KeyError가 발생했다. getattr 기본값을 사용하는 수집기로 수정한 뒤 다시 실행했다. Blender 저장본은 쓰지 않았다.',
 'World.use_nodes 제거 예정 경고와 wireframe_color_type enum0 경고는 읽기 과정에서 나타났다. 비교 결과의 허용 변경 목록과는 관계없다.'])
if not result['pass']:
    lines.extend(['','## 검증 차이','', '상세 차이는 v7-saved-validation.json을 확인한다. 자동으로 변경하거나 재저장하지 않았다.'])
(OUT/'v7-saved-validation.md').write_text('\n'.join(lines)+'\n')
print('V7_SAVED_VALIDATION',json.dumps({'pass':result['pass'],'checks':checks,'color_changed_count':len(allowed_object_diff),
    'unexpected_object_changes':len(unexpected_object_diff),'unexpected_scene_changes':len(unexpected_scene_diff),
    'report_before_mismatches':len(before_match),'report_after_mismatches':len(after_match)},ensure_ascii=False))
