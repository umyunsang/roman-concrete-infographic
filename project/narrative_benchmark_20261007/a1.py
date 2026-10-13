import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg = Image.open(W+'v8_11_map_print_bleed_5033x7087.png')
print('bg', bg.mode, bg.size, bg.info.keys(), 'icc' in bg.info)
r = Image.open('print_cmyk_300.tif'); print('render', r.mode, r.size, r.info.get('dpi'))
R = np.asarray(r).astype(np.int16)
tac = R.sum(axis=2)/255*100
print('TAC max %.1f  p99.99 %.1f p99.9 %.1f; n>300 %d n>302 %d n>305 %d n>310 %d of %d' % (tac.max(), np.percentile(tac,99.99), np.percentile(tac,99.9), (tac>300).sum(), (tac>302).sum(), (tac>305).sum(), (tac>310).sum(), tac.size))
ys,xs = np.where(tac>300)
if len(ys): print(' >300 bbox', ys.min(), ys.max(), xs.min(), xs.max(), 'top locs', list(zip(ys[:5],xs[:5])))
for c,n in enumerate('CMYK'): print(n, 'max', R[...,c].max())
np.save('tac.npy', tac.astype(np.float32))
# compare with original converted
srgb = ImageCms.createProfile('sRGB')
pso = ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
t = ImageCms.buildTransform(srgb, pso, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=0)
bgc = ImageCms.applyTransform(bg.convert('RGB'), t)
B = np.asarray(bgc).astype(np.int16)
h=min(B.shape[0],R.shape[0]); w=min(B.shape[1],R.shape[1])
# vector mask: where vector render differs from flat background fill
V = np.asarray(Image.open('print_vec_300.tif')).astype(np.int16)
bgfill = np.array([0.094,0.125,0.22,0.004])*255
vmask = (np.abs(V-bgfill).sum(axis=2)>6)
print('vector-ink pixels', vmask.sum())
np.save('vmask.npy', vmask)
d = np.abs(R[:h,:w]-B[:h,:w])
m = ~vmask[:h,:w]
for c,n in enumerate('CMYK'):
    dc=d[...,c][m]; print('diff', n, 'mean %.2f p99 %.1f max %d'%(dc.mean(), np.percentile(dc,99), dc.max()))
# also nobpc vs bpc check
t2 = ImageCms.buildTransform(srgb, pso, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
B2 = np.asarray(ImageCms.applyTransform(bg.convert('RGB'), t2)).astype(np.int16)
d2=np.abs(R[:h,:w]-B2[:h,:w])
print('vs BPC transform mean diff', [round(float(d2[...,c][m].mean()),2) for c in range(4)])
tacB = B.sum(axis=2)/255*100
print('original-converted TAC max %.1f'%tacB.max(), 'n>300', (tacB>300).sum())
