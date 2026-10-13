import json,sys
d=json.load(open(sys.argv[1]))
for t in d['texts']:
    id,box,rot,al,segs=t
    s=" | ".join(f"[{x[1].replace('Sans KR ','S-').replace('Serif KR ','SR-')} {x[2]} lh{x[3]} tr{x[4]} {x[5]}] {x[0]!r}" for x in segs)
    print(id, [round(v,1) for v in box], rot, al, s)
