import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/colorjudge_r9')
import numpy as np
from PIL import Image, ImageCms
from colorlib import de00, hex2rgb
R = '/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
PSO = ImageCms.getOpenProfile('/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/icc/pso/PSOcoated_v3.icc')
SRGB = ImageCms.createProfile('sRGB'); LAB = ImageCms.createProfile('LAB', 5000)
REL = ImageCms.Intent.RELATIVE_COLORIMETRIC
BPC = ImageCms.Flags.BLACKPOINTCOMPENSATION
t_s2lab = ImageCms.buildTransform(SRGB, LAB, 'RGB', 'LAB', REL)
t_c2lab = ImageCms.buildTransform(PSO, LAB, 'CMYK', 'LAB', REL)
t_s2c = {'BPC on (rubric)': ImageCms.buildTransform(SRGB, PSO, 'RGB', 'CMYK', REL, flags=BPC),
         'BPC off (D31)': ImageCms.buildTransform(SRGB, PSO, 'RGB', 'CMYK', REL)}
def lab_arr(img):
    a = np.array(img).astype(float)
    L = a[..., 0] * 100 / 255
    ab = a[..., 1:]
    ab = np.where(ab > 127, ab - 256, ab)  # Pillow LAB stores a,b as signed int8 in uint8
    return np.concatenate([L[..., None], ab], -1)
def roundtrip(img, t):
    cmyk = ImageCms.applyTransform(img, t)
    return lab_arr(ImageCms.applyTransform(img, t_s2lab)), lab_arr(ImageCms.applyTransform(cmyk, t_c2lab)), np.array(cmyk).astype(float) / 255 * 100
# sanity: white & a mid grey lab
chk = Image.fromarray(np.array([[[255, 255, 255], [128, 128, 128], [152, 56, 33]]], np.uint8))
print('sanity sRGB->Lab D50', np.round(lab_arr(ImageCms.applyTransform(chk, t_s2lab)), 1).tolist())
cols = {'accent #983821': '983821', 'disc render #9D3921': '9D3921', 'sea #9CCACA': '9CCACA', 'river #9BC9C9': '9BC9C9',
        'step1 water #3E8C94': '3E8C94', 'puddle #3E99A5': '3E99A5', 'water label #1B5760': '1B5760', 'calcium label #8A5427': '8A5427',
        'heading #2E2A22': '2E2A22', 'body #3E3A31': '3E3A31', 'secondary #59524A': '59524A',
        'arrow lit #7F2E1B': '7F2E1B', 'arrow lit #8D3520': '8D3520', 'arrow lit #7B2D1B': '7B2D1B'}
arr = np.array([[hex2rgb(v) for v in cols.values()]], np.uint8)
img = Image.fromarray(arr)
for name, t in t_s2c.items():
    a, b, cm = roundtrip(img, t)
    d = de00(a[0], b[0])
    print('==', name)
    for (k, _), dv, c in zip(cols.items(), d, cm[0]):
        print(f'   {k:24s} dE00 {dv:5.2f}  CMYK {np.round(c).astype(int).tolist()}')
poster = Image.open(R + 'r9/poster_1x.png').convert('RGB')
for name, t in t_s2c.items():
    a, b, cm = roundtrip(poster, t)
    d = de00(a, b)
    tac = cm.sum(-1)
    print(f'== poster {name}: frac dE00>5 {np.mean(d > 5)*100:.3f}%  >3 {np.mean(d > 3)*100:.3f}%  p99 {np.percentile(d, 99):.2f} max {d.max():.2f} | TAC max {tac.max():.1f}%  K max {cm[..., 3].max():.1f}%')
