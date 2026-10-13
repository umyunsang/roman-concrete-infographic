import json, numpy as np
from PIL import Image
from skimage import color, measure
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx=json.load(open(B+'assets_index.json')); A={a['id']:a for a in idx['assets']}
inv={o['name']:o for o in json.load(open(B+'inventory.json'))['objects']}
for k in range(1,6):
    aid='shape_core%d_marker'%k; a=A[aid]; x0,x1,y0,y1=a['crop_pt']
    im=np.asarray(Image.open(a['files']['isolated_rgba'])).astype(float)/255
    al=im[...,3]; L=color.rgb2lab(im[...,:3])[...,0]
    bx=inv['S_core%d_badge'%k]['bbox_projected_pt']; cx=(bx[0]+bx[1])/2; cy=(bx[2]+bx[3])/2
    H,W=al.shape; yy,xx=np.mgrid[0:H,0:W]; X=x0+(xx+0.5)/3; Y=y0+(yy+0.5)/3; rr=np.hypot(X-cx,Y-cy)
    near=rr<13
    # radius from alpha coverage per angle
    ang=np.arctan2(Y-cy,X-cx)
    radii=[]
    for t in np.linspace(-np.pi,np.pi,96,endpoint=False):
        sel=near&(np.abs(((ang-t+np.pi)%(2*np.pi))-np.pi)<0.04)
        if sel.sum()==0: continue
        rs=rr[sel]; a_=al[sel]
        # estimate edge radius: max r with alpha>0.5
        radii.append(rs[a_>0.5].max())
    radii=np.array(radii)
    prof=[np.median(L[(rr>=r0)&(rr<r0+1)&(al>0.98)]) for r0 in range(0,10)]
    print(aid,'center',round(cx,2),round(cy,2),'edge radius mean %.2f std %.3f range %.2f'%(radii.mean(),radii.std(),radii.max()-radii.min()),'radial L* 0..10pt:',[round(p,1) for p in prof])
    ub=inv['S_core%d_underline'%k]['bbox_projected_pt']
    # underline straightness: per column, centroid y
    c0=int((ub[0]-x0)*3)+3; c1=int((ub[1]-x0)*3)-3; r0=int((ub[2]-x0*0-y0)*3)-4; r1=int((ub[3]-y0)*3)+4
    sub=al[r0:r1,c0:c1]; ys=np.arange(r0,r1)[:,None]
    cen=(sub*ys).sum(0)/sub.sum(0); thick=sub.sum(0)/3
    print('   underline len %.1fpt thickness mean %.2fpt std %.3f, centroid y range %.3fpt'%(ub[1]-ub[0], thick.mean(), thick.std(), (cen.max()-cen.min())/3))
