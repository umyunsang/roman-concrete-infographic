"""개념도 v4: 성벽 없이 콜로세움을 크게, CORE를 외벽(위 두 층 띠)에 새긴다.

아이소 투영(화면 pt, y 아래로): 땅 X → (0.7071, +0.4082), 땅 Y → (0.7071, −0.4082), 높이 Z → (0, −0.8165).
콜로세움 바닥 = 땅 위 타원: 점(θ) = a·cosθ·e1 + b·sinθ·e2, e1=(1,1)/√2(화면 수평), e2=(1,−1)/√2(화면 아래·앞).
θ=90°가 정면(관찰자 쪽), 0°=오른쪽, 180°=왼쪽. 앞 반원(sinθ>0)만 외벽이 보인다.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.expanduser('~/Documents/로마콘크리트_3D')
W, H = 1191, 1684
CX, CY = 595, 930          # 콜로세움 바닥 타원 중심(화면)
A_, B_ = 535, 450          # 바닥 타원 반지름(땅 단위)
ZH = 270                   # 외벽 높이(땅 단위)
BAND = (0.42, 0.97)        # 글을 새기는 띠(높이 비율)
FRONT = (138, 42)          # 정면 외벽에서 글을 놓는 θ 범위(왼→오른, 기울기 ≤ 약 30°)
INNER = 0.955              # 뒤쪽 안벽(맨 윗층 안쪽 면) 반지름 비
FP = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
S = 3                      # 글 텍스처 배율

CORE = {   # 사용자 결정(10/7): CORE는 본문 없이 번호 + 제목만 새긴다
    1: (['굳은 뒤에도', '단단해지는 재료'], []),
    2: (['뜨겁게 섞어', '빨리 굳힘'], []),
    3: (['누르는 힘만', '받게 짓기'], []),
    4: (['금이 가도', '메우고 고침'], []),
    5: (['약 1,950년째', '서 있음'], []),
}
DETAIL = {
    1: ('재료 원리 · 해수 속 새 결정', ['바닷물이 스미면 보통 온도에서도', '새 결정이 자라 틈을 메움']),
    2: ('제작 원리 · 열과 석회', ['생석회가 물을 만나 열을 냄', '다 녹지 않은 알갱이가 남음']),
    3: ('구조 원리 · 벽과 기초', ['아래는 무거운 돌, 위는 가벼운 돌', '12m 넘는 기초 고리']),
    4: ('균열 원리 · 금이 메워지는 순서', ['금 → 물이 스밈 → 석회가 녹음', '다시 굳어 금을 메움']),
}
# 새길 자리(θ 중심, 도) — 왼쪽→오른쪽: ❶❷ 왼쪽, ❸❹ 정면, ❺ 오른쪽
SLOTS = {1: 152, 2: 124, 3: 99, 4: 74, 5: 36}


def iso(X, Y, Z=0.0):
    return (CX + 0.7071 * (X + Y), CY + 0.4082 * (X - Y) - 0.8165 * Z)


def ell(theta, a=A_, b=B_):
    c, s = math.cos(theta), math.sin(theta)
    e1 = (0.70711, 0.70711); e2 = (0.70711, -0.70711)
    return (a * c * e1[0] + b * s * e2[0], a * c * e1[1] + b * s * e2[1])


def P(theta, z, a=A_, b=B_):
    return iso(*ell(theta, a, b), z)


def background():
    base = Image.open(os.path.join(ROOT, 'comfy', 'inputs', 'map_textless_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    paper = Image.new('RGB', (W, H), (246, 246, 246))
    m = Image.new('L', (W, H), 255)
    ImageDraw.Draw(m).ellipse([CX - 640, CY - 520, CX + 640, CY + 330], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(45))
    bg = Image.composite(Image.blend(base, paper, 0.45), paper, m)
    top = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS).crop((0, 0, W, 240))
    bg.paste(top, (0, 0))
    return bg


def arc(z, t0, t1, n=120, a=A_, b=B_):
    return [P(t0 + (t1 - t0) * i / n, z, a, b) for i in range(n + 1)]


def draw_colosseum(d):
    full = math.tau
    # 바닥 그림자
    d.polygon([(x + 18, y + 10) for x, y in arc(0, 0, full)], fill=(215, 215, 215))
    # 위 테두리(윗면 고리) + 관람석 계단 + 경기장
    d.polygon(arc(ZH, 0, full), fill=(236, 236, 236), outline=(70, 70, 70))
    # 뒤쪽 안벽: 위 테두리 안쪽 수직 면(ZH-95 ~ ZH) — 경기장 너머로 보임
    inner = arc(ZH, math.pi, math.tau, a=A_ * INNER, b=B_ * INNER) + arc(ZH - 140, math.tau, math.pi, a=A_ * INNER, b=B_ * INNER)
    d.polygon(inner, fill=(222, 222, 222), outline=(80, 80, 80))
    for k, (sc, z) in enumerate([(0.86, ZH - 140), (0.74, ZH - 170), (0.62, ZH - 195), (0.52, ZH - 215)]):
        d.polygon(arc(z, 0, full, a=A_ * sc, b=B_ * sc), fill=(226 - 8 * k, 226 - 8 * k, 226 - 8 * k), outline=(110, 110, 110))
    d.polygon(arc(ZH - 225, 0, full, a=A_ * 0.46, b=B_ * 0.46), fill=(244, 240, 232), outline=(90, 90, 90))
    # 앞 외벽(보이는 반원)
    t0, t1 = 0.0, math.pi
    face = arc(0, t0, t1) + arc(ZH, t1, t0)
    d.polygon(face, fill=(205, 205, 205), outline=(60, 60, 60))
    # 층 띠 선
    for frac in (0.20, BAND[0], BAND[1]):
        d.line(arc(ZH * frac, t0, t1), fill=(80, 80, 80), width=2)
    # 1층·2층 아치(띠 아래)
    for frac0, frac1 in ((0.02, 0.18), (0.22, 0.38)):
        n = 34
        for i in range(n):
            th = math.pi * (i + 0.5) / n
            if math.sin(th) < 0.12:
                continue
            w = math.pi / n * 0.32
            z0, z1 = ZH * frac0, ZH * frac1
            pts = [P(th - w, z0), P(th + w, z0), P(th + w, z1 - (z1 - z0) * 0.35)]
            for k in range(0, 9):  # 아치 윗부분 반원
                ang = math.pi * k / 8
                pts.append(P(th + w * math.cos(ang), z1 - (z1 - z0) * 0.35 + (z1 - z0) * 0.35 * math.sin(ang)))
            pts.append(P(th - w, z1 - (z1 - z0) * 0.35))
            d.polygon(pts, fill=(120, 120, 120))
    # 맨 위 작은 창(띠 위)
    for i in range(46):
        th = math.pi * (i + 0.5) / 46
        if math.sin(th) < 0.12:
            continue
        z = ZH * 0.985; w = math.pi / 46 * 0.12
        d.polygon([P(th - w, z - 6), P(th + w, z - 6), P(th + w, z - 1), P(th - w, z - 1)], fill=(140, 140, 140))


def text_texture(num, title, body):
    fb = ImageFont.truetype(FP, 22 * S, index=6); fr = ImageFont.truetype(FP, 11.5 * S, index=0)
    tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    tw = int(max([tmp.textlength(t, font=fb) for t in title] + [tmp.textlength(t, font=fr) for t in body]) + 34 * S)
    th = int((27 * len(title) + (15 * len(body) + 10 if body else 4)) * S)
    img = Image.new('RGBA', (tw + 8 * S, th + 6 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    def carve(xy, s, f):   # 새긴 글: 밝은 테두리 아래 어두운 글
        d.text((xy[0] + S, xy[1] + S), s, font=f, fill=(245, 245, 245, 230))
        d.text(xy, s, font=f, fill=(20, 20, 20, 255))
    d.ellipse([0, 4 * S, 26 * S, 30 * S], fill=(20, 20, 20, 255))
    d.text((13 * S, 17 * S), str(num), font=ImageFont.truetype(FP, 15 * S, index=6), fill='white', anchor='mm')
    for i, t in enumerate(title):
        carve((33 * S, i * 27 * S), t, fb)
    for i, t in enumerate(body):
        carve((4 * S, (27 * len(title) + 8 + i * 15) * S), t, fr)
    return img


def arc_len(t0, t1, n=200, k=1.0, z=None):
    z = ZH * 0.7 if z is None else z
    pts = [P(t0 + (t1 - t0) * i / n, z, A_ * k, B_ * k) for i in range(n + 1)]
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def span_for(center_deg, width):
    """화면 호 길이가 width가 되도록 θ 범위(라디안)를 찾는다."""
    c = math.radians(center_deg); lo, hi = 0.01, 1.6
    for _ in range(40):
        mid = (lo + hi) / 2
        if arc_len(c + mid / 2, c - mid / 2) < width:
            lo = mid
        else:
            hi = mid
    return c + lo / 2, c - lo / 2          # 왼쪽(θ 큼) → 오른쪽(θ 작음)


def homography(src, dst):
    """dst 점 → src 점 변환 계수(PIL PERSPECTIVE용)."""
    Am, bv = [], []
    for (x, y), (u, v) in zip(dst, src):
        Am.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); bv.append(u)
        Am.append([0, 0, 0, x, y, 1, -v * x, -v * y]); bv.append(v)
    return np.linalg.solve(np.array(Am, float), np.array(bv, float)).tolist()


def theta_after(t_start, width, direction, k=1.0, z=None):
    """t_start에서 direction(+1/−1) 쪽으로 화면 호 길이 width만큼 간 θ."""
    lo, hi = 0.0, 2.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if arc_len(t_start, t_start + direction * mid, k=k, z=z) < width:
            lo = mid
        else:
            hi = mid
    return t_start + direction * lo


def wrap_text(canvas, tex, theta_l, theta_r, z_top, z_bot, strips=60, k=1.0):
    tw, th = tex.size
    for i in range(strips):
        u0, u1 = tw * i / strips, tw * (i + 1) / strips
        a0 = theta_l + (theta_r - theta_l) * i / strips; a1 = theta_l + (theta_r - theta_l) * (i + 1) / strips
        dst = [P(a0, z_top, A_ * k, B_ * k), P(a1, z_top, A_ * k, B_ * k), P(a1, z_bot, A_ * k, B_ * k), P(a0, z_bot, A_ * k, B_ * k)]
        src = [(u0, 0), (u1, 0), (u1, th), (u0, th)]
        xs = [p[0] for p in dst]; ys = [p[1] for p in dst]
        bx0, by0, bx1, by1 = int(min(xs)) - 1, int(min(ys)) - 1, int(max(xs)) + 2, int(max(ys)) + 2
        local = [(x - bx0, y - by0) for x, y in dst]
        coef = homography(src, local)
        piece = tex.transform((bx1 - bx0, by1 - by0), Image.PERSPECTIVE, coef, resample=Image.BICUBIC)
        mask = Image.new('L', piece.size, 0); ImageDraw.Draw(mask).polygon(local, fill=255)
        alpha = Image.composite(piece.split()[3], Image.new('L', piece.size, 0), mask)
        canvas.paste(piece, (bx0, by0), alpha)


def text_block(d, x, y, title, lines):
    f1 = ImageFont.truetype(FP, 13, index=6); f2 = ImageFont.truetype(FP, 10, index=0)
    d.text((x, y), title, font=f1, fill=(60, 60, 60))
    for i, l in enumerate(lines):
        d.text((x, y + 19 + i * 13), l, font=f2, fill=(95, 95, 95))


def build():
    img = background(); d = ImageDraw.Draw(img, 'RGBA')
    draw_colosseum(d)
    zt, zb = ZH * BAND[1] - 4, ZH * BAND[0] + 4
    texs = {n: text_texture(n, *CORE[n]) for n in CORE}
    # ❶: 뒤쪽 안벽, 뒤 가운데에서 약간 왼쪽(θ −118° 부근), 왼→오른 = θ 증가
    t1 = texs[1]; h1 = hgt_front = None
    h1 = 70 * 0.8165; w1 = t1.size[0] / t1.size[1] * h1
    half = theta_after(math.radians(-90), w1 / 2, -1, k=INNER, z=ZH - 60)
    s1 = half; e1 = theta_after(s1, w1, +1, k=INNER, z=ZH - 60)
    wrap_text(img, t1, s1, e1, ZH - 32, ZH - 102, k=INNER)
    # ❷~❺: 정면 외벽 θ 138°→42°에 차례로(간격 18px), 넘치면 높이를 줄여 다시
    usable = arc_len(math.radians(FRONT[0]), math.radians(FRONT[1]))
    hgt = (zt - zb) * 0.8165 * 0.62
    while True:
        ws = [texs[n].size[0] / texs[n].size[1] * hgt for n in (2, 3, 4, 5)]
        if sum(ws) + 18 * 3 <= usable or hgt < 40:
            break
        hgt *= 0.95
    z_mid = (zt + zb) / 2; z_top = z_mid + hgt / 0.8165 / 2; zb = z_mid - hgt / 0.8165 / 2
    lead = (usable - sum(ws) - 18 * 3) / 2
    t = theta_after(math.radians(FRONT[0]), lead, -1)
    pos = {}
    for n, w in zip((2, 3, 4, 5), ws):
        e = theta_after(t, w, -1)
        wrap_text(img, texs[n], t, e, z_top, zb)
        pos[n] = (t, e)
        t = theta_after(e, 18, -1)
    pos[1] = (s1, e1)
    print('front text height px', round(hgt, 1), 'usable', round(usable), 'widths', [round(w) for w in ws])
    d = ImageDraw.Draw(img, 'RGBA')
    # DETAIL: 짝 CORE와 같은 방향 바깥(아래쪽 호)
    for num, (x, y) in {1: (40, 330), 2: (40, 1250), 3: (330, 1330), 4: (640, 1330)}.items():
        text_block(d, x, y, *DETAIL[num])
    # 출발 화살표: 제목 → ❶
    x1, y1 = P(pos[1][0] + 0.03, ZH, A_ * INNER, B_ * INNER)
    d.line([(430, 236), (x1, y1 - 8)], fill=(17, 17, 17), width=2)
    d.polygon([(x1, y1 + 2), (x1 - 6, y1 - 10), (x1 + 6, y1 - 9)], fill=(17, 17, 17))
    fT = ImageFont.truetype(FP, 18, index=6); fN = ImageFont.truetype(FP, 11, index=0)
    d.text((24, 248), '개념도 v4 — 성벽 없이 콜로세움에 CORE를 새김(❶ 뒤쪽 안벽, ❷~❺ 정면 외벽)', font=fT, fill=(160, 20, 20))
    d.text((24, 272), 'CORE는 번호+제목만 새김(본문 없음) · 읽는 순서: 제목 → ❶(뒤 안벽) → ❷❸❹❺(정면, 왼→오른) · DETAIL은 같은 방향 바깥', font=fN, fill=(160, 20, 20))
    out = os.path.join(ROOT, 'sketch_v2', 'concept_v4_colosseum.png'); img.save(out); return out


if __name__ == '__main__':
    print(build())
