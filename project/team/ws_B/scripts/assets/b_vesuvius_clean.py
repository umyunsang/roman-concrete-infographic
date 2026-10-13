"""워커 B: 화산(스캔) 왼쪽 사면 밖에 떠 있는 반투명 점 부스러기 = 본체와 떨어진 작은 조각들 → 가까운 꼭짓점 합친 뒤
면 수가 가장 큰 덩어리의 1% 미만인 섬을 지움(한 번만, o['b_cleaned'])."""
import bpy, bmesh
o = bpy.data.objects['L07_vesuvius']
if not o.get('b_cleaned'):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.faces.ensure_lookup_table()
    seen = set(); comps = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]; comp = []; seen.add(f.index)
        while stack:
            g = stack.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index); stack.append(h)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    big = len(comps[0])
    kill = [f for c in comps if len(c) < 0.01 * big for f in c]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['b_cleaned'] = True
    print('vesuvius components', len(comps), 'largest', big, 'removed faces', len(kill))
else:
    print('vesuvius already cleaned')
