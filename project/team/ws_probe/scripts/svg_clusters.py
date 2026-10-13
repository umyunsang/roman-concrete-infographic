"""SVG 채운 면들을 경계 상자 겹침으로 묶어 '물체 덩어리'를 찾는다."""
import json, sys

def clusters(path, pad=0.6, skip_full=True):
    it = [i for i in json.load(open(path)) if i['fill'] != 'none' and i['closed']]
    if skip_full:
        it = [i for i in it if not (i['bbox'][2] - i['bbox'][0] > 1100 and i['bbox'][3] - i['bbox'][1] > 250)]
    n = len(it); par = list(range(n))
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a in range(n):
        A = it[a]['bbox']
        for b in range(a + 1, n):
            B = it[b]['bbox']
            if A[0] - pad <= B[2] and B[0] - pad <= A[2] and A[1] - pad <= B[3] and B[1] - pad <= A[3]:
                par[f(a)] = f(b)
    groups = {}
    for i in range(n):
        groups.setdefault(f(i), []).append(it[i])
    out = []
    for g in groups.values():
        xs0 = min(i['bbox'][0] for i in g); ys0 = min(i['bbox'][1] for i in g)
        xs1 = max(i['bbox'][2] for i in g); ys1 = max(i['bbox'][3] for i in g)
        out.append({'bbox': [xs0, ys0, xs1, ys1], 'n': len(g), 'fills': sorted({i['fill'] for i in g}), 'faces': g})
    return sorted(out, key=lambda c: (c['bbox'][1], c['bbox'][0]))

if __name__ == '__main__':
    cs = clusters(sys.argv[1])
    json.dump(cs, open(sys.argv[2], 'w'))
    for k, c in enumerate(cs):
        b = c['bbox']; print(k, [round(v) for v in b], 'w', round(b[2] - b[0]), 'h', round(b[3] - b[1]), 'faces', c['n'])
