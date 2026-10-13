import sys, json; sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/lib')
from cl import *
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
O='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc2/'
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/landmark_colosseum/'
g=json.load(open(O+'align.json'))['landmark_colosseum']; idm=json.load(open(O+'idr/id_map.json'))
iso=np.array(Image.open(B+'isolated_rgba.png')).astype(float); rgb=iso[...,:3]; a=iso[...,3]
m=np.array(Image.open(O+'idr/iso_mat_landmark_colosseum.png'))[g['Y']:g['Y']+g['h'],g['X']:g['X']+g['w']]
PX=2.9992
toks={'W':('RC.v12.colosseum_wall','#CDA477'),'I':('RC.v12.colosseum_interior','#B89D78'),'A':('RC.v12.arena_earth','#B5A07B'),'P':('RC.v12_4.piazza_travertine','#D2C2A2')}
M={}; Y=relY(rgb); S=np.zeros(Y.shape)
for k,(n,h) in toks.items():
  c=idm['mat_ids'][n]; M[k]=(m[...,0]==c[0])&(m[...,1]==c[1])&(m[...,2]==c[2])&(m[...,3]>127)
  S[M[k]]=Y[M[k]]/float(relY(h2r(h)))
full=a>=254
LAB=lab(rgb)
res=[]
for src,dst in [('W','I'),('I','W')]:
  lbl,n=ndi.label(M[src]); sizes=ndi.sum(M[src],lbl,range(1,n+1))
  for i,s in enumerate(sizes):
    if s<18: continue
    isl=lbl==(i+1)
    ring=ndi.binary_dilation(isl,iterations=3)&~isl
    rv=ring.sum(); 
    if rv==0: continue
    fd=(ring&M[dst]).sum()/rv
    if fd<0.8: continue
    # same-plane test: compare shading factor in island vs surrounding dst pixels (inner parts only)
    ii=ndi.binary_erosion(isl,iterations=1)&full
    if ii.sum()<6: ii=isl&full
    rr=ring&M[dst]&full
    if ii.sum()<4 or rr.sum()<4: continue
    si=np.median(S[ii]); sr=np.median(S[rr])
    same=abs(si-sr)/sr<0.10
    ci=np.median(rgb[ii],0); cr=np.median(rgb[rr],0)
    dE=float(de00(lab(ci),lab(cr)))
    cy,cx=ndi.center_of_mass(isl)
    res.append((src,round(s/PX**2,1),round(322.1+cx/PX,1),round(544.3+cy/PX,1),round(float(si),2),round(float(sr),2),same,round(dE,2),hx(ci),hx(cr)))
same=[r for r in res if r[6]]
print('islands >=2pt2 fully surrounded (>=80%) by the other token:',len(res),' same-plane (|dS|<10%):',len(same))
print(' by src: W-in-I',sum(1 for r in same if r[0]=='W'),' I-in-W',sum(1 for r in same if r[0]=='I'))
print(' same-plane dE00 median',round(float(np.median([r[7] for r in same])),2) if same else None,' n with dE00>2:',sum(1 for r in same if r[7]>2),' total area pt2',round(sum(r[1] for r in same if r[7]>2),1))
for r in sorted(same,key=lambda r:-r[1])[:15]: print('  ',r)
