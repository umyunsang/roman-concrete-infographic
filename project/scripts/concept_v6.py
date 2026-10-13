"""개념도 v6: 작아진 실제 콜로세움(Blender 렌더)을 중심에, 가까운 고리에 CORE(번호+제목), 먼 고리에 DETAIL."""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.expanduser('~/Documents/로마콘크리트_3D')
W, H = 1191, 1684
FP = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
CC = (595, 782)                    # 콜로세움 화면 중심(시각 중심)
CORE = {
    1: ('굳은 뒤에도', '단단해지는 재료', (223, 600)),
    2: ('뜨겁게 섞어', '빨리 굳힘', (150, 800)),
    3: ('누르는 힘만', '받게 짓기', (470, 1075)),
    4: ('금이 가도', '메우고 고침', (720, 1075)),
    5: ('약 1,950년째', '서 있음', (1030, 790)),
}
DETAIL = {   # 머리말, 2줄, 스케치에서 자를 모형 영역(pt), 놓을 자리(왼쪽 위)
    1: ('재료 원리 · 해수 속 새 결정', ['바닷물이 스미면 보통 온도에서도', '새 결정이 자라 틈을 메움'], (236, 382, 284, 430), (36, 360)),
    2: ('제작 원리 · 열과 석회', ['생석회에 물을 부으면 뜨거워지고', '다 녹지 않은 석회 알갱이가 남음'], (70, 980, 136, 1058), (36, 960)),
    3: ('구조 원리 · 벽과 기초', ['아래는 무거운 돌, 위는 가벼운 돌', '12m 넘는 기초 고리가 무게를 받음'], (634, 1112, 808, 1252), (250, 1200)),
    4: ('균열 원리 · 금이 메워지는 순서', ['금으로 스민 물이 석회 알갱이를 녹이고', '다시 굳어 금을 메움'], (984, 618, 1146, 668), (650, 1220)),
}
SUPPORT = {
    '항구': ('로마 항구 방파제 조각', '결정 관찰', '바닷물 속에서 새 결정이 자라 단단해짐', (60, 1540), (292, 1500)),
    '실험실': ('오늘의 실험실', '균열 충전 실험', '금으로 흐르던 물이 2주 안에 멈춤', (440, 1440), (600, 1528)),
    '폼페이': ('폼페이 공사현장(79년)', '배합 흔적', '마른 석회를 섞어 둔 원료 더미', (700, 1530), (860, 1440)),
    '프리베르눔': ('프리베르눔 성벽 조각', '석회·결정 관찰', '흰 석회 알갱이와 금을 메운 결정', (930, 960), (1040, 1100)),
}


