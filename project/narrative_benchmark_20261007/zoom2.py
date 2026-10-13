import json
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/'
idx={a['id']:a for a in json.load(open(R+'assets_index.json'))['assets']}
def z(aid, x0,x1,y0,y1, name, f=3, src='context'):
    a=idx[aid]; cx0,cx1,cy0,cy1=a['crop_pt']
    im=Image.open(a['files'][src])
    box=(int((x0-cx0)*3),int((y0-cy0)*3),int((x1-cx0)*3),int((y1-cy0)*3))
    c=im.crop(box); c=c.resize((c.width*f,c.height*f),Image.LANCZOS); c.save(name)
z('landmark_aqueduct',870,930,550,620,'z_aq1.png')
z('landmark_aqueduct',1020,1080,440,500,'z_aq2.png')
z('landmark_aqueduct',1090,1175,350,460,'z_aq3.png',f=2)
