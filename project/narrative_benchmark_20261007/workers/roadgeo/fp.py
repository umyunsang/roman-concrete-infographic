"""fp.py - per-object fingerprints (read-only) for before/after proofs.
Blender -b <in.blend> --factory-startup --python fp.py -- <out.json>
Uses integrate_assets.source_fingerprints (matrix, parent, collections, visibility, modifiers, mesh sha256 of
vertices/edges/loops/polys, material slot names) per object, hashed to one sha256 per object, plus the per-face
material index hash for meshes and the file sha256.
"""
import bpy, sys, json, runpy, hashlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
NB = HERE.parents[1]
H = runpy.run_path(str(NB / 'scripts/integrate_assets.py'), run_name='ia_lib')
out = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
fps = H['source_fingerprints'](list(bpy.data.objects))
res = {}
for n, r in fps.items():
    o = bpy.data.objects[n]
    if o.type == 'MESH':
        mi = np.empty(len(o.data.polygons), np.int32); o.data.polygons.foreach_get('material_index', mi)
        r['material_index_sha256'] = hashlib.sha256(mi.tobytes()).hexdigest()
    res[n] = H['json_hash'](r)
mats = {}
for m in bpy.data.materials:
    mats[m.name] = H['json_hash']({'diffuse': [round(v, 6) for v in m.diffuse_color]})
out.write_text(json.dumps({'blend': bpy.data.filepath, 'file_sha256': H['sha256_file'](bpy.data.filepath),
                           'objects': res, 'materials': mats}, indent=0, sort_keys=True))
print('FP', len(res), 'objects ->', out)