def background():
    base = Image.open(os.path.join(ROOT, 'comfy', 'inputs', 'map_textless_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    paper = Image.new('RGB', (W, H), (246, 246, 246))
    m = Image.new('L', (W, H), 255)
    ImageDraw.Draw(m).ellipse([CC[0] - 470, CC[1] - 330, CC[0] + 470, CC[1] + 330], fill=0)   # 옛 성벽·도시 지움
    m = m.filter(ImageFilter.GaussianBlur(40))
    bg = Image.composite(Image.blend(base, paper, 0.5), paper, m)
    top = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB').resize((W, H), Image.LANCZOS)
    bg.paste(top.crop((0, 0, W, 240)), (0, 0)); bg.paste(top.crop((0, 1600, W, H)), (0, 1600))
    return bg


def dashed(d, pts, col=(70, 70, 70, 160), w=3, on=10, off=8):
    acc, draw = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.dist((x0, y0), (x1, y1)); t = 0.0
        while t < L:
            seg = min((on if draw else off) - acc, L - t)
            if draw:
                a = (x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L); b = (x0 + (x1 - x0) * (t + seg) / L, y0 + (y1 - y0) * (t + seg) / L)
                d.line([a, b], fill=col, width=w)
            t += seg; acc += seg
            if acc >= (on if draw else off) - 1e-6:
                acc, draw = 0.0, not draw


def build():
    img = background(); d = ImageDraw.Draw(img, 'RGBA')
    # 콜로세움 둘레 길(아이소 땅 타원, ❶→❺ 반시계로 아래를 돌아감) — 옅게
    rx, ry = 370, 214; cyg = 840
    arcpts = [(CC[0] + rx * math.cos(math.radians(a)), cyg + ry * math.sin(math.radians(a))) for a in range(-150, -360 - 1, -3)]
    arcpts = [(CC[0] + rx * math.cos(math.radians(a)), cyg + ry * math.sin(math.radians(a))) for a in [-150 - i * 3 for i in range(0, 71)]]
    dashed(d, arcpts)
    # 실제 콜로세움 렌더
    col = Image.open(os.path.join(ROOT, 'renders', 'colosseum_small_2x.png')).convert('RGBA').resize((W, H), Image.LANCZOS)
    img.paste(col, (0, 0), col)
    d = ImageDraw.Draw(img, 'RGBA')
    # CORE: 가까운 고리, 번호+제목(크게)
    fT = ImageFont.truetype(FP, 23, index=6); fN = ImageFont.truetype(FP, 15, index=6)
    for n, (l1, l2, (x, y)) in CORE.items():
        tw = max(d.textlength(l1, font=fT), d.textlength(l2, font=fT)) + 34
        x0 = max(24, min(W - 24 - tw, x - tw / 2)); y0 = y - 30
        d.rounded_rectangle([x0 - 8, y0 - 8, x0 + tw + 8, y0 + 66], radius=6, fill=(255, 255, 255, 215))
        d.ellipse([x0, y0 + 3, x0 + 26, y0 + 29], fill=(17, 17, 17))
        d.text((x0 + 13, y0 + 16), str(n), font=fN, fill='white', anchor='mm')
        d.text((x0 + 34, y0), l1, font=fT, fill=(17, 17, 17)); d.text((x0 + 34, y0 + 30), l2, font=fT, fill=(17, 17, 17))
    # DETAIL: 먼 고리, 모형 + 머리말 + 2줄(작고 옅게)
    sk = Image.open(os.path.join(ROOT, 'ref', 'sketch_final_2x.png')).convert('RGB')
    fH = ImageFont.truetype(FP, 13, index=6); fB = ImageFont.truetype(FP, 10.5, index=0); fG = ImageFont.truetype(FP, 9.5, index=0)
    for n, (head, lines, crop, (x, y)) in DETAIL.items():
        c = sk.crop(tuple(v * 2 for v in crop)); c = c.resize((int(c.width * 0.6), int(c.height * 0.6)), Image.LANCZOS)
        img.paste(c, (x, y)); ty = y + c.height + 8
        d.text((x, ty), head, font=fH, fill=(60, 60, 60))
        for i, l in enumerate(lines):
            d.text((x, ty + 19 + i * 14), l, font=fB, fill=(95, 95, 95))
    # SUPPORT: 근거 장소(이름·관찰명·1줄 + 점선 핀)
    for key, (name, obs, desc, (x, y), (px, py)) in SUPPORT.items():
        d.text((x, y), name, font=fH, fill=(45, 45, 45)); d.text((x, y + 18), obs, font=fG, fill=(125, 125, 125)); d.text((x, y + 31), desc, font=fB, fill=(85, 85, 85))
        sx, sy = (x - 6, y + 8) if px < x else (x + d.textlength(name, font=fH) + 6, y + 8)
        dashed(d, [(sx, sy), (px, py)], col=(90, 90, 90, 255), w=1, on=4, off=4)
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=(60, 60, 60))
    # 출발: 제목 → ❶
    x1, y1 = CORE[1][2]
    d.line([(430, 236), (x1 + 20, y1 - 42)], fill=(17, 17, 17), width=2)
    d.polygon([(x1 + 18, y1 - 36), (x1 + 13, y1 - 49), (x1 + 25, y1 - 47)], fill=(17, 17, 17))
    d.text((24, 250), '개념도 v6 — 실제 콜로세움(Blender 렌더)을 중심에: 가까이 CORE(번호+제목) · 멀리 DETAIL · 더 멀리 SUPPORT (문안 임시)',
           font=ImageFont.truetype(FP, 14, index=6), fill=(160, 20, 20))
    out = os.path.join(ROOT, 'sketch_v2', 'concept_v6.png'); img.save(out); return out


if __name__ == '__main__':
    print(build())
