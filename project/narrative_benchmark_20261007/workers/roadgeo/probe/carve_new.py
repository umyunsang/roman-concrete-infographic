def carve(S, land):
    me = land.data
    if me.users > 1:
        land.data = me.copy(); me = land.data
    LW = world_verts(land); nv = len(LW)
    d_req = np.zeros(nv)                 # required lowering (cutting under the road + bank)
    d_lim = np.full(nv, np.inf)          # largest allowed lowering (0 = never move)
    work = np.zeros(nv, bool)            # vertices the smoothing may touch (region boxes)
    kd = guard_kd()
    rep = {}
    for name, objs, box in REGIONS:
        tris = []; nface = {}
        for on in objs:
            t, n = up_faces(need(on), S, box); nface[on] = n
            if len(t):
                tris.append(t)
        if not tris:
            raise RuntimeError(f'roadgeo step: region {name} selects no road faces')
        tris = np.concatenate(tris)
        R = SHOULDER + MAX_DROP / SLOPE
        xa, xb = tris[:, :, 0].min() - R - CELL, tris[:, :, 0].max() + R + CELL
        ya, yb = tris[:, :, 1].min() - R - CELL, tris[:, :, 1].max() + R + CELL
        nx = int(math.ceil((xb - xa) / CELL)) + 1; ny = int(math.ceil((yb - ya) / CELL)) + 1
        top = rasterize_max(tris, xa, ya, nx, ny)
        target = np.where(np.isfinite(top), top - D_BELOW, np.inf)
        cap = cone_cap(target)
        idx = np.nonzero((LW[:, 0] >= xa) & (LW[:, 0] <= xb) & (LW[:, 1] >= ya) & (LW[:, 1] <= yb))[0]
        c = bilinear(cap, xa, ya, LW[idx, :2])
        needv = np.maximum(0.0, LW[idx, 2] - c)
        d_req[idx] = np.maximum(d_req[idx], needv)
        work[idx] = True
        bvh, owner = protected_bvh((xa, xb, ya, yb), land)
        n_guard = n_rest = n_floor = 0; resting_on = {}
        for vi in idx:
            x, y, z = LW[vi]
            if kd.find_range((x, y, 0.0), PROTECT_R):
                d_lim[vi] = 0.0; n_guard += 1; continue
            if bvh is None:
                continue
            for ox, oy in ((0, 0), (0.35, 0), (-0.35, 0), (0, 0.35), (0, -0.35)):
                h = bvh.ray_cast(Vector((x + ox, y + oy, z + 3.0)), Vector((0, 0, -1)))
                if h[0] is None:
                    continue
                if h[0].z >= z - 0.05:                    # something stands on the ground here
                    if h[0].z <= z + 0.6:
                        d_lim[vi] = 0.0; n_rest += 1; resting_on[owner[h[2]]] = resting_on.get(owner[h[2]], 0) + 1
                        break
                else:                                     # something lies under the ground (water): stay above it
                    lim = z - (h[0].z + 0.05)
                    if lim < d_lim[vi]:
                        d_lim[vi] = lim
                    if lim < needv[np.searchsorted(idx, vi)]:
                        n_floor += 1
        rep[name] = {'road_faces': nface, 'grid': [nx, ny], 'terrain_vertices_in_box': int(len(idx)),
                     'vertices_needing_cut': int((needv > 1e-6).sum()),
                     'needed_drop_max': round(float(needv.max()), 3) if len(needv) else 0.0,
                     'pinned_guard_radius': n_guard, 'pinned_object_on_ground': n_rest,
                     'objects_on_ground': resting_on, 'limited_by_object_below': n_floor,
                     'world_box': [round(v, 2) for v in (xa, xb, ya, yb)]}
    # T_land topology: steep faces (diorama skirt, quay and pit walls) and border vertices with a coincident partner
    # (the skirt's top row duplicates the border of the top surface): partners move together, other steep
    # vertices are pinned.
    ls = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls)
    lt = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    le = np.empty(len(me.loops), np.int32); me.loops.foreach_get('edge_index', le)
    fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
    fn = fn.reshape(-1, 3) @ np.array(land.matrix_world.to_3x3()).T
    steep_f = np.abs(fn[:, 2]) / np.maximum(np.linalg.norm(fn, axis=1), 1e-12) < STEEP_NZ
    fidx = np.repeat(np.arange(len(ls)), lt)
    flat_v = np.zeros(nv, bool); flat_v[lv[~steep_f[fidx]]] = True
    steep_v = np.zeros(nv, bool); steep_v[lv[steep_f[fidx]]] = True
    E = np.empty(len(me.edges) * 2, np.int32); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
    ecount = np.bincount(le, minlength=len(E))
    border = np.zeros(nv, bool); border[E[ecount == 1].ravel()] = True
    cand = np.nonzero(border & work)[0]
    groups = []
    if len(cand):
        kt = KDTree(len(cand))
        for k, vi in enumerate(cand):
            kt.insert(LW[vi], k)
        kt.balance(); seen = set()
        for k, vi in enumerate(cand):
            if vi in seen:
                continue
            g = sorted({int(cand[j]) for _, j, _ in kt.find_range(LW[vi], 1e-4)})
            seen.update(g)
            if len(g) > 1:
                groups.append(g)
    grouped = np.zeros(nv, bool)
    for g in groups:
        grouped[g] = True
    pin_steep = work & steep_v & ~flat_v & ~grouped
    rep['pinned_steep_vertices'] = int(pin_steep.sum())
    rep['pinned_steep_vertices_needing_cut'] = int((pin_steep & (d_req > 1e-6)).sum())
    rep['border_partner_groups'] = len(groups)
    d_lim[pin_steep] = 0.0
    for g in groups:                                      # partners share requirement and limit
        d_req[g] = d_req[g].max(); d_lim[g] = d_lim[g].min()
    d_lim = np.maximum(d_lim, 0.0)
    # smooth fall-off: d = max(d_req, relaxed neighbour mean), clipped to d_lim, inside the work set only
    Ew = E[work[E[:, 0]] | work[E[:, 1]]]
    deg = np.zeros(nv); np.add.at(deg, Ew[:, 0], 1); np.add.at(deg, Ew[:, 1], 1)
    dr = np.minimum(d_req, d_lim)
    d = dr.copy()
    for _ in range(SMOOTH_ITERS):
        s = np.zeros(nv); np.add.at(s, Ew[:, 0], d[Ew[:, 1]]); np.add.at(s, Ew[:, 1], d[Ew[:, 0]])
        m = np.where(deg > 0, s / np.maximum(deg, 1), 0.0)
        d = np.where(work, np.minimum(np.maximum(dr, 0.5 * d + 0.5 * m), d_lim), 0.0)
        for g in groups:
            d[g] = d[g].max()
    d[d < 1e-5] = 0.0
    newz = LW[:, 2] - d
    rep['smoothing_iterations'] = SMOOTH_ITERS
    rep['vertices_needing_cut'] = int((d_req > 1e-6).sum())
    rep['vertices_needing_cut_but_limited'] = int((d_req > d_lim + 1e-6).sum())
    rep['cut_shortfall_max'] = round(float(np.max(d_req - np.minimum(d_req, d_lim))), 3)
    rep['lowered_by_smoothing_only'] = int(((d > 0) & (d_req <= 1e-6)).sum())
    rep['drop_max'] = round(float(d.max()), 3)
    changed = np.nonzero(np.abs(newz - LW[:, 2]) > 1e-7)[0]
    if len(changed):
        Mi = np.array(land.matrix_world.inverted())
        Wn = LW.copy(); Wn[:, 2] = newz
        co = (np.c_[Wn, np.ones(len(Wn))] @ Mi.T)[:, :3]
        me.vertices.foreach_set('co', co.ravel()); me.update()
    rep['T_land_vertices_changed'] = int(len(changed))
    return rep


