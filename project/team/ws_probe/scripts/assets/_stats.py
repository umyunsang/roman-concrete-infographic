import bpy
tot=0; rows=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o.visible_get():
        n=sum(len(p.vertices)-2 for p in o.data.polygons); tot+=n; rows.append((n,o.name,o.users_collection[0].name))
rows.sort(reverse=True)
print('TOTAL_TRIS',tot)
for r in rows[:25]: print('TRI',r)
