import json,sys
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def z(aid, x0,x1,y0,y1, name, f=2, src='context'):
    a=idx[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
    im=Image.open(a['files'][src])
    box=(int((x0-cx0)*3),int((y0-cy0)*3),int((x1-cx0)*3),int((y1-cy0)*3))
    c=im.crop(box); c=c.resize((c.width*f,c.height*f),Image.LANCZOS); c.save(name)
z('support_privernum',1010,1137,1060,1115,'z_priv_bottom.png')
z('support_ruin_observers',857,975,1190,1253,'z_ruin_bottom.png')
z('support_breakwater_block',440,512,1495,1540,'z_bw_corner.png',f=3)
z('support_harbor',31,240,1470,1536,'z_harbor_bottom.png')
z('support_harbor',300,399,1430,1536,'z_pilae.png',f=3)
