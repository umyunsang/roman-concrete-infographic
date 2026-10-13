import json,sys
d=json.load(open(sys.argv[1]))
for t in d['texts']:
    id_,box,rot,al,segs=t
    s=' | '.join(f"{x[0]!r} {x[1].split()[-1] if x[1] else ''} {x[2]} {x[3]} {x[5]}" for x in segs)
    print(id_, [round(v,1) for v in box], rot, al, s)
print({k:v for k,v in d.items() if k!='texts'})
