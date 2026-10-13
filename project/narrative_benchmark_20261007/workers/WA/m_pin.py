import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from colorm import lab
root, cx, cy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
idx = {a['id']: a for a in json.load(open(os.path.join(root, 'assets_index.json')))['assets']}
cp = idx['shape_pin_harbor']['crop_pt']
iso = np.asarray(Image.open(os.path.join(root, 'assets/shape_pin_harbor/isolated_rgba.png')).convert('RGBA'), float) / 255
L = lab(iso[..., :3])[..., 0]
yy, xx = np.mgrid[0:L.shape[0], 0:L.shape[1]]; px = cp[0] + xx / 3; py = cp[2] + yy / 3
m = (np.hypot(px - cx, py - cy) <= 1.2) & (iso[..., 3] > 0.9)
v = L[m]; print('dot interior L* min/median/max', round(v.min(), 1), round(float(np.median(v)), 1), round(v.max(), 1), 'range', round(v.max() - v.min(), 1),
              'bright(>L*med+5) area pt2', round(((v > np.median(v) + 5).sum()) / 9, 2))
