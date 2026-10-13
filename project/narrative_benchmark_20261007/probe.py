import bpy, bmesh, json, math, sys
from mathutils import Vector
names = sys.argv[sys.argv.index('--')+1].split(',')
dg = bpy.context.evaluated_depsgraph_get()
cam = bpy.data.objects.get('CAM_iso')
out = {}
if cam:
    c = cam.data
    fwd = cam.matrix_world.to_3x3() @ Vector((0,0,-1))
    out['camera'] = dict(type=c.type, ortho_scale=c.ortho_scale, lens=c.lens, loc=list(cam.location), rot=[math.degrees(a) for a in cam.rotation_euler], fwd=list(fwd), elev_deg=math.degrees(math.asin(-fwd.z)), azim_deg=math.degrees(math.atan2(fwd.y, fwd.x)))
for n in names:
    o = bpy.data.objects.get(n)
    if not o: out[n]=None; continue
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    # islands
    seen=set(); islands=[]
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; comp=[]; seen.add(v.index)
        while stack:
            x=stack.pop(); comp.append(x.index)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); stack.append(y)
        islands.append(len(comp))
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    mw = o.matrix_world
    ws = [mw @ v.co for v in bm.verts]
    if ws:
        mn = [min(p[i] for p in ws) for i in range(3)]; mx=[max(p[i] for p in ws) for i in range(3)]
    else: mn=mx=[0,0,0]
    smooth = sum(1 for f in bm.faces if f.smooth); 
    out[n] = dict(dims=list(o.dimensions), loc=list(o.location), rot=[math.degrees(a) for a in o.rotation_euler], scale=list(o.scale), world_min=mn, world_max=mx,
        faces=len(bm.faces), verts=len(bm.verts), islands=sorted(islands, reverse=True)[:12], n_islands=len(islands), boundary_edges=boundary, nonmanifold_edges=nonman,
        smooth_faces=smooth, mods=[(m.type, getattr(m,'width',None), getattr(m,'segments',None)) for m in o.modifiers], parent=o.parent.name if o.parent else None,
        hide_render=o.hide_render)
    bm.free(); oe.to_mesh_clear()
print('JSON_OUT'+json.dumps(out))
