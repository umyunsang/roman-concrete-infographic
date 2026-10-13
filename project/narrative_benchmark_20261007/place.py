import sys, re
from pypdf import PdfReader
r = PdfReader(sys.argv[1])
c = r.pages[0].get_contents().get_data()
for m in re.finditer(rb'((?:[-\d.]+\s+){6}cm)\s*(?:[^\n]*\n){0,3}?\s*(/R\d+)\s+Do', c):
    print(m.group(1).decode(), m.group(2).decode())
i = c.find(b'Do')
print(c[:600].decode('latin1'))
