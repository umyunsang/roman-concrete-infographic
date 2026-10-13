"""Enlarge only the existing Meshy modern frame in a preserved v4 scene."""
import argparse
import json
import runpy
import sys
from pathlib import Path
import bpy

root=Path(__file__).resolve().parents[1]
h=runpy.run_path(str(root/'scripts/integrate_assets.py'),run_name='helpers')
p=argparse.ArgumentParser()
p.add_argument('--bbox',nargs=4,type=float,required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
input_path=root/'out/roman_concrete_narrative_v4.blend'
assert Path(bpy.data.filepath).resolve()==input_path.resolve()
original_hash=h['sha256_file'](h['SOURCE'])
assert original_hash=='28d49f93c6edaf89bcbcc54ff1dfb94b0089cc2a0e43496032d46717c1a14cb3'
objects=list(bpy.data.objects)
before=h['source_fingerprints'](objects)
scene_before=h['scene_fingerprint'](bpy.context.scene)
ob=bpy.data.objects['NB_modern_building']
old_bbox=h['screen_bbox'](ob)
new_bbox=h['fit_projected_bbox'](ob,args.bbox,0.0,90.0)
zones=json.loads((root/'copy/text_zones_v9_live.json').read_text())
collisions=[z['id'] for z in zones if h['bbox_overlap'](new_bbox,z['b'],2)]
assert not collisions,('Live Figma text collision',collisions)
colosseum=h['screen_bbox'](bpy.data.objects['COL_ruined'])
assert not h['bbox_overlap'](new_bbox,colosseum,2),'Protected Colosseum overlap'
after=h['source_fingerprints'](objects)
changes=[]
for name in before:
 a,b=dict(before[name]),dict(after[name])
 if name==ob.name:
  for k in ['matrix_world','matrix_basis']:a.pop(k);b.pop(k)
 if a!=b:changes.append(name)
assert not changes,('Unrelated scene changes',changes)
assert scene_before==h['scene_fingerprint'](bpy.context.scene)
renders=h['render_two_pass'](root/'renders/narrative_v5.png')
assert scene_before==h['scene_fingerprint'](bpy.context.scene)
output=root/'out/roman_concrete_narrative_v5.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(output))
assert original_hash==h['sha256_file'](h['SOURCE'])
report={
 'input':str(input_path),'output':str(output),'changed_object':ob.name,
 'old_projected_bbox':old_bbox,'new_projected_bbox':new_bbox,
 'screen_scale_ratio':[(new_bbox[2]-new_bbox[0])/(old_bbox[2]-old_bbox[0]),(new_bbox[3]-new_bbox[1])/(old_bbox[3]-old_bbox[1])],
 'target_bbox':args.bbox,'text_overlap_count':len(collisions),
 'live_text_count':len(zones),'colosseum_overlap':False,
 'all_other_object_fingerprints_unchanged':True,
 'modern_mesh_and_color_unchanged':True,'camera_and_scene_flags_unchanged':True,
 'original_source_sha256':original_hash,'source_object_count':len(objects),
 'renders':renders,'fingerprints':after,'scene_fingerprint':scene_before
}
(root/'out/modern-frame-enlargement-v5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('MODERN_FRAME_ENLARGEMENT',json.dumps({k:v for k,v in report.items() if k not in ['fingerprints','scene_fingerprint']},ensure_ascii=False))
