exec(open("common.py").read())
bx=json.load(open('sub/boxes.json')); s=bx['s']
def Lstar(a):
    a=a[...,:3].astype(float)/255
    lin=np.where(a<=0.04045,a/12.92,((a+0.055)/1.055)**2.4)
    Y=0.2126*lin[...,0]+0.7152*lin[...,1]+0.0722*lin[...,2]
    return np.where(Y>0.008856,116*np.cbrt(Y)-16,903.3*Y)
out={}
for aid,pb in bx['boxes'].items():
    b=np.asarray(Image.open(f'sub/{aid}_base.png').convert('RGB')); u=np.asarray(Image.open(f'sub/{aid}_sub.png').convert('RGB'))
    D=Lstar(b)-Lstar(u)
    # M_A at render res: resample poster-grid M to this box
    x0,x1,y0,y1=pb
    Mg=M(aid)
    # sample M at render pixel centers
    yy,xx=np.mgrid[y0:y1,x0:x1]
    py=np.clip(((yy+0.5)/s*S).astype(int),0,H-1); px=np.clip(((xx+0.5)/s*S).astype(int),0,W-1)
    Mr=Mg[py,px]
    Mr_d=ndi.binary_dilation(Mr,iterations=2)
    cand=(D<=-2)&~Mr_d
    lab,n=ndi.label(cand)
    sizes=ndi.sum(cand,lab,range(1,n+1))
    keep=np.isin(lab,[i+1 for i,sz in enumerate(sizes) if sz/(s*s)>=4])
    np.save(f'sub/{aid}_sh.npy',keep)
    # changed pixels elsewhere (A hides things): pixels outside M where D>2
    out[aid]={'shadow_area_pt2':float(keep.sum()/(s*s)),'n_comp':int(sum(1 for sz in sizes if sz/(s*s)>=4)),'shadow_bbox_pt':None}
    if keep.any():
        ys,xs=np.where(keep); out[aid]['shadow_bbox_pt']=[round((x0+xs.min())/s,1),round((x0+xs.max()+1)/s,1),round((y0+ys.min())/s,1),round((y0+ys.max()+1)/s,1)]
    # visualise
    vis=b.copy(); vis[keep]=(vis[keep]*0.4+np.array([255,0,0])*0.6).astype(np.uint8)
    e=Mr&~ndi.binary_erosion(Mr); vis[e]=[0,0,255]
    Image.fromarray(vis).save(f'sub/{aid}_shvis.png')
    print(aid,out[aid])
json.dump(out,open('sub/shadow.json','w'))
