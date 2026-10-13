import sys, re, hashlib
from pypdf import PdfReader
from pypdf.generic import IndirectObject
p = sys.argv[1]
r = PdfReader(p)
root = r.trailer['/Root']
print("Trailer keys", list(r.trailer.keys()), "ID" in str(r.trailer.keys()))
print("Info", {k: str(v)[:80] for k,v in r.trailer['/Info'].items()})
oi = root.get('/OutputIntents')
print("OutputIntents:", oi)
if oi:
    for o in oi:
        o = o.get_object()
        print({k:(str(v)[:100]) for k,v in o.items() if k!='/DestOutputProfile'})
        prof = o['/DestOutputProfile'].get_object()
        data = prof.get_data()
        print("profile N", prof.get('/N'), "len", len(data), "md5", hashlib.md5(data).hexdigest())
        icc = open(sys.argv[2],'rb').read()
        print("matches PSOcoated_v3.icc:", data==icc, hashlib.md5(icc).hexdigest())
        print("profile desc", data[0:132][36:40], data[12:20], data[16:20])
md = root.get('/Metadata')
if md:
    x = md.get_object().get_data().decode('utf8','replace')
    for tag in ['pdfxid:GTS_PDFXVersion','pdf:Trapped','xmp:CreateDate','dc:title','pdf:Producer','xmpMM:DocumentID','xmpMM:InstanceID','xmp:ModifyDate','xmp:MetadataDate', 'pdfx:GTS_PDFXVersion']:
        m = re.search(tag+r'[^<>]*?>([^<]*)<', x) or re.search(tag+r'="([^"]*)"', x)
        print(tag, m.group(1) if m else None)
page = r.pages[0]
for k in ['/MediaBox','/CropBox','/BleedBox','/TrimBox','/ArtBox','/Group','/Rotate']:
    print(k, page.get(k))
res = page['/Resources']
print("Resource keys", list(res.keys()))
def walk_cs(res, depth=0, seen=set()):
    out = {}
    cs = res.get('/ColorSpace')
    if cs:
        for k,v in cs.get_object().items():
            vv = v.get_object()
            out[k] = str(vv)[:120]
    return out
print("ColorSpaces:", walk_cs(res))
xo = res.get('/XObject')
if xo:
    for k,v in xo.get_object().items():
        o = v.get_object()
        print("XObject", k, o.get('/Subtype'), o.get('/ColorSpace') if not isinstance(o.get('/ColorSpace'), IndirectObject) else o.get('/ColorSpace').get_object(), o.get('/Width'), o.get('/Height'), o.get('/Filter'), 'SMask' in str(o.keys()), o.get('/Group'), o.get('/Decode'))
        if o.get('/Subtype')=='/Form':
            print("  form res", list(o.get('/Resources',{}).keys()))
eg = res.get('/ExtGState')
if eg:
    for k,v in eg.get_object().items():
        print("ExtGState", k, dict(v.get_object()))
# content stream operators
c = page.get_contents().get_data()
print("content length", len(c))
ops = {}
for op in [b' rg', b' RG', b' k', b' K', b' g', b' G', b' sc', b' scn', b' SC', b' SCN', b' cs', b' CS', b' Do', b' gs', b' BT', b' sh']:
    ops[op.decode().strip()] = len(re.findall(re.escape(op)+rb'\s', c))
print(ops)
cs_used = set(re.findall(rb'(/\w+) cs', c)) | set(re.findall(rb'(/\w+) CS', c))
print("cs used", cs_used)
