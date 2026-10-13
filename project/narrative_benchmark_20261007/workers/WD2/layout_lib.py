"""Offline screen-layout helpers for WD2 (numpy + PIL + scipy). 1 grid cell = 1/RES pt."""
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

W_PT, H_PT = 1191, 1684
WD = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work'


class Ctx:
    def __init__(self, idmap=WD + '/workers/WD2/probe/idmap_v8_14_1pt.npz', export=WD + '/workers/WD2/probe/export_v8_14.npz',
                 spec=WD + '/review_loop/text_spec_r11.json', poster=WD + '/review_loop/r11/poster_2x.png'):
        d = np.load(idmap)
        roi = [int(v) for v in d["roi"]]; self.ids = np.full((H_PT, W_PT), -1, np.int32); self.ids_ovl = np.full((H_PT, W_PT), -1, np.int32)
        self.ids[roi[2]:roi[3], roi[0]:roi[1]] = d["ids"]; self.ids_ovl[roi[2]:roi[3], roi[0]:roi[1]] = d["ids_ovl"]
        self.names = list(d["names"]); self.names_ovl = list(d["names_ovl"])
        self.E = np.load(export); self.M = self.E['M']
        self.spec = json.load(open(spec))
        self.poster = np.asarray(Image.open(poster).convert('RGB')).astype(np.float32)

    def project(self, W):
        W = np.asarray(W, float)
        H = np.c_[W, np.ones(len(W))] @ self.M.T
        ndc = H[:, :2] / H[:, 3:4]
        return np.c_[(ndc[:, 0] + 1) / 2 * W_PT, (1 - (ndc[:, 1] + 1) / 2) * H_PT]

    def mask_of(self, names):
        idx = [self.names.index(n) for n in names if n in self.names]
        return np.isin(self.ids, idx)

    def obj_world(self, key, loc=None, rot_z=None, scale=None, dz=0.0):
        co = self.E[key + '_co'].astype(float); mw = self.E[key + '_mw']
        if loc is None and rot_z is None and scale is None:
            Wv = (np.c_[co, np.ones(len(co))] @ mw.T)[:, :3]
        else:
            # rebuild matrix from given loc/rot_z/scale (assumes no x/y rotation)
            sx = np.linalg.norm(mw[:3, 0]); s = scale if scale is not None else sx
            rz = rot_z if rot_z is not None else np.arctan2(mw[1, 0], mw[0, 0])
            c, si = np.cos(rz), np.sin(rz)
            R = np.array([[c, -si, 0], [si, c, 0], [0, 0, 1]]) * s
            L = np.array(loc) if loc is not None else mw[:3, 3]
            Wv = co @ R.T + L
        Wv[:, 2] += dz
        return Wv

    def raster(self, P, tri, res=1.0, shape=(H_PT, W_PT)):
        """rasterise projected triangles into a mask at res cells per pt (default 1pt)."""
        im = Image.new('1', (int(shape[1] * res), int(shape[0] * res)), 0)
        dr = ImageDraw.Draw(im)
        Q = P * res
        for t in tri:
            dr.polygon([tuple(Q[t[0]]), tuple(Q[t[1]]), tuple(Q[t[2]])], fill=1)
        return np.asarray(im, bool)

    def silhouette(self, key, **kw):
        Wv = self.obj_world(key, **kw)
        P = self.project(Wv)
        return self.raster(P, self.E[key + '_tri']), Wv, P

    def text_mask(self, ids=None, rotated_ink=True):
        m = np.zeros((H_PT, W_PT), bool)
        L = 0.299 * self.poster[..., 0] + 0.587 * self.poster[..., 1] + 0.114 * self.poster[..., 2]
        ink2 = L < 140
        for t in self.spec['texts']:
            nid, (x, y, w, h), rot = t[0], t[1], t[2]
            if ids is not None and nid not in ids:
                continue
            x0, y0, x1, y1 = int(np.floor(x)), int(np.floor(y)), int(np.ceil(x + w)), int(np.ceil(y + h))
            if rot != 0 and rotated_ink:
                sub = ink2[y0 * 2:y1 * 2, x0 * 2:x1 * 2]
                sub = sub.reshape(sub.shape[0] // 2, 2, sub.shape[1] // 2, 2).any(axis=(1, 3))
                m[y0:y1, x0:x1] |= sub
            else:
                m[y0:y1, x0:x1] = True
        return m


def dist_to(mask):
    """distance (pt) from every cell to the nearest True cell of mask."""
    if not mask.any():
        return np.full(mask.shape, 1e9)
    return ndimage.distance_transform_edt(~mask)


def gap(a, b_dist):
    """min distance between mask a and the set whose distance field is b_dist."""
    if not a.any():
        return 1e9
    return float(b_dist[a].min())
