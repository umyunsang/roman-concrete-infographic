import bpy,numpy as np,json,hashlib,runpy,ast
from collections import Counter
from pathlib import Path
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007');O=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/village-qa')
H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
RUNTIME={'rna_type','session_uid','is_updated','is_updated_data','is_updated_transform','is_runtime_data','is_evaluated','is_embedded_data'}
s=(O.parent/'construction-detail/verify_v11_saved.py').read_text();a=ast.parse(s)
for n in a.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['plain','scalar','world','normalize','digest','snap','diff','report_objects']:exec(ast.get_source_segment(s,n))
SOURCE=R/'out/roman_concrete_narrative_v9.blend';V11=R/'out/roman_concrete_narrative_v11.blend';P=json.loads((R/'out/construction-detail-v11.json').read_text())
source_sha_before=H['sha256_file'](SOURCE)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));now=snap()
objdiff=diff(report_objects(P['before'],now['objects']),now['objects'])
indexdiff=diff(P['indices_before'],{n:d['assignment_sha256'] for n,d in now['meshes'].items()})
bpy.ops.wm.open_mainfile(filepath=str(V11));previous=snap()
scene_current=json.loads(json.dumps(now['scene']));scene_previous=json.loads(json.dumps(previous['scene']))
old_collections=scene_current['basic']['collections'];scene_previous['basic']['collections']={k:scene_previous['basic']['collections'].get(k)for k in old_collections}
scenediff=diff(scene_previous,scene_current)+diff(previous['scene_extra'],now['scene_extra'])
viewportdiff=diff(previous['viewports'],now['viewports'])
oldmatdiff=[]
for name,m in now['materials'].items():
 if name not in previous['materials']:
  if name=='RC.v12.base_roman_support_stone':continue
  oldmatdiff.append({'path':name,'error':'material absent in previously validated savedv11 baseline'});continue
 oldmatdiff += [{'material':name,**c}for c in diff({k:v for k,v in previous['materials'][name].items() if k!='users'},{k:v for k,v in m.items() if k!='users'})]
source_sha_after=H['sha256_file'](SOURCE)
D={'source_sha_before':source_sha_before,'source_sha_after':source_sha_after,'previous_source_sha':P['source_sha256'],'saved_v11_sha':H['sha256_file'](V11),'original_canonical_sha':H['sha256_file'](H['SOURCE']),'source_stable_during_audit':source_sha_before==source_sha_after,'object_differences_against_previous_v9_snapshot':objdiff,'face_index_differences_against_previous_v9':indexdiff,'global_scene_differences_against_preserved_v11':scenediff,'viewport_differences_against_preserved_v11':viewportdiff,'old_material_differences_against_preserved_v11':oldmatdiff,'source_objects':len(now['objects']),'saved_v11_original_object_count':317,'method':'Fresh sourcev9 compared with exact productionv11 before snapshot+indices. Source global scene/UI/material properties compared with savedv11 already independently validated as preserving oldv9. Hidden runtimecache matrices normalized read-only from basis/parentinverse. Source file never written or restored.'}
(O/'source-v9-drift-validation.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
lines=['# v9 source drift audit','',f"Current SHA: {source_sha_after}",'',f"Object differences: {len(objdiff)}; faceindices: {len(indexdiff)}; globalscene: {len(scenediff)}; savedviewports: {len(viewportdiff)}; originalmaterials: {len(oldmatdiff)}.",'',D['method']]
for section in ['object_differences_against_previous_v9_snapshot','face_index_differences_against_previous_v9','global_scene_differences_against_preserved_v11','viewport_differences_against_preserved_v11','old_material_differences_against_preserved_v11']:
 for c in D[section][:25]:lines.append('- '+section+': '+json.dumps(c,ensure_ascii=False))
(O/'source-v9-drift-validation.md').write_text('\n'.join(lines)+'\n')
print('SOURCE_DRIFT '+json.dumps({k:v for k,v in D.items() if k.endswith('sha') or k.endswith('sha_before') or k.endswith('sha_after') or k=='source_stable_during_audit'},ensure_ascii=False));print('OBJECT_DIFF',json.dumps(objdiff[:40],ensure_ascii=False));print('INDEX_DIFF',json.dumps(indexdiff[:10],ensure_ascii=False));print('SCENE_DIFF',json.dumps(scenediff[:25],ensure_ascii=False));print('VIEWPORT_DIFF',json.dumps(viewportdiff[:25],ensure_ascii=False));print('MATERIAL_DIFF',json.dumps(oldmatdiff[:25],ensure_ascii=False))
