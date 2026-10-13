import numpy as np, json
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
pm=np.load('pm144.npy'); tm=np.load('tm144.npy'); sm=np.load('sm144.npy')
spec=json.load(open(RV+'text_spec_r9.json'))['texts']
def dil(m,n):
    for _ in range(n): m = m | np.roll(m,1,0) | np.roll(m,-1,0) | np.roll(m,1,1) | np.roll(m,-1,1)
    return m
pmd=dil(pm,2); tmd=dil(tm,2)
bad=[]
for t in spec:
    x,y,w,h=t[1]; x0=int(x*2)-2; y0=int(y*2)-2; x1=int((x+w)*2)+3; y1=int((y+h)*2)+3
    a=tm[y0:y1,x0:x1]; b=pm[y0:y1,x0:x1]
    cov_t = (a & pmd[y0:y1,x0:x1]).sum()/max(a.sum(),1)   # poster ink covered by print ink
    cov_p = (b & tmd[y0:y1,x0:x1]).sum()/max(b.sum(),1)
    txt=''.join(s[0] for s in t[4]).replace('\n','/')[:22]
    flag = '' if cov_t>0.9 and cov_p>0.9 else '  <<<'
    if flag: bad.append(t[0])
    print('%-7s rot%4s poster_ink %5d print_ink %5d cov_t %.2f cov_p %.2f %s%s'%(t[0], t[2], a.sum(), b.sum(), cov_t, cov_p, txt, flag))
print('BAD', bad)
