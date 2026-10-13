import bpy, bmesh, numpy as np, collections
O=bpy.data.objects
for n in ['R_core_road','R_via_appia','R_via_ostiensis','R1_road_landing1','B_pons1','R3_colosseum_podium','R4_arena_skin','COL_ruined','R8_pantheon']:
    o=O[n]; me=o.data
    print(n,'slots',[(i,s.material.name if s.material else None, s.link) for i,s in enumerate(o.material_slots)])
    if n.startswith('R_'):
        bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        seen=set(); cnt=collections.Counter()
        for f in bm.faces:
            if f.index in seen: continue
            st=[f]; seen.add(f.index); fs=[]
            while st:
                a=st.pop(); fs.append(a)
                for e in a.edges:
                    for g in e.link_faces:
                        if g.index not in seen: seen.add(g.index); st.append(g)
            kind='paver' if len(fs)<=40 else 'big'
            for x in fs: cnt[(kind,x.material_index)]+=1
            if kind=='big': cnt[('bigisland',len(fs))]+=1
        print('  ',dict(cnt))
        bm.free()
