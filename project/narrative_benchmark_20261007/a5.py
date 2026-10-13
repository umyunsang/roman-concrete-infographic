import numpy as np
from PIL import Image, ImageCms
Image.MAX_IMAGE_PIXELS=None
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
R = np.asarray(Image.open('print_cmyk_300.tif')).astype(np.float64)[:7087]
vm=np.load('vmask.npy')[:7087]
bg = Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
srgb = ImageCms.createProfile('sRGB'); pso = ImageCms.getOpenProfile(W+'PSOcoated_v3.icc')
t = ImageCms.buildTransform(srgb, pso, 'RGB', 'CMYK', renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC, flags=0)
B = np.asarray(ImageCms.applyTransform(bg, t)).astype(np.float64)
def coldiff(A, x, rows):
    return np.abs(A[rows, x]-A[rows, x-1]).sum(axis=1)
rows = np.where(~vm[:,2510:2524].any(axis=1))[0]
print('vertical seam x=2517')
for x in range(2513,2522):
    print('  x%d|%d render %.2f  source %.2f'%(x-1,x, coldiff(R,x,rows).mean(), coldiff(B,x,rows).mean()))
cols = np.where(~vm[3537:3551,:].any(axis=0))[0]
print('horizontal seam y=3544')
for y in range(3540,3549):
    print('  y%d|%d render %.2f  source %.2f'%(y-1,y, np.abs(R[y,cols]-R[y-1,cols]).sum(axis=1).mean(), np.abs(B[y,cols]-B[y-1,cols]).sum(axis=1).mean()))
# also check render column at seam vs neighbors average color shift (beige leak)
bgfill=np.array([0.094,0.125,0.22,0.004])*255
for x in (2516,2517):
    print('col',x,'mean dist to beige fill', np.abs(R[rows,x]-bgfill).sum(axis=1).mean(), 'neighbors', np.abs(R[rows,x-3]-bgfill).sum(axis=1).mean())
