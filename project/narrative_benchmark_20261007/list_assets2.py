import bpy, json
out={}
for c in bpy.data.collections:
    if c.name in ('Collection',): continue
    names=sorted(o.name for o in c.objects if o.type=='MESH' and not o.hide_render)
    out[c.name]=names
print('JSONOUT'+json.dumps(out,ensure_ascii=False))
