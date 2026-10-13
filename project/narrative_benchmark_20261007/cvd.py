import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image
from colorlib import *
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
mp = np.array(Image.open(R + 'r9/map_only_2x.png').convert('RGB')).astype(float)
def med(x0, y0, x1, y1):
    sub = mp[int(y0*2):int(y1*2), int(x0*2):int(x1*2)].reshape(-1, 3)
    return np.median(sub, 0), sub.std(0).mean()
road, rs = med(1000, 950, 1060, 960)
road2, rs2 = med(300, 1010, 330, 1040)
print('road sample', np.round(road), 'std', round(rs, 1), '| road2', np.round(road2), 'std', round(rs2, 1))
H = hex2rgb
pairs21 = [
 ('CORE 제목 1줄/2줄 #2E2A22-#983821', H('2E2A22'), H('983821'), 0.5),
 ('개념색 물/칼슘 #1B5760-#8A5427', H('1B5760'), H('8A5427'), 0.25),
 ('강조 제목/본문 #983821-#2E2A22', H('983821'), H('2E2A22'), 0.25),
]
pairs22 = [
 ('땅/바다 #EEE2CC-#9CCACA', H('EEE2CC'), H('9CCACA'), 2),
 ('강/길(아피아) #9BC9C9-road', H('9BC9C9'), road, 2),
 ('이정표 판(밝은 면 최暗 #7B2D1B)/종이 #EEE2CC', H('7B2D1B'), H('EEE2CC'), 2),
 ('이정표 판 #7B2D1B/길', H('7B2D1B'), road, 2),
 ('이정표 판 #8D3520/길', H('8D3520'), road, 2),
 ('이정표 판 #7F2E1B/종이', H('7F2E1B'), H('EEE2CC'), 2),
 ('강조 원판 #9D3921/비CORE 큐브 #8A6C5C', H('9D3921'), H('8A6C5C'), 2),
 ('강조 #983821/비CORE 큐브 #8A6C5C', H('983821'), H('8A6C5C'), 2),
 ('이정표 판 #8D3520/큐브 #8A6C5C', H('8D3520'), H('8A6C5C'), 2),
 ('현대 골조 #727576/콜로세움 #A78763', H('727576'), H('A78763'), 2),
 ('현대 연구 도구 #546671/로마 책 #7B5E40', H('546671'), H('7B5E40'), 2),
 ('실험실 판 #B2C0BE/로마 석재 #B6AB93', H('B2C0BE'), H('B6AB93'), 2),
]
for title, pairs in (('CL-21', pairs21), ('CL-22', pairs22)):
    print('==', title)
    for name, a, b, deg in pairs:
        ds = [float(szafir_D(a, b, deg))] + [float(szafir_D(cvd(a, k), cvd(b, k), deg)) for k in ('protan', 'deutan', 'tritan')]
        print(f'  {name:42s} {deg}deg  normal {ds[0]:.2f}  protan {ds[1]:.2f}  deutan {ds[2]:.2f}  tritan {ds[3]:.2f}  min {min(ds):.2f}')
