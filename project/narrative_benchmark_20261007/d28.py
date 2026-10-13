import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.sparse.csgraph import minimum_spanning_tree
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def fm(aid):
    a=idx[aid]; x0,x1,y0,y1=a['crop_pt']
    al=np.array(Image.open(a['files']['isolated_rgba']))[...,3]>=128
    M=np.zeros((5052,3573),bool); u0=int(round(x0*3)); v0=int(round(y0*3)); h,w=al.shape
    M[v0:v0+h,u0:u0+w]=al[:5052-v0,:3573-u0]; return M
plate=lambda b: b.startswith(('fields_','road_','water_')) or b=='ground_land'
for A in ['trees_s','trees_se']:
    MA=fm(A)
    ys,xs=np.nonzero(MA); sl=(slice(max(0,ys.min()-300),ys.max()+300),slice(max(0,xs.min()-300),xs.max()+300))
    m=MA[sl]
    lab,n=ndi.label(m)
    # pairwise min distances between components
    D=np.zeros((n,n))
    dts=[ndi.distance_transform_edt(lab!=i+1) for i in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            D[i,j]=D[j,i]=dts[i][lab==j+1].min()/3
    mst=minimum_spanning_tree(D).toarray()
    g_in=mst.max() if n>1 else 0
    dA=ndi.distance_transform_edt(~m)
    outs=[]
    for B in idx:
        if B==A or plate(B): continue
        MB=fm(B)[sl]
        if MB.any(): outs.append((round(float(dA[MB].min()/3),1),B))
    outs.sort()
    print('28',A,'components',n,'MST edges',sorted(np.round(mst[mst>0],1).tolist()),'g_in %.1f'%g_in,'g_out',outs[:3],'ratio %.2f'%(outs[0][0]/g_in if g_in else float('inf')))
