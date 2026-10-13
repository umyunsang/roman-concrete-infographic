"""Verify a freshly reopened draft against a freshly reopened canonical source.
Hidden viewport objects need temporary evaluation to populate matrix_world.
Camera session_uid is a runtime identifier, excluded from persisted comparison.
No blend file is saved by this script.
"""
import json,runpy
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]
h=runpy.run_path(str(root/'scripts/integrate_assets.py'),run_name='helpers')
report=json.loads((root/'out/integration-report-v4.json').read_text())
draft_path=bpy.data.filepath

def settled_fingerprints(objects):
 states={o.name:o.hide_viewport for o in objects}
 try:
  for ob in objects:ob.hide_viewport=False
  bpy.context.view_layer.update()
  result=h['source_fingerprints'](objects)
  for name,record in result.items():
   record['hide_viewport']=states[name]
   if 'camera_data' in record:record['camera_data'].pop('session_uid',None)
  return result
 finally:
  for ob in objects:ob.hide_viewport=states[ob.name]
  bpy.context.view_layer.update()

objects=[bpy.data.objects[name] for name in report['source_object_names']]
actual=settled_fingerprints(objects)
assert h['scene_fingerprint'](bpy.context.scene)==report['saved_scene_fingerprint'], 'Saved scene settings mismatch'
assert not any('FIT_PROXY' in o.name for o in bpy.data.objects), 'Temporary fit proxy persisted'
asset_bbox_checks=[]
for asset in report['assets']:
 ob=bpy.data.objects[asset['object']]
 names=asset['visible_gray_copy_groups'] or [ob.name]+[i['object'] for i in asset['illustrative_lime_inclusions']]
 boxes=[h['screen_bbox'](bpy.data.objects[n]) for n in names]
 box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
 assert max(abs(a-b) for a,b in zip(box,asset['projected_bbox']))<.01, asset['id']+' saved bbox differs'
 asset_bbox_checks.append({'id':asset['id'],'projected_bbox':box})
bpy.ops.wm.open_mainfile(filepath=str(h['SOURCE']))
expected=settled_fingerprints(list(bpy.data.objects))
assert set(expected)==set(actual), 'Original object names differ'
changes=[]
for name in expected:
 a,b=dict(expected[name]),dict(actual[name])
 if name in report['allowed_visibility_changes']:
  for key in ['hide_render','hide_viewport']:a.pop(key,None);b.pop(key,None)
 if a!=b:changes.append(name)
assert not changes, 'Saved original properties differ: '+str(changes)
assert h['sha256_file'](h['SOURCE'])==report['source_sha256'], 'Original bytes changed'
result={'fresh_reload_verified':True,'source_object_count':len(expected),'source_bytes_preserved':True,'original_mesh_topology_transforms_colors_camera_constraints_preserved':True,'allowed_visibility_changes':report['allowed_visibility_changes'],'all_new_assets_present':True,'new_asset_saved_bboxes_verified':asset_bbox_checks,'temporary_fit_proxy_count':0,'draft':draft_path,'verification_method':'Fresh canonical and draft comparison; hidden viewport objects temporarily evaluated and restored; runtime camera session_uid excluded'}
(root/'out/saved-draft-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('SAVED_DRAFT_VALIDATION',json.dumps(result,ensure_ascii=False))
