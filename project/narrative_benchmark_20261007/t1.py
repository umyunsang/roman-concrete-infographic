import sys;sys.path.insert(0,'.')
from lib import *
for aid in ['core1_modern_building','core2_hot_mixing','detail_core3_lime_specimen','detail_core4_three_cubes','detail_d1_seawater','detail_d2_making','detail_d3_tower','support_core5_lab','basic_recipe','basic_sources']:
    a,ctx,iso=load(aid)
    M=iso[...,3]>=128
    Lc=Lstar_rgb(ctx);Li=Lstar_rgb(iso[...,:3])
    d=(Lc-Li)[M]
    print(aid, ctx.shape, iso.shape, 'Mfrac %.3f'%M.mean(), 'ctx-iso L in M: med %.2f p10 %.2f p90 %.2f'%(np.median(d),np.percentile(d,10),np.percentile(d,90)), 'medLctx %.1f medLiso %.1f'%(np.median(Lc[M]),np.median(Li[M])))
