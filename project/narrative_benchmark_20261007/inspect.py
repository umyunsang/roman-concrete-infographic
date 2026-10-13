import sys, pypdf, re, hashlib
from pypdf.generic import IndirectObject, DictionaryObject, ArrayObject, NameObject, StreamObject
p = sys.argv[1]
r = pypdf.PdfReader(p)
root = r.trailer['/Root']
print('Root keys', list(root.keys()))
print('Info', {k: str(v)[:80] for k,v in (r.trailer.get('/Info') or {}).items()})
oi = root.get('/OutputIntents')
if oi:
    for o in oi:
        o = o.get_object()
        print('OI', {k:(str(v)[:100]) for k,v in o.items() if k!='/DestOutputProfile'})
        prof = o['/DestOutputProfile'].get_object()
        data = prof.get_data()
        print(' profile keys', {k:str(v) for k,v in prof.items()}, 'len', len(data), 'md5', hashlib.md5(data).hexdigest())
        print(' local icc md5', hashlib.md5(open(sys.argv[2],'rb').read()).hexdigest() if len(sys.argv)>2 else '')
md = root.get('/Metadata')
if md:
    x = md.get_object().get_data().decode('utf8','replace')
    for tag in ['GTS_PDFXVersion','pdfxid','Trapped','CreateDate','ModifyDate','DocumentID','InstanceID','RenditionClass','title','Producer','CreatorTool','VersionID']:
        for m in re.finditer(r'<[^>]*%s[^>]*>[^<]*'%tag, x):
            print(' XMP', m.group(0)[:160])
        for m in re.finditer(r'%s="[^"]*"'%tag, x):
            print(' XMPattr', m.group(0)[:160])
pg = r.pages[0]
print('page keys', list(pg.keys()))
for k in ['/MediaBox','/CropBox','/BleedBox','/TrimBox','/ArtBox']:
    print(k, pg.get(k))
print('Group', pg.get('/Group'))
res = pg['/Resources']
print('res keys', list(res.keys()))
seen=set()
cs_count={}
def walk(o, path, depth=0):
    if depth>40: return
    if isinstance(o, IndirectObject):
        key=(o.idnum,o.generation)
        if key in seen: return
        seen.add(key)
        o=o.get_object()
    if isinstance(o, DictionaryObject):
        for k,v in o.items():
            if k in ('/Parent',): continue
            if k in ('/ColorSpace','/CS','/BaseColorSpace','/Alternate'):
                vv = v.get_object() if isinstance(v,IndirectObject) else v
                s=str(vv)[:120]
                if isinstance(vv, DictionaryObject):
                    for kk,cc in vv.items():
                        cc2 = cc.get_object() if isinstance(cc,IndirectObject) else cc
                        desc=str(cc2)[:100]
                        if isinstance(cc2, ArrayObject) and len(cc2)>1 and cc2[0]=='/ICCBased':
                            desc='ICCBased N=%s'%cc2[1].get_object().get('/N')
                        cs_count[(path+k+kk, desc)] = cs_count.get((path+k+kk,desc),0)+1
                else:
                    if isinstance(vv, ArrayObject) and len(vv)>1 and vv[0]=='/ICCBased':
                        s='ICCBased N=%s'%vv[1].get_object().get('/N')
                    cs_count[(k,s)] = cs_count.get((k,s),0)+1
            walk(v, path, depth+1)
    elif isinstance(o, ArrayObject):
        for v in o: walk(v, path, depth+1)
walk(pg, '')
for k,v in sorted(cs_count.items(), key=lambda x:-x[1])[:40]:
    print('CS', v, k)
# xobjects
xo = res.get('/XObject')
if xo:
    xo=xo.get_object()
    for n,v in xo.items():
        vo=v.get_object()
        print('XO', n, vo.get('/Subtype'), vo.get('/Width'), vo.get('/Height'), vo.get('/ColorSpace') if not isinstance(vo.get('/ColorSpace'),IndirectObject) else vo.get('/ColorSpace').get_object(), vo.get('/Filter'), vo.get('/BBox'), 'Group', vo.get('/Group'), 'Decode', vo.get('/Decode'))
egs = res.get('/ExtGState')
if egs:
    egs=egs.get_object()
    for n,v in egs.items():
        print('GS', n, {k:str(x)[:60] for k,x in v.get_object().items()})
cont = pg.get_contents()
data = cont.get_data() if cont else b''
print('content len', len(data))
ops = {}
for op in [b' rg', b' RG', b' k', b' K', b' g', b' G', b' sc', b' scn', b' SC', b' SCN', b' cs', b' CS', b' Do', b' gs', b' sh', b' BT', b' Tf']:
    ops[op.decode()] = len(re.findall(re.escape(op)+rb'[\s\n]', data))
print(ops)
print(data[:1500].decode('latin1'))
