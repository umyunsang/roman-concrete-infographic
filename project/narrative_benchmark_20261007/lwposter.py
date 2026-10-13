import sys; sys.path.insert(0,'lib')
from m import *
idm=np.asarray(Image.open(BASE+'idpass/id_id_map.png'))[...,:3].astype(int)
code=idm[...,0]*65536+idm[...,1]*256+idm[...,2]
land=code==(98*65536+14*256+2)
P=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png').convert('RGB')).astype(float)
Mo=np.asarray(Image.open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/map_only_2x.png').convert('RGB')).astype(float)
print(idm.shape,P.shape)
h=min(idm.shape[0],P.shape[0]); w=min(idm.shape[1],P.shape[1])
land=land[:h,:w]; P=P[:h,:w]; Mo=Mo[:h,:w]
# exclude overlay-pass objects: overlay id map
ov=np.asarray(Image.open(BASE+'idpass/id_id_overlay.png'))
ovm=(ov[...,3]>0) if ov.shape[-1]==4 else (ov[...,:3].sum(-1)>0)
ovm=ovm[:h,:w]
notext=np.abs(P-Mo).max(-1)<=8
g=land&~ndi.binary_dilation(ovm,iterations=2)&notext
g=ndi.binary_erosion(g,iterations=1)
u,inv=np.unique(P[g].astype(int),axis=0,return_inverse=True)
Lu=lab(u.astype(float))[:,0]; O=oklch(u.astype(float))
lwu=(Lu>=95)&(O[:,1]<=0.035)&(O[:,2]>=70)&(O[:,2]<=110)
lw=np.zeros(g.shape,bool); lw[g]=lwu[inv.ravel()]
print('ground px',g.sum(),'lw px',lw.sum(),'%.3f%%'%(lw.sum()/g.sum()*100))
lb,nb=ndi.label(lw); sz=ndi.sum(lw,lb,range(1,nb+1)); com=ndi.center_of_mass(lw,lb,range(1,nb+1))
big=[(s/4,c[1]/1.9992,c[0]/1.9992,k+1) for k,(s,c) in enumerate(zip(sz,com)) if s>=4]
print('blobs >=1pt2:',len(big),'area pt2',round(sum(b[0] for b in big),1))
T=json.load(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/text_spec_r11.json'))['texts']
B={t[0]:t[1] for t in T}
def dist(bx,x,y):
    X,Y,Wb,Hb=bx; dx=max(X-x,0,x-(X+Wb)); dy=max(Y-y,0,y-(Y+Hb)); return (dx*dx+dy*dy)**0.5
for tid in ['790:187','790:188','790:166','790:109','790:112','790:113','790:127','790:108','790:178']:
    near=[b for b in big if dist(B[tid],b[1],b[2])<=60]
    print(tid,B[tid],'blobs within 60pt:',len(near),'pt2',round(sum(b[0] for b in near),1),'max',round(max([b[0] for b in near],default=0),1),'min dist',round(min([dist(B[tid],b[1],b[2]) for b in big]),1))
# L* stats of lw blobs near 4 labels
sel=[b for b in big if dist(B['790:188'],b[1],b[2])<=60 or dist(B['790:187'],b[1],b[2])<=60]
mm=np.isin(lb,[b[3] for b in sel])
print('near-④ lw blob pixel color median', desc(np.median(P[mm],0)), 'L p95 %.1f'%np.percentile(Lstar(P[mm]),95))
ring=ndi.binary_dilation(mm,iterations=6)&g&~lw
print('surrounding ground median', desc(np.median(P[ring],0)))
