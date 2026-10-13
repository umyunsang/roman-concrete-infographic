import sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
md = r.trailer['/Root']['/Metadata'].get_object()
print(md.get_data().decode('utf8','replace'))
print("Root keys", list(r.trailer['/Root'].keys()))
print("Version header", r.pdf_header)
