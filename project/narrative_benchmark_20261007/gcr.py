import numpy as np, subprocess
ICC='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/PSOcoated_v3.icc'
def lab_of(cmyks):
    inp='\n'.join(' '.join('%.1f'%v for v in c) for c in cmyks)+'\n'
    out=subprocess.run(['transicc','-i',ICC,'-o','*Lab','-t1','-n'],input=inp,capture_output=True,text=True).stdout
    vals=[list(map(float,l.split())) for l in out.strip().split('\n') if len(l.split())==3 and not l.startswith('Copyright')]
    return np.array(vals[-len(cmyks):])
def de00(l1,l2):
    L1,a1,b1=l1.T; L2,a2,b2=l2.T
    C1=np.hypot(a1,b1); C2=np.hypot(a2,b2); Cb=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7))); a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1); C2p=np.hypot(a2p,b2)
    h1=np.degrees(np.arctan2(b1,a1p))%360; h2=np.degrees(np.arctan2(b2,a2p))%360
    dL=L2-L1; dC=C2p-C1p; dh=h2-h1; dh=np.where(dh>180,dh-360,np.where(dh<-180,dh+360,dh))
    dH=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2)); Lb=(L1+L2)/2; Cbp=(C1p+C2p)/2
    hb=np.where(np.abs(h1-h2)<=180,(h1+h2)/2,np.where(h1+h2<360,(h1+h2+360)/2,(h1+h2-360)/2))
    T=1-0.17*np.cos(np.radians(hb-30))+0.24*np.cos(np.radians(2*hb))+0.32*np.cos(np.radians(3*hb+6))-0.2*np.cos(np.radians(4*hb-63))
    dth=30*np.exp(-((hb-275)/25)**2); RC=2*np.sqrt(Cbp**7/(Cbp**7+25**7))
    SL=1+0.015*(Lb-50)**2/np.sqrt(20+(Lb-50)**2); SC=1+0.045*Cbp; SH=1+0.015*Cbp*T; RT=-np.sin(np.radians(2*dth))*RC
    return np.sqrt((dL/SL)**2+(dC/SC)**2+(dH/SH)**2+RT*(dC/SC)*(dH/SH))
for name,orig,drop in (('#1B5760',(84.7,31.0,35.3,52.2),1),('#8A5427',(16.1,60.8,91.4,45.5),0)):
    ref=lab_of([orig])[0]
    cands=[]
    rng=np.arange(0,101,2.5)
    grid=[]
    for a in rng:
        for b in rng:
            for k in np.arange(40,101,2.5):
                c=[0,0,0,0]; others=[i for i in range(3) if i!=drop]
                c[others[0]]=a; c[others[1]]=b; c[3]=k; grid.append(c)
    labs=lab_of(grid)
    d=de00(np.repeat(ref[None],len(grid),0),labs)
    order=np.argsort(d)[:5]
    print(name,'orig',orig,'Lab',ref.round(2))
    for i in order: print('   ',grid[i],'TAC',sum(grid[i]),'dE00 %.2f'%d[i])
