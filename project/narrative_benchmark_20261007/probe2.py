from PIL import Image
import numpy as np
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/r9/'
P=np.asarray(Image.open(R+'poster_2x.png').convert('RGB')).astype(int)
M=np.asarray(Image.open(R+'map_only_2x.png').convert('RGB')).astype(int)
D=(np.abs(P-M).sum(2)>30).astype(np.uint8)*255
Image.fromarray(D).resize((1191//1,1684//1)).save('diff_1x.png')
Image.open(R+'map_only_2x.png').resize((1191,1684)).save('map_1x.png')
