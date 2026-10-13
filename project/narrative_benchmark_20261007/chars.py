import json,unicodedata,re
spec=json.load(open('../nb_work/review_loop/text_spec_r9.json'))['texts']
cps={}
for t in spec:
    text=''.join(s[0] for s in t[4])
    for ch in text:
        if not ('가'<=ch<='힣') and not ch.isalnum() and ch not in ' \n':
            cps.setdefault((ch,hex(ord(ch)),unicodedata.name(ch,'?')),[]).append(t[0])
    lines=text.split('\n')
    if len(lines)>1 or len(text)>12:
        print(t[0],[ (l,len(l)) for l in lines])
for k,v in cps.items(): print(k,len(v),v[:6])
# middle dot contexts
for t in spec:
    text=''.join(s[0] for s in t[4])
    for m in re.finditer('·',text):
        a=text[max(0,m.start()-1)]; b=text[m.end()] if m.end()<len(text) else ''
        print(t[0], repr(text[max(0,m.start()-6):m.end()+6]), 'spaced' if a==' ' else 'attached')
