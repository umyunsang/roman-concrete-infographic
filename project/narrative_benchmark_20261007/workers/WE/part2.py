# ------------------------------------------------------------------ roads: paving parts, landing ends, paving bed
CELL = 0.10        # world units, raster for the paving bed / carving caps
BED_D = float(os.environ.get('WE_BED_D', '0.03'))      # bed top below the lowest paver top around it
BED_HEX = os.environ.get('WE_BED_HEX', '')             # '' = paving material RC.road.selce_basalt
BED_MAT = 'RC.road.joint_bed'


def road_parts(o):
    lab, flab, ls, lt, lv = islands(o)
    n = int(lab.max()) + 1 if len(lab) else 0
    nf = np.bincount(flab, minlength=n)
    return lab, flab, ls, lt, lv, nf


def delete_islands(o, kill):
    lab, flab, ls, lt, lv, nf = road_parts(o)
    return delete_faces_and_islands(o, np.isin(flab, list(kill)))


def road_landing1(S):
    """road_core_nw FORM-18: the paving parts of R_core_road whose centre lies under the landing disc
    R1_road_landing1 (radius + 0.09) are removed, and so are the small paving fragments that stick out past its rim
    (parts whose centre is within rim + 0.6 and that lie outside the road's kerb lines, i.e. beyond the road end)."""
    road = need('R_core_road'); l1 = need('R1_road_landing1')
    Wl = world_verts(l1); c = Wl[:, :2].mean(0); r = float(np.linalg.norm(Wl[:, :2] - c, axis=1).max())
    lab, flab, ls, lt, lv, nf = road_parts(road)
    W = world_verts(road)
    kill = []
    for k in range(len(nf)):
        if nf[k] >= KERB_MIN_FACES:
            continue
        w = W[lab == k]
        if np.linalg.norm(w[:, :2].mean(0) - c) < r + 0.09:
            kill.append(k)
    n = delete_islands(road, kill)
    log('road_landing1', {'centre': c.round(3).tolist(), 'radius': round(r, 3), 'paving_parts_removed': len(kill), 'faces': n})


def road_landing5(S):
    """road_core_se FORM-19: paving bits beyond the landing disc R1_road_landing5 (screen 936-949 x 865-869) and the
    kerb-less 1-4-face paving strip east of the east kerb (screen x > 953.9, y 866-892) are removed."""
    road = need('R_core_road')
    lab, flab, ls, lt, lv, nf = road_parts(road)
    W = world_verts(road); P = S.project(W)
    kill = []
    for k in range(len(nf)):
        if nf[k] >= KERB_MIN_FACES:
            continue
        p = P[lab == k].mean(0)
        if (935.5 <= p[0] <= 950.0 and 863.0 <= p[1] <= 871.0) or (p[0] > 953.9 and 866.0 <= p[1] <= 892.0):
            kill.append(k)
    n = delete_islands(road, kill)
    log('road_landing5', {'paving_parts_removed': len(kill), 'faces': n})


def raster(tris, x0, y0, nx, ny, mode='max'):
    """z of triangles (m,3,3) on a CELL grid (cell centres x0 + i*CELL); max or min where several overlap; nan elsewhere."""
    fill = -np.inf if mode == 'max' else np.inf
    G = np.full((ny, nx), fill)
    for t in tris:
        a, b, c = t
        i0 = max(0, int(math.floor((t[:, 0].min() - x0) / CELL))); i1 = min(nx - 1, int(math.ceil((t[:, 0].max() - x0) / CELL)))
        j0 = max(0, int(math.floor((t[:, 1].min() - y0) / CELL))); j1 = min(ny - 1, int(math.ceil((t[:, 1].max() - y0) / CELL)))
        if i1 < i0 or j1 < j0:
            continue
        X, Y = np.meshgrid(x0 + np.arange(i0, i1 + 1) * CELL, y0 + np.arange(j0, j1 + 1) * CELL)
        v0 = b[:2] - a[:2]; v1 = c[:2] - a[:2]
        den = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(den) < 1e-12:
            continue
        px = X - a[0]; py = Y - a[1]
        u = (px * v1[1] - v1[0] * py) / den; v = (v0[0] * py - px * v0[1]) / den; w = 1 - u - v
        e = 0.35 * CELL / max(1e-6, math.sqrt(abs(den)))           # half a cell of slack: thin strips still mark cells
        inside = (u >= -e) & (v >= -e) & (w >= -e)
        z = w * a[2] + u * b[2] + v * c[2]
        sub = G[j0:j1 + 1, i0:i1 + 1]
        if mode == 'max':
            np.maximum(sub, np.where(inside, z, -np.inf), out=sub)
        else:
            np.minimum(sub, np.where(inside, z, np.inf), out=sub)
    G[~np.isfinite(G)] = np.nan
    return G


