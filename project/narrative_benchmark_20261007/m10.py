import numpy as np, json
from PIL import Image
idx=json.load(open('../nb_work/review_loop/obj_r11/assets_index.json'))
A={a['id']:a for a in idx['assets']}
a=A['road_appia']; x0,x1,y0,y1=a['crop_pt']
al=np.asarray(Image.open(a['files']['isolated_rgba']))[...,3]>128
xs=[];ys=[];ws=[]
for c in range(al.shape[1]):
    r=np.nonzero(al[:,c])[0]
    if len(r)<5: continue
    xs.append(x0+c/3); ys.append(y0+(r.min()+r.max())/6); ws.append((r.max()-r.min())/3)
xs=np.array(xs); ys=np.array(ys)
print("x %.1f-%.1f, centre y at x=870,950,1030,1110,1185:"%(xs.min(),xs.max()), [round(float(np.interp(x,xs,ys)),1) for x in (870,950,1030,1110,1185)], "width median %.1f"%np.median(ws))
# chord deviation over whole
def maxdev(i,j):
    p=np.c_[xs[i:j],ys[i:j]]; a_=p[0]; b=p[-1]; d=b-a_; n=np.array([-d[1],d[0]])/np.linalg.norm(d)
    return np.abs((p-a_)@n).max()
print("whole chord max deviation %.1f pt over %.0f pt"%(maxdev(0,len(xs)), xs.max()-xs.min()))
# longest straight run with deviation <= 1.5pt (about 1 stone width/2)
best=(0,0,0)
n=len(xs)
for tol in (1.0,2.0):
    best=(0,0,0); j=0
    for i in range(0,n,3):
        j=max(j,i+2)
        while j<n and maxdev(i,j+1)<=tol: j+=1
        if xs[j-1]-xs[i]>best[0]: best=(xs[j-1]-xs[i],xs[i],xs[j-1])
    print("longest run with dev<=%.1fpt: %.0f pt (x %.0f-%.0f)"%(tol,*best))
