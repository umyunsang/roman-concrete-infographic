import bpy
import json
import sys
from pathlib import Path
from collections import Counter
from bpy_extras.object_utils import world_to_camera_view

out = Path(sys.argv[sys.argv.index('--') + 1])
s = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
W,H=1191.0,1684.0
inventory=[]
for ob in bpy.data.objects:
    record={"name":ob.name,"type":ob.type,"collections":[c.name for c in ob.users_collection],"hide_render":ob.hide_render,"hide_viewport":ob.hide_viewport,"location":list(ob.location),"dimensions":list(ob.dimensions),"color":list(ob.color)}
    if ob.type=='MESH':
        me=ob.evaluated_get(deps).to_mesh()
        me.calc_loop_triangles()
        record.update(vertices=len(me.vertices),triangles=len(me.loop_triangles),materials=[m.name if m else None for m in ob.data.materials])
        if s.camera and me.vertices:
            pts=[world_to_camera_view(s,s.camera,ob.matrix_world@v.co) for v in me.vertices]
            record['screen_bbox_pt']=[round(min(p.x for p in pts)*W,2),round((1-max(p.y for p in pts))*H,2),round(max(p.x for p in pts)*W,2),round((1-min(p.y for p in pts))*H,2)]
        ob.evaluated_get(deps).to_mesh_clear()
    elif ob.type=='FONT':
        record['body']=ob.data.body
    inventory.append(record)
summary={
 'source':bpy.data.filepath,'blender_version':bpy.app.version_string,
 'scene':s.name,'render':{'engine':s.render.engine,'resolution_x':s.render.resolution_x,'resolution_y':s.render.resolution_y,'resolution_percentage':s.render.resolution_percentage,'filepath':s.render.filepath,'image_format':s.render.image_settings.file_format,'transparent':s.render.film_transparent},
 'camera': {'name':s.camera.name,'type':s.camera.data.type,'lens':s.camera.data.lens,'ortho_scale':s.camera.data.ortho_scale,'location':list(s.camera.location),'rotation_euler':list(s.camera.rotation_euler)} if s.camera else None,
 'collections':[{'name':c.name,'objects':len(c.objects),'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.data.collections],
 'object_counts':dict(Counter(ob.type for ob in bpy.data.objects)),
 'material_count':len(bpy.data.materials),
 'materials':[{'name':m.name,'use_nodes':m.use_nodes} for m in bpy.data.materials],
 'images':[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file),'source':i.source} for i in bpy.data.images],
 'texts':[t.name for t in bpy.data.texts],
 'cameras':[o.name for o in bpy.data.objects if o.type=='CAMERA'],
 'visible_mesh_count':sum(o.type=='MESH' and not o.hide_render for o in bpy.data.objects),
 'visible_mesh_triangles':sum(r.get('triangles',0) for r in inventory if not r['hide_render']),
 'inventory':inventory
}
out.write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('READ_ONLY_AUDIT',out,'objects',len(inventory),'triangles',summary['visible_mesh_triangles'])
