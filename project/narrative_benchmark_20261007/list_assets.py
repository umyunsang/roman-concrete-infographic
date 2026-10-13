import bpy, json
out={}
def walk(c, depth=0):
    objs=[o for o in c.objects if o.type=='MESH' and not o.hide_render]
    out.setdefault('collections',[]).append({'name':c.name,'depth':depth,'n_mesh':len(objs),'children':[ch.name for ch in c.children]})
    for ch in c.children: walk(ch, depth+1)
walk(bpy.context.scene.collection)
prefixes={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render: continue
    p=o.name.split('.')[0]
    p=p.split('_')[0]+'_'+(p.split('_')[1] if '_' in p else '')
    prefixes[p]=prefixes.get(p,0)+1
out['prefixes']=prefixes
print('JSONOUT'+json.dumps(out,ensure_ascii=False))
