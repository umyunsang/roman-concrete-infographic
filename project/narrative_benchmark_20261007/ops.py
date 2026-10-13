import sys, re, collections
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
c = r.pages[0].get_contents().get_data()
# tokenise roughly
toks = re.findall(rb'[-+]?\d*\.?\d+|/[^\s/\[\]()<>]+|[A-Za-z\'"*]+|\[|\]', c)
stack=[]; cur=None; curS=None; counts=collections.Counter(); scounts=collections.Counter(); lw=collections.Counter()
order=[]
ctm_ops=collections.Counter()
for t in toks:
    if re.match(rb'^[-+]?\d*\.?\d+$', t): stack.append(float(t)); continue
    if t.startswith(b'/'): stack.append(t); continue
    op=t.decode()
    if op=='k':
        cur=tuple(round(x*100,1) for x in stack[-4:]); order.append(cur)
    elif op=='K':
        curS=tuple(round(x*100,1) for x in stack[-4:])
    elif op in ('f','f*','F','B','B*','b','b*'):
        counts[cur]+=1
    elif op in ('S','s'):
        scounts[curS]+=1
    elif op=='w':
        lw[stack[-1] if stack else None]+=1
    ctm_ops[op]+=1
    stack=[]
print("fill colors (CMYK %) -> fill ops:")
for k,v in sorted(counts.items(), key=lambda x:-x[1]): print(" ", k, "TAC=%.1f"%sum(k) if k else '', v)
print("stroke colors:", scounts)
print("linewidths:", lw.most_common(10))
print("ops:", ctm_ops.most_common(30))
