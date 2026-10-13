import sys; sys.path.insert(0,"/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/oc_b1")
from base import *
p=np.asarray(Image.open(B+'nb_work/review_loop/r11/poster_1x.png').convert('RGB')).astype(float)
L=lab(p.reshape(-1,3))[:,0]
sel=L[(L>84)&(L<92)]
print('Lpaper', np.median(sel), len(sel))
for hx_ in ['#D3BE9E','#B5A68B','#8D6C49','#B9976F','#FFF4DD','#DED1AF','#526873','#A47C66','#9C5C43','#C99C78','#CDC7AE','#B5A07B','#983821','#82B9BC','#A9A69F','#C7BEAA']:
    c=h2r(hx_); print(hx_, 'oklch',np.round(oklch(c),3), 'L*',round(float(lab(c)[0]),1))
print('dE stone-plinth',de00(lab(h2r('#D3BE9E')),lab(h2r('#B5A68B'))))
print('dE basin-arena',de00(lab(h2r('#B9976F')),lab(h2r('#B5A07B'))))
print('dE cloth blend-registry',de00(lab(h2r('#A47C66')),lab(h2r('#9C5C43'))))
print('dE linen-stone',de00(lab(h2r('#DED1AF')),lab(h2r('#D3BE9E'))))
print('dE stone-volcano',de00(lab(h2r('#D3BE9E')),lab(h2r('#CDC7AE'))))
