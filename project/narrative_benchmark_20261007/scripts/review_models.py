"""Read-only Meshy geometry review renders; no .blend save."""
import bpy,runpy,sys,json,math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
helpers=runpy.run_path(str(ROOT/'scripts/integrate_assets.py'),run_name='integration_helpers')
out=ROOT/'renders/model_review';out.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
cam_data=bpy.data.cameras.new('review_camera');cam=bpy.data.objects.new('review_camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
cam_data.type='ORTHO';cam_data.ortho_scale=3.2
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
sh=scene.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(0.92,0.92,0.92)
jobs=json.load(open(ROOT/'meshy_jobs.json'))['tasks'];report=[]
requested=set(sys.argv[sys.argv.index('--')+1:]) if '--' in sys.argv else set(jobs)
for name,j in jobs.items():
 if name not in requested:continue
 ob=helpers['import_glb']({'id':name,'path':str(ROOT/'models'/(name+'.glb')),'grayscale':0.72,'source_task_id':j['task_id']})
 ob.scale=(2.0/max(ob.dimensions),)*3;bpy.context.view_layer.update()
 center=Vector((0,0,ob.dimensions.z/2));cam.location=center+Vector((5,-7,5));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 for degrees in [0,90,180,270]:
  ob.rotation_euler.z=math.radians(degrees);scene.render.filepath=str(out/f'{name}-{degrees}.png');bpy.ops.render.render(write_still=True)
 ob.data.calc_loop_triangles();report.append({'id':name,'triangles':len(ob.data.loop_triangles),'render_angles':[0,90,180,270]})
 bpy.data.objects.remove(ob,do_unlink=True)
(out/'review_inventory.json').write_text(json.dumps(report,indent=2))
print('MODEL_REVIEW_DONE',json.dumps(report))
