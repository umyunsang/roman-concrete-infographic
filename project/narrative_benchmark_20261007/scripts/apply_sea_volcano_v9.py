"""Add face-region materials only to sea models and Vesuvius; preserve v8."""
import hashlib, json, runpy
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/roman_concrete_narrative_v8.blend'
OUT=ROOT/'out/roman_concrete_narrative_v9.blend'
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert H['sha256_file'](SOURCE)=='d179c5abdce8a9b0b48cf3f34cad9331b61e048f2e8edef504f430cee172ef3c'
source_sha=H['sha256_file'](SOURCE);canonical_sha=H['sha256_file'](H['SOURCE'])
states={o.name:o.hide_viewport for o in bpy.data.objects}
def snap():
 for o in bpy.data.objects:o.hide_viewport=False
 bpy.context.view_layer.update()
 result=H['source_fingerprints'](list(bpy.data.objects))
 for name,v in result.items():
  v['hide_viewport']=states[name]
  if 'camera_data' in v:v['camera_data'].pop('session_uid',None)
 for o in bpy.data.objects:o.hide_viewport=states[o.name]
 bpy.context.view_layer.update()
 return result
def indices(o):
 return hashlib.sha256(b''.join(int(p.material_index).to_bytes(2,'little')for p in o.data.polygons)).hexdigest()
before=snap();scene_before=H['scene_fingerprint'](bpy.context.scene)
indices_before={o.name:indices(o)for o in bpy.data.objects if o.type=='MESH'}
old_materials={m.name:{'color':list(m.diffuse_color),'roughness':m.roughness,'role':m.get('semantic_role'),'hex':m.get('sRGB_hex')}for m in bpy.data.materials}
specs={};palette={};lanes={}
for filename in ['sea_object_parts.py','volcano_parts.py']:
 module=runpy.run_path(str(ROOT/'scripts'/filename),run_name='part_helpers')
 parts=module['build_assignments'](bpy)
 assert not set(parts)&set(specs)
 specs.update(parts);palette.update(module['PALETTE'])
 lanes[filename]={n:{'default':s['default'],'counts':{r:len(i)for r,i in s['faces'].items()},'notes':s.get('notes','')}for n,s in parts.items()}
assert set(specs)=={'L09_portus_lighthouse','L09_portus_mole','L12_harbor_pilae','NB_marine_breakwater','L07_vesuvius'},list(specs)
materials={}
def lin(hex):
 v=[int(hex[i:i+2],16)/255 for i in (1,3,5)]
 return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
def material(role):
 if role not in materials:
  rgba=(*lin(palette[role]),1.)
  m=bpy.data.materials.new('RC.v13.'+role);m.diffuse_color=rgba;m.roughness=.85
  m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF')
  bsdf.inputs['Base Color'].default_value=rgba;bsdf.inputs['Roughness'].default_value=.85
  m['semantic_role']=role;m['sRGB_hex']=palette[role];materials[role]=m
 return materials[role]
applied={};isolated=[]
for name,spec in specs.items():
 ob=bpy.data.objects[name];assert ob.type=='MESH' and not ob.hide_render
 if ob.data.users>1:ob.data=ob.data.copy();isolated.append(name)
 roles=[spec['default']]+[r for r in spec['faces']if r!=spec['default']]
 assert all(r in palette for r in roles)
 n=len(ob.data.polygons);assigned={};slots={r:i for i,r in enumerate(roles)}
 ob.data.materials.clear()
 for role in roles:ob.data.materials.append(material(role))
 for poly in ob.data.polygons:poly.material_index=0
 for role,ids in spec['faces'].items():
  assert len(ids)==len(set(ids))
  for i in ids:
   assert isinstance(i,int)and 0<=i<n
   assert i not in assigned,(name,i,assigned.get(i),role)
   assigned[i]=role;ob.data.polygons[i].material_index=slots[role]
 actual={r:0 for r in roles}
 for p in ob.data.polygons:actual[roles[p.material_index]]+=1
 assert all(v>0 for v in actual.values()),(name,actual)
 applied[name]={'default':spec['default'],'material_roles':roles,'face_counts':actual,'polygon_count':n,'notes':spec.get('notes',''),'assignment_sha256':indices(ob)}
after=snap();changes={n:[k for k in before[n]if before[n][k]!=after[n][k]]for n in before if before[n]!=after[n]}
assert set(changes)==set(specs)and all(v==['materials']for v in changes.values()),changes
indices_after={o.name:indices(o)for o in bpy.data.objects if o.type=='MESH'}
assert all(indices_before[n]==indices_after[n]for n in indices_before if n not in specs)
assert all(old_materials[m.name]=={'color':list(m.diffuse_color),'roughness':m.roughness,'role':m.get('semantic_role'),'hex':m.get('sRGB_hex')}for m in bpy.data.materials if m.name in old_materials)
assert bpy.context.scene.display.shading.color_type=='MATERIAL'
assert scene_before==H['scene_fingerprint'](bpy.context.scene)
assert H['sha256_file'](SOURCE)==source_sha and H['sha256_file'](H['SOURCE'])==canonical_sha
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'input':str(SOURCE),'output':str(OUT),'source_sha256':source_sha,'canonical_sha256':canonical_sha,'preserved_object_count':len(before),
 'geometry_transforms_camera_visibility_preserved':True,'only_five_target_materials_changed':True,'new_material_count':len(materials),'total_material_count':len(bpy.data.materials),
 'materials':{r:{'name':m.name,'hex':palette[r],'linear_color':list(m.diffuse_color)}for r,m in materials.items()},'applied':applied,'lanes':lanes,
 'shared_data_isolated':isolated,'before':before,'after':after,'indices_before':indices_before,'indices_after':indices_after,
 'render_passes':H['render_two_pass'](ROOT/'renders/narrative_v9_sea_volcano.png')}
(ROOT/'out/poster-sea-volcano-v9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'copy/sea_volcano_palette_v13.json').write_text(json.dumps({'part_colors':palette,'materials':report['materials'],'render_mode':'Workbench MATERIAL','objects':list(specs)},ensure_ascii=False,indent=2)+'\n')
print('SEA_VOLCANO_V9_COMPLETE',json.dumps({k:report[k]for k in ['output','preserved_object_count','new_material_count','total_material_count']},ensure_ascii=False))
