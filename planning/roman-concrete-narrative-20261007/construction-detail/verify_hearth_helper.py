import bpy,runpy,json,hashlib
from pathlib import Path
P=Path(__file__).parent
R=Path('/Users/um-yunsang/Documents/로마콘크리트_3D/narrative_benchmark_20261007')
H=runpy.run_path(str(R/'scripts/integrate_assets.py'),run_name='helpers')
source=Path(bpy.data.filepath)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(source);obj=bpy.data.objects['D2_lime_kiln'];geom=H['mesh_fingerprint'](obj.data);matindices=[p.material_index for p in obj.data.polygons];materialnames=[m.name for m in obj.data.materials];matrix=[list(row) for row in obj.matrix_basis]
h=runpy.run_path(str(P/'hearth_object_parts.py'));a=h['build_assignments'](bpy);r=a[obj.name];seen=[i for ids in r['faces'].values() for i in ids]
assert len(seen)==len(set(seen)) and all(0<=i<len(obj.data.polygons) for i in seen)
assert H['mesh_fingerprint'](obj.data)==geom
assert [p.material_index for p in obj.data.polygons]==matindices and [m.name for m in obj.data.materials]==materialnames
assert [list(row) for row in obj.matrix_basis]==matrix and sha(source)==before
counts={r['default']:len(obj.data.polygons)-len(seen),**{k:len(v) for k,v in r['faces'].items()}}
report={'pass':True,'source':str(source),'sourceSHA':before,'sourceSHAAfter':sha(source),'geometrySHA':geom,'helperSHA':sha(P/'hearth_object_parts.py'),'counts':counts,'palette':h['PALETTE'],'helperReadMutations':0,'indicesUniqueInRange':True}
(P/'hearth-part-assignments.json').write_text(json.dumps(a,indent=2)+'\n');(P/'hearth-part-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('HEARTH_HELPER_PASS '+json.dumps(report))
