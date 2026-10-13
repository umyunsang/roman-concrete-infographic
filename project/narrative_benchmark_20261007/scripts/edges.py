import numpy as np, json
from PIL import Image
from skimage import color
from scipy import ndimage as ndi
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
  return len(ys), round(float(np.abs(r).max()),2), round(float(r.std()),2)
def inner_edge(aid,xr,yr):
  a=A[aid]; im=np.asarray(Image.open(a['files']['isolated']).convert('RGB')).astype(float)/255
  x0,y0=a['crop_pt'][0],a['crop_pt'][2]
  L=ndi.gaussian_filter(color.rgb2lab(im)[...,0],0.8)
  gx=np.gradient(L,axis=1)
  ys=[];xs=[]
  for py in np.arange(yr[0],yr[1],1/3):
    r=int(round((py-y0)*3)); c0,c1=int((xr[0]-x0)*3),int((xr[1]-x0)*3); g=np.abs(gx[r,c0:c1]); i=int(np.argmax(g))
    if 0<i<len(g)-1:
      d=(g[i-1]-g[i+1])/(2*(g[i-1]-2*g[i]+g[i+1])+1e-9); ys.append(py); xs.append(x0+(c0+i+d)/3)
  ys=np.array(ys); xs=np.array(xs); p=np.polyfit(ys,xs,1); r=xs-np.polyval(p,ys)
  return len(ys), round(float(np.abs(r).max()),2), round(float(r.std()),2)
print('town right silhouette vertical 1443-1467', edge('landmark_pompeii_town',(895,907),(1443,1467),'right'))
print('town tall tower corner (inner) 1465-1498', inner_edge('landmark_pompeii_town',(866,875),(1465,1498)))
print('lighthouse shaft front corner (inner) 1430-1476', inner_edge('support_harbor',(76,86),(1430,1476)))
print('pomsite right wall right edge 1462-1495', edge('support_pompeii_site',(740,752),(1462,1495),'right'))
print('pomsite right wall front corner (inner) 1462-1497', inner_edge('support_pompeii_site',(728,736),(1462,1497)))
