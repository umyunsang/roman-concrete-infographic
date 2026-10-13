import sys
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/obj_r11/assets/'
aid=sys.argv[1]; mx=int(sys.argv[2]) if len(sys.argv)>2 else 1400
a=Image.open(R+aid+'/context.png').convert('RGB'); b=Image.open(R+aid+'/isolated.png').convert('RGB')
w,h=a.size; im=Image.new('RGB',(w*2+10,h),(255,255,255)); im.paste(a,(0,0)); im.paste(b,(w+10,0))
s=min(1.0, mx/im.size[0]); im=im.resize((int(im.size[0]*s),int(im.size[1]*s)),Image.LANCZOS)
im.save(aid+'_pair.png'); print(im.size)
