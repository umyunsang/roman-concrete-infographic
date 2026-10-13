import bpy, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=sc.camera
W,H=1191,1684
names=['C5_researchers','L08_pompeii_site','L09_portus_mole','L12_harbor_pilae','L09_portus_lighthouse','L11_privernum_wall','NB_marine_breakwater','L08_pompeii','L05_aqua_claudia']
dg=bpy.context.evaluated_depsgraph_get()
out={}
for nm in names:
    ob=bpy.data.objects[nm]; oe=ob.evaluated_get(dg); me=oe.to_mesh(); mw=ob.matrix_world
    co=[world_to_camera_view(sc,cam,mw@v.co) for v in me.vertices]
    mats=[s.material.name if s.material else '' for s in ob.material_slots]
    polys=[]
    for p in me.polygons:
        pts=[(round(co[i].x*W,3),round((1-co[i].y)*H,3)) for i in p.vertices]
        z=sum(co[i].z for i in p.vertices)/len(p.vertices)
        polys.append([mats[p.material_index] if p.material_index<len(mats) else '',round(z,4),pts])
    out[nm]=polys
    oe.to_mesh_clear()
json.dump(out,open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oi_b1/proj_polys.json','w'))
print('done',{k:len(v) for k,v in out.items()})
