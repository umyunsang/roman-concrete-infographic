import json, numpy as np
from PIL import Image
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
m=Image.open(B+'full/full_map_pass.png').convert('RGBA')
o=Image.open(B+'full/full_overlay_pass.png').convert('RGBA')
print(m.size,o.size)
c=Image.alpha_composite(m,o)
bg=Image.new('RGBA',c.size,(255,255,255,255))
c=Image.alpha_composite(bg,c).convert('RGB')
c.save('full3x.png')
a=np.array(Image.open(B+'full/full_map_pass.png'))[...,3]
print('map alpha min',a.min(), (a<255).mean())
