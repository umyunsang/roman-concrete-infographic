import os
import sys, json
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas/c')
from m import *

OUT = os.environ.get('WC_OUT', '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas/c/out')

def segment(aid):
    A, oi, rgba, ctx, ids = load_asset(aid)
    s = A['scale']
    alpha = rgba[..., 3]
    mask = alpha > 127
    rgb = rgba[..., :3]
    H, W = mask.shape
    mats = {}
    for n in A['objects']:
        for mm in oi[n][1]['materials']:
            mats[mm['material']] = mm['diffuse_hex']
    mlist = list(mats)
    ramps = {mn: lab(ramp(mats[mn])) for mn in mlist}
    objmats = {}
    idnum = {}
    for n in A['objects']:
        k, o = oi[n]
        idnum[k] = (n, o['pass'])
        objmats[n] = [mm['material'] for mm in o['materials']]
    # object assignment
    objmap = np.full((H, W), '', dtype=object)
    ov = ids['overlay']; mp = ids['map']
    ys, xs = np.nonzero(mask)
    L = lab(rgb[ys, xs])
    # distance to each material ramp
    dist = np.zeros((len(ys), len(mlist)))
    for j, mn in enumerate(mlist):
        r = ramps[mn]
        for c0 in range(0, len(L), 20000):
            dist[c0:c0 + 20000, j] = de00(L[c0:c0 + 20000, None, :], r[None, :, :]).min(1)
    part = np.full(len(ys), -1)
    objn = np.full(len(ys), '', dtype=object)
    names = [idnum[k][0] for k in idnum]
    lab_img = np.zeros((H, W), int)
    for k, (n, p) in idnum.items():
        src = ov if p == 'overlay' else mp
        sel = (src == k) & mask
        if p == 'map':
            # overlay objects of this asset win
            sel &= ~np.isin(ov, [kk for kk, (nn, pp) in idnum.items() if pp == 'overlay'])
        lab_img[sel] = k
    valid = lab_img > 0
    if valid.any():
        _, (iy, ix) = ndi.distance_transform_edt(~valid, return_indices=True)
        filled = lab_img[iy, ix]
    else:
        filled = lab_img
    for t in range(len(ys)):
        y, x = ys[t], xs[t]
        k = filled[y, x]
        cand = idnum[k][0] if k in idnum else None
        if cand is not None:
            objn[t] = cand
            js = [mlist.index(mn) for mn in objmats[cand]]
            j = js[int(np.argmin(dist[t, js]))]
        else:
            j = int(np.argmin(dist[t]))
        part[t] = j
    P = np.full((H, W), -1); P[ys, xs] = part
    O = np.full((H, W), '', dtype=object); O[ys, xs] = objn
    mind = np.full((H, W), np.nan); mind[ys, xs] = dist[np.arange(len(ys)), part]
    return dict(A=A, rgb=rgb, mask=mask, ctx=ctx, P=P, O=O, mlist=mlist, mats=mats, mind=mind, s=s, objmats=objmats)

def stats(seg, j, erode_pt=1.5):
    s = seg['s']; P = seg['P']; rgb = seg['rgb']
    pm = P == j
    area_pt2 = pm.sum() / s / s
    e = int(round(erode_pt * s))
    inner = ndi.binary_erosion(pm, iterations=e)
    if inner.sum() < 68:
        inner = ndi.binary_erosion(pm, iterations=2)
    if inner.sum() < 10:
        inner = pm
    px = rgb[inner]
    Ls = lab(px)[:, 0]
    lo, hi = np.percentile(Ls, 60), np.percentile(Ls, 90)
    sel = (Ls >= lo) & (Ls <= hi)
    lit = px[sel].mean(0) if sel.sum() else px.mean(0)
    Lall = lab(rgb[pm])[:, 0]
    ys, xs = np.nonzero(pm)
    bw, bh = (xs.max() - xs.min() + 1) / s, (ys.max() - ys.min() + 1) / s
    return dict(area=area_pt2, n_inner=int(inner.sum()), lit=lit, lit_hex=hx(lit), litL=float(lab(lit)[0]),
                ok=oklch(lit), p95=float(np.percentile(Lall, 95)), p25=float(np.percentile(Lall, 25)),
                inner=inner, bbox=(bw, bh), med=np.median(px, 0))

if __name__ == '__main__':
    aid = sys.argv[1]
    seg = segment(aid)
    import pickle
    keep = {k: v for k, v in seg.items()}
    pickle.dump(keep, open(f'{OUT}/seg_{aid}.pkl', 'wb'))
    print('##', aid, seg['A']['crop_pt'])
    for j, mn in enumerate(seg['mlist']):
        if (seg['P'] == j).sum() == 0:
            print(mn, 'no px'); continue
        st = stats(seg, j)
        tok = h2r(seg['mats'][mn]); tok_ok = oklch(tok)
        print(f"{mn:45s} tok {seg['mats'][mn]} tokOk L{tok_ok[0]:.3f} C{tok_ok[1]:.3f} h{tok_ok[2]:.1f} | area {st['area']:.1f}pt2 bbox {st['bbox'][0]:.1f}x{st['bbox'][1]:.1f} | lit {st['lit_hex']} L*{st['litL']:.1f} C{st['ok'][1]:.3f} h{st['ok'][2]:.1f} | p95 {st['p95']:.1f} p25 {st['p25']:.1f} | inner {st['n_inner']}")
