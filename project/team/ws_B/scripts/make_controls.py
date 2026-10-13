"""스케치 SVG → ComfyUI 제어 이미지 4종.

출력(comfy/inputs/):
- start_color.png  : 로마 팔레트로 칠하고 스케치 명암을 3단 음영으로 옮긴 '색칠 디오라마 초안'(img2img 시작점)
- edges.png        : 면 경계선(검정 바탕 흰 선) — ControlNet Canny/경계 입력
- gray.png         : 글 없는 회색 다이어그램(캔버스 크기)
- masks/*.png      : 물체 묶음별 마스크(인페인트·영역 프롬프트용)
캔버스: 너비 W, 프레임 1191pt를 균일 배율 s로 그리고 아래쪽만 여백(늘이지 않음).
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.expanduser('~/Documents/로마콘크리트_3D')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from palette import PALETTE, oklch_to_linear_srgb, linear_to_hex  # noqa: E402
from svg_objects import objects  # noqa: E402

W = int(os.environ.get('CANVAS_W', 1216))
S = W / 1191.0
H = int(math.ceil(1684 * S / 16.0) * 16)
SS = 3  # 초표본(안티에일리어싱)
OUT = os.path.join(ROOT, 'comfy', 'inputs')
os.makedirs(os.path.join(OUT, 'masks'), exist_ok=True)


def srgb(key, f=1.0, tint=0.0):
    """팔레트 색(선형) × 명암 f, 그늘 라벤더 tint → sRGB 0~255."""
    lin = oklch_to_linear_srgb(*PALETTE[key][:3])
    lav = oklch_to_linear_srgb(0.62, 0.055, 285)
    c = [(1 - tint) * a + tint * b for a, b in zip(lin, lav)]
    c = [v * f for v in c]
    h = linear_to_hex(c)
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def gray_of(fill):
    if fill in ('white', '#FFFFFF', '#ffffff'):
        return 255
    if fill.startswith('#') and len(fill) == 7:
        r, g, b = (int(fill[i:i + 2], 16) for i in (1, 3, 5))
        return (r + g + b) / 3
    return 200


def shade(g):
    """스케치 회색값 → 3단 툰(밝은 면 1.0 / 중간 0.87 / 그늘 0.72+라벤더), 아주 어두운 개구부 0.45."""
    if g >= 225:
        return 1.0, 0.0
    if g >= 170:
        return 0.87, 0.05
    if g >= 95:
        return 0.72, 0.22
    return 0.45, 0.35


def load(name):
    return [i for i in json.load(open(os.path.join(ROOT, 'ref', 'svg', f'{name}.json')))
            if i['fill'] != 'none' and i['closed'] and i['bbox'] != [0, 0, 1191, 1684]]


def ring_path():
    it = json.load(open(os.path.join(ROOT, 'ref', 'svg', 'path.json')))
    best = max((i for i in it if not i['closed']), key=lambda i: len(i['pts']))
    return best['pts']


RING = ring_path()


def dist_to_ring(x, y):
    d = 1e9
    for (ax, ay), (bx, by) in zip(RING, RING[1:]):
        vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy or 1
        t = max(0, min(1, ((x - ax) * vx + (y - ay) * vy) / L))
        d = min(d, math.hypot(ax + t * vx - x, ay + t * vy - y))
    return d


def inside(b, x0, y0, x1, y1):
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return x0 <= cx <= x1 and y0 <= cy <= y1


def classify(layer, ob):
    b = ob['bbox']; w, h = b[2] - b[0], b[3] - b[1]
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    if layer == 'back':
        if b[1] < 330 and h > 40:
            return 'mountain'
        if inside(b, 790, 330, 1020, 545):
            return 'aqueduct'
        if inside(b, 130, 600, 185, 720):
            return 'kiln'
        if (inside(b, 930, 330, 1191, 560) or inside(b, 0, 370, 200, 625)) and w > 60:
            return 'hill'
        if dist_to_ring(cx, b[3] - 8) < 26 or dist_to_ring(cx, cy) < 22:
            return 'wall'
        return 'house'
    if layer == 'front':
        if inside(b, 880, 1340, 1500, 1800) and w > 40:
            return 'volcano'
        if b[0] >= 1000 and b[3] <= 1420 and b[1] >= 1250 and w < 70:
            return 'smoke'
        if inside(b, 120, 1380, 370, 1540):
            return 'harbor'
        if inside(b, 800, 1390, 960, 1495) and w > 100:
            return 'plaza'
        if (inside(b, 300, 780, 600, 990) or inside(b, 980, 1000, 1185, 1155)) and w > 70:
            return 'hill'
        if inside(b, 750, 825, 890, 930) and w > 90:
            return 'plaza'
        if inside(b, 620, 910, 790, 1050) and w > 120:
            return 'plaza'
        if w < 12 and h > 20:
            return 'tree'
        if dist_to_ring(cx, b[3] - 8) < 26 or dist_to_ring(cx, cy) < 22 or h > 150:
            return 'wall'
        return 'house'
    return 'house'


def face_color(cls, f, ob_bbox):
    g = gray_of(f['fill']); k, t = shade(g)
    fb = f['bbox']; fcy = (fb[1] + fb[3]) / 2
    top = ob_bbox[1] + 0.45 * (ob_bbox[3] - ob_bbox[1])
    if cls == 'house':
        key = 'terracotta' if (fcy <= top and g < 245) else 'house_wall'
        if g >= 240 and fcy <= top:
            key = 'terracotta'; k = 1.0
    elif cls == 'mountain':
        key = 'mountain'
    elif cls in ('wall', 'aqueduct', 'harbor'):
        key = 'tuff_stone'
    elif cls == 'hill':
        key = 'ochre_field' if g >= 225 else 'tuff_stone'
    elif cls == 'kiln':
        key = 'terracotta'
    elif cls == 'volcano':
        key = 'volcano_dark' if g < 110 else 'volcano_ash'
    elif cls == 'smoke':
        key = 'sky_ambient'; k, t = (1.0, 0.0) if g >= 225 else (0.9, 0.1)
    elif cls == 'plaza':
        key = 'ground_road' if g >= 225 else 'tuff_stone'
    elif cls == 'tree':
        return (96, 128, 92)
    else:
        key = 'house_wall'
    return srgb(key, k, t)


def P(pts):
    return [(x * S * SS, y * S * SS) for x, y in pts]


def main():
    big = (W * SS, H * SS)
    col = Image.new('RGB', big, srgb('ground_meadow'))
    edg = Image.new('L', big, 0)
    ids = Image.new('I', big, 0)
    dc, de, di = ImageDraw.Draw(col), ImageDraw.Draw(edg), ImageDraw.Draw(ids)
    face_counter = [1]

    def idpoly(pts):
        di.polygon(pts, fill=face_counter[0]); face_counter[0] += 1
    masks = {}

    def mask(name):
        if name not in masks:
            masks[name] = Image.new('L', big, 0)
        return ImageDraw.Draw(masks[name])

    lw = max(1, int(round(1.4 * SS)))
    # 1) 땅: 위쪽 띠·도로·밭·해안 염전
    for f in load('ground'):
        fill = f['fill']; b = f['bbox']
        if b[1] == 0 and b[3] <= 300:
            c = srgb('sky_ambient')
        elif fill in ('#DEDEDE',) and f['stroke'] == '#555555':
            c = srgb('ground_road'); mask('roads').polygon(P(f['pts']), fill=255)
        elif fill in ('#D4D4D4', '#DADADA', '#E2E2E2', '#DEDEDE'):
            c = srgb('ochre_field', 1.0 if fill in ('#E2E2E2', '#DEDEDE') else 0.93); mask('fields').polygon(P(f['pts']), fill=255)
        elif fill == '#F4F4F4':
            c = srgb('ground_road', 0.97)
        elif fill == '#999999':
            c = srgb('ground_meadow', 0.75, 0.1)
        else:
            continue
        dc.polygon(P(f['pts']), fill=c)
        if fill != '#999999':
            idpoly(P(f['pts']))
    # 2) 물
    for f in load('water'):
        fill = f['fill']
        key, mname = {'#CDCDCD': ('water_sea', 'sea'), '#B0B0B0': ('ochre_field', 'coast'), '#B3B3B3': ('water_river', 'river')}.get(fill, (None, None))
        if not key:
            continue
        dc.polygon(P(f['pts']), fill=srgb(key, 0.97 if mname == 'coast' else 1.0))
        idpoly(P(f['pts']))
        mask(mname).polygon(P(f['pts']), fill=255)
    # 3) 입체: 뒤 → 콜로세움 → 앞 → 실험실 (SVG 칠 순서 유지)
    stats = {}
    for layer in ('back', 'colosseum', 'front', 'lab'):
        faces = load(layer)
        cls_of = {}
        if layer in ('back', 'front'):
            for ob in objects(os.path.join(ROOT, 'ref', 'svg', f'{layer}.json')):
                c = classify(layer, ob)
                stats[(layer, c)] = stats.get((layer, c), 0) + 1
                for fid in ob['ids']:
                    cls_of[fid] = (c, ob['bbox'])
        for f in faces:
            if layer == 'colosseum':
                cls, ob_b = 'colosseum', f['bbox']
                g = gray_of(f['fill']); k, t = shade(g)
                c = srgb('travertine', k, t)
            elif layer == 'lab':
                cls, ob_b = 'lab', f['bbox']
                g = gray_of(f['fill']); k, t = shade(g)
                c = srgb('house_wall' if g >= 200 else 'tuff_stone', k, t)
            else:
                cls, ob_b = cls_of.get(f['id'], ('house', f['bbox']))
                c = face_color(cls, f, ob_b)
            dc.polygon(P(f['pts']), fill=c)
            idpoly(P(f['pts']))
            mask(cls).polygon(P(f['pts']), fill=255)
    # 보이는 경계: ID가 바뀌는 픽셀
    import numpy as np
    a = np.asarray(ids, dtype=np.int64)
    e = np.zeros(a.shape, bool)
    e[:, 1:] |= a[:, 1:] != a[:, :-1]; e[1:, :] |= a[1:, :] != a[:-1, :]
    edg = Image.fromarray((e * 255).astype('uint8')).filter(ImageFilter.MaxFilter(lw | 1))
    # 저장
    col.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, 'start_color.png'))
    edg.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, 'edges.png'))
    gray = Image.open(os.path.join(OUT, 'map_textless_2x.png')).convert('L')
    gw, gh = W, int(round(1684 * S))
    g2 = Image.new('L', (W, H), 235); g2.paste(gray.resize((gw, gh), Image.LANCZOS), (0, 0))
    g2.save(os.path.join(OUT, 'gray.png'))
    for name, m in masks.items():
        m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.MaxFilter(5))
        m.save(os.path.join(OUT, 'masks', f'{name}.png'))
    json.dump({'canvas': [W, H], 'scale_px_per_pt': S, 'pad_bottom_px': H - 1684 * S,
               'classes': {f'{k[0]}:{k[1]}': v for k, v in sorted(stats.items())}},
              open(os.path.join(OUT, 'controls_meta.json'), 'w'), ensure_ascii=False, indent=1)
    print('canvas', W, H, 'scale', round(S, 5), 'masks', sorted(masks))
    print({f'{k[0]}:{k[1]}': v for k, v in sorted(stats.items())})


if __name__ == '__main__':
    main()