def shift(G, dy, dx, fill):
    H = np.full_like(G, fill)
    ny, nx = G.shape
    ys0, ys1 = max(0, dy), ny + min(0, dy); xs0, xs1 = max(0, dx), nx + min(0, dx)
    H[ys0:ys1, xs0:xs1] = G[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return H


def disk(r):
    R = int(math.ceil(r))
    return [(dy, dx) for dy in range(-R, R + 1) for dx in range(-R, R + 1) if dx * dx + dy * dy <= r * r + 1e-9]


def dilate(M, r):
    out = np.zeros_like(M)
    for dy, dx in disk(r):
        out |= shift(M, dy, dx, False)
    return out


def erode(M, r):
    return ~dilate(~M, r)


def nan_min_filter(G, r):
    out = np.full_like(G, np.nan)
    with np.errstate(invalid='ignore'):
        for dy, dx in disk(r):
            H = shift(G, dy, dx, np.nan)
            out = np.fmin(out, H)
    return out


def face_tris(o, faces):
    W = world_verts(o); me = o.data
    tris = []
    for f in faces:
        v = list(me.polygons[f].vertices)
        for k in range(1, len(v) - 1):
            tris.append(W[[v[0], v[k], v[k + 1]]])
    return np.array(tris).reshape(-1, 3, 3)


def world_normals_z(o):
    me = o.data
    fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
    fn = fn.reshape(-1, 3) @ np.array(o.matrix_world.to_3x3()).T
    return fn[:, 2] / np.maximum(np.linalg.norm(fn, axis=1), 1e-12)


class BedGrid:
    def __init__(self, x0, y0, nx, ny, Z, M):
        self.x0, self.y0, self.nx, self.ny, self.Z, self.M = x0, y0, nx, ny, Z, M

    def at(self, xy, grow=1):
        """bed z under each point (min over a (2*grow+1)^2 neighbourhood of bed cells), nan if no bed."""
        i = np.rint((xy[:, 0] - self.x0) / CELL).astype(int); j = np.rint((xy[:, 1] - self.y0) / CELL).astype(int)
        out = np.full(len(xy), np.nan)
        Zm = np.where(self.M, self.Z, np.nan)
        for dj in range(-grow, grow + 1):
            for di in range(-grow, grow + 1):
                ii = i + di; jj = j + dj
                ok = (ii >= 0) & (ii < self.nx) & (jj >= 0) & (jj < self.ny)
                v = np.full(len(xy), np.nan); v[ok] = Zm[jj[ok], ii[ok]]
                out = np.fmin(out, v)
        return out


def build_bed(S):
    """road_core_* PLACE-03 / HIER-09 / OV-RSW-23, road_appia HIER-09: a thin paving bed under the joints of the
    core road and the Via Appia. Footprint = paving tops + kerb tops, closed by 0.3 (joints, kerb notches, the wedge
    at the south bridge's east ramp), shrunk one cell so it stays inside the outer kerb edges and off the bridge decks
    and landing discs. Its top lies BED_D below the lowest paver top within 0.4, so the joints show a shallow floor in
    paving colour instead of a deep shadow or the paper-coloured ground."""
    grids = []
    verts_all, faces_all = [], []
    block = []
    for bn in ('B_pons1', 'B_pons2', 'R1_road_landing1', 'R1_road_landing5', 'R4_bridge_west_bed'):
        b = need(bn); Wb = world_verts(b)
        block.append((bn, convex_hull(Wb[:, :2]), float(Wb[:, 2].min())))
    info = {}
    for name in ('R_core_road', 'R_via_appia'):
        o = need(name)
        lab, flab, ls, lt, lv, nf = road_parts(o)
        nz = world_normals_z(o)
        pav = nf[flab] < KERB_MIN_FACES
        tops = np.nonzero(pav & (nz > 0.7))[0]
        kerb = np.nonzero(~pav & (np.abs(nz) > 0.7))[0]
        Tt = face_tris(o, tops); Tk = face_tris(o, kerb)
        W = world_verts(o)
        x0, y0 = W[:, 0].min() - 1.0, W[:, 1].min() - 1.0
        nx = int(math.ceil((W[:, 0].max() + 1.0 - x0) / CELL)) + 1; ny = int(math.ceil((W[:, 1].max() + 1.0 - y0) / CELL)) + 1
        Zt = raster(Tt, x0, y0, nx, ny, 'max')
        Zk = raster(Tk, x0, y0, nx, ny, 'max')
        M0 = np.isfinite(Zt) | np.isfinite(Zk)
        Mc = erode(dilate(M0, 3), 3) | M0
        Mb = erode(Mc, 1)
        X, Y = np.meshgrid(x0 + np.arange(nx) * CELL, y0 + np.arange(ny) * CELL)
        cells = np.c_[X.ravel(), Y.ravel()]
        for bn, H, zbot in block:
            if bn.startswith('B_pons') or bn == 'R4_bridge_west_bed':
                d = dist_to_hulls(cells, [H]).reshape(ny, nx)
                Mb &= ~(d < 0.05)
        Zmin = nan_min_filter(Zt, 4)
        Zb = Zmin - BED_D
        for bn, H, zbot in block:                      # stay under the landing discs
            if bn.startswith('R1_road_landing'):
                d = dist_to_hulls(cells, [H]).reshape(ny, nx)
                near = d < 0.15
                Zb = np.where(near & np.isfinite(Zb), np.minimum(Zb, zbot - 0.012), Zb)
        Mb &= np.isfinite(Zb)
        grids.append(BedGrid(x0, y0, nx, ny, Zb, Mb))
        # mesh: one quad per bed cell, corner z = mean of the bed cells around it
        js, is_ = np.nonzero(Mb)
        Zc = np.where(Mb, Zb, 0.0); Mc_ = Mb.astype(float)
        Zp = np.pad(Zc, 1); Mp = np.pad(Mc_, 1)
        cs = Zp[:-1, :-1] + Zp[1:, :-1] + Zp[:-1, 1:] + Zp[1:, 1:]
        cn = Mp[:-1, :-1] + Mp[1:, :-1] + Mp[:-1, 1:] + Mp[1:, 1:]
        cz = np.where(cn > 0, cs / np.maximum(cn, 1), 0.0)               # (ny+1, nx+1) corners
        used = np.zeros((ny + 1, nx + 1), bool)
        for dj, di in ((0, 0), (0, 1), (1, 0), (1, 1)):
            used[js + dj, is_ + di] = True
        vid = -np.ones((ny + 1, nx + 1), np.int64)
        vj, vi = np.nonzero(used)
        base = sum(len(v) for v in verts_all)
        vid[vj, vi] = base + np.arange(len(vj))
        verts_all.append(np.c_[x0 + (vi - 0.5) * CELL, y0 + (vj - 0.5) * CELL, cz[vj, vi]])
        faces_all.append(np.c_[vid[js, is_], vid[js, is_ + 1], vid[js + 1, is_ + 1], vid[js + 1, is_]])
        info[name] = {'bed_cells': int(Mb.sum()), 'paving_top_faces': int(len(tops)), 'kerb_top_faces': int(len(kerb)),
                      'closing_added_cells': int((Mc & ~M0).sum())}
    V = np.vstack(verts_all); Fc = np.vstack(faces_all)
    me = bpy.data.meshes.get(BED_NAME)
    if me is None:
        me = bpy.data.meshes.new(BED_NAME)
    else:
        me.clear_geometry()
    me.from_pydata(V.tolist(), [], Fc.tolist())
    me.update()
    ob = bpy.data.objects.get(BED_NAME)
    if ob is None:
        ob = bpy.data.objects.new(BED_NAME, me)
        for col in need('R_core_road').users_collection:
            col.objects.link(ob)
    elif ob.data != me:
        ob.data = me
    ob.matrix_world = Matrix.Identity(4)
    pave = bpy.data.materials.get('RC.road.selce_basalt')
    if BED_HEX:
        m = bpy.data.materials.get(BED_MAT) or pave.copy()
        m.name = BED_MAT
        lin = hex_lin(BED_HEX); m.diffuse_color = (*lin, 1.0)
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    n.inputs['Base Color'].default_value = (*lin, 1.0)
        pave = m
    me.materials.clear(); me.materials.append(pave)
    ob.hide_render = False; ob.hide_viewport = False
    info['faces'] = len(me.polygons); info['material'] = pave.name; info['depth_below_min_top'] = BED_D
    log('paving_bed', info)
    return grids


def lower_road5_bed(grids):
    """road_core_se COLOR-25 / FORM-19: R1_road5_bed sank into / covered the pavers; it drops 0.12 and in any case
    0.03 under the new paving bed, so the pavers and the bed show and nothing z-fights."""
    o = need('R1_road5_bed'); W = world_verts(o)
    z = W[:, 2] - 0.12
    for g in grids:
        b = g.at(W[:, :2], grow=2)
        z = np.where(np.isfinite(b), np.minimum(z, b - 0.03), z)
    d = W[:, 2] - z
    W[:, 2] = z
    set_world_verts(o, W)
    log('road5_bed', {'lowered_by': np.round(d, 3).tolist()})


# ------------------------------------------------------------------ terrain
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def eval_world_verts(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg); me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    ev.to_mesh_clear()
    return (np.c_[co, np.ones(len(co))] @ np.array(o.matrix_world).T)[:, :3]


def ground_contacts(T, box, exclude, band=(-0.6, 0.45), cap=25000):
    """xy of the vertices of other render-visible objects (map + overlay) that lie near the ground in box."""
    x0, x1, y0, y1 = box
    pts, names = [], {}
    seen = set()
    for o in map_visible_objects() + overlay_objects():
        if o.name in seen or o.name in exclude or o.name in NOT_GROUND or o.name in OWNED_SET:
            continue
        seen.add(o.name)
        Wv = eval_world_verts(o)
        if not len(Wv):
            continue
        m = (Wv[:, 0] > x0) & (Wv[:, 0] < x1) & (Wv[:, 1] > y0) & (Wv[:, 1] < y1)
        if not m.any():
            continue
        sub = Wv[m]
        if len(sub) > cap:
            sub = sub[::len(sub) // cap + 1]
        tz = T.zs(sub[:, :2])
        dz = sub[:, 2] - tz
        k = np.isfinite(tz) & (dz > band[0]) & (dz < band[1])
        if k.any():
            pts.append(sub[k, :2]); names[o.name] = int(k.sum())
    return (np.vstack(pts) if pts else np.zeros((0, 2))), names


class TerrainEdit:
    """all T_land height edits are collected on a copy of the original z and written once."""
    def __init__(self):
        self.o = need('T_land')
        self.W0 = world_verts(self.o)
        self.xy = self.W0[:, :2]
        self.z0 = self.W0[:, 2].copy()
        self.z = self.z0.copy()
        ls, lt, lv, E = mesh_topo(self.o)
        self.ls, self.lt, self.lv, self.E = ls, lt, lv, E
        me = self.o.data
        fn = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fn)
        self.fnz = np.abs(fn.reshape(-1, 3)[:, 2])
        fidx = np.repeat(np.arange(len(ls)), lt)
        self.steep = np.zeros(len(self.z0), bool)
        self.steep[lv[(self.fnz < 0.7)[fidx]]] = True
        self.notes = {}

    def box(self, x0, x1, y0, y1):
        return np.nonzero((self.xy[:, 0] >= x0) & (self.xy[:, 0] <= x1) & (self.xy[:, 1] >= y0) & (self.xy[:, 1] <= y1))[0]

    def pin_limit(self, idx, pins, r0=0.35, fade=0.5):
        """largest |dz| allowed at idx given ground-contact points of other objects."""
        if len(pins) == 0:
            return np.full(len(idx), np.inf)
        d = KD2(pins).dists(self.xy[idx])
        return np.maximum(0.0, d - r0) * fade

    def blend_to(self, idx, target, w, lim=None):
        dz = w * (target - self.z[idx])
        if lim is not None:
            dz = np.clip(dz, -lim, lim)
        self.z[idx] += dz
        return dz

    def cap(self, idx, cap, lim=None):
        dz = np.minimum(0.0, cap - self.z[idx])
        dz = np.where(np.isfinite(dz), dz, 0.0)
        if lim is not None:
            dz = np.maximum(dz, -lim)
        self.z[idx] += dz
        return dz

    def write(self):
        W = self.W0.copy(); W[:, 2] = self.z
        set_world_verts(self.o, W)
        ch = np.abs(self.z - self.z0) > 1e-6
        return int(ch.sum()), round(float(np.abs(self.z - self.z0).max()), 3)


def op_hill(TE, T0, S):
    """ground_land OBJ_COLOR-07 (④ window) + support_ruin_observers RO-2: the crescent hill around the ruin scene
    (C5_researchers) and the ④ cube pits keeps its shape but its relief above the plain (z 0.9) is scaled x0.4 (soft
    knee), fading out towards the pine grove on its north-east crest and pinned under every object that stands on it.
    Around the ruin scene the ground is levelled to the scene's own base height for 2.6 units (25 pt) and blended
    into the lowered hill over the next 2.6 units, so no slope runs along its outline."""
    box = (38.0, 80.0, -42.0, -2.0)
    idx = TE.box(*box)
    z = TE.z[idx]; xy = TE.xy[idx]
    c, alpha, d0 = 0.9, 0.4, 0.25
    d = z - c
    f = np.where(d > 0, alpha * d + (1 - alpha) * d0 * (1 - np.exp(-np.maximum(d, 0) / d0)), d)
    zt = c + f
    fx = smoothstep(box[0], box[0] + 3, xy[:, 0]) * smoothstep(box[1], box[1] - 3, xy[:, 0])
    fy = smoothstep(box[2], box[2] + 3, xy[:, 1]) * smoothstep(box[3], box[3] - 3, xy[:, 1])
    grove = np.array((70.0, -12.0))
    fg = smoothstep(6.0, 14.0, np.linalg.norm(xy - grove, axis=1))
    w = fx * fy * fg
    target = z + w * (zt - z)
    # ruin scene: footprint raster + base height along its outline
    c5 = bpy.data.objects.get('C5_researchers')
    ring_info = None
    if c5 is not None:
        Wc = eval_world_verts(c5)
        tz = T0.zs(Wc[::3, :2]); sub = Wc[::3]
        cont = np.isfinite(tz) & (sub[:, 2] - tz > -0.6) & (sub[:, 2] - tz < 0.45)
        base = sub[cont]
        Tc = face_tris(c5, range(len(c5.data.polygons))) if False else None
        # footprint = cells covered by the projected (top-down) faces of the scene
        me = c5.data
        tri = []
        for p in me.polygons:
            v = list(p.vertices)
            for k in range(1, len(v) - 1):
                tri.append([v[0], v[k], v[k + 1]])
        tri = np.array(tri)
        Wl = world_verts(c5)
        fx0, fy0 = Wl[:, 0].min() - 0.2, Wl[:, 1].min() - 0.2
        nx = int((Wl[:, 0].max() + 0.2 - fx0) / CELL) + 2; ny = int((Wl[:, 1].max() + 0.2 - fy0) / CELL) + 2
        G = raster(Wl[tri], fx0, fy0, nx, ny, 'max')
        foot = np.isfinite(G)
        fj, fi = np.nonzero(foot)
        fcells = np.c_[fx0 + fi * CELL, fy0 + fj * CELL]
        edge = foot & ~erode(foot, 1)
        ej, ei = np.nonzero(edge)
        ecells = np.c_[fx0 + ei * CELL, fy0 + ej * CELL]
        rho = KD2(fcells).dists(xy)
        inside = np.zeros(len(xy), bool)
        ii = np.rint((xy[:, 0] - fx0) / CELL).astype(int); jj = np.rint((xy[:, 1] - fy0) / CELL).astype(int)
        ok = (ii >= 0) & (ii < nx) & (jj >= 0) & (jj < ny)
        inside[ok] = foot[jj[ok], ii[ok]]
        # base height at the outline: mean z of the base-contact vertices near each outline cell
        kb = KD2(base[:, :2])
        hz = np.empty(len(ecells))
        for n_, q in enumerate(ecells):
            res = kb.kd.find_n((q[0], q[1], 0.0), 6)
            hz[n_] = np.mean([base[i_, 2] for _, i_, _ in res])
        ke = KD2(ecells)
        near_e = np.array([ke.kd.find_n((p[0], p[1], 0.0), 4) for p in xy[rho < 6.0]], dtype=object)
        h_edge = np.full(len(xy), np.nan)
        h_edge[rho < 6.0] = [np.mean([hz[i_] for _, i_, _ in r]) for r in near_e]
        R1, R2 = 2.6, 5.2
        wr = 1.0 - smoothstep(R1, R2, rho)                 # 1 near the scene, 0 beyond R2
        ring = (~inside) & np.isfinite(h_edge) & (rho < R2)
        target[ring] = wr[ring] * (h_edge[ring] - 0.03) + (1 - wr[ring]) * target[ring]
        target[inside] = z[inside]
        ring_info = {'base_contact_vertices': int(len(base)), 'footprint_cells': int(foot.sum()),
                     'outline_base_z_min_med_max': np.round(np.percentile(hz, [0, 50, 100]), 3).tolist()}
    pins, names = ground_contacts(T0, box, exclude={'C5_researchers'})
    lim = TE.pin_limit(idx, pins)
    dz = TE.blend_to(idx, target, 1.0, lim)
    log('hill', {'vertices': int(len(idx)), 'lowered_max': round(float(-dz.min()), 3), 'raised_max': round(float(dz.max()), 3),
                 'pinned_objects': names, 'ruin_scene': ring_info})


def op_bench(TE, T0):
    """support_core5_lab OP-core5-01: the ground under the lab bench footprint (+0.4) is levelled to the bench's
    bottom (z_b - 0.01) and blended back over 1.6 units, so the bench no longer floats over the tilted ground."""
    b = need('R1_lab_bench'); Wb = world_verts(b); zb = float(Wb[:, 2].min())
    H = convex_hull(Wb[:, :2])
    lo = H.min(0) - 3; hi = H.max(0) + 3
    idx = TE.box(lo[0], hi[0], lo[1], hi[1])
    rho = poly_dist(TE.xy[idx], H)
    w = 1.0 - smoothstep(0.4, 2.0, rho)
    pins, names = ground_contacts(T0, (lo[0], hi[0], lo[1], hi[1]), exclude={'R1_lab_bench'})
    lim = TE.pin_limit(idx, pins)
    dz = TE.blend_to(idx, np.full(len(idx), zb - 0.01), w, lim)
    log('bench', {'bench_bottom_z': round(zb, 3), 'vertices': int((np.abs(dz) > 1e-6).sum()), 'raised_max': round(float(dz.max()), 3),
                  'lowered_max': round(float(-dz.min()), 3), 'pinned_objects': names})


def cone_cap_points(TE, idx, src_xy, src_cap, shoulder, slope, radius):
    """cap(p) = min over sources s of src_cap(s) + slope * max(0, |p - s| - shoulder), sources within radius."""
    kd = KDTree(len(src_xy))
    for i, p in enumerate(src_xy):
        kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    cap = np.full(len(idx), np.inf)
    for n_, vi in enumerate(idx):
        x, y = TE.xy[vi]
        for co, i_, d in kd.find_range((x, y, 0.0), radius):
            v = src_cap[i_] + slope * max(0.0, d - shoulder)
            if v < cap[n_]:
                cap[n_] = v
    return cap


def op_bed_cap(TE, grids):
    """the ground stays 0.025 under the paving bed (joints show bed, not ground)."""
    tot = 0; mx = 0.0
    for g in grids:
        x1 = g.x0 + g.nx * CELL; y1 = g.y0 + g.ny * CELL
        idx = TE.box(g.x0, x1, g.y0, y1)
        b = g.at(TE.xy[idx], grow=2)
        ok = np.isfinite(b)
        dz = TE.cap(idx[ok], b[ok] - 0.025)
        tot += int((dz < -1e-6).sum()); mx = max(mx, float(-dz.min()) if len(dz) else 0.0)
    log('bed_cap', {'vertices_lowered': tot, 'max_drop': round(mx, 3)})


def op_plate_cap(TE, T0, F):
    """fields_* OP03 / FORM-15 / COLOR-24: wherever the ground reaches within 0.03 of a field plate (or above it), it
    is lowered to plate - 0.03 (flat 0.25 beyond the plate, then a 0.5 slope), so no ground shows through a plate."""
    fid = np.nonzero(F.kind[F.flab] == 'plate')[0]
    tris = []
    for f in fid:
        v = F.lv[F.ls[f]:F.ls[f] + F.lt[f]]
        for k in range(1, len(v) - 1):
            tris.append(F.W[[v[0], v[k], v[k + 1]]])
    tris = np.array(tris)
    x0, y0 = tris[:, :, 0].min() - 1, tris[:, :, 1].min() - 1
    nx = int((tris[:, :, 0].max() + 1 - x0) / CELL) + 2; ny = int((tris[:, :, 1].max() + 1 - y0) / CELL) + 2
    G = raster(tris, x0, y0, nx, ny, 'min')
    jj, ii = np.nonzero(np.isfinite(G))
    src = np.c_[x0 + ii * CELL, y0 + jj * CELL]; scap = G[jj, ii] - 0.03
    # only terrain vertices that could violate: within reach and above (plate - 0.03 - 0.4)
    gi = np.rint((TE.xy[:, 0] - x0) / CELL).astype(int); gj = np.rint((TE.xy[:, 1] - y0) / CELL).astype(int)
    ok = (gi >= 3) & (gi < nx - 3) & (gj >= 3) & (gj < ny - 3)
    Gd = nan_min_filter(G, 8)
    cand = np.zeros(len(TE.z), bool)
    cand[ok] = np.isfinite(Gd[gj[ok], gi[ok]]) & (TE.z[ok] > Gd[gj[ok], gi[ok]] - 0.03)
    idx = np.nonzero(cand & ~TE.steep)[0]
    if len(idx) == 0:
        log('plate_cap', {'vertices_lowered': 0}); return
    cap = cone_cap_points(TE, idx, src, scap, 0.25, 0.5, 0.85)
    lo = TE.xy[idx].min(0) - 1; hi = TE.xy[idx].max(0) + 1
    pins, names = ground_contacts(T0, (lo[0], hi[0], lo[1], hi[1]), exclude=set())
    lim = TE.pin_limit(idx, pins)
    dz = TE.cap(idx, cap, lim)
    log('plate_cap', {'vertices_lowered': int((dz < -1e-6).sum()), 'max_drop': round(float(-dz.min()), 3),
                      'pinned_objects': len(names)})


WATER_Z = -0.40


def op_bridge_carve(TE, T0, S):
    """bridge_north / bridge_south OBJ_PLACE-02: beside and under the arch spans (masonry footprint + 0.8 across the
    deck, not past the abutments' outer faces) the bank is lowered to just above the water (z -0.38), rising back at
    a 0.5 slope; ground under the roads and other objects stays (pinned)."""
    res = {}
    for bn in ('B_pons1', 'B_pons2'):
        o = need(bn); W = world_verts(o)
        lab, flab, ls, lt, lv = islands(o)
        mas = [k for k in range(int(lab.max()) + 1) if W[lab == k, 2].min() < -0.5]
        Wm = W[np.isin(lab, mas)]
        # deck axis from the masonry footprint (PCA)
        c = Wm[:, :2].mean(0); U, s_, Vt = np.linalg.svd(Wm[:, :2] - c, full_matrices=False)
        ax = Vt[0]; pe = np.array((-ax[1], ax[0]))
        t = (Wm[:, :2] - c) @ ax; u = (Wm[:, :2] - c) @ pe
        tmin, tmax, umin, umax = t.min(), t.max(), u.min() - 0.8, u.max() + 0.8
        R = 3.0
        idx = TE.box(c[0] - 12, c[0] + 12, c[1] - 12, c[1] + 12)
        q = TE.xy[idx] - c
        tq = q @ ax; uq = q @ pe
        dt = np.maximum(0, np.maximum(tmin - tq, tq - tmax)); du = np.maximum(0, np.maximum(umin - uq, uq - umax))
        dist = np.hypot(dt, du)
        cap = WATER_Z + 0.02 + 0.5 * dist
        sel = dist < R
        pins, names = ground_contacts(T0, (c[0] - 12, c[0] + 12, c[1] - 12, c[1] + 12), exclude=set(), band=(-0.6, 0.45))
        # roads are WE objects (not in ground_contacts): pin their contacts explicitly
        rp = []
        for rn in ('R_core_road', 'R4_bridge_west_bed', BED_NAME):
            ro = bpy.data.objects.get(rn)
            if ro is None:
                continue
            Wr = world_verts(ro)
            m = (np.abs(Wr[:, 0] - c[0]) < 12) & (np.abs(Wr[:, 1] - c[1]) < 12)
            rp.append(Wr[m, :2])
        allp = np.vstack([pins] + rp) if len(rp) else pins
        lim = TE.pin_limit(idx[sel], allp, r0=0.25, fade=0.6)
        dz = TE.cap(idx[sel], cap[sel], lim)
        res[bn] = {'axis': ax.round(3).tolist(), 'span_t': [round(float(tmin), 2), round(float(tmax), 2)],
                   'vertices_lowered': int((dz < -1e-6).sum()), 'max_drop': round(float(-dz.min()), 3) if len(dz) else 0,
                   'pinned_objects': names}
    log('bridge_carve', res)


def bridge_clamp(T):
    """bridge_* OBJ_PLACE-02: no masonry vertex stays more than 0.05 under the ground (over land)."""
    res = {}
    for bn in ('B_pons1', 'B_pons2'):
        o = need(bn); W = world_verts(o)
        g = T.zs(W[:, :2])
        land = np.isfinite(g)
        newz = np.where(land, np.maximum(W[:, 2], g - 0.05), W[:, 2])
        res[bn] = {'vertices_raised': int((newz > W[:, 2] + 1e-6).sum()), 'max_raise': round(float((newz - W[:, 2]).max()), 3)}
        W[:, 2] = newz
        set_world_verts(o, W)
    log('bridge_clamp', res)


def cliff_creases(TE):
    """ground_land OBJ_FORM-20: the edges between near-vertical faces (cliffs, quay and bank walls, the diorama
    skirt) and the gently sloping ground above are marked sharp, so the cliff faces no longer take the top
    surface's fan normals (vertical seams)."""
    me = TE.o.data
    fnz = np.empty(len(me.polygons) * 3); me.polygons.foreach_get('normal', fnz); fnz = np.abs(fnz.reshape(-1, 3)[:, 2])
    bm = bmesh.new(); bm.from_mesh(me)
    sharp = np.zeros(len(me.edges), bool)
    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        fs = e.link_faces
        if len(fs) == 2:
            a, b = fnz[fs[0].index], fnz[fs[1].index]
            if min(a, b) < 0.35 and max(a, b) > 0.75:
                sharp[e.index] = True
    bm.free()
    a = me.attributes.get('sharp_edge')
    if a is None:
        a = me.attributes.new('sharp_edge', 'BOOLEAN', 'EDGE')
    cur = np.zeros(len(me.edges), bool); a.data.foreach_get('value', cur)
    a.data.foreach_set('value', cur | sharp)
    me.update()
    log('cliff_creases', {'edges_marked': int(sharp.sum())})
