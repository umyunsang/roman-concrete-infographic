"""지도 렌더 + Figma 글 오버레이(투명도 있는 RGBA, 보통 겹치기) → 포스터 합성.
python3 team/compose.py <map_2x.png> <out_poster.png>
오버레이 text_overlay_rgba_2x.png = Figma 오버레이 프레임(671:78)을 검은·흰 바탕으로 두 번 내보내 차이로 알파를 구한 것
(곱하기 합성은 흰 글자 — CORE 번호 원판 안 숫자 — 를 지워 버려서 바꿈).
"""
import sys
from PIL import Image
o = Image.open('/Users/um-yunsang/Documents/로마콘크리트_3D/team/text_overlay_rgba_2x.png').convert('RGBA')
m = Image.open(sys.argv[1]).convert('RGBA').resize(o.size, Image.LANCZOS)
p = Image.alpha_composite(m, o).convert('RGB')
p.save(sys.argv[2])
p.resize((o.size[0] // 2, o.size[1] // 2), Image.LANCZOS).save(sys.argv[2].replace('.png', '_1x.png'))
print('poster', sys.argv[2])
