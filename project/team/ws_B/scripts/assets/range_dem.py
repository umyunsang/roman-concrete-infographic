"""워커 B · 비평 6: 아펜니노 봉우리들을 하나의 산줄기로 잇는 '실제 고도' 산괴(massif).
terrain_hf.py와 같은 화면→지리 변환으로 실제 DEM(z11)을 가는 화면 격자(1pt)에 깔고, 봉우리 밑을 지나는 등뼈 둘레 띠(envelope)로 잘라
→ assets/range_relief.npz (u0, v0, step, R: 높이(세계 단위), E: 띠 0..1)
시스템 python3: python3 range_dem.py <z11 타일 폴더>
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image
from scipy.interpolate import RegularGridInterpolator

ROOT = '/Users/um-yunsang/Documents/로마콘크리트_3D/team/ws_B/'
DEM_DIR = sys.argv[1]
Z = 11
STEP = 1.0
U0, U1, V0, V1 = 0.0, 1200.0, 200.0, 520.0
K_KM = float(os.environ.get('RG_K', 3.9))         # 세계 단위 / km (가로 축척 ≈ 1단위 350m → 약 1.15배 과장)
BASE_M = 230.0      # 이 고도 아래는 0 (캄파냐 평야)
SKIRT = float(os.environ.get('RG_SKIRT', 2.9))   # 봉우리 기슭 높이(세계 단위)


def smooth01(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def gblur(a, sig):
    r = int(3 * sig); x = np.arange(-r, r + 1); k = np.exp(-x * x / (2 * sig * sig)); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 0, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, mode='valid'), 1, a)


tiles = {}
for p in glob.glob(os.path.join(DEM_DIR, 't_*.png')):
    _, x, y = os.path.basename(p)[:-4].split('_'); tiles[(int(x), int(y))] = p
xs = sorted({k[0] for k in tiles}); ys = sorted({k[1] for k in tiles}); TX0, TY0 = xs[0], ys[0]
mos = np.zeros((len(ys) * 256, len(xs) * 256), dtype=np.float32)
for (x, y), p in tiles.items():
    a = np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)
    mos[(y - TY0) * 256:(y - TY0 + 1) * 256, (x - TX0) * 256:(x - TX0 + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768


def dem(lon, lat):
    n = 2 ** Z
    px = ((lon + 180) / 360 * n - TX0) * 256
    py = ((1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / math.pi) / 2 * n - TY0) * 256
    x0 = np.clip(np.floor(px).astype(int), 0, mos.shape[1] - 2); y0 = np.clip(np.floor(py).astype(int), 0, mos.shape[0] - 2)
    fx = np.clip(px - x0, 0, 1); fy = np.clip(py - y0, 0, 1)
    return (mos[y0, x0] * (1 - fx) + mos[y0, x0 + 1] * fx) * (1 - fy) + (mos[y0 + 1, x0] * (1 - fx) + mos[y0 + 1, x0 + 1] * fx) * fy


uu, vv = np.meshgrid(np.arange(U0, U1 + 1e-6, STEP), np.arange(V0, V1 + 1e-6, STEP), indexing='ij')
LAT0, LON0 = 42.0, 12.8
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 111.0
gA = complex((12.565 - LON0) * KX, (42.075 - LAT0) * KY); gB = complex((13.02 - LON0) * KX, (41.95 - LAT0) * KY)
sA = complex(240.0, -530.0); sB = complex(1060.0, -392.0)
T = (sB - sA) / (gB - gA)
def dem_screen(u, v):
    g_ = (u - 1j * v - sA) / T + gA
    return dem(LON0 + g_.real / KX, LAT0 + g_.imag / KY)


# 화면 왼쪽(u<500)은 실제로 티베르 골짜기·평야라 산이 없음 → 산지 다른 곳(u+560, v+120; 지도에서 평야로 덮여 안 보이는 자리)의 실제 고도를 빌려 이음
_w = smooth01((uu - 470) / 90.0)
D = _w * dem_screen(uu, vv) + (1 - _w) * dem_screen(uu + 560.0, vv + 120.0)
D = gblur(D, 2.4 / STEP)   # 워커 B: 0.8→2.4, 높이맵이 세로로 늘어난 듯한 잔줄 완화
Rr = np.clip(D - BASE_M, 0, None) / 1000.0 * K_KM

# 세계 좌표(원근 사다리꼴) — full_grid의 3.5pt 격자에서 보간
G = np.load(ROOT + 'assets/full_grid.npz')
gu, gv = G['u'][:, 0], G['v'][0, :]
WX = RegularGridInterpolator((gu, gv), G['wx'])(np.c_[uu.ravel(), vv.ravel()]).reshape(uu.shape)
WY = RegularGridInterpolator((gu, gv), G['wy'])(np.c_[uu.ravel(), vv.ravel()]).reshape(uu.shape)
FOOT = json.load(open(ROOT + 'assets/object_footprints.json'))


def wpt(u, v):
    i = int(np.clip(round((u - U0) / STEP), 0, uu.shape[0] - 1)); j = int(np.clip(round((v - V0) / STEP), 0, uu.shape[1] - 1))
    return WX[i, j], WY[i, j]


pk = {k: b for k, b in FOOT.items() if k.startswith('L01_')}
main = sorted([k for k in pk if k != 'L01_terminillo'], key=lambda k: pk[k][0])
sp = np.array([wpt((pk[k][0] + pk[k][2]) / 2, pk[k][1] * 0.45 + pk[k][3] * 0.55) for k in main])
sp = np.r_[[sp[0] + (sp[0] - sp[1]) * 0.35], sp, [sp[-1] + (sp[-1] - sp[-2]) * 0.9]]
seg = np.r_[0, np.cumsum(np.hypot(*np.diff(sp, axis=0).T))]
ss = np.linspace(0, seg[-1], 300)
SP = np.c_[np.interp(ss, seg, sp[:, 0]), np.interp(ss, seg, sp[:, 1])]
for _ in range(4):
    SP[1:-1] = 0.25 * SP[:-2] + 0.5 * SP[1:-1] + 0.25 * SP[2:]
d2 = np.full(WX.shape, 1e18); off = np.zeros(WX.shape); sat = np.zeros(WX.shape)
for k in range(len(SP)):
    dx, dy = WX - SP[k, 0], WY - SP[k, 1]
    dd = dx * dx + dy * dy
    m = dd < d2
    d2 = np.where(m, dd, d2); off = np.where(m, dx - dy, off); sat = np.where(m, ss[k], sat)
dr = np.sqrt(d2)
SIG_F, SIG_B = float(os.environ.get('RG_SIGF', 7.0)), float(os.environ.get('RG_SIGB', 12.0))
_sf = SIG_F * (1 + 0.28 * np.sin(sat / 8.5 + 0.7) + 0.16 * np.sin(sat / 3.7 + 2.1))   # 앞 기슭선이 들쭉날쭉(띠 모양 아님)
E = np.where(off > 0, np.exp(-(dr / _sf) ** 2 / 2), np.exp(-(dr / SIG_B) ** 2 / 2))
E *= smooth01((uu - 200) / 45.0)                       # 티베르 발원 골짜기 왼쪽은 따로
E *= smooth01((vv - 248) / 34.0)                       # 머리말(헤더) 글 밑은 평탄


def box_mask(boxes, pad, soft):
    m = np.zeros(uu.shape)
    for b in boxes:
        dx = np.maximum(np.maximum(b[0] - pad - uu, uu - b[2] - pad), 0); dy = np.maximum(np.maximum(b[1] - pad - vv, vv - b[3] - pad), 0)
        m = np.maximum(m, 1 - smooth01(np.hypot(dx, dy) / soft))
    return m


_TJ = json.load(open(ROOT + 'loop/figma_texts.json'))
TXT = [t['b'] for t in _TJ if t['kind'] not in ('title', 'header', 'timeline', 'place', 'label')]


def ell_mask(boxes, pad, soft):
    """글 상자를 감싸는 타원(빈터) — 네모 계단 없이 둥근 분지처럼 낮아짐"""
    m = np.zeros(uu.shape)
    for b in boxes:
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        rx, ry = (b[2] - b[0]) / 2 * 1.42 + pad, (b[3] - b[1]) / 2 * 1.42 + pad
        d = np.sqrt(((uu - cx) / rx) ** 2 + ((vv - cy) / ry) ** 2)      # 1 = 타원 둘레
        m = np.maximum(m, 1 - smooth01((d - 1) * min(rx, ry) / soft))
    return m
TXT_S = [t['b'] for t in _TJ if t['kind'] in ('place', 'label')]   # 지명·라벨(작은 글)은 둘레를 좁게만 낮춤 — 봉우리 기슭이 평평하게 깎여 절벽처럼 보이던 것
OBJ = [b for k, b in FOOT.items() if not k.startswith('L01_') and b[1] < 560]
E *= (1 - box_mask(TXT, 4.0, 32.0)) * (1 - ell_mask(TXT_S, 2.0, 22.0))          # 글 상자 둘레는 둥글고 완만하게 낮아짐(네모 홈 없이)
E *= 1 - box_mask(OBJ, 2.0, 34.0)   # 워커 B: 물체 둘레 산괴를 넓게 완만히 낮춤(가파른 분지 벽이 커튼 줄무늬로 보이던 것)
# 강(티베르) 둘레
P = json.load(open(ROOT + 'assets/terrain_polys.json'))
riv = np.asarray(P['river'][0][0])
best = np.full(uu.shape, 1e9)
for (ax, ay), (bx, by) in zip(riv[:-1], riv[1:]):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy + 1e-12
    t = np.clip(((uu - ax) * dx + (vv - ay) * dy) / L2, 0, 1)
    best = np.minimum(best, np.hypot(uu - (ax + t * dx), vv - (ay + t * dy)))
E *= smooth01((best - 8) / 30.0)
R = Rr * E
# 봉우리 밑 기슭(skirt): 봉우리 발자국 타원마다 둥근 기슭 + 실제 고도의 잔주름 → 봉우리 아랫단이 기슭에 묻혀 '탁자 위 바위'가 아님
Dd = D - gblur(D, 5.0 / STEP)
detail = 1 + 0.45 * np.tanh(Dd / 90.0)
S = np.zeros(uu.shape); S_plain = np.zeros(uu.shape)
for k, b in pk.items():
    cx, cy = (b[0] + b[2]) / 2, b[1] * 0.4 + b[3] * 0.6
    rx, ry = (b[2] - b[0]) / 2 * 1.05 + 10, (b[3] - b[1]) / 2 * 1.25 + 10
    if k == 'L01_terminillo':
        # 왼쪽 끝 외딴 봉우리: 실제 고도 잔주름 없이 둥근 기슭(빌려 온 DEM 주름이 세로 줄무늬로 보이던 것)
        S_plain = np.maximum(S_plain, SKIRT * 0.85 * np.exp(-(((uu - cx) / (rx * 1.1)) ** 2 + ((vv - cy) / (ry * 1.1)) ** 2) * 1.4))
        continue
    S = np.maximum(S, SKIRT * np.exp(-(((uu - cx) / rx) ** 2 + ((vv - cy) / ry) ** 2) ** 1.3 * 1.6))
S *= (1 - box_mask(TXT, 4.0, 30.0)) * (1 - ell_mask(TXT_S, 2.0, 18.0)) * (1 - box_mask(OBJ, 2.0, 30.0)) * smooth01((best - 8) / 30.0) * smooth01((vv - 248) / 34.0)
S_plain *= (1 - ell_mask(TXT_S, 2.0, 18.0)) * (1 - box_mask(OBJ, 2.0, 30.0)) * smooth01((best - 8) / 30.0) * smooth01((vv - 248) / 34.0)
R = np.maximum(R, S * detail) + 0.25 * np.minimum(R, S * detail)
R = np.maximum(R, S_plain)
np.savez_compressed(ROOT + 'assets/range_relief.npz', u0=U0, v0=V0, step=STEP, R=R.astype(np.float32), E=E.astype(np.float32))
print('range relief', R.shape, 'max', float(R.max()), 'mean in band', float(R[E > 0.5].mean()), 'band px', int((E > 0.02).sum()))
# 미리보기: 언덕 음영
gy_, gx_ = np.gradient(R * 7.0, STEP)
shade = np.clip(0.75 + 0.6 * (-gx_ * 0.6 + gy_ * 0.8) / np.sqrt(1 + gx_ ** 2 + gy_ ** 2), 0, 1)
Image.fromarray((shade.T * 255).astype(np.uint8)).save(os.environ.get('RG_PREVIEW', '/tmp/range_preview.png'))
