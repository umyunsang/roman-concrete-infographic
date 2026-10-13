import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
vmask=np.load('vmask.npy')[:7087]
bg = Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
srgb = ImageCms.createProfile('sRGB'); pso = ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
t = ImageCms.buildTransform(srgb, pso, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=0)
B = np.asarray(ImageCms.applyTransform(bg, t)).astype(np.int16)
R = np.asarray(Image.open('print_cmyk_300.tif')).astype(np.int16)[:7087]
# Also compare directly the tile jpgs on disk and extracted pdf jpgs
d = np.abs(R-B).max(axis=2)
vm=vmask.copy()
for _ in range(4):
    vm = vm | np.roll(vm,1,0) | np.roll(vm,-1,0) | np.roll(vm,1,1) | np.roll(vm,-1,1)
d[vm]=0
bs=100
H,Wd=d.shape
g=(d[:H//bs*bs,:Wd//bs*bs]>60).reshape(H//bs,bs,Wd//bs,bs).sum(axis=(1,3))
idx=np.dstack(np.unravel_index(np.argsort(-g.ravel())[:12], g.shape))[0]
for (by,bx) in idx:
    print('block y%d x%d count %d  pt(x %.0f-%.0f, y %.0f-%.0f)'%(by*bs,bx*bs,g[by,bx], bx*bs*.24-8.5,(bx+1)*bs*.24-8.5, by*bs*.24-8.5,(by+1)*bs*.24-8.5))
# save a crop of the worst block: original RGB vs render softproof
by,bx=idx[0]
y0,x0=by*bs-50,bx*bs-50
crop_o = bg.crop((x0,y0,x0+200,y0+200)).resize((600,600),Image.NEAREST)
t2 = ImageCms.buildTransform(pso, srgb, 'CMYK', 'RGB', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=ImageCms.Flags.BLACKPOINTCOMPENSATION)
rc = Image.open('print_cmyk_300.tif').crop((x0,y0,x0+200,y0+200))
crop_r = ImageCms.applyTransform(rc, t2).resize((600,600),Image.NEAREST)
canvas=Image.new('RGB',(1210,600),'white'); canvas.paste(crop_o,(0,0)); canvas.paste(crop_r,(610,0)); canvas.save('worst_diff.png')
print('saved crop at', x0,y0)
