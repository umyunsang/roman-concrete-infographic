"""catalog.json 항목 갱신: python3 catalog_set.py <id> '<json 필드>'  (같은 id는 병합)"""
import json, sys, datetime
P = '/Users/um-yunsang/Documents/로마콘크리트_3D/assets/catalog.json'
d = json.load(open(P))
key = 'meshy_queue' if len(sys.argv) > 3 and sys.argv[3] == 'queue' else 'assets'
d.setdefault(key, [])
rid, fields = sys.argv[1], json.loads(sys.argv[2])
for e in d[key]:
    if e['id'] == rid:
        e.update(fields)
        break
else:
    d[key].append({'id': rid, **fields})
d['updated'] = datetime.datetime.now().isoformat(timespec='minutes')
json.dump(d, open(P, 'w'), ensure_ascii=False, indent=1)
print('ok', rid, key)
