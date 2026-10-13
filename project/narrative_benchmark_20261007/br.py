from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
B='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/'
D=Image.open(B+'review_loop/r10/poster_2x.png').convert('RGB')
P=Image.open('print_proof300.png')
# design pt region x 1100-1191, y 1500-1600 ; print px = (pt+8.5)*300/72
def pcrop(x0,y0,x1,y1):
    f=300/72
    return P.crop((int((x0+8.5)*f),int((y0+8.5)*f),int((x1+8.5)*f),int((y1+8.5)*f)))
x0,y0,x1,y1=1080,1440,1199.5,1560
d=D.crop((x0*2,y0*2,min(x1,1191)*2,y1*2)).resize((int((min(x1,1191)-x0)*300/72), int((y1-y0)*300/72)))
p=pcrop(x0,y0,x1,y1)
out=Image.new('RGB',(d.width+p.width+10,max(d.height,p.height)),(255,255,255)); out.paste(d,(0,0)); out.paste(p,(d.width+10,0))
dr=ImageDraw.Draw(out); xt=d.width+10+int((1191-x0)*300/72); dr.line([(xt,0),(xt,out.height)],fill=(255,0,255))
out.save('cmp_br.png'); print(out.size)
