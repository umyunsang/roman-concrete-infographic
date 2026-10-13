import bpy,json,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
h=runpy.run_path(str(root/'scripts/integrate_assets.py'),run_name='helpers')
r=json.loads((root/'out/integration-report-v4.json').read_text())
draft=h['source_fingerprints']([bpy.data.objects[n] for n in r['source_object_names']])
scene=h['scene_fingerprint'](bpy.context.scene)
bpy.ops.wm.open_mainfile(filepath=str(h['SOURCE']))
source=h['source_fingerprints'](list(bpy.data.objects))
def diff(a,b,path=''):
 if type(a)!=type(b):return [(path,a,b)]
 if isinstance(a,dict):
  rows=[]
  for k in a.keys()|b.keys():
   if k not in a or k not in b:rows.append((path+'.'+str(k),a.get(k),b.get(k)))
   else:rows.extend(diff(a[k],b[k],path+'.'+str(k)))
  return rows
 if isinstance(a,list):
  if len(a)!=len(b):return [(path,a,b)]
  return [r for i,(x,y) in enumerate(zip(a,b)) for r in diff(x,y,path+f'[{i}]')]
 return [] if a==b else [(path,a,b)]
changes=[]
for name in source:
 a,b=dict(source[name]),dict(draft[name])
 if name in r['allowed_visibility_changes']:
  for field in ['hide_render','hide_viewport']:a.pop(field);b.pop(field)
 changes.extend(diff(a,b,name))
result={'changes':changes,'source_count':len(source),'draft_scene_changes':diff(r['saved_scene_fingerprint'],scene),'draft_raw_snapshot_sha256':h['json_hash'](draft),'source_raw_snapshot_sha256':h['json_hash'](source)}
(root/'out/reload-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('RELOAD_DIFF',json.dumps(result,ensure_ascii=False))
