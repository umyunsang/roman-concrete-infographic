"""compose_assets.py - Pillow side of render_assets.py (run with: uv run -q --no-project --with pillow --with numpy
python -I compose_assets.py <compose_jobs.json>).

Crop arithmetic is the same as scripts/crop.py: alpha-composite map + overlay pass, s = image width / 1191,
crop (round(x0*s), round(y0*s), round(x1*s), round(y1*s)), resize to (round(w*z/s), round(h*z/s)) LANCZOS.
Isolated passes are border renders cropped to iso_px_box, so their crop is offset by the box origin.
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

spec = json.loads(Path(sys.argv[1]).read_text())
FW = spec['frame_w']
full = Image.alpha_composite(Image.open(spec['full_map']).convert('RGBA'),
                             Image.open(spec['full_overlay']).convert('RGBA')).convert('RGB')
s = full.width / FW
winx, winy = spec['win']
checks = {'full_size_px': list(full.size), 'full_size_expected': [winx, winy], 'full_size_ok': list(full.size) == [winx, winy]}


def crop_resize(im, box_pt, z, off=(0, 0)):
    x0, x1, y0, y1 = box_pt
    c = im.crop((round(x0 * s) - off[0], round(y0 * s) - off[1], round(x1 * s) - off[0], round(y1 * s) - off[1]))
    return c.resize((round(c.width * z / s), round(c.height * z / s)), Image.Resampling.LANCZOS)


def load_iso(mp, op, pxb):
    m = Image.open(mp).convert('RGBA'); o = Image.open(op).convert('RGBA')
    want = (pxb[1] - pxb[0], pxb[3] - pxb[2])
    if m.size != want or o.size != want:
        raise SystemExit(f'border render size {m.size}/{o.size} != expected {want} for {mp}')
    return Image.alpha_composite(m, o).convert('RGB')


res = {'assets': {}, 'checks': checks}
for j in spec['jobs']:
    z = j['scale']
    ctx = crop_resize(full, j['crop_pt'], z)
    iso_full = load_iso(j['iso_map'], j['iso_overlay'], j['iso_px_box'])
    iso = crop_resize(iso_full, j['crop_pt'], z, off=(j['iso_px_box'][0], j['iso_px_box'][2]))
    if iso.size != ctx.size:
        raise SystemExit(f'{j["id"]}: isolated {iso.size} != context {ctx.size}')
    Path(j['out_context']).parent.mkdir(parents=True, exist_ok=True)
    ctx.save(j['out_context']); iso.save(j['out_isolated'])
    # isolated background = world colour of the map pass; count pixels that differ from it
    a = np.asarray(iso).astype(int)
    corner = np.asarray(Image.open(j['iso_map']).convert('RGB')).reshape(-1, 3)
    vals, cnts = np.unique(corner, axis=0, return_counts=True)
    bgc = vals[cnts.argmax()]
    nonbg = int((np.abs(a - bgc).max(-1) > 3).sum())
    res['assets'][j['id']] = {'size': list(ctx.size), 'iso_nonbg_px': nonbg, 'iso_bg_rgb': bgc.tolist()}

# self-test: border renders with nothing hidden vs full render, same pixel box
st = []
for t in spec['selftests']:
    pxb = t['px_box']
    b = load_iso(t['map'], t['overlay'], pxb)
    f = full.crop((pxb[0], pxb[2], pxb[1], pxb[3]))
    d = np.abs(np.asarray(b).astype(int) - np.asarray(f).astype(int))
    st.append({'id': t['id'], 'px_box': pxb, 'max_abs_diff': int(d.max()), 'mean_abs_diff': round(float(d.mean()), 4),
               'pct_px_diff_gt_2': round(100 * float((d.max(-1) > 2).mean()), 3)})
res['selftests'] = st

# contact sheet: 3 columns, each cell = label + context thumb + isolated thumb
font_path = spec.get('font')
def font(sz):
    try:
        return ImageFont.truetype(font_path, sz) if font_path else ImageFont.load_default()
    except OSError:
        return ImageFont.load_default()
F1, F2 = font(17), font(13)
TW, TH, PAD, LAB = 270, 210, 10, 46
CW = 2 * TW + 3 * PAD
CH = LAB + TH + PAD
cols = 3
rows = -(-len(spec['jobs']) // cols)
title_h = 50
sheet = Image.new('RGB', (cols * CW + PAD, title_h + rows * CH + PAD), (250, 248, 244))
d = ImageDraw.Draw(sheet)
d.text((PAD, 12), f'심사 단위 자산 {len(spec["jobs"])}개 · 왼쪽 = 포스터 맥락 크롭, 오른쪽 = 단독 렌더(같은 상자) · '
                  f'{Path(spec.get("blend", "")).name}', fill=(40, 36, 30), font=F1)
for k, j in enumerate(spec['jobs']):
    r, c = divmod(k, cols)
    x, y = PAD + c * CW, title_h + r * CH
    d.rectangle([x, y, x + CW - PAD, y + CH - 4], outline=(200, 192, 180))
    d.text((x + 6, y + 4), f'{k + 1:02d} {j["id"]}  [{j["role"]}]', fill=(30, 28, 24), font=F2)
    d.text((x + 6, y + 23), j['name'][:44], fill=(80, 74, 66), font=F2)
    for i, pth in enumerate((j['out_context'], j['out_isolated'])):
        im = Image.open(pth).convert('RGB')
        im.thumbnail((TW, TH), Image.Resampling.LANCZOS)
        ox = x + PAD // 2 + i * (TW + PAD) + (TW - im.width) // 2
        oy = y + LAB + (TH - im.height) // 2
        sheet.paste(im, (ox, oy))
sheet.save(spec['contact_sheet'])
res['contact_sheet_size'] = list(sheet.size)
Path(spec['result']).write_text(json.dumps(res, ensure_ascii=False, indent=1))
print('COMPOSE', len(spec['jobs']), 'assets', 'selftests', st)
