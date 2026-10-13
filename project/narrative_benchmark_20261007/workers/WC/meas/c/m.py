import os
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SP = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad'
RL = SP + '/nb_work/review_loop'
import os
OR = os.environ.get('WC_ROOT', RL + '/obj_r11').rstrip('/')

# ---------- color library ----------
def s2l(c):
    c = np.asarray(c, float) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def l2s(l):
    l = np.clip(np.asarray(l, float), 0, 1)
    return 255 * np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)
M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
WP = np.array([0.95047, 1.0, 1.08883])
def lab(rgb):
    xyz = s2l(rgb) @ M.T / WP
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def de00(l1, l2):
    l1 = np.asarray(l1, float); l2 = np.asarray(l2, float)
    L1, a1, b1 = l1[..., 0], l1[..., 1], l1[..., 2]; L2, a2, b2 = l2[..., 0], l2[..., 1], l2[..., 2]
    C1 = np.hypot(a1, b1); C2 = np.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p = (1 + G) * a1; a2p = (1 + G) * a2
    C1p = np.hypot(a1p, b1); C2p = np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360; h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp = L2 - L1; dCp = C2p - C1p
    dhp = h2p - h1p; dhp = np.where(dhp > 180, dhp - 360, dhp); dhp = np.where(dhp < -180, dhp + 360, dhp)
    dhp = np.where(C1p * C2p == 0, 0, dhp)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp / 2))
    Lbp = (L1 + L2) / 2; Cbp = (C1p + C2p) / 2
    hsum = h1p + h2p
    hbp = np.where(np.abs(h1p - h2p) > 180, (hsum + 360) / 2, hsum / 2); hbp = np.where(C1p * C2p == 0, hsum, hbp)
    T = 1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp)) + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63))
    dth = 30 * np.exp(-((hbp - 275) / 25) ** 2)
    RC = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    RT = -np.sin(np.radians(2 * dth)) * RC
    return np.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))
def oklch(rgb):
    l = s2l(rgb)
    lms = l @ np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]]).T
    lms = np.cbrt(lms)
    L = lms @ np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]]).T
    C = np.hypot(L[..., 1], L[..., 2]); h = np.degrees(np.arctan2(L[..., 2], L[..., 1])) % 360
    return np.stack([L[..., 0], C, h], -1)
def h2r(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
def hx(c):
    c = np.clip(np.asarray(c).round(), 0, 255).astype(int); return '#%02X%02X%02X' % tuple(c[:3])
ND = {0.25: (8.37, 16.11, 19.46), 0.5: (6.74, 9.98, 13.34), 2: (5.47, 6.84, 7.99)}
def Dsz(lab1, lab2, deg):
    n = ND[deg]; d = np.asarray(lab1) - np.asarray(lab2)
    return float(np.sqrt((d[0] / (2 * n[0])) ** 2 + (d[1] / (2 * n[1])) ** 2 + (d[2] / (2 * n[2])) ** 2))
MACH = {
 'protan': np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
 'deutan': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
 'tritan': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}
def cvd(rgb, kind):
    l = s2l(rgb) @ MACH[kind].T
    return l2s(np.clip(l, 0, 1))
def wcag(c1, c2):
    def Y(c):
        l = s2l(c); return 0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]
    y1, y2 = Y(np.asarray(c1, float)), Y(np.asarray(c2, float))
    return float((max(y1, y2) + 0.05) / (min(y1, y2) + 0.05))
def ramp(hexc):
    lin = s2l(h2r(hexc))
    ks = np.linspace(0.15, 1.8, 60)
    return l2s(lin[None, :] * ks[:, None])
def deg_for(pt):
    return 0.25 if pt <= 12 else (0.5 if pt <= 50 else 2)

ACC = h2r('#983821'); ACCLAB = lab(ACC)

def load_asset(aid):
    idx = json.load(open(OR + '/assets_index.json'))
    inv = json.load(open(OR + '/inventory.json'))
    A = next(a for a in idx['assets'] if a['id'] == aid)
    objs = inv['objects']
    oi = {o['name']: (i + 1, o) for i, o in enumerate(objs)}
    rgba = np.array(Image.open(A['files']['isolated_rgba'])).astype(float)
    ctx = np.array(Image.open(A['files']['context']).convert('RGB')).astype(float)
    x0, x1, y0, y1 = A['crop_pt']; s = A['scale']
    H, W = rgba.shape[:2]
    # id maps upsampled to crop
    ids = {}
    for p, f in (('map', OR + '/idpass/id_id_map.png'), ('overlay', OR + '/idpass/id_id_overlay.png')):
        a = np.array(Image.open(f)).astype(int)
        ys = (y0 + (np.arange(H) + 0.5) / s) * 1.9992; xs = (x0 + (np.arange(W) + 0.5) / s) * 1.9992
        yi = np.clip(ys.astype(int), 0, a.shape[0] - 1); xi = np.clip(xs.astype(int), 0, a.shape[1] - 1)
        sub = a[yi][:, xi]
        k = ((sub[..., 0] - 2) // 4) + 64 * ((sub[..., 1] - 2) // 4) + 4096 * ((sub[..., 2] - 2) // 4)
        k[sub[..., 3] == 0] = 0
        ids[p] = k
    return A, oi, rgba, ctx, ids
