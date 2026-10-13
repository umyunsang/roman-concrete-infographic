from PIL import Image
Image.MAX_IMAGE_PIXELS=None
RV='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
W='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/out/print/'
bg=Image.open(W+'v8_11_map_print_bleed_5033x7087.png').convert('RGB')
mo=Image.open(RV+'r9/map_only_2x.png').convert('RGB')
s=1/0.2400159
regs=[(630,1180,820,1270),(1010,690,1150,760),(790,900,870,970)]
rows=[]
for (x0,y0,x1,y1) in regs:
    k=3
    a=mo.crop((x0*2,y0*2,x1*2,y1*2)).resize(((x1-x0)*k,(y1-y0)*k),Image.LANCZOS)
    b=bg.crop((round((x0+8.5)*s),round((y0+8.5)*s),round((x1+8.5)*s),round((y1+8.5)*s))).resize(((x1-x0)*k,(y1-y0)*k),Image.LANCZOS)
    w,h=a.size; t=Image.new('RGB',(w,2*h+6),'white'); t.paste(a,(0,0)); t.paste(b,(0,h+6)); rows.append(t)
Wt=sum(r.size[0] for r in rows)+10*len(rows); Ht=max(r.size[1] for r in rows)
o=Image.new('RGB',(Wt,Ht),'white'); x=0
for r in rows: o.paste(r,(x,0)); x+=r.size[0]+10
o.thumbnail((1500,1000)); o.save('objdiff.png'); print(o.size)
