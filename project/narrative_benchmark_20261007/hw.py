import numpy as np, math
from PIL import Image
R='/private/tmp/claude-501/-Users-um-yunsang/73df8d3b-73af-481e-9f8b-64064c56fc53/scratchpad/nb_work/review_loop/'
ov=Image.open(R+'obj_r11/full/full_overlay_pass.png')
S=2.9992
x0,x1,y0,y1=190,230,1490,1525
c=ov.crop([int(x0*S),int(y0*S),int(x1*S),int(y1*S)]).split()[3]
ang=math.degrees(math.atan2(1518.1-1496.6,222.1-197.6))
r=c.rotate(ang,resample=Image.BICUBIC,expand=True)
a=np.array(r).astype(float)/255
# rows = perpendicular; columns = along-line. find the line row band
rowsum=a.sum(1); rr=np.argmax(rowsum)
band=a[max(0,rr-8):rr+9]
colw=band.sum(0)/S  # width in pt per column
on=colw>0.9
ws=colw[on]
print('angle',round(ang,1),'n on cols',on.sum(),'median width pt',round(float(np.median(ws)),3),'p10/p90',round(float(np.percentile(ws,10)),3),round(float(np.percentile(ws,90)),3))
# same for a horizontal d3 leader (S_lead04) and vertical pompeii line for calibration
def hw(box, vertical=False):
    x0,x1,y0,y1=box
    c=np.array(ov.crop([int(x0*S),int(y0*S),int(x1*S),int(y1*S)]).split()[3]).astype(float)/255
    s=c.sum(1 if vertical else 0)/S
    s=s[s>0.9]; return round(float(np.median(s)),3)
print('d3 lead04', hw([375,388,1229,1235]))
print('d3 lead06', hw([367,386,1255,1262]))
print('d2 lead02', hw([131,139,1004,1010]))
print('pompeii', hw([720,728,1500,1545],vertical=True))
print('underline core1', hw([540,630,431,437]))
