from PIL import Image
P='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r11/poster_2x.png'
im=Image.open(P).convert('RGB')
print(im.size)
def crop(name,x0,y0,x1,y1,z=3):
    c=im.crop((int(x0*2),int(y0*2),int(x1*2),int(y1*2)))
    c=c.resize((c.width*z//2*1, c.height*z//2*1), Image.LANCZOS) if z!=2 else c
    c.save(name)
crop('d3_area.png',250,1170,440,1330,z=4)
crop('d2_area.png',60,960,200,1030,z=6)
crop('harbor_area.png',150,1450,300,1560,z=5)
crop('pompeii_area.png',650,1440,800,1580,z=5)
