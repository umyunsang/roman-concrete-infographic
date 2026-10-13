import sys, re, collections
from pypdf import PdfReader
r=PdfReader(sys.argv[1]); p=r.pages[0]
print('page keys', list(p.keys()))
props=p['/Resources']['/Properties']
items=list(props.get_object().items())
print('Properties count', len(items)); 
for k,v in items[:3]: print(' ',k, dict(v.get_object()))
c=p.get_contents().get_data()
tags=collections.Counter(re.findall(rb'(/\w+)\s*(?:/\w+|<<[^>]*>>)\s*BDC', c))
print('BDC tags', tags)
print(re.findall(rb'/\w+\s*(?:/\w+|<<[^>]*>>)\s*BDC', c)[:3])
