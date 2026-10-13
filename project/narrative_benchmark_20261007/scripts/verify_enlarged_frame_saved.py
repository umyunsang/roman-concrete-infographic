"""Read-only fresh v5/v4 comparison: only modern-frame transform may differ."""
import json,runpy
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]
h=runpy.run_path(str(root/'scripts/integrate_assets.py'),run_name='helpers')
report=json.loads((root/'out/modern-frame-enlargement-v5.json').read_text())
assert Path(bpy.data.filepath)==Path(report['output'])
def snap():
 states={o.name:o.hide_viewport for o in bpy.data.objects}
 try:
  for o in bpy.data.objects:o.hide_viewport=False
  bpy.context.view_layer.update()
  result=h['source_fingerprints'](list(bpy.data.objects))
  for name,item in result.items():
   item['hide_viewport']=states[name]
   if 'camera_data'in item:item['camera_data'].pop('session_uid',None)
  return result
 finally:
  for o in bpy.data.objects:o.hide_viewport=states[o.name]
  bpy.context.view_layer.update()
v5=snap();scene5=h['scene_fingerprint'](bpy.context.scene)
newbox=h['screen_bbox'](bpy.data.objects['NB_modern_building'])
assert max(abs(a-b)for a,b in zip(newbox,report['new_projected_bbox']))<.01
bpy.ops.wm.open_mainfile(filepath=report['input'])
v4=snap();assert set(v4)==set(v5)
changed=[]
for name in v4:
 a,b=dict(v4[name]),dict(v5[name])
 if name=='NB_modern_building':
  for key in ['matrix_world','matrix_basis']:a.pop(key);b.pop(key)
 if a!=b:changed.append(name)
assert not changed,changed
assert scene5==h['scene_fingerprint'](bpy.context.scene)
result={'fresh_reload_verified':True,'only_modern_frame_transform_changed':True,'all_other_objects_preserved':len(v4)-1,'same_camera_and_scene_flags':True,'saved_bbox':newbox,'object_count':len(v4),'original_source_sha256':h['sha256_file'](h['SOURCE'])}
assert result['original_source_sha256']==report['original_source_sha256']
(root/'out/enlarged-frame-saved-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('ENLARGED_FRAME_SAVED_VALIDATION',json.dumps(result,ensure_ascii=False))
