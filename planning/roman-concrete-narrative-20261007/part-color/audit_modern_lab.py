"""Export read-only topology/geometry evidence for modern and lab part selection."""
import json
from pathlib import Path
import bpy
import numpy as np

OUT=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/part-color')
OUT.mkdir(parents=True,exist_ok=True)
report={}
arrays={}
for name in ['NB_modern_building','S_lab_island']:
 ob=bpy.data.objects[name]; mesh=ob.data; count=len(mesh.vertices)
 v=np.empty(count*3);mesh.vertices.foreach_get('co',v);v=v.reshape(-1,3)
 edge=np.empty(len(mesh.edges)*2,dtype=np.int32);mesh.edges.foreach_get('vertices',edge);edge=edge.reshape(-1,2)
 parent=np.arange(count)
 def find(a):
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 for a,b in edge:
  ra,rb=find(a),find(b)
  if ra!=rb:parent[rb]=ra
 roots=np.array([find(i) for i in range(count)])
 unique=np.unique(roots);root_order=sorted(unique,key=lambda r:-int(np.sum(roots==r)))
 idx={r:i for i,r in enumerate(root_order)}
 vi=np.array([idx[r] for r in roots],dtype=np.int32)
 starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
 totals=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_total',totals)
 loops=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',loops)
 centers=np.array([p.center[:] for p in mesh.polygons])
 normals=np.array([p.normal[:] for p in mesh.polygons])
 areas=np.array([p.area for p in mesh.polygons])
 fi=vi[loops[starts]]
 components=[]
 for i,r in enumerate(root_order):
  p=v[vi==i]; fp=np.nonzero(fi==i)[0]
  centered=p-p.mean(0)
  eig=np.linalg.eigvalsh(centered.T@centered/max(len(p),1)).tolist()
  components.append({'id':i,'vertices':len(p),'faces':len(fp),'face_indices':fp.tolist(),
   'min':p.min(0).tolist(),'max':p.max(0).tolist(),'span':np.ptp(p,axis=0).tolist(),
   'centroid':p.mean(0).tolist(),'covariance_eigenvalues':eig,'area':float(areas[fp].sum())})
 report[name]={'object':name,'matrix_world':[list(row) for row in ob.matrix_world],
  'min':v.min(0).tolist(),'max':v.max(0).tolist(),'vertices':len(v),'faces':len(fi),
  'component_count':len(components),'components':components}
 key='modern' if name=='NB_modern_building' else 'lab'
 arrays.update({key+'_vertices':v,key+'_edges':edge,key+'_face_starts':starts,key+'_face_totals':totals,
  key+'_loops':loops,key+'_centers':centers,key+'_normals':normals,key+'_areas':areas,
  key+'_vertex_components':vi,key+'_face_components':fi,key+'_matrix_world':np.array(ob.matrix_world)})
np.savez_compressed(OUT/'modern-lab-geometry.npz',**arrays)
(OUT/'modern-lab-topology.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:{x:d[x] for x in ['vertices','faces','component_count','min','max']} for k,d in report.items()}))
