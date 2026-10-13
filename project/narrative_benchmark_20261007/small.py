from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r10/'
im=Image.open(R+'map_only_2x.png').convert('RGB'); im.resize((1191//1,1684//1)).crop((0,0,1191,1684)).save('map_1x.png')
