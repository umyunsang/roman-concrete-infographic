"""Aggregate object-round journal results into findings_by_asset.json/.md under objDir."""
import json, sys, collections
J, OUT = sys.argv[1], sys.argv[2]
by = collections.defaultdict(dict); tally = collections.defaultdict(collections.Counter)
for line in open(J):
    d = json.loads(line)
    if d.get('type') != 'result' or not d.get('result'): continue
    r = d['result']
    for a in r['assets']:
        by[a['id']][r['field']] = {'grade': a['grade'], 'findings': a['findings'], 'batch': r['batch']}
        tally[r['field']][a['grade']] += 1
json.dump(by, open(OUT + '/findings_by_asset.json', 'w'), ensure_ascii=False, indent=1)
lines = ['# 물체 심사 지적 (자산별)', '', '| 분야 | 등급 분포 |', '|---|---|']
lines += [f'| {k} | {dict(v)} |' for k, v in sorted(tally.items())]
for aid in sorted(by):
    fs = by[aid]
    bad = {k: v for k, v in fs.items() if v['grade'] != 'AAA' or v['findings']}
    if not bad: continue
    lines.append(f"\n## {aid} — " + ', '.join(f"{k}:{v['grade']}" for k, v in sorted(fs.items())))
    for k, v in sorted(bad.items()):
        for f in v['findings']:
            lines.append(f"- **[{f['severity']}] {k} {f['id']}** {f['title']}\n  - 증거: {f['evidence']}\n  - 해법({f['fix_tool']}): {f['fix']}")
open(OUT + '/findings_by_asset.md', 'w').write('\n'.join(lines) + '\n')
print(json.dumps({k: dict(v) for k, v in tally.items()}, ensure_ascii=False))
nb = sum(1 for a in by.values() for v in a.values() for f in v['findings'] if f['severity'] != 'minor')
print('assets', len(by), 'blocker+major', nb)
