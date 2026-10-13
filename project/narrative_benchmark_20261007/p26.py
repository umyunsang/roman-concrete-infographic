import sys, json; sys.path.insert(0,'.')
from faces import *
from PIL import ImageCms
ICC='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/PSOcoated_v3.icc'
srgb=ImageCms.createProfile('sRGB'); pso=ImageCms.getOpenProfile(ICC)
t1=ImageCms.buildTransform(srgb,pso,'RGB','CMYK',renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
t2=ImageCms.buildTransform(pso,srgb,'CMYK','RGB',renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC)
def printsim(C):
    im=Image.fromarray(C.astype(np.uint8)); cm=ImageCms.applyTransform(im,t1); back=ImageCms.applyTransform(cm,t2)
    return np.array(back).astype(np.float64)
out={}
for aid,mat in [('support_breakwater_block','RC.v12.roman_stone'),('support_harbor','RC.v12.roman_stone'),('support_pompeii_site','RC.v12.roman_stone'),('support_privernum','RC.v12.roman_stone'),('support_ruin_observers','RC.v12.roman_stone'),('landmark_pompeii_town','RC.v12.roman_stone'),('landmark_lime_kiln',None),('landmark_aqueduct','RC.v12.roman_stone'),('landmark_vesuvius',None),('landmark_apennines',None)]:
    F=facemaps(aid,None,mat=mat); d=F['d']
    P=printsim(d['C']); Lp=Lstar(P); Lc=F['Lc']
    r={}
    for k in ['topE','FLE','FRE','Lam','Sig']:
        m=F[k]
        if m.sum()>30: r[k]=(round(float(np.median(Lc[m])),2),round(float(np.median(Lp[m])),2))
    def pair(a,b):
        if a in r and b in r:
            pre=r[a][0]-r[b][0]; post=r[a][1]-r[b][1]; return (round(pre,2),round(post,2),round(post/pre,3) if pre else None)
    res={'top-L':pair('topE','FLE'),'L-R':pair('FLE','FRE'),'top-R':pair('topE','FRE'),'Lam-Sig':pair('Lam','Sig')}
    print(aid,res)
    out[aid]=res
json.dump(out,open('p26.json','w'),indent=1)
