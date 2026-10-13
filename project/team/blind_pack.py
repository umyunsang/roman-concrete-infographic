"""블라인드 비교 묶음 만들기: 워커 포스터들에 임의 라벨(P/Q/R…)을 붙여 같은 영역끼리 나란히 잘라 붙임.
python3 team/blind_pack.py <회차번호> <ws이름1> <ws이름2> ...
→ team/judge_r<N>/ : full.png(전체 나란히), tile_<행><열>.png(6구역 2배 확대 나란히), base_full.png(기준본 참고)
   라벨↔워커 대응은 team/judge_r<N>/.sealed_map.json (심사 끝날 때까지 열지 않음)
"""
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

T = Path('/Users/um-yunsang/Documents/로마콘크리트_3D/team')
rnd, names = sys.argv[1], sys.argv[2:]
out = T / f'judge_r{rnd}'
out.mkdir(exist_ok=True)
labels = 'PQRSTUV'[:len(names)]
order = names[:]
random.SystemRandom().shuffle(order)
(out / '.sealed_map.json').write_text(json.dumps(dict(zip(labels, order))))
P2 = [Image.open(T / f'ws_{n}/out/poster_2x.png').convert('RGB') for n in order]
W, H = P2[0].size                     # 2382×3368 (1pt=2px)
try:
    F = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 56)
except OSError:
    F = ImageFont.load_default()


def side(ims, tags, gap=24):
    w, h = ims[0].size
    can = Image.new('RGB', (w * len(ims) + gap * (len(ims) - 1), h + 80), 'white')
    d = ImageDraw.Draw(can)
    for i, (im, t) in enumerate(zip(ims, tags)):
        x = i * (w + gap)
        can.paste(im, (x, 80))
        d.text((x + 10, 10), t, fill='black', font=F)
    return can


small = [p.resize((W // 2, H // 2), Image.LANCZOS) for p in P2]
side(small, labels).save(out / 'full.png')
base = Image.open(T / 'baseline_r16_poster_1x.png').convert('RGB')
base.save(out / 'base_full.png')
R, C = 3, 2
for r in range(R):
    for c in range(C):
        box = (c * W // C, r * H // R, (c + 1) * W // C, (r + 1) * H // R)
        side([p.crop(box) for p in P2], [f'{l}  ({r}{c})' for l in labels]).save(out / f'tile_{r}{c}.png')
print('pack', out, 'labels', labels)
