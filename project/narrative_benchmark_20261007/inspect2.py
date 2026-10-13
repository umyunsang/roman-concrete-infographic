import sys, pypdf, re, zlib
r = pypdf.PdfReader(sys.argv[1])
print('trailer keys', list(r.trailer.keys()), r.trailer.get('/ID'))
pg = r.pages[0]
c = pg['/Contents']
print('contents raw', type(c), c)
co = c.get_object()
print(type(co))
try:
    data = co.get_data()
except Exception as e:
    print('err', e); data=b''
print('len', len(data))
open(sys.argv[2],'wb').write(data)
md = r.trailer['/Root']['/Metadata'].get_object().get_data().decode('utf8','replace')
print(md[:3000])
res = pg['/Resources']
print('Properties', res.get('/Properties'))
for n,v in res['/XObject'].get_object().items():
    vo=v.get_object()
    print(n, {k:str(x)[:80] for k,x in vo.items() if k not in ('/Length',)})
