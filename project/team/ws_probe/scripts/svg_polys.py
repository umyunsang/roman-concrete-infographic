"""Figma SVG(프레임 좌표 = pt)에서 채워진 도형을 다각형 점 목록으로 뽑는다(절대 M/L/H/V/C/Q/Z)."""
import re, json, sys

TOK = re.compile(r'[MLHVCQZmlhvcqz]|-?\d*\.?\d+(?:e-?\d+)?')


def bez(p0, p1, p2, p3, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return out


def parse_d(d):
    toks = TOK.findall(d); i = 0; cmd = None
    subs, cur, pos, start = [], [], (0, 0), (0, 0)
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd in 'Zz':
                if cur: subs.append((cur, True)); cur = []
                pos = start; continue
        if cmd == 'M':
            if cur: subs.append((cur, False))
            pos = (num(), num()); start = pos; cur = [pos]; cmd = 'L'
        elif cmd == 'L':
            pos = (num(), num()); cur.append(pos)
        elif cmd == 'H':
            pos = (num(), pos[1]); cur.append(pos)
        elif cmd == 'V':
            pos = (pos[0], num()); cur.append(pos)
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); p = (num(), num())
            cur += bez(pos, c1, c2, p); pos = p
        elif cmd == 'Q':
            c = (num(), num()); p = (num(), num())
            c1 = (pos[0] + 2/3*(c[0]-pos[0]), pos[1] + 2/3*(c[1]-pos[1])); c2 = (p[0] + 2/3*(c[0]-p[0]), p[1] + 2/3*(c[1]-p[1]))
            cur += bez(pos, c1, c2, p); pos = p
        else:
            raise ValueError(f'unsupported {cmd}')
    if cur: subs.append((cur, False))
    return subs


def extract(path):
    s = open(path, encoding='utf-8').read()
    items = []
    for m in re.finditer(r'<path ([^>]*?)/?>', s):
        a = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(1)))
        if 'd' not in a:
            continue
        subs = parse_d(a['d'])
        for k, (pts, closed) in enumerate(subs):
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            items.append({'id': a.get('id', ''), 'sub': k, 'fill': a.get('fill', 'none'), 'stroke': a.get('stroke', 'none'),
                          'sw': float(a.get('stroke-width', 0) or 0), 'closed': closed,
                          'bbox': [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)],
                          'pts': [[round(x, 2), round(y, 2)] for x, y in pts]})
    return items


if __name__ == '__main__':
    items = extract(sys.argv[1])
    json.dump(items, open(sys.argv[2], 'w'), ensure_ascii=False)
    for it in items:
        if it['fill'] not in ('none',) and it['bbox'] != [0, 0, 1191, 1684]:
            print(it['id'], it['sub'], it['fill'], it['stroke'], 'closed' if it['closed'] else 'open', it['bbox'], len(it['pts']))
