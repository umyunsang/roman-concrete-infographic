import json,numpy as np
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
B=Path('/Users/um-yunsang/.planning/roman-concrete-narrative-20261007/construction-detail')
a=np.load(B/'counterclockwise-road-geometry.npz');h=np.load(B/'village-plan.hero.npz')
W,H=1191,1684

def raster(n):
 im=Image.new('1',(W,H));d=ImageDraw.Draw(im);p=a[n+'_points'];loops=a[n+'_loops'];starts=a[n+'_starts'];totals=a[n+'_totals']
 for s,c in zip(starts,totals):d.polygon([tuple(v) for v in p[loops[s:s+c]]],fill=1)
 return im
road=Image.new('1',(W,H));
for n in ['R_core_road','R_via_appia','R_via_ostiensis','B_pons1','B_pons2']:
 road=Image.fromarray(np.asarray(road)|np.asarray(raster(n)))
water=raster('L02_tiber');land=raster('T_land')
p=h['points'];z=h['worldz'];lo=z.min();hi=z.max();q=p[z<lo+(hi-lo)*.02]
pts=sorted(set(map(tuple,q.tolist())))
def cross(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
l=[]
for v in pts:
 while len(l)>=2 and cross(l[-2],l[-1],v)<=0:l.pop()
 l.append(v)
u=[]
for v in reversed(pts):
 while len(u)>=2 and cross(u[-2],u[-1],v)<=0:u.pop()
 u.append(v)
hull=l[:-1]+u[:-1];herofoot=Image.new('1',(W,H));ImageDraw.Draw(herofoot).polygon(hull,fill=1)
print('hero ground hull bounds',q.min(0).tolist(),q.max(0).tolist())
rects={
'NW_vault':[348,634,427,660],
'N_house':[555,590,625,615],
'NE_market':[824,604,900,634],
'W_prep':[68,902,206,945],
'W_scaffold':[370,895,396,922],
'E_scaffold':[798,891,827,923],
'SW_yard':[358,1201,464,1234],
'S_life':[551,1182,608,1206],
'SE_yard':[746,1208,835,1235],
}
rows=[]
for n,r in rects.items():
 im=Image.new('1',(W,H));ImageDraw.Draw(im).rectangle(r,fill=1);m=np.asarray(im)
 row={'name':n,'floor_rect':r,'road_pixels':int(np.count_nonzero(m&np.asarray(road))),'water_pixels':int(np.count_nonzero(m&np.asarray(water))),'outside_terrain_pixels':int(np.count_nonzero(m&~np.asarray(land))),'hero_ground_pixels':int(np.count_nonzero(m&np.asarray(herofoot)))};rows.append(row);print(row)
np.savez_compressed(B/'village-plan.masks.npz',road=np.asarray(road),water=np.asarray(water),land=np.asarray(land),hero_ground=np.asarray(herofoot))
(B/'village-plan.floor-audit.json').write_text(json.dumps({'canvas':[W,H],'heroLow2percentHull':hull,'rectangles':rows},indent=2)+'\n')
im=Image.new('RGB',(W,H),'#efe8d2');im.paste('#89c8d0',mask=water.convert('L'));im.paste('#a49c83',mask=road.convert('L'));im.paste('#ceb991',mask=herofoot.convert('L'));d=ImageDraw.Draw(im)
for row in rows:d.rectangle(row['floor_rect'],outline='#355967',width=2);d.text((row['floor_rect'][0],row['floor_rect'][1]-12),row['name'],fill='#355967')
im.save(B/'village-plan.floor-audit.png')
