"""Preserve map geometry/layout and implement real per-part material assignments."""
import hashlib, json, runpy
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/roman_concrete_narrative_v7.blend'
OUT=ROOT/'out/roman_concrete_narrative_v8.blend'
H=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='helpers')
P=json.loads((ROOT/'copy/color_system_v11.json').read_text())
R=json.loads((ROOT/'out/poster-color-v7.json').read_text())
PART_PALETTE={
 'concrete':'#B9BEC0','steel':'#344E5A','labstone':'#B9C7C5','roof':'#527882',
 'glass':'#3F9DAA','base':'#9FACA6','skin':'#C99C78','linen':'#DED1AF',
 'cloth':'#9C5C43','toolwood':'#8D6C49','toolmetal':'#526873',
 'basin':'#B9976F','mixture':'#8B6950','raw_lime':'#FFF4DD','raw_ash':'#A4876D',
 'roman_stone':'#D3BE9E','colosseum_wall':'#CDA477','colosseum_interior':'#B89D78',
 'arena_earth':'#B5A07B','roman_roof':'#A88565','roman_plinth':'#B5A68B',
 'foliage':'#75865C','foliage_light':'#8D9A70','trunk':'#8D6C49',
}
COLORS={**{'base_'+k:h for k,h in P['tokens'].items()},**PART_PALETTE}
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert H['sha256_file'](SOURCE)=='2c22462b8cd9f169f6eb12822befa415c9c42a256eca86ae4e5ead5820d1b4b8'
source_sha=H['sha256_file'](SOURCE);canonical_sha=H['sha256_file'](H['SOURCE'])
assert len(bpy.data.materials)==0
states={o.name:o.hide_viewport for o in bpy.data.objects}
def snap():
 for o in bpy.data.objects:o.hide_viewport=False
 bpy.context.view_layer.update()
 result=H['source_fingerprints'](list(bpy.data.objects))
 for name,v in result.items():
  v['hide_viewport']=states[name]
  if 'camera_data'in v:v['camera_data'].pop('session_uid',None)
 for o in bpy.data.objects:o.hide_viewport=states[o.name]
 bpy.context.view_layer.update()
 return result
before=snap();scene_before=H['scene_fingerprint'](bpy.context.scene)
specs={};lane_reports={}
for file in ['modern_lab_parts.py','process_people_parts.py','heritage_tree_parts.py']:
 module=runpy.run_path(str(ROOT/'scripts'/file),run_name='part_helpers')
 parts=module['build_assignments'](bpy)
 conflicts=set(specs)&set(parts)
 assert not conflicts,(file,conflicts)
 specs.update(parts);lane_reports[file]={n:{'default':s['default'],'counts':{r:len(i)for r,i in s['faces'].items()},'notes':s.get('notes','')}for n,s in parts.items()}
materials={}
def lin(hex):
 v=[int(hex[i:i+2],16)/255 for i in (1,3,5)]
 return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
def material(role):
 if role not in materials:
  rgba=(*lin(COLORS[role]),1.)
  m=bpy.data.materials.new('RC.v12.'+role);m.diffuse_color=rgba;m.roughness=.85
  m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF')
  bsdf.inputs['Base Color'].default_value=rgba;bsdf.inputs['Roughness'].default_value=.85
  m['semantic_role']=role;m['sRGB_hex']=COLORS[role]
  materials[role]=m
 return materials[role]
applied={};isolated=[]
for name,base in R['color_assignments'].items():
 ob=bpy.data.objects[name]
 assert ob.type=='MESH',name
 if ob.data.users>1:
  ob.data=ob.data.copy();isolated.append(name)
 spec=specs.get(name,{'default':'base_'+base['token'],'faces':{},'notes':'Existing separately modeled semantic part; preserved base palette.'})
 roles=[spec['default']]+[r for r in spec['faces']if r!=spec['default']]
 assert all(r in COLORS for r in roles),(name,roles)
 n=len(ob.data.polygons);assigned={};slots={r:i for i,r in enumerate(roles)}
 ob.data.materials.clear()
 for role in roles:ob.data.materials.append(material(role))
 for poly in ob.data.polygons:poly.material_index=0
 for role,indices in spec['faces'].items():
  assert len(indices)==len(set(indices)),(name,role,'duplicate')
  for i in indices:
   assert isinstance(i,int)and 0<=i<n,(name,role,i,n)
   assert i not in assigned,(name,'overlapping region',i,assigned.get(i),role)
   assigned[i]=role;ob.data.polygons[i].material_index=slots[role]
 actual={r:0 for r in roles}
 for poly in ob.data.polygons:actual[roles[poly.material_index]]+=1
 applied[name]={'default':spec['default'],'material_roles':roles,'face_counts':actual,'polygon_count':n,'notes':spec.get('notes',''),
  'assignment_sha256':hashlib.sha256(bytes().join(int(p.material_index).to_bytes(2,'little')for p in ob.data.polygons)).hexdigest()}
assert set(specs)<=set(applied),('Nonvisible spec objects',set(specs)-set(applied))
scene=bpy.context.scene;assert scene.display.shading.color_type=='OBJECT'
scene.display.shading.color_type='MATERIAL'
# Save Solid viewport screens in Material color mode as well as render shading.
viewport_changes=[]
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   for space in area.spaces:
    if space.type=='VIEW_3D':
     if space.shading.color_type!='MATERIAL':viewport_changes.append({'screen':screen.name,'before':space.shading.color_type,'after':'MATERIAL'})
     space.shading.color_type='MATERIAL'
after=snap();changes={n:[k for k in before[n]if before[n][k]!=after[n][k]]for n in before if before[n]!=after[n]}
assert all(v==['materials']for v in changes.values()),changes
assert set(changes)<=set(applied)
assert scene_before==H['scene_fingerprint'](scene)
assert H['sha256_file'](SOURCE)==source_sha and H['sha256_file'](H['SOURCE'])==canonical_sha
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'input':str(SOURCE),'output':str(OUT),'source_sha256':source_sha,'canonical_sha256':canonical_sha,
 'preserved_object_count':len(before),'geometry_transforms_camera_visibility_preserved':True,
 'material_count':len(materials),'colored_meshes':len(applied),'per_part_mesh_count':sum(sum(c>0 for c in a['face_counts'].values())>1 for a in applied.values()),
 'materials':{r:{'name':m.name,'hex':COLORS[r],'linear_color':list(m.diffuse_color)}for r,m in materials.items()},
 'applied':applied,'lanes':lane_reports,'shared_data_isolated':isolated,'viewport_changes':viewport_changes,
 'before':before,'after':after,'render_passes':H['render_two_pass'](ROOT/'renders/narrative_v8_parts.png')}
(ROOT/'out/poster-part-materials-v8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'copy/part_material_palette_v12.json').write_text(json.dumps({'part_colors':PART_PALETTE,'all_materials':report['materials'],'render_mode':'Workbench MATERIAL','preserved':'current v7 geometry/layout + 95 Figma texts'},ensure_ascii=False,indent=2)+'\n')
print('PART_COLOR_V8_COMPLETE',json.dumps({k:report[k]for k in ['output','preserved_object_count','material_count','colored_meshes','per_part_mesh_count']},ensure_ascii=False))
