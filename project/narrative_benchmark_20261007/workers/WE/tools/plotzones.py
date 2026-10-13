import sys, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d = np.load(sys.argv[1], allow_pickle=True); outp = sys.argv[2]
for n in ('hill', 'privn', 'bench'):
    Z = d[n + '_Z']; x0, x1, y0, y1 = d[n + '_ext']
    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(Z, origin='lower', extent=(x0, x1, y0, y1), cmap='terrain')
    cs = ax.contour(np.linspace(x0, x1, Z.shape[1]), np.linspace(y0, y1, Z.shape[0]), Z, levels=np.arange(-1, 4, 0.2), colors='k', linewidths=0.4)
    ax.clabel(cs, fontsize=6)
    if n + '_objs' in d:
        for k in d[n + '_objs']:
            v = d[f'{n}__{k}']
            ax.scatter(v[:, 0], v[:, 1], s=0.3, alpha=0.3)
            ax.text(v[:, 0].mean(), v[:, 1].mean(), str(k)[:14], fontsize=6)
    plt.colorbar(im); ax.set_title(n); fig.savefig(f'{outp}_{n}.png', dpi=80); plt.close(fig)
