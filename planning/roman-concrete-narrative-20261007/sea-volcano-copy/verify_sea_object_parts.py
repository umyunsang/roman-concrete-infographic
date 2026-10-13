"""Read-only helper verification. Does not mutate scene, materials, UI or save/render."""
import bpy,runpy,json,hashlib,struct
from pathlib import Path
p=Path(__file__).parent
source=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007/out/roman_concrete_narrative_v8.blend')
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
before=sha(source)
h=runpy.run_path(str(p/'sea_object_parts.py'))
r=h['build_assignments'](bpy)
report={'source':str(source),'sourceSHA':before,'helperSHA':sha(p/'sea_object_parts.py'),'palette':h['PALETTE'],'objects':{},'pass':True}
for name,a in r.items():
 obj=bpy.data.objects[name];m=obj.data
 seen=[]
 for role,inds in a['faces'].items():
  assert role in h['PALETTE'] and role!=a['default']
  assert all(0<=i<len(m.polygons) for i in inds)
  seen.extend(inds)
 assert len(seen)==len(set(seen))
 counts={a['default']:len(m.polygons)-len(seen),**{role:len(inds) for role,inds in a['faces'].items()}}
 topo=hashlib.sha256()
 for v in m.vertices:topo.update(struct.pack('<3f',*v.co))
 for e in m.edges:topo.update(struct.pack('<2I',*e.vertices))
 for l in m.loops:topo.update(struct.pack('<I',l.vertex_index))
 for q in m.polygons:topo.update(struct.pack('<2I',q.loop_start,q.loop_total))
 report['objects'][name]={'verts':len(m.vertices),'polygons':len(m.polygons),'counts':counts,'notes':a['notes'],'topologySHA':topo.hexdigest(),'assignmentsSHA':hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
report['sourceSHAAfter']=sha(source)
assert report['sourceSHAAfter']==before=='d179c5abdce8a9b0b48cf3f34cad9331b61e048f2e8edef504f430cee172ef3c'
(p/'sea-object-part-assignments.json').write_text(json.dumps(r,indent=2)+'\n')
(p/'sea-object-part-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SEA_PARTS_PASS '+json.dumps({name:data['counts'] for name,data in report['objects'].items()}))
