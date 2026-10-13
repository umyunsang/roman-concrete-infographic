exec(open('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oi_b1/feat.py').read().split("feature('landmark_vesuvius'")[0])
m=mask('landmark_lime_kiln')
x0,y0,x1,y1=120,640,200,720
for yy in range(y0,y1,4):
    row=[]
    for xx in range(x0,x1,4):
        c=L[yy*2:yy*2+8,xx*2:xx*2+8]; mm=m[yy*2:yy*2+8,xx*2:xx*2+8]
        row.append('%3d'%np.median(c[mm]) if mm.mean()>0.5 else ' --')
    print(yy,' '.join(row))
