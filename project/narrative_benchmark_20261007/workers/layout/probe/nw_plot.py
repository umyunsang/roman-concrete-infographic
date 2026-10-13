import sys, json, numpy as np
from PIL import Image, ImageDraw
sys.argv_saved = sys.argv
D = np.load(sys.argv[1]); sol = json.load(open(sys.argv[2])); out = sys.argv[3]
exec(open(sys.argv[4]).read().split('# initial guess')[0].replace('D = np.load(sys.argv[1]); RMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 4.0', 'RMIN = sol["RMIN"]'))
GX0, GY0, SC = 260, 430, 3
im = Image.new('RGB', (int(360 * SC), int(290 * SC)), 'white'); dr = ImageDraw.Draw(im)
cols = {'COL_ruined': (200, 140, 80), 'R8_pantheon': (150, 80, 40), 'F_centuriatio': (90, 160, 90), 'MS1_core1_to_2': (180, 0, 0),
        'L02_tiber': (80, 160, 220), 'W_water_marks': (80, 160, 220), 'R1_road_landing1': (120, 120, 120), 'B_pons1': (100, 100, 100),
        'R3_colosseum_podium': (210, 200, 170)}
for k, c in cols.items():
    P = D['obs_' + k][::7]
    for x, y in P: dr.point(((x - GX0) * SC, (y - GY0) * SC), fill=c)
x = np.r_[sol['u'], sol['L']]; s, P, th, kap = path(x)
for E in band(s, P, th, step=2):
    q = proj(E); dr.line([((a - GX0) * SC, (b - GY0) * SC) for a, b in q], fill=(0, 0, 0), width=1)
q = proj(np.c_[P, tz(P)]); dr.line([((a - GX0) * SC, (b - GY0) * SC) for a, b in q], fill=(255, 0, 255), width=1)
for gx in range(280, 620, 20): dr.text(((gx - GX0) * SC, 2), str(gx), fill=(0, 0, 0))
for gy in range(440, 720, 20): dr.text((2, (gy - GY0) * SC), str(gy), fill=(0, 0, 0))
im.save(out); print('saved')
