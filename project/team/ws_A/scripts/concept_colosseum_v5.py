"""개념도 v5: 아레나를 줄이고 콜로세움 디테일(4층 외벽·관람석·하이포지움)을 살린 뒤 글(CORE 새김 + DETAIL·SUPPORT·연표)을 넣는다."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import concept_colosseum as cc

ROOT = cc.ROOT; W, H = cc.W, cc.H; FP = cc.FP
cc.CX, cc.CY, cc.A_, cc.B_, cc.ZH = 595, 930, 535, 450, 290
cc.INNER = 0.955
P, arc = cc.P, cc.arc
ZH = cc.ZH
ST = {'L1': (0.0, 0.19), 'C1': (0.19, 0.21), 'L2': (0.21, 0.38), 'C2': (0.38, 0.40),
      'BAND': (0.40, 0.80), 'C3': (0.80, 0.82), 'ATTIC': (0.82, 1.0)}
LIGHT = (-0.75, 0.25)   # 화면 왼쪽 위에서 오는 빛(땅 e1·e2 성분)

DETAIL = {
    1: ('재료 원리 · 해수 속 새 결정', ['바닷물이 스미면 보통 온도에서도', '새 결정이 자라 틈을 메움'], (236, 382, 284, 430), (40, 300)),
    2: ('제작 원리 · 열과 석회', ['생석회에 물을 부으면 뜨거워지고', '다 녹지 않은 석회 알갱이가 남음'], (70, 980, 136, 1058), (36, 1205)),
    3: ('구조 원리 · 벽과 기초', ['아래는 무거운 돌, 위는 가벼운 돌', '12m 넘는 기초 고리가 무게를 받음'], (634, 1112, 808, 1252), (300, 1235)),
    4: ('균열 원리 · 금이 메워지는 순서', ['금으로 스민 물이 석회 알갱이를 녹이고', '다시 굳어 금을 메움'], (984, 618, 1146, 668), (590, 1250)),
}
SUPPORT = {   # 이름, 관찰명, 설명 1줄, 글 자리, 핀 끝(장소)
    '항구': ('로마 항구 방파제 조각', '결정 관찰', '바닷물 속에서 새 결정이 자라 단단해짐', (60, 1540), (292, 1500)),
    '실험실': ('오늘의 실험실', '균열 충전 실험', '금으로 흐르던 물이 2주 안에 멈춤', (470, 1430), (600, 1528)),
    '폼페이': ('폼페이 공사현장(79년)', '배합 흔적', '마른 석회를 섞어 둔 원료 더미', (700, 1530), (860, 1440)),
    '프리베르눔': ('프리베르눔 성벽 조각', '석회·결정 관찰', '흰 석회 알갱이와 금을 메운 결정', (915, 1185), (1040, 1120)),
}


def shade(theta, base=206, amp=34):
    """외벽 법선(땅)과 빛 방향의 내적으로 회색 명도."""
    nx, ny = math.cos(theta) / cc.A_, math.sin(theta) / cc.B_
    L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
    k = nx * LIGHT[0] + ny * LIGHT[1]
    v = int(base + amp * k)
    return (v, v, v)


def strip(d, t0, t1, z0, z1, fill, a=None, b=None, outline=None):
    a = a or cc.A_; b = b or cc.B_
    pts = [P(t0, z0, a, b), P(t1, z0, a, b), P(t1, z1, a, b), P(t0, z1, a, b)]
    d.polygon(pts, fill=fill, outline=outline)


def arch(d, th, w, z0, z1, fill):
    zs = z1 - (z1 - z0) * 0.32
    pts = [P(th - w, z0), P(th + w, z0), P(th + w, zs)]
    for k in range(1, 10):
        ang = math.pi * k / 10
        pts.append(P(th + w * math.cos(ang), zs + (z1 - zs) * math.sin(ang)))
    pts.append(P(th - w, zs))
    d.polygon(pts, fill=fill)


def draw(d):
    A_, B_ = cc.A_, cc.B_; full = math.tau
    # 그림자
    d.polygon([(x + 22, y + 12) for x, y in arc(0, 0, full)], fill=(212, 212, 212))
    # 윗면 고리(외벽 두께)
    d.polygon(arc(ZH, 0, full), fill=(238, 238, 238), outline=(70, 70, 70))
    # 뒤쪽 안벽(꼭대기 회랑 뒷벽) — ❶ 새김 자리
    ki = cc.INNER
    d.polygon(arc(ZH, math.pi, full, a=A_ * ki, b=B_ * ki) + arc(ZH - 120, full, math.pi, a=A_ * ki, b=B_ * ki), fill=(224, 224, 224), outline=(80, 80, 80))
    # 회랑 기둥(❶ 글 자리 밖)
    for i in range(48):
        th = math.pi + math.pi * (i + 0.5) / 48
        if abs(th - 1.5 * math.pi) < 0.42:
            continue
        x0, y0 = P(th, ZH - 6, A_ * ki, B_ * ki); x1, y1 = P(th, ZH - 112, A_ * ki, B_ * ki)
        d.line([(x0, y0), (x1, y1)], fill=(150, 150, 150), width=2)
    # 관람석: 꼭대기(0.93, ZH-120) → 아레나 가장자리(0.34, 52) 계단 줄
    rings = 26
    for i in range(rings + 1):
        f = i / rings
        sc = 0.93 - (0.93 - 0.36) * f
        z = (ZH - 120) - (ZH - 120 - 58) * (f ** 0.85)
        sector = 0 if f < 0.34 else (1 if f < 0.68 else 2)
        base = (232, 220, 208)[sector] - (i % 2) * 7
        d.polygon(arc(z, 0, full, a=A_ * sc, b=B_ * sc), fill=(base, base, base), outline=(150, 150, 150) if i % 2 == 0 else None)
    # 구역 경계(복도) 진하게
    for f in (0.34, 0.68):
        sc = 0.93 - (0.93 - 0.36) * f; z = (ZH - 120) - (ZH - 120 - 58) * (f ** 0.85)
        d.line(arc(z, 0, full, a=A_ * sc, b=B_ * sc), fill=(90, 90, 90), width=2)
    # 방사 통로
    for i in range(24):
        th = math.tau * i / 24
        pts = [P(th, (ZH - 120) - (ZH - 178) * (f ** 0.85), A_ * (0.93 - 0.57 * f), B_ * (0.93 - 0.57 * f)) for f in (0.0, 0.34, 0.68, 1.0)]
        d.line(pts, fill=(120, 120, 120), width=2)
    # 포디움 벽 + 작은 아레나 + 하이포지움
    d.polygon(arc(58, 0, full, a=A_ * 0.36, b=B_ * 0.36), fill=(170, 170, 170), outline=(60, 60, 60))
    d.polygon(arc(46, 0, full, a=A_ * 0.335, b=B_ * 0.335), fill=(242, 236, 224), outline=(70, 70, 70))
    # 하이포지움: 아레나 가운데를 열어 지하 벽 줄
    hyp = arc(46, 0, full, a=A_ * 0.25, b=B_ * 0.22)
    d.polygon(hyp, fill=(120, 116, 110))
    for j in range(-4, 5):
        y = j / 5.0
        pts = []
        for t in range(-20, 21):
            x = t / 20.0
            if x * x + y * y <= 1:
                X = A_ * 0.25 * x; Y = B_ * 0.22 * y
                e = (0.70711 * X + 0.70711 * Y, 0.70711 * X - 0.70711 * Y)
                pts.append(cc.iso(e[0], e[1], 46))
        if len(pts) > 1:
            d.line(pts, fill=(205, 198, 186), width=2)
    # 앞 외벽: 조각마다 빛 음영
    n = 90
    for i in range(n):
        t0, t1 = math.pi * i / n, math.pi * (i + 1) / n
        strip(d, t0, t1, 0, ZH, shade((t0 + t1) / 2))
    # 코니스(돌림띠)
    for key in ('C1', 'C2', 'C3'):
        z0, z1 = (ZH * v for v in ST[key])
        for i in range(n):
            t0, t1 = math.pi * i / n, math.pi * (i + 1) / n
            c = shade((t0 + t1) / 2, base=228, amp=22)
            strip(d, t0, t1, z0, z1, c)
        d.line(arc(z0, 0, math.pi), fill=(70, 70, 70), width=1); d.line(arc(z1, 0, math.pi), fill=(70, 70, 70), width=1)
    # 1·2층 아치 + 반원기둥
    bays = 44
    for key in ('L1', 'L2'):
        z0, z1 = (ZH * v for v in ST[key])
        for i in range(bays):
            th = math.pi * (i + 0.5) / bays
            if math.sin(th) < 0.1:
                continue
            arch(d, th, math.pi / bays * 0.30, z0 + 3, z1 - 6, (98, 98, 98))
            tc = math.pi * i / bays
            if math.sin(tc) > 0.1:
                strip(d, tc - 0.006, tc + 0.006, z0, z1, shade(tc, base=226, amp=20), outline=(90, 90, 90))
    # 애틱: 창 + 벽기둥 + 차양 받침
    z0, z1 = (ZH * v for v in ST['ATTIC'])
    for i in range(bays):
        th = math.pi * (i + 0.5) / bays
        if math.sin(th) < 0.1:
            continue
        if i % 2 == 0:
            w = math.pi / bays * 0.16
            strip(d, th - w, th + w, z0 + (z1 - z0) * 0.40, z0 + (z1 - z0) * 0.62, (110, 110, 110))
        tc = math.pi * i / bays
        if math.sin(tc) > 0.1:
            d.line([P(tc, z0), P(tc, z1)], fill=(120, 120, 120), width=2)
            strip(d, tc - 0.008, tc + 0.008, z1 - 10, z1 - 4, (90, 90, 90))
    # 외곽선
    d.line(arc(0, 0, math.pi), fill=(50, 50, 50), width=2)
    d.line(arc(ZH, 0, math.pi), fill=(50, 50, 50), width=2)
    for t in (0.0, math.pi):
        d.line([P(t, 0), P(t, ZH)], fill=(50, 50, 50), width=2)


def inscriptions(img):
    zb0, zt0 = ZH * ST['BAND'][0], ZH * ST['BAND'][1]
    texs = {n: cc.text_texture(n, *cc.CORE[n]) for n in cc.CORE}
    # ❶ 뒤쪽 안벽 가운데
    t1 = texs[1]; h1 = 96 * 0.8165; w1 = t1.size[0] / t1.size[1] * h1
    s1 = cc.theta_after(math.radians(-90), w1 / 2, -1, k=cc.INNER, z=ZH - 60)
    e1 = cc.theta_after(s1, w1, +1, k=cc.INNER, z=ZH - 60)
    cc.wrap_text(img, t1, s1, e1, ZH - 14, ZH - 110, k=cc.INNER)
    # ❷~❺ 정면 띠
    usable = cc.arc_len(math.radians(146), math.radians(34), z=(zb0 + zt0) / 2)
    hgt = (zt0 - zb0) * 0.8165 * 0.90
    ws = [texs[n].size[0] / texs[n].size[1] * hgt for n in (2, 3, 4, 5)]
    while sum(ws) + 22 * 3 > usable:
        hgt *= 0.95; ws = [texs[n].size[0] / texs[n].size[1] * hgt for n in (2, 3, 4, 5)]
    zm = (zb0 + zt0) / 2; zt, zb = zm + hgt / 0.8165 / 2, zm - hgt / 0.8165 / 2
    print('CORE 새김 높이 px', round(hgt, 1), '폭', [round(w) for w in ws], '가용', round(usable))
    t = cc.theta_after(math.radians(146), (usable - sum(ws) - 66) / 2, -1, z=zm)
    for n, w in zip((2, 3, 4, 5), ws):
        e = cc.theta_after(t, w, -1, z=zm)
        cc.wrap_text(img, texs[n], t, e, zt, zb)
        t = cc.theta_after(e, 22, -1, z=zm)
    return s1, e1


def detail_and_support(img, d):
    sk = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB')
    fH = ImageFont.truetype(FP, 13, index=6); fB = ImageFont.truetype(FP, 10.5, index=0); fG = ImageFont.truetype(FP, 9.5, index=0)
    for num, (head, lines, crop, (x, y)) in DETAIL.items():
        c = sk.crop(tuple(v * 2 for v in crop)); c = c.resize((int(c.width * 0.62), int(c.height * 0.62)), Image.LANCZOS)
        img.paste(c, (x, y))
        ty = y + c.height + 8
        d.text((x, ty), head, font=fH, fill=(55, 55, 55))
        for i, l in enumerate(lines):
            d.text((x, ty + 19 + i * 14), l, font=fB, fill=(90, 90, 90))
    for key, (name, obs, desc, (x, y), (px, py)) in SUPPORT.items():
        d.text((x, y), name, font=fH, fill=(40, 40, 40))
        d.text((x, y + 18), obs, font=fG, fill=(120, 120, 120))
        d.text((x, y + 31), desc, font=fB, fill=(80, 80, 80))
        # 점선 핀(이름 줄에서 장소로)
        sx, sy = (x - 6, y + 8) if px < x else (x + d.textlength(name, font=fH) + 6, y + 8)
        L = math.dist((sx, sy), (px, py)); n = max(2, int(L // 6))
        for i in range(0, n, 2):
            a = (sx + (px - sx) * i / n, sy + (py - sy) * i / n); b = (sx + (px - sx) * (i + 1) / n, sy + (py - sy) * (i + 1) / n)
            d.line([a, b], fill=(90, 90, 90), width=1)
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(60, 60, 60))


def build():
    img = cc.background(); d = ImageDraw.Draw(img, 'RGBA')
    draw(d)
    s1, e1 = inscriptions(img)
    d = ImageDraw.Draw(img, 'RGBA')
    detail_and_support(img, d)
    # 연표(최종안 맨 아래 띠)
    sk = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    img.paste(sk.crop((0, 1600, W, H)), (0, 1600))
    # 출발 화살표
    x1, y1 = P(math.radians(-90), ZH, cc.A_ * cc.INNER, cc.B_ * cc.INNER)
    d.line([(430, 236), (x1, y1 - 8)], fill=(17, 17, 17), width=2)
    d.polygon([(x1, y1 + 2), (x1 - 6, y1 - 10), (x1 + 6, y1 - 9)], fill=(17, 17, 17))
    fT = ImageFont.truetype(FP, 16, index=6)
    d.text((24, 248), '개념도 v5 — 작은 아레나·4층 외벽·관람석·하이포지움 + CORE 새김 + DETAIL·SUPPORT·연표 (문안은 임시)', font=fT, fill=(160, 20, 20))
    out = os.path.join(ROOT, 'sketch_v2', 'concept_v5_colosseum.png'); img.save(out); return out


if __name__ == '__main__':
    print(build())
