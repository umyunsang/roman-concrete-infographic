"""SVG 면을 '공유 꼭짓점'으로 묶어 물체 단위로 나눈다(코드로 그린 아이소 도형은 한 물체의 면이 꼭짓점을 정확히 공유)."""
import json, sys
from PIL import Image, ImageDraw


def objects(path, tol=0.25, min_shared=2):
    it = [i for i in json.load(open(path)) if i['fill'] != 'none' and i['closed']]
    it = [i for i in it if not (i['bbox'][2] - i['bbox'][0] > 1100 and i['bbox'][3] - i['bbox'][1] > 250)]
    key = lambda p: (round(p[0] / tol), round(p[1] / tol))
    owners = {}
    for idx, f in enumerate(it):
        for p in {key(p) for p in f['pts']}:
            owners.setdefault(p, []).append(idx)
    par = list(range(len(it)))
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    shared = {}
    for p, ids in owners.items():
        for a in ids:
            for b in ids:
                if a < b:
                    shared[(a, b)] = shared.get((a, b), 0) + 1
    for (a, b), n in shared.items():
        if n >= min_shared:
            par[find(a)] = find(b)
    groups = {}
    for i in range(len(it)):
        groups.setdefault(find(i), []).append(it[i])
    out = []
    for g in groups.values():
        xs0 = min(i['bbox'][0] for i in g); ys0 = min(i['bbox'][1] for i in g)
        xs1 = max(i['bbox'][2] for i in g); ys1 = max(i['bbox'][3] for i in g)
        out.append({'bbox': [xs0, ys0, xs1, ys1], 'n': len(g), 'fills': sorted({i['fill'] for i in g}), 'ids': [i['id'] for i in g]})
    return sorted(out, key=lambda c: (round(c['bbox'][1] / 20), c['bbox'][0]))


if __name__ == '__main__':
    name = sys.argv[1]
    obs = objects(f'ref/svg/{name}.json')
    json.dump(obs, open(f'ref/svg/{name}_objects.json', 'w'))
    im = Image.open(f'ref/layers/{name}.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    for k, c in enumerate(obs):
        x0, y0, x1, y1 = c['bbox']
        d.rectangle([x0, y0, x1, y1], outline=(220, 30, 30, 255))
        d.text((x0 + 1, y0 + 1), str(k), fill=(0, 0, 220, 255))
    bg.convert('RGB').save(f'ref/svg/{name}_objects.png')
    print(name, len(obs), 'objects')
