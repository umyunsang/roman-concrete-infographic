"""개념도 v3: 커진 성벽 고리를 CORE 글 레이아웃 뼈대로 쓰는 A안(벽면 새김)·B안(보루 위 수평 글).

아이소 투영(화면 pt, y 아래로): 땅 X → (0.7071, +0.4082), 땅 Y → (0.7071, −0.4082), 높이 Z → (0, −0.8165).
성벽: 아이소 축에 맞춘 팔각형(변 방향 = X, Y, 두 대각선). 앞 변(6시)은 정면을 향해 글이 기울지 않음.
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.expanduser('~/Documents/로마콘크리트_3D')
W, H = 1191, 1684
CX, CY = 595, 860          # 성벽 고리 땅 중심(화면)
R = 520                    # 팔각형 외접 반지름(땅 단위 = pt) — build()에서 변형별로 바꿈
WALL_H, WALL_T = 52, 26    # 성벽 높이·두께
FP = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
FB = ImageFont.truetype(FP, 20, index=6)   # Bold
FR = ImageFont.truetype(FP, 11, index=0)
FD = ImageFont.truetype(FP, 13, index=6)
FDR = ImageFont.truetype(FP, 10, index=0)

CORE = {
    1: ('굳은 뒤에도 단단해지는 재료', ['석회+화산재+물이 돌처럼 굳고', '바닷물 속에서 새 결정이 자람']),
    2: ('뜨겁게 섞어 빨리 굳힘', ['마른 석회에 물을 부으면 뜨겁게 굳고', '남은 석회 알갱이가 ❹의 재료']),
    3: ('누르는 힘만 받게 짓기', ['아치·둥근 천장이 누르는 힘만 받고', '아래는 무겁게, 위는 가볍게']),
    4: ('금이 가도 메우고, 쓰면서 고침', ['금에 스민 물이 석회를 녹였다 다시 굳힘', '계속 쓰인 건물은 계속 고쳐짐']),
    5: ('약 1,950년째 서 있음', ['80년에 지은 콜로세움이', '지금도 로마에 서 있음']),
}
DETAIL = {
    1: ('재료 원리 · 해수 속 새 결정', ['바닷물이 스미면 보통 온도에서도', '새 결정이 자라 틈을 메움']),
    2: ('제작 원리 · 열과 석회', ['생석회가 물을 만나 열을 냄', '다 녹지 않은 알갱이가 남음']),
    3: ('구조 원리 · 벽과 기초', ['아래는 무거운 돌, 위는 가벼운 돌', '12m 넘는 기초 고리']),
    4: ('균열 원리 · 금이 메워지는 순서', ['금 → 물이 스밈 → 석회가 녹음', '다시 굳어 금을 메움']),
}


def iso(X, Y, Z=0.0):
    return (CX + 0.7071 * (X + Y), CY + 0.4082 * (X - Y) - 0.8165 * Z)


def octagon(r):
    return [(r * math.cos(math.radians(22.5 + 45 * k)), r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]


def background():
    base = Image.open(os.path.join(ROOT, 'comfy', 'inputs', 'map_textless_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    paper = Image.new('RGB', (W, H), (246, 246, 246))
    # 가운데(옛 성벽·도시)는 지우고 바깥 지형만 옅게
    m = Image.new('L', (W, H), 255); dm = ImageDraw.Draw(m)
    dm.ellipse([CX - 610, CY - 380, CX + 610, CY + 360], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(40))
    bg = Image.composite(Image.blend(base, paper, 0.45), paper, m)
    # 커진 콜로세움(1.35배) — 원래 콜로세움 영역을 잘라 확대
    col = base.crop((450, 605, 835, 985)); s = 1.35
    col = col.resize((int(col.width * s), int(col.height * s)), Image.LANCZOS)
    cm = Image.new('L', col.size, 0); ImageDraw.Draw(cm).ellipse([8, 8, col.width - 8, col.height - 8], fill=255)
    cm = cm.filter(ImageFilter.GaussianBlur(10))
    bg.paste(col, (int(CX - col.width / 2), int(CY - 90 - col.height / 2)), cm)
    # 제목 띠(최종안 위쪽 그대로)
    top = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS).crop((0, 0, W, 240))
    bg.paste(top, (0, 0))
    return bg


def face_poly(p, q, z0, z1, off):
    """땅 선분 p→q를 off만큼 밀어낸 수직 면(z0~z1)의 화면 다각형."""
    (x0, y0), (x1, y1) = p, q
    return [iso(x0 + off[0], y0 + off[1], z0), iso(x1 + off[0], y1 + off[1], z0),
            iso(x1 + off[0], y1 + off[1], z1), iso(x0 + off[0], y0 + off[1], z1)]


def draw_wall(d, gaps=()):
    """팔각 성벽(두께 있는 상자 8개) — 먼 변부터. 보이는 면만 칠한다."""
    outer, inner = octagon(R + WALL_T / 2), octagon(R - WALL_T / 2)
    segs = []
    for k in range(8):
        a, b = outer[k], outer[(k + 1) % 8]; ai, bi = inner[k], inner[(k + 1) % 8]
        mid = iso((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        segs.append((mid[1], k, a, b, ai, bi))
    segs.sort()
    faces = {}
    for _, k, a, b, ai, bi in segs:
        nx, ny = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
        vis_out = (nx - ny) > 0.05      # 바깥 면이 카메라(+X, −Y) 쪽을 향함
        top = [iso(*a, WALL_H), iso(*b, WALL_H), iso(*bi, WALL_H), iso(*ai, WALL_H)]
        if not vis_out:
            d.polygon([iso(*ai, 0), iso(*bi, 0), iso(*bi, WALL_H), iso(*ai, WALL_H)], fill=(214, 214, 214), outline=(70, 70, 70))
            faces[k] = ('inner', ai, bi)
        d.polygon(top, fill=(238, 238, 238), outline=(70, 70, 70))
        if vis_out:
            d.polygon([iso(*a, 0), iso(*b, 0), iso(*b, WALL_H), iso(*a, WALL_H)], fill=(196, 196, 196), outline=(70, 70, 70))
            faces[k] = ('outer', a, b)
        # 총안(톱니) 몇 개
        for t in (0.15, 0.35, 0.55, 0.75):
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            q = (px + (b[0] - a[0]) * 0.08, py + (b[1] - a[1]) * 0.08)
            d.polygon([iso(px, py, WALL_H), iso(*q, WALL_H), iso(*q, WALL_H + 8), iso(px, py, WALL_H + 8)], fill=(225, 225, 225), outline=(90, 90, 90))
    return faces


def ring_point(k, t=0.5, z=WALL_H, r=R):
    oc = octagon(r); a, b = oc[k], oc[(k + 1) % 8]
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def text_block(d, x, y, title, lines, core=True, num=None, anchor='mm'):
    f1, f2 = (FB, FR) if core else (FD, FDR)
    lh = 15 if core else 13
    tw = max([d.textlength(title, font=f1) + (26 if num else 0)] + [d.textlength(l, font=f2) for l in lines])
    th = (24 if core else 17) + lh * len(lines)
    x0 = x - tw / 2 if anchor == 'mm' else x
    x0 = max(24, min(W - 24 - tw, x0))
    y0 = y - th / 2
    if num:
        d.ellipse([x0, y0 + 2, x0 + 20, y0 + 22], fill=(17, 17, 17)); d.text((x0 + 10, y0 + 12), str(num), font=FD, fill='white', anchor='mm')
    d.text((x0 + (26 if num else 0), y0), title, font=f1, fill=(17, 17, 17))
    for i, l in enumerate(lines):
        d.text((x0, y0 + (26 if core else 18) + i * lh), l, font=f2, fill=(40, 40, 40) if core else (90, 90, 90))
    return (x0, y0, x0 + tw, y0 + th)


def sheared_text(img, title, lines, num, p_a, p_b, z0, z1, off):
    """글을 그린 뒤 벽면(평행사변형)에 아핀 변환으로 붙인다(A안)."""
    tw, th = 420, 120
    t = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.ellipse([6, 22, 34, 50], fill=(17, 17, 17)); d.text((20, 36), str(num), font=ImageFont.truetype(FP, 18, index=6), fill='white', anchor='mm')
    d.text((44, 18), title, font=ImageFont.truetype(FP, 30, index=6), fill=(17, 17, 17))
    for i, l in enumerate(lines):
        d.text((8, 60 + i * 28), l, font=ImageFont.truetype(FP, 22, index=0), fill=(35, 35, 35))
    poly = face_poly(p_a, p_b, z0, z1, off)   # [아래왼, 아래오, 위오, 위왼]
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = poly
    # 출력 (X,Y) = 위왼 + u*(위오−위왼)/tw + v*(아래왼−위왼)/th 의 역변환
    ax, ay = (x2 - x3) / tw, (y2 - y3) / tw
    bx, by = (x0 - x3) / th, (y0 - y3) / th
    det = ax * by - ay * bx
    inv = (by / det, -bx / det, (bx * y3 - by * x3) / det, -ay / det, ax / det, (ay * x3 - ax * y3) / det)
    warped = t.transform(img.size, Image.AFFINE, inv, resample=Image.BICUBIC)
    img.paste(warped, (0, 0), warped)


def perimeter(u0, u1, r):
    oc = octagon(r); out = []
    k0, k1 = int(u0), int(u1)
    def at(u):
        k = int(u) % 8; t = u - int(u); a, b = oc[k], oc[(k + 1) % 8]
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    out.append(at(u0))
    for k in range(k0 + 1, k1 + 1):
        if k < u1:
            out.append(oc[k % 8])
    out.append(at(u1))
    return out


def path_and_discs(d, stations, params):
    route = []
    for u0, u1 in zip(params, params[1:]):
        route += perimeter(u0, u1, R)[:-1]
    route.append(perimeter(params[-2], params[-1], R)[-1])
    pts = [iso(*p, WALL_H) for p in route]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = int(math.hypot(xb - xa, yb - ya) // 12)
        for i in range(0, n, 2):
            d.line([(xa + (xb - xa) * i / n, ya + (yb - ya) * i / n), (xa + (xb - xa) * (i + 1) / n, ya + (yb - ya) * (i + 1) / n)], fill=(17, 17, 17), width=4)
    for i, (x, y) in enumerate([iso(*p, WALL_H) for p in stations], 1):
        d.ellipse([x - 13, y - 8, x + 13, y + 8], fill=(17, 17, 17), outline='white', width=2)
        d.text((x, y), str(i), font=FD, fill='white', anchor='mm')


def detail_blocks(d):
    # 짝 CORE와 같은 방향의 바깥쪽
    text_block(d, 40, 330, *DETAIL[1], core=False, anchor='lm')
    text_block(d, 30, 1120, *DETAIL[2], core=False, anchor='lm')
    text_block(d, 330, 1300, *DETAIL[3], core=False, anchor='lm')
    text_block(d, 650, 1300, *DETAIL[4], core=False, anchor='lm')


# 팔각형 변 k의 화면 위치: 0=3시(옆선), 1=1~2시, 2=12시, 3=10~11시(안쪽 면 보임), 4=9시(옆선), 5=7~8시, 6=6시(정면), 7=4~5시
def build(variant):
    global R, WALL_H
    R, WALL_H = (500, 95) if variant == 'A' else (465, 52)
    img = background(); d = ImageDraw.Draw(img, 'RGBA')
    faces = draw_wall(d)
    st = {1: ring_point(3, 0.5), 2: ring_point(4, 0.5), 3: ring_point(6, 0.28), 4: ring_point(6, 0.72), 5: ring_point(0, 0.5)}
    if variant == 'A':
        st[2] = ring_point(5, 0.5); st[5] = ring_point(7, 0.5)
    if variant == 'A':
        # 보이는 벽면에 새김: ❶ 왼위 변 안쪽 면, ❷ 왼아래 변 바깥 면, ❸❹ 아래 변 바깥 면(정면·수평), ❺ 오른아래 변 바깥 면
        o, i_ = octagon(R + WALL_T / 2), octagon(R - WALL_T / 2)
        def seg(k, t0, t1, outer=True):
            A, B = (o if outer else i_)[k], (o if outer else i_)[(k + 1) % 8]
            return (A[0] + (B[0] - A[0]) * t0, A[1] + (B[1] - A[1]) * t0), (A[0] + (B[0] - A[0]) * t1, A[1] + (B[1] - A[1]) * t1)
        for num, (k, t0, t1, outer) in {1: (3, 0.1, 0.9, False), 2: (5, 0.08, 0.92, True), 3: (6, 0.04, 0.48, True), 4: (6, 0.52, 0.96, True), 5: (7, 0.08, 0.92, True)}.items():
            a, b = seg(k, t0, t1, outer)
            if not outer:
                a, b = b, a
            sheared_text(img, CORE[num][0], CORE[num][1], num, a, b, 4, WALL_H - 4, (0, 0))
        d = ImageDraw.Draw(img, 'RGBA')
        label = 'A안 — 성벽 벽면에 CORE를 새김(로마 비문처럼)'
        note = '앞 변(❸❹)은 정면이라 수평, ❶❷❺는 벽 방향 따라 ±30° 기울어짐 → 글 각도 3종 공존'
    else:
        # 보루(넓은 망루)를 정거장마다 두고 수평 글을 보루 위에 얹음
        for num, p in st.items():
            s = 34
            bx, by = p
            box = [(bx - s, by - s), (bx + s, by - s), (bx + s, by + s), (bx - s, by + s)]
            Z = WALL_H + 18
            for (pa, pb) in zip(box, box[1:] + box[:1]):
                nx, ny = ((pa[0] + pb[0]) / 2 - bx), ((pa[1] + pb[1]) / 2 - by)
                if nx - ny > 0:
                    d.polygon([iso(*pa, 0), iso(*pb, 0), iso(*pb, Z), iso(*pa, Z)], fill=(190, 190, 190), outline=(60, 60, 60))
            d.polygon([iso(*q, Z) for q in box], fill=(244, 244, 244), outline=(60, 60, 60))
        anchors = {1: (st[1], (-60, -120)), 2: (st[2], (-95, -120)), 3: (st[3], (-160, 80)), 4: (st[4], (20, 80)), 5: (st[5], (-140, -120))}
        for num, (p, (dx, dy)) in anchors.items():
            x, y = iso(*p, WALL_H + 18)
            text_block(d, x + dx, y + dy, *CORE[num], core=True, num=num, anchor='lm')
            d.line([(x, y - 6), (x + dx + 10, y + dy + 20 if dy < 0 else y + dy - 22)], fill=(60, 60, 60, 200), width=1)
        label = 'B안 — 성벽 보루(망루) 위에 CORE를 수평 글로 얹음'
        note = '모든 설명 글 수평 1종(땅 지명만 기울기) — 지난 각도 피드백 유지'
    params = [3.5, 5.5 if variant == 'A' else 4.5, 6.28, 6.72, 8.5]
    path_and_discs(d, [st[k] for k in range(1, 6)], params)
    detail_blocks(d)
    # 출발 화살표(제목 → ❶)
    x1, y1 = iso(*st[1], WALL_H)
    d.line([(430, 236), (x1 + 4, y1 - 16)], fill=(17, 17, 17), width=2)
    d.text((24, 248), label, font=ImageFont.truetype(FP, 18, index=6), fill=(160, 20, 20))
    d.text((24, 272), note, font=FR, fill=(160, 20, 20))
    out = os.path.join(ROOT, 'sketch_v2', f'concept_v3_{variant}.png')
    img.save(out)
    return out


if __name__ == '__main__':
    for v in sys.argv[1:] or ['A', 'B']:
        print(build(v))
