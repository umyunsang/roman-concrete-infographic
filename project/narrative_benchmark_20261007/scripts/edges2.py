import numpy as np, json
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(R+'assets_index.json')); A={a['id']:a for a in idx['assets']}
def edge(aid, xr, yr, side):
  a=A[aid]; al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3].astype(float)/255
  x0,y0=a['crop_pt'][0],a['crop_pt'][2]
  ys=[];xs=[]
  for py in np.arange(yr[0],yr[1],1/3):
    r=int(round((py-y0)*3)); c0,c1=int((xr[0]-x0)*3),int((xr[1]-x0)*3); row=al[r,c0:c1]
    idxs=range(len(row)-1) if side=='left' else range(len(row)-2,-1,-1)
    for i in idxs:
      a0,a1=row[i],row[i+1]
      if (a0-0.5)*(a1-0.5)<=0 and a0!=a1: ys.append(py); xs.append(x0+(c0+i+(0.5-a0)/(a1-a0))/3); break
  ys=np.array(ys); xs=np.array(xs); p=np.polyfit(ys,xs,1); r=xs-np.polyval(p,ys)
  return dict(n=len(ys), max_abs=round(float(np.abs(r).max()),2), p2p_half=round(float((r.max()-r.min())/2),2), std=round(float(r.std()),2), prof=[round(float(v),2) for v in r[::3]])
for name,args in [('town_right_1448_1467',('landmark_pompeii_town',(895,907),(1448,1467),'right')),
                  ('town_right_1441_1460',('landmark_pompeii_town',(895,907),(1441,1460),'right')),
                  ('site_rightwall_1458_1486',('support_pompeii_site',(740,752),(1458,1486),'right')),
                  ('lh_left_1429_1438',('support_harbor',(60,80),(1429,1438),'left')),
                  ('lh_left_1442_1450',('support_harbor',(60,80),(1442,1450),'left')),
                  ('lh_left_1454_1462',('support_harbor',(60,80),(1454,1462),'left')),
                  ('lh_right_1429_1438',('support_harbor',(85,105),(1429,1438),'right')),
                  ('lh_right_1442_1450',('support_harbor',(85,105),(1442,1450),'right')),
                  ('lh_right_1454_1462',('support_harbor',(85,105),(1454,1462),'right'))]:
  print(name, edge(*args))
