import sys
sys.path.insert(0,'/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/workers/WC/meas')
from compose import crop
SP={'core34':(380,900,1100,1320,2),'core3z':(430,580,1120,1300,3),'core4z':(610,850,1120,1260,4),'core5z':(975,1170,655,770,4),
    'd1z':(20,145,1545,1672,4),'core1':(520,950,330,600,2)}
src,tag=sys.argv[1],sys.argv[2]; which=sys.argv[3].split(',') if len(sys.argv)>3 else list(SP)
for k in which:
    x0,x1,y0,y1,s=SP[k]; crop(src,x0,x1,y0,y1,f'../crops/{tag}_{k}.png',s)
